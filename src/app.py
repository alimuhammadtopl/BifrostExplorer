import json
import time
import sqlite3
from flask import Flask, request
from flask_cors import CORS
from src.database import Database
import src.utils.jsonrpc as rpc


app = Flask(__name__)
CORS(app)

###Read configurations from config
with open('config.json') as f:
    config = json.load(f)
    app.config.update(config)

# def print_json(json_data):
#     print(json.dumps(json_data, indent = 4))


@app.route("/", methods=["POST"])
def setup_test():
    return "Hello, your server is working!"

###Creating a new database instance for each query to ensure connection safety between api threads
@app.route("/api", methods=["POST"])
def rpc_handler():
    try:
        req = request.get_json()
        database = Database(app.config["database_path"])
        database.conn = sqlite3.connect(database.filename)
        database.cur = database.conn.cursor()

        ###Try to minimize number of queries frontend would need so make sure to serve more information if possible
        ###For example: return list of transaction jsons for get_transactions_by_block_id instead of just list of transaction ids so clients dont have to re-query
        ###Dont expose too many of the LokiPy endpoints for use via the app's api because that increases requests to the node which this app is attempting to subvert
        ###Implement asserts on req id and maybe params before checking method

        validation_proposition = rpc.validate_request(req)
        if validation_proposition != 0:
            rpc.make_error_resp(validation_proposition, rpc.rpc_errors[validation_proposition], req["id"])

        if req["method"] == "block_by_id":
            return rpc.rpc_success_response(database.block_by_id(req["params"]["blockHash"]), req["id"])

        elif req["method"] == "block_by_number":
                return rpc.rpc_success_response(database.block_by_number(req["params"]["blockNumber"]), req["id"])

        elif req["method"] == "transactions_by_block_number":
            return rpc.rpc_success_response(database.transactions_by_block_number(req["params"]["blockNumber"]), req["id"])

        elif req["method"] == "transactions_by_block_id":
            return rpc.rpc_success_response(database.transactions_by_block_id(req["params"]["blockHash"]), req["id"])

        elif req["method"] == "number_of_confirmed_transactions":
            return rpc.rpc_success_response(database.number_of_confirmed_transactions(), req["id"])

        elif req["method"] == "transaction_by_id":
            return rpc.rpc_success_response(database.transaction_by_id(req["params"]["transactionId"]), req["id"])

        elif req["method"] == "transactions_by_asset_code":
            return rpc.rpc_success_response(database.transactions_by_asset_code(req["params"]["assetCode"]), req["id"])

        elif req["method"] == "transactions_by_issuer":
            return rpc.rpc_success_response(database.transactions_by_issuer(req["params"]["issuer"]), req["id"])

        elif req["method"] == "transactions_by_issuer_by_asset_code":
            return rpc.rpc_success_response(database.transactions_by_issuer_by_asset_code(req["params"]["issuer"], req["params"]["assetCode"]), req["id"])

        elif req["method"] == "transactions_by_public_key":
            return rpc.rpc_success_response(database.transactions_by_public_key(req["params"]["publicKey"]), req["id"])

        elif req["method"] == "transactions_in_mempool":
            database.chain_full_url = app.config["chain_url"] + ":" + app.config["chain_port"]
            if app.config["chain_api_key"] is not None and app.config["chain_api_key"] is not "":
                database.chain_api_key = app.config["chain_api_key"]
            return rpc.rpc_success_response(database.transactions_in_mempool(), req["id"])


        elif req["method"] == "average_block_delay":
            return

        elif req["method"] == "average_block_delay_for_last_n_blocks":
            return

        elif req["method"] == "average_block_delay_between_blocks":
            return

        elif req["method"] == "current_block_height":
            return rpc.rpc_success_response(database.current_block_height(), req["id"])

        elif req["method"] == "block_difficulty":
            return

        elif req["method"] == "block_size_by_id":
            return

    except:
        return rpc.make_error_resp(-32603, rpc.rpc_errors[-32603], None)
