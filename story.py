from dataclasses import dataclass


@dataclass
class Story:
    url: str = ''
    id: int = ''
    loadedFromHist: bool = False
    openCount: int = 0
    title: str = ''
