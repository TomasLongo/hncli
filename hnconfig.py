from dataclasses import dataclass

@dataclass
class HnConfig:
    n: int = 20

    # absolute path to historyfile
    histfile: str = "~/hnclient/stories.history"
    readLaterFile: str = "~/hnclient/readlater"
    showOpenCount: bool = False
    quiet: bool = False
    debug: bool = False

config = HnConfig()
