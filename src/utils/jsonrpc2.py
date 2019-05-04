import src.utils.response_constants as const


def validate_request(request, config):
    try:
        req = request.get_json()
        ###Checking for api_key in request if specified in config file
        if "app_api_key" in config:
            if config["app_api_key"] is not "" and config["app_api_key"] is not None:
                headers = request.headers
                request_api_key = headers.get("api-key")
                if request_api_key is not config["app_api_key"]:
                    return make_error_resp(const.INVALID_API_KEY_CODE, const.INVALID_API_KEY, None)
        return True
    except:
        return make_error_resp(const.PARSE_ERR_CODE, const.PARSE_ERR, None)


def validate_batch(obj):
    if len(obj) == 0:
        return make_error_resp(const.INVALID_REQ_CODE, const.INVALID_REQ, None)
    else:
        return True


def validate_obj(obj, config):
    if not isinstance(obj, dict):
        return make_error_resp(const.PARSE_ERR_CODE, const.PARSE_ERR, None)
    if "id" not in obj:
        return make_error_resp(const.INVALID_REQ_CODE, const.INVALID_REQ, None)
    else:
        _id = obj["id"]
        if not (isinstance(_id, int) or isinstance(_id, str) or _id is None):
            return make_error_resp(const.INVALID_REQ_CODE, const.INVALID_REQ, None)
    if "jsonrpc" not in obj or "2.0" != obj["jsonrpc"]:
        return make_error_resp(const.INVALID_REQ_CODE, const.INVALID_REQ, None)
    if "method" not in obj:
        return make_error_resp(const.INVALID_REQ_CODE, const.INVALID_REQ, None)
    if obj["method"] not in config["method_names"]:
        return make_error_resp(const.NO_METHOD_CODE, const.NO_METHOD, _id)
    return True


def make_success_resp(result, _id):
    return {
        "jsonrpc": "2.0",
        "result": result,
        "id": _id
    }


def make_error_resp(code, msg, _id):
    return {
        "jsonrpc": "2.0",
        "error": {
            "code": code,
            "message": msg
        },
        "id": _id
    }
