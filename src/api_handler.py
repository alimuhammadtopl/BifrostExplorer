import os
import concurrent
import sqlite3
import src.utils.response_constants as const
import src.utils.jsonrpc2 as rpc
import json
import src.endpoint_handlers.handlers_consolidated as hc


methods = dict()
# for method_name in json.load(open("config.json", "r"))["method_names"]:
###Read configurations from config
with open(os.path.abspath(os.path.join('','config.json'))) as f:
    config = json.load(f)
    app.config.update(config)

    for method_name in app.config["method_names"]:
        methods[method_name] = getattr(hc, method_name)


def handle_request(request, logger):
    evaluation = rpc.validate_request(request)
    if evaluation is True:
        req = request.get_json()
        if isinstance(req, list):
            return handle_batch(req, logger)
        else:
            config = json.load(open("config.json", "r"))
            return handle_obj(req, config, logger)
    else:
        return evaluation


def handle_batch(obj, logger):
    evaluation = rpc.validate_batch(obj)
    if evaluation is True:
        config = json.load(open("config.json", "r"))
        executor = concurrent.ThreadPoolExecutor(max_workers=(len(obj) % 20))
        promises = []
        for _ in obj:
            promises.append(executor.submit(handle_obj, _, config, logger))
        results = []
        for promise in promises:
            result = promise.result()
            if result != const.NO_RESPONSE:
                results.append(result)
        if len(results) == 0:
            results = const.NO_RESPONSE
        return results
    else:
        return evaluation


def handle_obj(obj, config, logger):
    evaluation = rpc.validate_obj(obj, config)
    if evaluation is True:
        method_name = obj["method"]
        params = obj.get("params", {})
        _id = obj.get("id", None)
        conn = sqlite3.connect(config["database_path"])
        try:
            result = method_call(method_name, params, _id, conn, logger, config)
            conn.close()
            if "id" in obj:
                return rpc.make_success_resp(result, _id)
            else:
                return const.NO_RESPONSE
        except Exception as e:
            conn.close()
            log.log_error({
                "method": method_name,
                "params": params,
                "error": str(e)
            })
            return rpc.make_error_resp(const.INTERNAL_ERROR_CODE, const.INTERNAL_ERROR, _id)
    else:
        return evaluation


def method_call(method_name, params, _id, conn, logger, config):
    return methods.get(
        method_name,
        lambda v, w, x, y, z: rpc.make_error_resp(const.NO_METHOD_CODE, const.NO_METHOD, _id)
    )(params, _id, conn, logger, config)
