from dataclasses import dataclass


@dataclass
class HnConfig:
    n: int = 20
    histfileBase: str = "~/hnclient"
    histfileName: str = "stories.history"


config = HnConfig()
