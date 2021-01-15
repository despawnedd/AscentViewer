import os

def checkForLogsFolder():
    if os.path.exists("source/data/user/logs"):
        assert True

def checkForAssetsFolder():
    if os.path.exists("source/data/assets"):
        assert True