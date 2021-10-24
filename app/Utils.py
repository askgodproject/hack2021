from os.path import join
from os.path import split
import json
from nltk.corpus import wordnet

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

def compareLists(list1, list2, score_increment, log_matches):
    match_score = 0
    # See if any elements from list 1 are in list 2; converting to sets removes duplicates, and we don't care about ordering
    for list1_element in set(list1):
        for list2_element in set(list2):
            if list1_element == list2_element:
                match_score += score_increment
                if log_matches:
                    print("Increment score (" + str(match_score) + ") because " + list1_element + " == " + list2_element)

    return match_score

def compareEntries(entry1, entry2, use_similar_words, score_increment, score_max, log_matches):
    match_score = 0

    # Directly compare the lists (if it's just a string, make it a single element list)
    entry1_list = [entry1] if type(entry1) == str else entry1
    entry2_list = [entry2] if type(entry2) == str else entry2
    match_score += compareLists(entry1_list, entry2_list, score_increment, log_matches)
    
    # Test with similar words if requested
    if use_similar_words:
        entry1_list_similar = []
        for word in entry1_list:
            synsets = wordnet.synsets(word)
            for set in synsets:
                entry1_list_similar.extend(set.lemma_names())
        
        entry2_list_similar = []
        for word in entry2_list:
            synsets = wordnet.synsets(word)
            for set in synsets:
                entry2_list_similar.extend(set.lemma_names())

        match_score += compareLists(entry1_list_similar, entry2_list_similar, score_increment, log_matches)

    # Return total matching score, reducing to max if needed
    if match_score > score_max:
        print("Score " + str(match_score) + " too large, reducing to " + str(score_max))
        match_score = score_max
    return match_score
