import json
import os


def path_to_dict(loc):
    if not os.path.exists(loc):
        return ''
    d = {'name': os.path.basename(loc)}
    if os.path.isdir(loc):
        d['type'] = "directory"
        d['children'] = [path_to_dict(os.path.join(loc, x)) for x in os.listdir
                         (loc)]
    else:
        d['type'] = "file"
    return d


def path_string(loc="./toShare"):
    return json.dumps(path_to_dict(loc))


def strToClientJson(jsonStr, path='client.json'):

    newData = json.loads(jsonStr)
    with open(path, "w") as jsonFile:
        json.dump(newData, jsonFile)
