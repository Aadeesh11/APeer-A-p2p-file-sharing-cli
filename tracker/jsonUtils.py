import json
import debug
import threading


class RecordsStructure:
    def __init__(self):
        self.indexLock = threading.Lock()
        self.peers = {}

    def updateJsonFile(self, address, directoryJsonString, cliendP2Pport, path="indexed.json"):
        self.indexLock.acquire()
        try:
            addr = str(address[0]) + ':' + cliendP2Pport
            with open(path, "r") as jsonFile:
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
