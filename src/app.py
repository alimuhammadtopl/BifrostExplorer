import json
import time
from flask import Flask, request
from flask_cors import CORS
from src.database import Database
import src.apiEndpoints as endpoints
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

        ###Try to minimize number of queries frontend would need so make sure to serve more information if possible
        ###For example: return list of transaction jsons for get_transactions_by_block_id instead of just list of transaction ids so clients dont have to re-query
        ###Dont expose too many of the LokiPy endpoints for use via the app's api because that increases requests to the node which this app is attempting to subvert

        validation_proposition = rpc.validate_request(req)
        if validation_proposition != 0:
            rpc.error_response(validation_proposition, rpc.rpc_errors[validation_proposition], req["id"])

        if req["method"] == "block_by_id":
            if "blockHash" in req["params"]:
                return rpc.success_response(endpoints.block_by_id(database, req["params"]["blockHash"]), req["id"])
            else:
                ###Invalid params
                return rpc.error_response(-32602, rpc.rpc_errors[-32602], None)

        elif req["method"] == "block_by_number":
            if "blockNumber" in req["params"]:
                return rpc.success_response(endpoints.block_by_number(database, req["params"]["blockNumber"]), req["id"])
            else:
                return rpc.error_response(-32602, rpc.rpc_errors[-32602], None)

        elif req["method"] == "transactions_by_block_number":
            if "blockNumber" in req["params"]:
                return rpc.success_response(endpoints.transactions_by_block_number(database, req["params"]["blockNumber"]), req["id"])
            else:
                return rpc.error_response(-32602, rpc.rpc_errors[-32602], None)

        elif req["method"] == "transactions_by_block_id":
            if "blockHash" in req["params"]:
                return rpc.success_response(endpoints.transactions_by_block_id(database, req["params"]["blockHash"]), req["id"])
            else:
                return rpc.error_response(-32602, rpc.rpc_errors[-32602], None)

        elif req["method"] == "number_of_confirmed_transactions":
            return rpc.success_response(endpoints.number_of_confirmed_transactions(database), req["id"])

        elif req["method"] == "transaction_by_id":
            if "transactionId" in req["params"]:
                return rpc.success_response(endpoints.transaction_by_id(database, req["params"]["transactionId"]), req["id"])
            else:
                return rpc.error_response(-32602, rpc.rpc_errors[-32602], None)

        elif req["method"] == "transactions_by_asset_code":
            if "assetCode" in req["params"]:
                return rpc.success_response(endpoints.transactions_by_asset_code(database, req["params"]["assetCode"]), req["id"])
            else:
                return rpc.error_response(-32602, rpc.rpc_errors[-32602], None)

        elif req["method"] == "transactions_by_issuer":
            if "issuer" in req["params"]:
                return rpc.success_response(endpoints.transactions_by_issuer(database, req["params"]["issuer"]), req["id"])
            else:
                return rpc.error_response(-32602, rpc.rpc_errors[-32602], None)

        elif req["method"] == "transactions_by_issuer_by_asset_code":
            if "assetCode" in req["params"] and "issuer" in req["params"]:
                return rpc.success_response(endpoints.transactions_by_issuer_by_asset_code(database, req["params"]["issuer"], req["params"]["assetCode"]), req["id"])
            else:
                return rpc.error_response(-32602, rpc.rpc_errors[-32602], None)

        elif req["method"] == "transactions_by_public_key":
            if "publicKey" in req["params"]:
                return rpc.success_response(endpoints.transactions_by_public_key(database, req["params"]["publicKey"]), req["id"])
            else:
                return rpc.error_response(-32602, rpc.rpc_errors[-32602], None)

        elif req["method"] == "transactions_in_mempool":
            database.chain_full_url = app.config["chain_url"] + ":" + app.config["chain_port"]
            if app.config["chain_api_key"] is not None and app.config["chain_api_key"] is not "":
                database.chain_api_key = app.config["chain_api_key"]
            return rpc.success_response(endpoints.transactions_in_mempool(database), req["id"])

        elif req["method"] == "average_block_delay":
            return rpc.success_response(endpoints.average_block_delay(database), req["id"])

        elif req["method"] == "average_delay_between_specified_blocks":
            if "block1" in req["params"] and "block2" in req["params"]:
                return rpc.success_response(endpoints.average_delay_between_specified_blocks(database, req["params"]["block1"], req["params"]["block2"]), req["id"])
            else:
                return rpc.error_response(-32602, rpc.rpc_errors[-32602], None)

        elif req["method"] == "current_block_height":
            return rpc.success_response(endpoints.current_block_height(database), req["id"])

        # elif req["method"] == "block_difficulty":
        #     return
        #
        # elif req["method"] == "block_size_by_id":
        #     return
        else:
            ###Method not found
            return rpc.error_response(-32601, rpc.rpc_errors[-32601], None)

    except Exception as e:
        ###Internal error
        return rpc.error_response(-32603, rpc.rpc_errors[-32603] + ": " + str(e), None)
