from pydoc import locate
import copy


def typize_structure(struct):
    if isinstance(struct, dict):
        res = {}
        for key in struct:
            res[key] = typize_structure(struct[key])
    elif isinstance(struct, list):
        res = []
        for e in struct:
            res.append(typize_structure(e))
    elif isinstance(struct, tuple):
        res = []
        for e in struct:
            res.append(typize_structure(e))
        res = tuple(res)
    else:
        res = locate(struct)
    return res


def permute(base, opts):
    if len(opts) == 0:
        return [base]
    w_opt_base = copy.deepcopy(base)
    key = list(opts.keys())[0]
    w_opt_base[key] = opts[key]
    opts_left = {k: v for k, v in opts.items() if k != key}
    res_w_opt = permute(w_opt_base, opts_left)
    res_wo_opt = permute(base, opts_left)
    return res_w_opt + res_wo_opt


def expand(param_scheme):
    for param_name in param_scheme:
        if isinstance(param_scheme[param_name], dict):
            param_scheme[param_name] = expand(param_scheme[param_name])
    statics = {}
    options = {}
    for param_name in param_scheme:
        if param_name[0] == "?":
            options[param_name[1:]] = param_scheme[param_name]
        else:
            statics[param_name] = param_scheme[param_name]
    return permute(statics, options)


def typize_config(config):
    # options syntax expansion
    param_schemes = config["param_schemes"]
    for method_name in param_schemes:
        expanded_schemes = []
        for param_scheme in param_schemes[method_name]:
            expanded_schemes += expand(param_scheme)
        param_schemes[method_name] = expanded_schemes

    # typization
    typized_param_scheme_dict = {}
    for method_name in param_schemes:
        typized_param_schemes = []
        for param_scheme in param_schemes[method_name]:
            typized_param_scheme = {}
            for param_name in param_scheme:
                typized_param_scheme[param_name] = typize_structure(param_scheme[param_name])
            typized_param_schemes.append(typized_param_scheme)
        typized_param_scheme_dict[method_name] = typized_param_schemes
    return typized_param_scheme_dict


def check_params_against_scheme(scheme, params):
    result = False
    if isinstance(scheme, list):
        for sub_scheme in scheme:
            result = result or check_params_against_scheme(sub_scheme, params)
        return result
    if isinstance(scheme, type):  # base case
        return isinstance(params, scheme)
    valid = True
    for param in params:
        if param not in scheme:
            valid = False
            break
        if not check_params_against_scheme(scheme[param], params[param]):
            valid = False
            break
    if valid:
        return True
    return False


def check_params_against_scheme_set(scheme_set, params):
    acc = False
    for scheme in scheme_set:
        acc = acc or check_params_against_scheme(scheme, params)
        if acc:
            break
    return acc
