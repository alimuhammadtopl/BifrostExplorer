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
            if method_name == "transactions_in_mempool":
                database.chain_full_url = app.config["chain_url"] + ":" + app.config["chain_port"] + "/"
                if app.config["chain_api_key"] is not None and app.config["chain_api_key"] is not "":
                    database.chain_api_key = app.config["chain_api_key"]
                return json.dumps(rpc.make_success_resp(hc.transactions_in_mempool(database), req["id"]))
            else:
                ###Method not found
                return json.dumps(make_error_resp(const.NO_METHOD_CODE, const.NO_METHOD, _id))
        else:
            return json.dumps(evaluation)

    except Exception as e:
        ###Internal error
        return json.dumps(rpc.make_error_resp(const.INTERNAL_ERROR_CODE, const.INTERNAL_ERROR, _id))

###Handling the rate limit error message response
@app.errorhandler(429)
def rate_limit_error_handler(e):
    return json.dumps(rpc.make_error_resp(const.RATE_LIMIT_REACHED_CODE, const.RATE_LIMIT_REACHED + ": " + str(e), None))


def start_flaskapp(config):
    serve(app, host='0.0.0.0', port=app.config["app_api_port"])
