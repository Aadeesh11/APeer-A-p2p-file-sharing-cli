from os import walk, path
import json


def strToClientJson(jsonStr, path='client.json'):
    print(jsonStr)
    newData = json.loads(jsonStr)
    with open(path, "w") as jsonFile:
        json.dump(newData, jsonFile)


def file_to_dict(fpath):
    return {
        'name': path.basename(fpath),
        'type': 'file',
        'copy_Paste_This': fpath,
    }


def folder_to_dict(rootpath):
    return {
        'name': path.basename(rootpath),
        'type': 'folder',
        'copy_Paste_This': rootpath,
        'children': [],
    }


def tree_to_dict(rootpath):
    root_dict = folder_to_dict(rootpath)
    for root, folders, files in walk(rootpath):
        root_dict['children'] = [file_to_dict(
            path.sep.join([root, fpath])) for fpath in files]
        root_dict['children'] += [tree_to_dict(path.sep.join([root, folder]))
                                  for folder in folders]
        return root_dict


def tree_to_json(rootdir="toShare", pretty_print=True):
    js = ''
    for root, folders, files in walk(rootdir):
        root_dict = [tree_to_dict(path.sep.join([root, folder]))
                     for folder in folders]
        root_dict += [file_to_dict(path.sep.join([root, fpath]))
                      for fpath in files]

        js = json.dumps(root_dict)

        return js


def printTreeOnScreen():
    with open("client.json", 'r') as f:
        data = json.load(f)

    print(json.dumps(data, indent=4))
