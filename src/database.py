from LokiPy import Requests
import json
import numpy as np
import sqlite3

def printJson(jsonData):
    print(json.dumps(jsonData, indent = 4))

###parses txs array from a block and converts it to comma separated txHash string###
def createTxsString(txs):
    txString = ""
    for tx in txs:
        try:
            txString = txString + tx["txHash"] + ","
        except Exception as e:
            print("Could not get transaction hash from block: ", e)
            raise
    if txString is not "":
        txString = txString[0:len(txString)-1]
    return txString

###parses a transaction and converts it to comma separated addresses string of to addresses###
###NOTE: does not check unique address
###Returns a string or None since toAddresses column accepts NULL values
def createToAddressesString(transactionResult):
    propString = ""
    if "to" in transactionResult:
        propString = ""
        for toInstance in transactionResult["to"]:
            try:
                propString = propString + toInstance["proposition"] + ","
            except Exception as e:
                print("Could not get proposition from transaction: ", e)
                raise

        return propString[0:len(propString)-1]

    else:
        return None

###parses a transaction and converts it to comma separated addresses string of to addresses###
###NOTE: does not check unique address
###Returns a string or None since fromAddresses column accepts NULL values
def createFromAddressesString(transactionResult):
    propString = ""
    if "from" in transactionResult:
        propString = ""
        for fromInstance in transactionResult["from"]:
            try:
                propString = propString + fromInstance["proposition"] + ","
            except Exception as e:
                print("Could not get proposition from transaction: ", e)
                raise

        return propString[0:len(propString)-1]

    else:
        return None


###parses a transaction and converts it to comma separated newBoxes string of newly created boxes ids###
###Returns a string or None since newBoxes column accepts NULL values
def createNewBoxesString(transactionResult):
    boxesString = ""
    if "newBoxes" in transactionResult:
        boxesString = ""
        for newBoxesInstance in transactionResult["newBoxes"]:
            try:
                boxesString = boxesString + newBoxesInstance + ","
            except Exception as e:
                print("Could not get proposition from transaction: ", e)
                raise

        return boxesString[0:len(boxesString)-1]

    else:
        return None

###parses a transaction and converts it to comma separated boxesToRemove string of destroyed boxes ids###
###Returns a string or None since boxesToRemove column accepts NULL values
def createBoxesToRemoveString(transactionResult):
    boxesString = ""
    if "boxesToRemove" in transactionResult:
        boxesString = ""
        for boxesToRemoveInstance in transactionResult["boxesToRemove"]:
            try:
                boxesString = boxesString + boxesToRemoveInstance + ","
            except Exception as e:
                print("Could not get proposition from transaction: ", e)
                raise

        return boxesString[0:len(boxesString)-1]

    else:
        return None


