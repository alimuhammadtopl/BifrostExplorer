from LokiPy import Requests
import json
import numpy as np
import sqlite3

def printJson(jsonData):
    print(json.dumps(jsonData, indent = 4))

###parses txs array from a block and converts it to comma separated txHash strings###
def createTxsString(txs):
    txString = ""
    for tx in txs:
        try:
            txString = tx["id"] + ","
        except:
            txString = tx["txHash"] + ","
    if len(txString[0:len(txString)-1]) > 0:
        return txString[0:len(txString)-1]
    else:
        return txString

##Need to standardize txJson parameters that are required vs secondary and also naming convention for json parameters eg txHash vs id
def parseTransactionsFromBlockAndUpdateDB(txsArray):
    for tx in txsArray:
        try:
            transactionResult = LokiObj.getTransactionById(tx["txHash"])["result"]
            try:
                conn.execute("INSERT INTO transactions VALUES (?,?,?,?,?)", (transactionResult["txHash"], transactionResult["timestamp"], transactionResult["blockNumber"], transactionResult["blockHash"], json.dumps(transactionResult)))
            except:
                conn.execute("INSERT INTO transactions VALUES (?,?,?,?,?)", (transactionResult["id"], transactionResult["timestamp"], transactionResult["blockNumber"], transactionResult["blockHash"], json.dumps(transactionResult)))
        except:
            continue



class Database:
    def __init__(self, database_filename, chain_url):
        self.fileName = database_filename
        self.chainUrl = chain_url
        self.conn = None
        self.cur = None


    def init(self):
        ####query chain for history list#####
        print("Initializing db")
        LokiObj = Requests.LokiPy()
        LokiObj.setUrl(self.chainUrl)
        history = np.array(LokiObj.printChain()["result"]["history"].split(','))
        ###Getting topmost block
        historyInstance = LokiObj.getBlockById(history[-1])["result"]
        # Querying parentId of 1st block returns 500 error None.get
        # printJson(LokiObj.getBlockById("4vJ9JU1bJJE96FWSJKvHsmmFADCg4gpZQff4P3bkLKi"))

        ###database####
        # conn = sqlite3.connect('sqlite.db')
        self.conn = sqlite3.connect(self.fileName)
        self.cur = self.conn.cursor();
        create_transactions_table = """ CREATE TABLE IF NOT EXISTS transactions (
                                            txHash text PRIMARY KEY,
                                            timestamp text NOT NULL,
                                            blockNumber integer NOT NULL,
                                            blockHash text NOT NULL,
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
        self.cur.execute(create_blocks_table)
        self.cur.execute(create_transactions_table)
        ###blocks Table###
        self.cur.execute("INSERT INTO blocks VALUES (?,?,?,?,?,?,?)", (historyInstance["blockNumber"], historyInstance["id"], historyInstance["timestamp"], historyInstance["signature"], createTxsString(historyInstance["txs"]), historyInstance["parentId"], json.dumps(historyInstance)))

        ###transactions Table###
        parseTransactionsFromBlockAndUpdateDB(historyInstance["txs"])


        while historyInstance["parentId"] != None:
            try:
                print(historyInstance["blockNumber"])
                historyInstance = LokiObj.getBlockById(historyInstance["parentId"])["result"]
                self.cur.execute("INSERT INTO blocks VALUES (?,?,?,?,?,?,?)", (historyInstance["blockNumber"], historyInstance["id"], historyInstance["timestamp"], historyInstance["signature"], createTxsString(historyInstance["txs"]), historyInstance["parentId"], json.dumps(historyInstance)))

            except:
                historyInstance["parentId"] = None

        self.conn.commit()
        self.conn.close()


    def queryAndUpdate(self):
        print("Entered queryAndUpdate")
        LokiObj = Requests.LokiPy()
        LokiObj.setUrl(self.chainUrl)
        history = np.array(LokiObj.printChain()["result"]["history"].split(','))
        self.conn = sqlite3.connect(self.fileName)
        self.cur = self.conn.cursor()
        currentIndex = -1
        ###Getting topmost block
        historyInstance = LokiObj.getBlockById(history[currentIndex])["result"]
        # c = self.curr.execute("SELECT * FROM blocks");
        # for row in c:
        #     print(row);
        c = self.cur.execute("SELECT * FROM blocks WHERE blockNumber=?", (historyInstance["blockNumber"],))
        data = c.fetchall()
        ###Accessing parent of topmost block until a block is queried that already exists in db
        while len(data) < 1:
            self.cur.execute("INSERT INTO blocks VALUES (?,?,?,?,?,?,?)", (historyInstance["blockNumber"], historyInstance["id"], historyInstance["timestamp"], historyInstance["signature"], createTxsString(historyInstance["txs"]), historyInstance["parentId"], json.dumps(historyInstance)))
            parseTransactionsFromBlockAndUpdateDB(historyInstance["txs"])
            currentIndex = currentIndex - 1
            ###Getting parent of topmost block
            historyInstance = LokiObj.getBlockById(history[currentIndex])["result"]
            c = self.cur.execute("SELECT * FROM blocks WHERE blockNumber=?", (historyInstance["blockNumber"],))
            data = c.fetchall()
        self.conn.commit()
        self.conn.close()
