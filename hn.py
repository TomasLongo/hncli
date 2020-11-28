#! /usr/bin/python3

import sys
import requests
import webbrowser
from rich.console import Console
from rich.text import Text

from hnconfig import config

options = sys.argv[1:]

topStories = " https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty"
itemBaseURL = " https://hacker-news.firebaseio.com/v0/item/"


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
        # check on wier die Storyid schon geladen haben. Wenn ja, nimm
        # die Story aus der History

        storyFromHistory = getStoryFromHistory(itemID, history)
        if storyFromHistory is not None:
            processedStories.append(storyFromHistory)
            continue

        itemResponse = requests.get(f'{itemBaseURL}/{itemID}/.json')
        json = itemResponse.json()

        story = {
            "id": json["id"],
            "title": json["title"],
            "loadedFromHist": False
        }

        story["url"] = ""
        if "url" in json:
            story["url"] = json["url"]

        processedStories.append(story)

    writeToHistoryFile(list(filter(lambda s: s["loadedFromHist"] == False, processedStories)))

    return processedStories


def getStoryFromHistory(storyID: int, history):
    """ Fetches a specific story from the history. Returns None if not found """
    for h in history:
        if h["id"] == storyID:
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
            story = {"loadedFromHist": True, "id": int(tokens[0]), "url": tokens[2], "title": tokens[1]}
            loadedStories.append(story)

    return loadedStories


def writeToHistoryFile(stories):
    """ Writes the passed list of stories to a file concverting ist fields into csv format """

    with open('./stories.history', 'a') as historyFile:
        for story in stories:
            storyID = str(story["id"])
            title = story["title"]
            url = story["url"]

            historyFile.write(f'{storyID};{title};{url}\n')


# fetch the story with passed id and open its url in the browser
def openInBrowser(itemID):
    """
        Opens the passed story id in the browser
        Tries to first load the story from the history. If not present in
        history, will reach out to the hn service
    """
    storiesFromHistory = loadFromHistoryFile()
    urlToLoad = ""
    story = getStoryFromHistory(itemID, storiesFromHistory)
    print(story)
    if story is not None and urlToLoad is "":
        print('from hist')
        item = fetchStory(itemID)
        urlToLoad = item["url"]

    webbrowser.open_new_tab(urlToLoad)
    exitPeacefully()


if len(options) == 0:
    stories = fetchTopStories(loadFromHistoryFile())
    cons = Console()
    for story in stories:
        color = "green" if story["loadedFromHist"] == True else "magenta"
        text = Text(str(story["id"]), style=color)
        text.append(f' {story["title"]}', style="yellow")

        cons.print(text)

    exitPeacefully()

command = options[0]

if command == "open":
    openInBrowser(int(options[1]))
