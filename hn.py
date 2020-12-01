#! /usr/bin/python3

import sys
import requests
import webbrowser
from rich.console import Console
from rich.text import Text
from rich.markdown import Markdown

from hnconfig import config

from dataclasses import dataclass

options = sys.argv[1:]

topStories = " https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty"
itemBaseURL = " https://hacker-news.firebaseio.com/v0/item/"


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

        story = Story(url=json["url"], title=json["title"], loadedFromHist=False, id=json["id"])

        if "url" in json:
            story.url = json["url"]

        processedStories.append(story)

    # Stories already loaded from the history are not rewritten to ti
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
    with open('./stories.history', 'r') as historyFile:
        for line in historyFile:
            stripped = line.strip()
            if stripped == "":
                continue

            tokens = line.split(";")
            story = Story(url=tokens[2], loadedFromHist=True, id=int(tokens[0]), title=tokens[1])
            loadedStories.append(story)

    return loadedStories


def writeToHistoryFile(stories):
    """ Writes the passed list of stories to a file concverting ist fields into csv format """

    with open('./stories.history', 'a') as historyFile:
        for story in stories:
            historyFile.write(f'{story.id};{story.title};{story.url}\n')


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

    print(urlToLoad)
    webbrowser.open_new_tab(urlToLoad)
    exitPeacefully()


def printStoriesWithRich(stories, cons):
    for story in stories:
        color = "green" if story.loadedFromHist is True else "magenta"
        text = Text(str(story.id), style=color)
        if story.url is not "":
            text = text.append(" \U0001f517")
        text.append(f' {story.title}', style="yellow")

        cons.print(text)


if len(options) == 0:
    stories = fetchTopStories(loadFromHistoryFile())
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

