from LokiPy import Requests
import json
import numpy as np
import sqlite3
import src.utils.parseJson as parseJson


#################################################################
########################### DATABASE ############################
#################################################################

class Database:
    def __init__(self, database_filename, chain_full_url, api_key=None):
        self.fileName = database_filename
        self.chainFullUrl = chain_full_url
        self.chainApiKey = api_key
        self.LokiObj = Requests.LokiPy()
        self.conn = None
        self.cur = None


    def parseAddressesFromTransactionAndUpdateDB(self, transactionResult):
        print("----------------Entered parseAddressesFromTransactionAndUpdateDB")
        addressesSet = set()
        if "to" in transactionResult:
            for toInstance in transactionResult["to"]:
                try:
                    addressesSet.add(toInstance["proposition"])
                except Exception as e:
                    print("Could not get proposition from transaction: ", e)
                    raise
        if "from" in transactionResult:
            for fromInstance in transactionResult["from"]:
                try:
                    addressesSet.add(fromInstance["proposition"])
                except Exception as e:
                    print("Could not get proposition from transaction: ", e)
                    raise
        ###for each unqiue address in transaction, update addresses table, appending the txHash to the string of txHashes in the transactions column
        for address in addressesSet:
            c = self.cur.execute("SELECT transactions FROM addresses WHERE publicKey=?", (address,))
            data = c.fetchall()
            newTransactionString = ""
            if len(data) == 0:
                newTransactionString = transactionResult["txHash"]
                self.cur.execute("INSERT INTO addresses VALUES (?,?)", (address, newTransactionString))
            else:
                ###Will only ever be a single value list if not empty
                for transactionString in data:
                    newTransactionString = transactionString[0] + "," + transactionResult["txHash"]
                    self.cur.execute("UPDATE addresses SET transactions=? WHERE publicKey=?",
                    (newTransactionString, address))



    def parseAssetsFromTransactionAndUpdateDB(self, transactionResult):
        print("----------------Entered parseAssetsFromTransactionAndUpdateDB")
        if "assetCode" in transactionResult:
            try:
                c = self.cur.execute("SELECT transactions FROM assets WHERE assetCode=?", (transactionResult["assetCode"],))
                data = c.fetchall()
                if len(data) == 0:
                    self.cur.execute("INSERT INTO assets VALUES (?,?)", (transactionResult["assetCode"],transactionResult["txHash"]))
                else:
                    for transactionString in data:
                        newTransactionString = transactionString[0] + "," + transactionResult["txHash"]
                        self.cur.execute("UPDATE assets SET transactions=? WHERE assetCode=?",
                        (newTransactionString, transactionResult["assetCode"]))
            except Exception as e:
                print("Could not insert transaction into assets table: ", e)
                raise



    def parseTransactionsFromBlockAndUpdateDB(self, txsArray):
        print(">>>>>>>>>>>>>>>>>>>>>>Entered parseTransactionsFromBlockAndUpdateDB")
        for tx in txsArray:
            try:
                transactionResult = self.LokiObj.getTransactionById(tx["txHash"])["result"]
                try:
                    self.cur.execute("INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?,?,?,?)", (transactionResult["txHash"], transactionResult["timestamp"], transactionResult["blockNumber"], transactionResult["blockHash"], parseJson.createToAddressesString(transactionResult),
                    parseJson.createFromAddressesString(transactionResult),
                    parseJson.createNewBoxesString(transactionResult),
                    parseJson.createBoxesToRemoveString(transactionResult),
                    transactionResult["fee"],
                    parseJson.createSignaturesString(transactionResult),
                    json.dumps(transactionResult)))
                except Exception as e:
                    print("Could not insert block into blocks table: ", e)
                    raise
                ###updating the addresses table
                self.parseAddressesFromTransactionAndUpdateDB(transactionResult)
                ###updating assets table if transaction contains the assetCode field in its json
                if "assetCode" in transactionResult:
                    self.parseAssetsFromTransactionAndUpdateDB(transactionResult)
            except Exception as e:
                print("Getting transaction by id and parsing result failed: ", e)
                raise

        # c = self.cur.execute("SELECT * FROM transactions WHERE txHash=?", (transactionResult["txHash"],))
        # data = c.fetchall()


    def init(self):
        ### Settings the url and apiKey of the database's LokiPy instance
        print("=====================Initializing db=========================")
        self.LokiObj.setUrl(self.chainFullUrl)
        if self.chainApiKey is not None:
            self.LokiObj.setApiKey(self.chainApiKey)
        ####query chain for history list#####
        history = np.array(self.LokiObj.printChain()["result"]["history"].split(','))
        ###Getting topmost block
        historyInstance = self.LokiObj.getBlockById(history[-1])["result"]
        # Querying parentId of 1st block returns 500 error None.get
        # printJson(LokiObj.getBlockById("4vJ9JU1bJJE96FWSJKvHsmmFADCg4gpZQff4P3bkLKi"))

        ###database connection intialization####
        self.conn = sqlite3.connect(self.fileName)
        self.cur = self.conn.cursor()

        create_transactions_table = """ CREATE TABLE IF NOT EXISTS transactions (
                                            txHash text PRIMARY KEY,
                                            timestamp text NOT NULL,
                                            blockNumber integer NOT NULL,
                                            blockHash text NOT NULL,
                                            toAddresses text,
                                            fromAddresses text,
                                            newBoxes text,
                                            boxesToRemove text,
                                            fee integer,
                                            signatures text,
                                            txJson text NOT NULL
                                        ); """
        create_blocks_table = """ CREATE TABLE IF NOT EXISTS blocks (
                                        blockNumber integer PRIMARY KEY,
                                        blockHash text NOT NULL,
                                        timestamp text NOT NULL,
                                        signature text NOT NULL,
                                        txs text,
                                        parentId text NOT NULL,
                                        blockJson text NOT NULL
                                    ); """
        create_addresses_table = """ CREATE TABLE IF NOT EXISTS addresses (
                                        publicKey text PRIMARY KEY,
                                        transactions text
                                    ); """
        create_assets_table = """ CREATE TABLE IF NOT EXISTS assets (
                                        assetCode text PRIMARY KEY,
                                        transactions text
                                    ); """
        self.cur.execute(create_blocks_table)
        self.cur.execute(create_transactions_table)
        self.cur.execute(create_addresses_table)
        self.cur.execute(create_assets_table)
        ###blocks Table###
        self.cur.execute("INSERT INTO blocks VALUES (?,?,?,?,?,?,?)", (historyInstance["blockNumber"], historyInstance["id"], historyInstance["timestamp"], historyInstance["signature"], parseJson.createTxsString(historyInstance["txs"]), historyInstance["parentId"], json.dumps(historyInstance)))
        ###transactions Table###
        self.parseTransactionsFromBlockAndUpdateDB(historyInstance["txs"])

        while historyInstance["parentId"] != None:
            try:
                # print(historyInstance["blockNumber"])
                historyInstance = self.LokiObj.getBlockById(historyInstance["parentId"])["result"]
                self.cur.execute("INSERT INTO blocks VALUES (?,?,?,?,?,?,?)", (historyInstance["blockNumber"], historyInstance["id"], historyInstance["timestamp"], historyInstance["signature"], parseJson.createTxsString(historyInstance), historyInstance["parentId"], json.dumps(historyInstance)))
                self.parseTransactionsFromBlockAndUpdateDB(historyInstance["txs"])
            except:
                historyInstance["parentId"] = None

        self.conn.commit()
        self.conn.close()
        print("Finished initializing db")



    def queryAndUpdate(self):
        print("======================Entered queryAndUpdate=======================")
        history = np.array(self.LokiObj.printChain()["result"]["history"].split(','))
        ###database connection intialization####
        self.conn = sqlite3.connect(self.fileName)
        self.cur = self.conn.cursor()
        currentIndex = -1
        ###Getting topmost block
        historyInstance = self.LokiObj.getBlockById(history[currentIndex])["result"]
        # c = self.curr.execute("SELECT * FROM blocks");
        # for row in c:
        #     print(row);
        c = self.cur.execute("SELECT * FROM blocks WHERE blockNumber=?", (historyInstance["blockNumber"],))
        data = c.fetchall()
        ###Accessing parent of topmost block until a block is queried that already exists in db
        while len(data) < 1:
            self.cur.execute("INSERT INTO blocks VALUES (?,?,?,?,?,?,?)", (historyInstance["blockNumber"], historyInstance["id"], historyInstance["timestamp"], historyInstance["signature"], parseJson.createTxsString(historyInstance), historyInstance["parentId"], json.dumps(historyInstance)))
            self.parseTransactionsFromBlockAndUpdateDB(historyInstance["txs"])
            self.parseAddressesFromTransactionAndUpdateDB(historyInstance["txs"])
            currentIndex = currentIndex - 1
            ###Getting parent of topmost block
            historyInstance = self.LokiObj.getBlockById(history[currentIndex])["result"]
            c = self.cur.execute("SELECT * FROM blocks WHERE blockNumber=?", (historyInstance["blockNumber"],))
            data = c.fetchall()
        self.conn.commit()
        self.conn.close()
