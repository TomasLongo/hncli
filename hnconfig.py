from dataclasses import dataclass


@dataclass
class HnConfig:
    n: int = 20


config = HnConfig()
