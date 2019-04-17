import copy
import json

success_response_json = {
    "jsonrpc": "2.0",
    "id": 1,
    "result": "This is the default result. You are seeing this because the endpoint returning this has not been fully setup yet",
}

error_response_json = {
    "jsonrpc": "2.0",
    "error": {
        "code": 0,
        "message": "ERROR : This is the default error message. You are seeing this because the endpoint returning this has not been fully setup yet"
    },
    "id": 1
}

rpc_errors = {
    -32700: "Parse error",
    -32600: "Invalid Request",
    -32601: "Method not found",
    -32602: "Invalid params",
    -32603: "Internal error",
    -32000: "Server error"
}

application_errors = {
    -30000: "unknown error",
    -30001: "invalid api key"

    # -30017: "endpoint currently unimplemented"
}

def success_response(result, id):
    r = copy.deepcopy(success_response_json)
    r["result"] = result
    r["id"] = id
    return json.dumps(r)

def error_response(code, msg, id):
    r = copy.deepcopy(error_response_json)
    r["error"]["code"] = code
    r["error"]["message"] = msg
    r["id"] = id
    return json.dumps(r)


def validate_request(request):
    try:
        assert req["jsonrpc"] == "2.0"
        # if req["method"] not in methods:
        #         return -32601
        assert isinstance(req["id"], int)
        return 0
    except:
        return -32600