class Database:
    def __init__(self, database_filename, chain_url, api_key=None):
        self.fileName = database_filename
        self.chainUrl = chain_url
        self.chainApiKey = api_key
        self.LokiObj = Requests.LokiPy()
        self.conn = None
        self.cur = None


    def parseAddressesFromTransactionAndUpdateDB(self, transactionResult):
        addressesSet = {}
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
                c = self.cur.execute("INSERT INTO addresses VALUES (?,?)", (address, newTransactionString))
            else:
                ###Will only ever be a single value list if not empty
                for transactionString in data:
                    newTransactionString = transactionString[0] + "," + transactionResult["txHash"]
                    c = self.cur.execute("UPDATE addresses SET transactions=? WHERE publicKey=?",
                    (newTransactionString, address))




    def parseTransactionsFromBlockAndUpdateDB(self, txsArray):
        for tx in txsArray:
            try:
                transactionResult = self.LokiObj.getTransactionById(tx["txHash"])["result"]
                try:
                    self.cur.execute("INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?,?)", (transactionResult["txHash"], transactionResult["timestamp"], transactionResult["blockNumber"], transactionResult["blockHash"], createToAddressesString(transactionResult),
                    createFromAddressesString(transactionResult),
                    createNewBoxesString(transactionResult),
                    createBoxesToRemoveString(transactionResult),
                    json.dumps(transactionResult)))
                except Exception as e:
                    print("Could not insert block into blocks table: ", e)
                    raise
                # insertTransactionInAddressesTable(transactionResult)
            except Exception as e:
                print("Getting transaction by id and parsing result failed: ", e)
                raise
                # self.parseAddressesFromTransactionAndUpdateDB(transactionResult)

        c = self.cur.execute("SELECT * FROM transactions WHERE txHash=?", (transactionResult["txHash"],))
        data = c.fetchall()


    def init(self):
        ### Settings the url and apiKey of the database's LokiPy instance
        print("Initializing db")
        self.LokiObj.setUrl(self.chainUrl)
        if self.chainApiKey is not None:
            self.LokiObj.setApiKey(self.chainApiKey)
        ####query chain for history list#####
        history = np.array(self.LokiObj.printChain()["result"]["history"].split(','))
        ###Getting topmost block
        historyInstance = self.LokiObj.getBlockById(history[-1])["result"]
        # Querying parentId of 1st block returns 500 error None.get
        # printJson(LokiObj.getBlockById("4vJ9JU1bJJE96FWSJKvHsmmFADCg4gpZQff4P3bkLKi"))

        ###database####
        self.conn = sqlite3.connect(self.fileName)
        self.cur = self.conn.cursor()

        ###########################
        ###TODO add assets table###
        ###########################


        ###########################
        ###TODO add fees and signatures to transactions table (and look for other fields to add)###
        ###########################


        create_transactions_table = """ CREATE TABLE IF NOT EXISTS transactions (
                                            txHash text PRIMARY KEY,
                                            timestamp text NOT NULL,
                                            blockNumber integer NOT NULL,
                                            blockHash text NOT NULL,
                                            toAddresses text,
                                            fromAddresses text,
                                            newBoxes text,
                                            boxesToRemove text,
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
        self.cur.execute(create_blocks_table)
        self.cur.execute(create_transactions_table)
        self.cur.execute(create_addresses_table)
        ###blocks Table###
        self.cur.execute("INSERT INTO blocks VALUES (?,?,?,?,?,?,?)", (historyInstance["blockNumber"], historyInstance["id"], historyInstance["timestamp"], historyInstance["signature"], createTxsString(historyInstance["txs"]), historyInstance["parentId"], json.dumps(historyInstance)))
        ###transactions Table###
        self.parseTransactionsFromBlockAndUpdateDB(historyInstance["txs"])
        ###addresses Table###
        self.parseAddressesFromTransactionAndUpdateDB(historyInstance["txs"])

        while historyInstance["parentId"] != None:
            try:
                # print(historyInstance["blockNumber"])
                historyInstance = self.LokiObj.getBlockById(historyInstance["parentId"])["result"]
                self.cur.execute("INSERT INTO blocks VALUES (?,?,?,?,?,?,?)", (historyInstance["blockNumber"], historyInstance["id"], historyInstance["timestamp"], historyInstance["signature"], createTxsString(historyInstance["txs"]), historyInstance["parentId"], json.dumps(historyInstance)))
                self.parseTransactionsFromBlockAndUpdateDB(historyInstance["txs"])
                self.parseAddressesFromTransactionAndUpdateDB(historyInstance["txs"])
            except:
                historyInstance["parentId"] = None

        self.conn.commit()
        self.conn.close()
        print("Finished initializing db")


    def queryAndUpdate(self):
        print("Entered queryAndUpdate")
        history = np.array(self.LokiObj.printChain()["result"]["history"].split(','))
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
            self.cur.execute("INSERT INTO blocks VALUES (?,?,?,?,?,?,?)", (historyInstance["blockNumber"], historyInstance["id"], historyInstance["timestamp"], historyInstance["signature"], createTxsString(historyInstance["txs"]), historyInstance["parentId"], json.dumps(historyInstance)))
            self.parseTransactionsFromBlockAndUpdateDB(historyInstance["txs"])
            self.parseAddressesFromTransactionAndUpdateDB(historyInstance["txs"])
            currentIndex = currentIndex - 1
            ###Getting parent of topmost block
            historyInstance = self.LokiObj.getBlockById(history[currentIndex])["result"]
            c = self.cur.execute("SELECT * FROM blocks WHERE blockNumber=?", (historyInstance["blockNumber"],))
            data = c.fetchall()
        self.conn.commit()
        self.conn.close()
