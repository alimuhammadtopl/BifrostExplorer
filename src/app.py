import json
import os
import sys
import sqlite3
from waitress import serve
from flask import Flask, request
from flask_cors import CORS
from src.database import Database
import src.utils.jsonrpc2 as rpc
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import src.api_handler as handle
import src.endpoint_handlers.handlers_consolidated as hc
import src.utils.response_constants as const


app = Flask(__name__)
CORS(app)

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=[]
)

###Read configurations from config
with open(os.path.abspath(os.path.join('','config.json'))) as f:
    config = json.load(f)
    app.config.update(config)

@app.route("/", methods=["POST"])
def setup_test():
    return "Hello, your server is working!"

###Creating a new database instance for each query to ensure connection safety between api threads
@app.route("/api", methods=["POST"])
def api_rpc_handler():
    resp = handle.handle_request(request, app.logger)
    if resp != const.NO_RESPONSE:
        return json.dumps(resp)



    # try:
    #     req = request.get_json()
    #     validation_proposition = rpc.validate_request(req)
    #     if validation_proposition != 0:
    #         rpc.error_response(validation_proposition, rpc.rpc_errors[validation_proposition], req["id"])
    #
    #     ###Checking for api_key in request if specified in config file
    #     if "app_api_key" in app.config:
    #         if app.config["app_api_key"] is not "" and app.config["app_api_key"] is not None:
    #             headers = request.headers
    #             request_api_key = headers.get("api-key")
    #             if request_api_key is not app.config["app_api_key"]:
    #                 return rpc.error_response(-30001, rpc.application_errors[-30001], None)
    #
    #     database = Database(app.config["database_path"])
    #
    #     if req["method"] == "block_by_hash":
    #         if "blockHash" in req["params"]:
    #             return rpc.success_response(endpoints.block_by_id(database, req["params"]["blockHash"]), req["id"])
    #         else:
    #             ###Invalid params
    #             return rpc.error_response(-32602, rpc.rpc_errors[-32602], None)
    #
    #     elif req["method"] == "block_by_number":
    #         if "blockNumber" in req["params"]:
    #             return rpc.success_response(endpoints.block_by_number(database, req["params"]["blockNumber"]), req["id"])
    #         else:
    #             return rpc.error_response(-32602, rpc.rpc_errors[-32602], None)
    #
    #     elif req["method"] == "transactions_by_block_number":
    #         if "blockNumber" in req["params"]:
    #             return rpc.success_response(endpoints.transactions_by_block_number(database, req["params"]["blockNumber"]), req["id"])
    #         else:
    #             return rpc.error_response(-32602, rpc.rpc_errors[-32602], None)
    #
    #     elif req["method"] == "transactions_by_block_hash":
    #         if "blockHash" in req["params"]:
    #             return rpc.success_response(endpoints.transactions_by_block_id(database, req["params"]["blockHash"]), req["id"])
    #         else:
    #             return rpc.error_response(-32602, rpc.rpc_errors[-32602], None)
    #
    #     elif req["method"] == "number_of_confirmed_transactions":
    #         return rpc.success_response(endpoints.number_of_confirmed_transactions(database), req["id"])
    #
    #     elif req["method"] == "transaction_by_hash":
    #         if "transactionHash" in req["params"]:
    #             return rpc.success_response(endpoints.transaction_by_id(database, req["params"]["transactionHash"]), req["id"])
    #         else:
    #             return rpc.error_response(-32602, rpc.rpc_errors[-32602], None)
    #
    #     elif req["method"] == "transactions_by_asset_code":
    #         if "assetCode" in req["params"]:
    #             return rpc.success_response(endpoints.transactions_by_asset_code(database, req["params"]["assetCode"]), req["id"])
    #         else:
    #             return rpc.error_response(-32602, rpc.rpc_errors[-32602], None)
    #
    #     elif req["method"] == "transactions_by_issuer":
    #         if "issuer" in req["params"]:
    #             return rpc.success_response(endpoints.transactions_by_issuer(database, req["params"]["issuer"]), req["id"])
    #         else:
    #             return rpc.error_response(-32602, rpc.rpc_errors[-32602], None)
    #
    #     elif req["method"] == "transactions_by_issuer_by_asset_code":
    #         if "assetCode" in req["params"] and "issuer" in req["params"]:
    #             return rpc.success_response(endpoints.transactions_by_issuer_by_asset_code(database, req["params"]["issuer"], req["params"]["assetCode"]), req["id"])
    #         else:
    #             return rpc.error_response(-32602, rpc.rpc_errors[-32602], None)
    #
    #     elif req["method"] == "transactions_by_public_key":
    #         if "publicKey" in req["params"]:
    #             return rpc.success_response(endpoints.transactions_by_public_key(database, req["params"]["publicKey"]), req["id"])
    #         else:
    #             return rpc.error_response(-32602, rpc.rpc_errors[-32602], None)
    #
    #     elif req["method"] == "average_block_delay":
    #         return rpc.success_response(endpoints.average_block_delay(database), req["id"])
    #
    #     elif req["method"] == "average_delay_between_specified_blocks":
    #         if "block1" in req["params"] and "block2" in req["params"]:
    #             return rpc.success_response(endpoints.average_delay_between_specified_blocks(database, req["params"]["block1"], req["params"]["block2"]), req["id"])
    #         else:
    #             return rpc.error_response(-32602, rpc.rpc_errors[-32602], None)
    #
    #     elif req["method"] == "current_block_height":
    #         return rpc.success_response(endpoints.current_block_height(database), req["id"])
    #
    #     # elif req["method"] == "block_difficulty":
    #     #     if "blockHash" in req["params"]:
    #     #         return rpc.success_response(endpoints.block_difficulty(database, req["params"]["blockHash"]), req["id"])
    #     #     else:
    #     #         return rpc.error_response(-32602, rpc.rpc_errors[-32602], None)
    #     #
    #
    #     # elif req["method"] == "block_size_by_id":
    #     #     return
    #     else:
    #         ###Method not found
    #         return rpc.error_response(-32601, rpc.rpc_errors[-32601], None)
    #
    # except Exception as e:
    #     ###Internal error
    #     return rpc.error_response(-32603, rpc.rpc_errors[-32603] + ": " + str(e), None)

