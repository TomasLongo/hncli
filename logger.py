import sys

config = None

def init(conf):
    global config
    config = conf


def logInfo(msg: str):
    print(msg)


def logDebug(msg: str):
    if config.debug is True:
        print(msg, file=sys.stderr)
