import json
import time
import sqlite3
from flask import Flask, request
from flask_cors import CORS
from src.database import Database


app = Flask(__name__)
CORS(app)

###Read configurations from config
with open('config.json') as f:
    config = json.load(f)
    app.config.update(config)

def print_json(json_data):
    print(json.dumps(json_data, indent = 4))



@app.route("/", methods=["POST"])
def setup_test():
    return "Hello, your server is working!"

###Creating a new database instance for each query to ensure connection safety between api threads
@app.route("/api", methods=["POST"])
def rpc_handler():
    req = request.get_json()
    database = Database(app.config["database_path"])
    database.conn = sqlite3.connect(database.filename)
    database.cur = database.conn.cursor()
    # c = database.cur.execute("SELECT * from addresses")
    # return json.dumps(c.fetchall())

    ###Try to minimize number of queries frontend would need to make so serve more information if possible
    ###For example: return list of transaction jsons for get_transactions_by_block_id instead of just list of transaction ids so clients dont have to re-query
    if req["method"] == "block_by_id":

        return
    elif req["method"] == "block_by_number":

        return
    elif req["method"] == "transactions_by_block_number":

        return
    elif req["method"] == "transactions_by_block_id":

        return
    elif req["method"] == "all_confirmed_transactions":

        return
    elif req["method"] == "transaction_by_id":

        return
    elif req["method"] == "transactions_by_asset_code":

        return
    elif req["method"] == "transactions_by_issuer":

        return
    elif req["method"] == "transactions_by_issuer_by_asset_code":

        return
    elif req["method"] == "transactions_by_public_key":

        return
    elif req["method"] == "transactions_in_mempool":

        return
    elif req["method"] == "average_block_delay":

        return
    elif req["method"] == "current_block_height":

        return
    elif req["method"] == "block_difficulty":

        return
    elif req["method"] == "block_size_by_id":

        return