###Separating routes that directly query node so that rate limiting can be applied
@app.route("/node", methods=["POST"])
@limiter.limit(
    "1/3seconds"
    if "api_rate_limit" not in app.config or app.config["app_api_rate_limit"] is None
    else app.config["app_api_rate_limit"]
    )
def node_rpc_handler():
    try:
        evaluation = rpc.validate_request(request)
        req = request.get_json()
        evaluation = rpc.validate_obj(req, app.config)
        if evaluation is True:
            method_name = req["method"]
            params = req.get("params", {})
            _id = req.get("id", None)

            database = Database(app.config["database_path"])
            if req["method"] == "transactions_in_mempool":
                database.chain_full_url = app.config["chain_url"] + ":" + app.config["chain_port"] + "/"
                if app.config["chain_api_key"] is not None and app.config["chain_api_key"] is not "":
                    database.chain_api_key = app.config["chain_api_key"]
                return rpc.make_success_resp(getattr(hc, "transactions_in_mempool", database), req["id"])
            else:
                ###Method not found
                return make_error_resp(const.NO_METHOD_CODE, const.NO_METHOD, _id)
        else:
            return evaluation

    except Exception as e:
        ###Internal error
        return rpc.make_error_resp(const.INTERNAL_ERROR_CODE, const.INTERNAL_ERROR, _id)

###Handling the rate limit error message response
@app.errorhandler(429)
def rate_limit_error_handler(e):
    return rpc.make_error_resp(cons.RATE_LIMIT_REACHED_CODE, const.RATE_LIMIT_REACHED + ": " + str(e), None)


def start_flaskapp(config):
    serve(app, host='0.0.0.0', port=app.config["app_api_port"])
