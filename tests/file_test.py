# https://www.geeksforgeeks.org/python-check-if-a-file-or-directory-exists-2/
import os

def test_checkForLogsFolder():
    if os.path.isdir("source/data/user/temp/logs"):
        assert True
    else:
        assert False

def test_checkForAssetsFolder():
    if os.path.isdir("source/data/assets"):
        assert True
    else:
        assert False
