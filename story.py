from dataclasses import dataclass


@dataclass
class Story:
    url: str = ''
    id: int = ''
    loadedFromHist: bool = False
    openCount: int = 0
    title: str = ''
    starred: bool = False

def copyStory(src):
    return Story(
        url=src.url,
        id=src.id,
        loadedFromHist=src.loadedFromHist,
        openCount=src.openCount,
        title=src.title,
        starred=src.starred
    )
