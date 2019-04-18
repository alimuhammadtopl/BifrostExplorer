from LokiPy import Requests
import json
import numpy as np
import sqlite3
import src.utils.parseJson as parseJson


#################################################################
########################### DATABASE ############################
#################################################################

###Modify init so that same database class can be used for querying database only without chain interaction

class Database:
    def __init__(self, database_filename, chain_full_url=None, api_key=None):
        self.filename = database_filename
        self.chain_full_url = chain_full_url
        self.chain_api_key = api_key
        self.loki_obj = None
        self.conn = None
        self.cur = None


    def parse_transaction_and_update_adresses_table(self, transaction_result):
        addresses_set = set()
        if "to" in transaction_result:
            for to_instance in transaction_result["to"]:
                try:
                    addresses_set.add(to_instance["proposition"])
                except Exception as e:
                    print("Could not get proposition from transaction: ", e)
                    raise
        if "from" in transaction_result:
            for from_instance in transaction_result["from"]:
                try:
                    addresses_set.add(from_instance["proposition"])
                except Exception as e:
                    print("Could not get proposition from transaction: ", e)
                    raise
        ###for each unqiue address in transaction, update addresses table, appending the txHash to the string of txHashes in the transactions column
        for address in addresses_set:
            c = self.cur.execute("SELECT transactions FROM addresses WHERE publicKey=?", (address,))
            data = c.fetchall()
            new_transaction_string = ""
            if len(data) == 0:
                new_transaction_string = transaction_result["txHash"]
                self.cur.execute("INSERT INTO addresses VALUES (?,?)", (address, new_transaction_string))
            else:
                ###Will only ever be a single value list if not empty
                for transaction_string in data:
                    new_transaction_string = transaction_string[0] + "," + transaction_result["txHash"]
                    self.cur.execute("UPDATE addresses SET transactions=? WHERE publicKey=?",
                    (new_transaction_string, address))



    def parse_transaction_and_update_assets_table(self, transaction_result):
        if "assetCode" in transaction_result:
            try:
                c = self.cur.execute("SELECT transactions FROM assets WHERE assetCode=?", (transaction_result["assetCode"],))
                data = c.fetchall()
                if len(data) == 0:
                    self.cur.execute("INSERT INTO assets VALUES (?,?)", (transaction_result["assetCode"],transaction_result["txHash"]))
                else:
                    for transaction_string in data:
                        new_transaction_string = transaction_string[0] + "," + transaction_result["txHash"]
                        self.cur.execute("UPDATE assets SET transactions=? WHERE assetCode=?",
                        (new_transaction_string, transaction_result["assetCode"]))
            except Exception as e:
                print("Could not insert transaction into assets table: ", e)
                raise

    def parse_transaction_and_update_issuers_table(self, transaction_result):
        if "issuer" in transaction_result:
            try:
                c = self.cur.execute("SELECT transactions FROM issuers WHERE issuer=?", (transaction_result["issuer"],))
                data = c.fetchall()
                if len(data) == 0:
                    self.cur.execute("INSERT INTO issuers VALUES (?,?)", (transaction_result["issuer"],transaction_result["txHash"]))
                else:
                    for transaction_string in data:
                        new_transaction_string = transaction_string[0] + "," + transaction_result["txHash"]
                        self.cur.execute("UPDATE issuers SET transactions=? WHERE issuer=?",
                        (new_transaction_string, transaction_result["issuer"]))
            except Exception as e:
                print("Could not insert transaction into issuers table: ", e)
                raise


    def parse_transactions_array_and_update_tables(self, txs_array):
        for tx in txs_array:
            try:
                transaction_result = self.loki_obj.getTransactionById(tx["txHash"])["result"]
                try:
                    self.cur.execute("INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (transaction_result["txHash"], transaction_result["txType"], transaction_result["timestamp"], transaction_result["blockNumber"], transaction_result["blockHash"], parseJson.create_to_addresses_string(transaction_result),
                    parseJson.create_from_addresses_string(transaction_result),
                    parseJson.create_new_boxes_string(transaction_result),
                    parseJson.create_boxes_to_remove_string(transaction_result),
                    transaction_result["fee"],
                    parseJson.create_signatures_string(transaction_result),
                    json.dumps(transaction_result)))
                except Exception as e:
                    print("Could not insert block into blocks table: ", e)
                    raise
                ###updating the addresses table
                self.parse_transaction_and_update_adresses_table(transaction_result)
                ###updating assets table if transaction contains the assetCode field in its json
                if "assetCode" in transaction_result:
                    self.parse_transaction_and_update_assets_table(transaction_result)
                ###updating issuers table if transaction contains the issuer field in its json
                if "issuer" in transaction_result:
                    self.parse_transaction_and_update_issuers_table(transaction_result)
            except Exception as e:
                print("Getting transaction by id and parsing result failed: ", e)
                raise


    ###Initialize database from chain###
    def init(self):
        ### Settings the url and apiKey of the database's LokiPy instance
        self.loki_obj = Requests.LokiPy()
        self.loki_obj.setUrl(self.chain_full_url)
        if self.chain_api_key is not None:
            self.loki_obj.setApiKey(self.chain_api_key)
        ####query chain for history list#####
        try:
            history = np.array(self.loki_obj.printChain()["result"]["history"].split(','))
            ###Getting topmost block
            history_instance = self.loki_obj.getBlockById(history[-1])["result"]
            # Querying parentId of 1st block returns 500 error None.get
            # printJson(loki_obj.getBlockById("4vJ9JU1bJJE96FWSJKvHsmmFADCg4gpZQff4P3bkLKi"))
        except Exception as e:
            print("Querying chain for initialization failed: \n", e)
            raise

        ###database connection intialization####
        print("=====================Initializing db=========================")
        self.conn = sqlite3.connect(self.filename)
        self.cur = self.conn.cursor()

        create_transactions_table = """ CREATE TABLE IF NOT EXISTS transactions (
                                            txHash text PRIMARY KEY,
                                            txType text,
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
                                        transactions text,
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
        create_issuers_table = """ CREATE TABLE IF NOT EXISTS issuers (
                                        issuer text PRIMARY KEY,
                                        transactions text
                                    ); """
        self.cur.execute(create_blocks_table)
        self.cur.execute(create_transactions_table)
        self.cur.execute(create_addresses_table)
        self.cur.execute(create_assets_table)
        self.cur.execute(create_issuers_table)
        ###blocks Table###
        ###TODO: check that block does not already exist in table (insert error occurs when stopping and restarting app quickly and new block hasnt been forged yet)
        try:
            self.cur.execute("INSERT INTO blocks VALUES (?,?,?,?,?,?,?)", (history_instance["blockNumber"], history_instance["id"], history_instance["timestamp"], history_instance["signature"], parseJson.create_transactions_string(history_instance["txs"]), history_instance["parentId"], json.dumps(history_instance)))
            ###transactions Table###
            self.parse_transactions_array_and_update_tables(history_instance["txs"])
        except:
            print("Insert failure: Could not insert into blocks table. Likely blockNumber already exists. If error persists old database may need to be deleted")
            ###To prevent entering below while loop since if insert failed because blockNumber already exists then it is likely that previous blockNumbers (parent blocks) also exist
            # history_instance["parentId"] = None

        while history_instance["parentId"] != None:
            try:
                ###If attempting to insert into existing blockNumber this try block will throw an exception and loop execution ends since while condition is forced to fail on exception###
                history_instance = self.loki_obj.getBlockById(history_instance["parentId"])["result"]
                self.cur.execute("INSERT INTO blocks VALUES (?,?,?,?,?,?,?)", (history_instance["blockNumber"], history_instance["id"], history_instance["timestamp"], history_instance["signature"], parseJson.create_transactions_string(history_instance), history_instance["parentId"], json.dumps(history_instance)))
                self.parse_transactions_array_and_update_tables(history_instance["txs"])
            except:
                history_instance["parentId"] = None

        self.conn.commit()
        self.conn.close()
        print("Finished initializing db")

    ###Query chain and update database###
    ###Method is wrapped in try block with except pass to ensure that script continues to attempt updates to database even if it fails at some instance, for example, due to closed connection to chain
    def query_chain_and_update_database(self):
        try:
            print("======================Entered query_chain_and_update_database=======================")
            history = np.array(self.loki_obj.printChain()["result"]["history"].split(','))
            ###database connection intialization####
            self.conn = sqlite3.connect(self.filename)
            self.cur = self.conn.cursor()
            current_index = -1
            ###Getting topmost block
            history_instance = self.loki_obj.getBlockById(history[current_index])["result"]
            c = self.cur.execute("SELECT * FROM blocks WHERE blockNumber=?", (history_instance["blockNumber"],))
            data = c.fetchone()
            ###Accessing parent of topmost block until a block is queried that already exists in db
            while data is None:
                self.cur.execute("INSERT INTO blocks VALUES (?,?,?,?,?,?,?)", (history_instance["blockNumber"], history_instance["id"], history_instance["timestamp"], history_instance["signature"], parseJson.create_transactions_string(history_instance), history_instance["parentId"], json.dumps(history_instance)))
                self.parse_transactions_array_and_update_tables(history_instance["txs"])
                self.parse_transaction_and_update_adresses_table(history_instance["txs"])
                current_index = current_index - 1
                ###Getting parent of topmost block
                history_instance = self.loki_obj.getBlockById(history[current_index])["result"]
                c = self.cur.execute("SELECT * FROM blocks WHERE blockNumber=?", (history_instance["blockNumber"],))
                data = c.fetchone()

            self.conn.commit()
            self.conn.close()

        except Exception as e:
            print("Unable to update database: \n", e)
            pass
