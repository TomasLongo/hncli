import sys

from hnconfig import config


def logInfo(msg: str):
    print(msg)


def logDebug(msg: str):
    if config.debug is True:
        print(msg, file=sys.stderr)
