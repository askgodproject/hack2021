import argparse
import sys
import os

# Retrieves Scripture text of a given passage using the given language and translation.
# If the optional filename is provided at the end, the passage content will be written there as well as to the standard output
#
# Usage:
#   python3 biblereader.py <passage reference> <language> <version> [<output file>]
# Examples:
#   python3 biblereader.py John.3.16 ENG ESV
#   python3 biblereader.py John.3.16-John.3.18 ENG NIV output.txt
# Note that passage references are in OSIS format

sys.path.insert(0, os.path.abspath(__file__+"/../../app"))
from Passage import Passage
from DBPManager import DBPManager

passage_ref = sys.argv[1]
language = sys.argv[2]
version = sys.argv[3]
filename = sys.argv[4] if len(sys.argv) == 5 else None
print(passage_ref + " " + language + " " + version)

passage = Passage(passage_ref)
text = passage.text(DBPManager(language, version))

print(passage_ref + ":")
print(text)

if filename is not None:
    handle = open(filename, "w")
    handle.write(text)
    handle.close()
