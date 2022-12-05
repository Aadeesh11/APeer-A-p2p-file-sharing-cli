import json
import debug
import threading
import os


class RecordsStructure:
    def __init__(self):
        self.indexLock = threading.Lock()
        self.peers = {}

    def updateJsonFile(self, address, directoryJsonString, path="indexed.json"):
        self.indexLock.acquire()
        try:

            addr = str(address[0]) + ':' + str(address[1])
            with open(path, "r") as jsonFile:
                print(jsonFile)
                data = json.load(jsonFile)
            if (directoryJsonString == None and addr in data.keys()):
                del data[addr]
                with open(path, "w") as jsonFile:
                    json.dump(data, jsonFile)
            elif directoryJsonString != None:
                data[addr] = json.loads(directoryJsonString)
                with open(path, "w") as jsonFile:
                    json.dump(data, jsonFile)
        except:
            raise
        finally:
            self.indexLock.release()

    def sendJsonFileData(self, path="indexed.json"):
        try:
            with open(path, "r") as jsonFile:
                print(jsonFile)
                data = json.load(jsonFile)
            return json.dumps(data)
        except:
            debug.pr(f"Couldnt send json")
            raise


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
