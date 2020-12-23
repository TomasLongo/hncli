from dataclasses import dataclass


@dataclass
class HnConfig:
    def __init__(self, cliOptions):
        self.n = cliOptions.storyCount
        self.showOpenCount = cliOptions.openCount
        self.quiet = cliOptions.quiet
        self.debug = cliOptions.debug
        self.rlTTL = cliOptions.rlTTL

    n: int = 20

    # absolute path to historyfile
    histfile: str = "~/hnclient/stories.history"
    readLaterFile: str = "~/hnclient/readlater"
    showOpenCount: bool = False
    quiet: bool = False
    debug: bool = False
    rlTTL: int = 2
