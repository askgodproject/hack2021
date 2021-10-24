from os.path import join
from os.path import split
import json

def read_json(path):
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

def write_json(path, json_data):
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
