import sys
import logging
import datetime
import json
import os

from data.lib.headerlike import *

# from https://stackoverflow.com/a/31688396/14558305 and https://stackoverflow.com/a/39215961/14558305
class StreamToLogger:
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.level, line.rstrip())

    def flush(self):
        pass

try:
    os.chdir(os.path.abspath(__file__.replace(os.path.basename(__file__), "../..")))
except:
    pass

config = json.load(open("data/user/config.json", encoding="utf-8"))

logfile = f"data/user/temp/logs/log_{datetime.datetime.now().strftime(date_format_file)}.log"

# thanks to Jan and several other sources for this
loggingLevel = getattr(logging, config["debug"]["logging"]["loggingLevel"])
logging.basicConfig(level=loggingLevel,
                    handlers=[logging.StreamHandler(), logging.FileHandler(logfile, "a", "utf-8")],
                    format="[%(asctime)s | %(name)s | %(funcName)s | %(levelname)s] %(message)s",
                    datefmt=date_format)

ascvLogger = logging.getLogger("Main logger")
stderrLogger = logging.getLogger("stderr logger")
sys.stderr = StreamToLogger(stderrLogger, logging.ERROR)

with open(logfile, "a") as f: # this code is a bit messy but all this does is just write the same thing both to the console and the logfile
    logIntroLine = "="*20 + "[ BEGIN LOG ]" + "="*20
    f.write(f"{logIntroLine}\n")
