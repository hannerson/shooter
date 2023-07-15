# utils

def flatten_dictionary(value:dict) -> dict:
    result = {}
    key_list = []
    _flatten_dictionary(value, result, key_list)
    return result

def _flatten_dictionary(ivalue:dict, ovalue:dict, key_list:list) -> None:
    if not isinstance(ivalue, dict):
        key = ''
        key = key.join(key_list)
        ovalue[key] = ivalue
        return
    for k,v in ivalue.items():
        key_list.append(k)
        _flatten_dictionary(v, ovalue, key_list)
        key_list.pop()

if __name__ == "__main__":
    d = {"a":{"a":{"a":1}},"b":{"a":{"a":2}}}
    print (flatten_dictionary(d))