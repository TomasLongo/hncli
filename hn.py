#! /usr/bin/python3

import sys
import os
import requests
import webbrowser
import asyncio

from concurrent.futures import ThreadPoolExecutor

from rich.console import Console
from rich.text import Text
from rich.markdown import Markdown

from hnconfig import config

from dataclasses import dataclass

options = sys.argv[1:]

topStories = " https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty"
itemBaseURL = " https://hacker-news.firebaseio.com/v0/item/"


def checkHistfileAndCreateIfNeccessary(config):
    """
        Checks if the historyfile exists. If not construct it.
        Returns the path to the histfile
    """
    base = config.histfileBase
    if "~" in base:
        base = os.path.expanduser(base)

    histPath = os.path.join(base, config.histfileName)
    if os.path.isfile(histPath) is False:
        try:
            os.mkdir(base)
            hf = open(histPath, 'w')
            hf.close()
        except FileExistsError:
            print(f'{histPath} already exists')

    return histPath


histFilePath = checkHistfileAndCreateIfNeccessary(config)


@dataclass
class Story:
    url: str = ''
    id: int = ''
    loadedFromHist: bool = False
    openCount: int = 0
    title: str = ''


def exitPeacefully():
    sys.exit(0)


def fetchStory(id):
    resp = requests.get(f'{itemBaseURL}/{id}.json')
    return resp.json()


# fetchHistory: liste von stories die aus dem Historyfile geladen wurden
#               Wird verwendet um zu entscheiden ob wir die story von
#               HN laden muessen
def fetchTopStories(fetchHistory):
    resp = requests.get(topStories)

    itemIDs = resp.json()

    idsToProcess = itemIDs[:config.n]
    processedStories = []
    history = loadFromHistoryFile()
    for itemID in idsToProcess:
        storyFromHistory = getStoryFromHistory(itemID, history)
        if storyFromHistory is not None:
            processedStories.append(storyFromHistory)
            continue

        itemResponse = requests.get(f'{itemBaseURL}/{itemID}/.json')
        json = itemResponse.json()

        story = Story(title=json["title"], loadedFromHist=False, id=json["id"])

        if "url" in json:
            story.url = json["url"]

        processedStories.append(story)

    # Stories already loaded from the history are not rewritten to ti
    writeToHistoryFile(list(filter(lambda s: s.loadedFromHist is False, processedStories)))

    return processedStories


def fetchSingleStory(storyID):
    itemResponse = requests.get(f'{itemBaseURL}/{storyID}/.json')
    json = itemResponse.json()

    story = Story(title=json["title"], loadedFromHist=False, id=json["id"])

    if "url" in json:
        story.url = json["url"]

    return story


async def fetchTopStoriesParallel():
    resp = requests.get(topStories)
    itemIDs = resp.json()

    history = loadFromHistoryFile()
    with ThreadPoolExecutor(max_workers=10) as excutor:
        loop = asyncio.get_event_loop()

        processedStories = []
        tasks = []
        for storyID in itemIDs[:config.n]:
            storyFromHistory = getStoryFromHistory(storyID, history)

            if storyFromHistory is not None:
                processedStories.append(storyFromHistory)
                continue

            tasks.append(
                loop.run_in_executor(
                    excutor,
                    fetchSingleStory,
                    storyID
                )
            )

        for story in await asyncio.gather(*tasks):
            processedStories.append(story)

        writeToHistoryFile(list(filter(lambda s: s.loadedFromHist is False, processedStories)))

        return processedStories


def getStoryFromHistory(storyID: int, history):
    """ Fetches a specific story from the history. Returns None if not found """

    for h in history:
        if h.id == storyID:
            return h

    return None


def isStoryInHistory(storyID, history):
    for h in history:
        if h["id"] == storyID:
            return True

    return False


# Loads stories from the history file.
# Returns a list of story objects
def loadFromHistoryFile():
    """ Loads all stories from the history file """

    loadedStories = []
    with open(histFilePath, 'r') as historyFile:
        for line in historyFile:
            stripped = line.strip('\n ')
            if stripped == "":
                continue

            tokens = line.split(";")
            if len(tokens) != 4:
                print(f'Error reading line in historyFile')

            story = Story(url=tokens[2].rstrip(),
                          loadedFromHist=True,
                          id=int(tokens[0]),
                          title=tokens[1],
                          openCount=int(tokens[3]))

            loadedStories.append(story)

    return loadedStories


def writeToHistoryFile(stories):
    """ Appends the passed list of stories to a file concverting ist fields into csv format """

    with open(histFilePath, 'a') as historyFile:
        for story in stories:
            historyFile.write(f'{story.id};{story.title};{story.url};{story.openCount}\n')


# fetch the story with passed id and open its url in the browser
def openInBrowser(itemID: int):
    """
        Opens the passed story id in the browser
        Tries to first load the story from the history. If not present in
        history, will reach out to the hn service
    """
    storiesFromHistory = loadFromHistoryFile()
    urlToLoad = ""
    story = getStoryFromHistory(itemID, storiesFromHistory)
    if story is None:
        item = fetchStory(itemID)
        urlToLoad = item.url
    else:
        urlToLoad = story.url
        incrementOpenCountInHistory(story.id)

    print(urlToLoad)
    webbrowser.open_new_tab(urlToLoad)
    exitPeacefully()


def overwriteHistoryFile(stories):
    """ Replaces the history file with the passed stories """
    with open(histFilePath, 'w') as historyFile:
        for story in stories:
            historyFile.write(f'{story.id};{story.title};{story.url};{story.openCount}\n')


def incrementOpenCountInHistory(storyID: int):
    stories = loadFromHistoryFile()
    story = getStoryFromHistory(storyID, stories)
    story.openCount = story.openCount + 1
    overwriteHistoryFile(stories)


def printStoriesWithRich(stories, cons):
    for story in stories:
        color = "green" if story.loadedFromHist is True else "magenta"
        text = Text(str(story.id), style=color)
        if story.url is not "":
            text = text.append(" \U0001f517")
        text.append(f' {story.title}', style="yellow")

        cons.print(text)


if len(options) == 0:
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(fetchTopStoriesParallel())
    loop.run_until_complete(future)

    stories = future.result()

    cons = Console()
    for story in stories:
        color = "green" if story.loadedFromHist is True else "magenta"
        text = Text(str(story.id), style=color)
        if story.url is not "":
            text = text.append(" \U0001f517")
        text.append(f' {story.title}', style="yellow")

        cons.print(text)

    exitPeacefully()

command = options[0]

if command == "open":
    openInBrowser(int(options[1]))
elif command == "lh":
    cons = Console()
    cons.print(Markdown("## From History"))
    stories = loadFromHistoryFile()
    printStoriesWithRich(stories[:config.n], cons)

