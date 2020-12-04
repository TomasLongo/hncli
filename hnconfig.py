from dataclasses import dataclass


@dataclass
class HnConfig:
    n: int = 20

    # absolute path to historyfile
    histfile: str = "~/hnclient/stories.history"


config = HnConfig()
