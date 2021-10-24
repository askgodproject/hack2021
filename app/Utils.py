from os.path import join
from os.path import split
import json

def pythonPath(sourcefile, root_dirname):
    # go up the directory tree until we get to the root directory of the repo
    sub_path = sourcefile
    last_component = ""
    while last_component != root_dirname:
        (sub_path, last_component) = split(sub_path)
    return join(sub_path, last_component)

def datasetsPath(sourcefile, dataset, root_dirname):
    rootpath = pythonPath(sourcefile, root_dirname)
    # the dataset root folder is in the same directory
    datasets_path = join(rootpath, "data")

    # append the dataset filename
    path = join(datasets_path, dataset)
    return path

def readJson(path):
    """
    #Reads in the json data file at path

    @param path The JSON filepath
    @return The json data as a dictionary or None if there is an error
    """
    if path is None:
        print("Invalid json path")
        return None
    data = None
    try:
        data_file = open(path, "r")
        data = json.load(data_file)
        data_file.close()
    except Exception as error:
        print(error)

    return data

def writeJson(path, json_data):
    """
    Writes the given dictionary to the given path, in json format

    @param path The JSON filepath
    @param json_data The data to write
    @return void
    """
    if path is None:
        print("Invalid file path")
    try:
        file_handle = open(path, "w")
        json.dump(json_data, file_handle, indent=4)        
    except Exception as error:
        print(error)
    finally:
        if file_handle:
            file_handle.close()
