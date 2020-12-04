#! /usr/bin/python3

import sys
import requests
import webbrowser
import asyncio

from concurrent.futures import ThreadPoolExecutor

from rich.console import Console
from rich.text import Text
from rich.markdown import Markdown

from hnconfig import config
from history import History
from story import Story


options = sys.argv[1:]

topStories = " https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty"
itemBaseURL = " https://hacker-news.firebaseio.com/v0/item/"

history = History(config)


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
    for itemID in idsToProcess:
        storyFromHistory = history.getStory(itemID)
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
    history.appendToHistory(list(filter(lambda s: s.loadedFromHist is False, processedStories)))

    return processedStories


def fetchSingleStory(storyID):
    """ Fetch a story from the hn api and return a stry object """

    itemResponse = requests.get(f'{itemBaseURL}/{storyID}/.json')
    json = itemResponse.json()

    story = Story(title=json["title"], loadedFromHist=False, id=json["id"])

    if "url" in json:
        story.url = json["url"]

    return story


async def fetchTopStoriesParallel():
    resp = requests.get(topStories)
    itemIDs = resp.json()

    with ThreadPoolExecutor(max_workers=10) as excutor:
        loop = asyncio.get_event_loop()

        processedStories = []
        tasks = []
        for storyID in itemIDs[:config.n]:
            storyFromHistory = history.getStory(storyID)

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

        return processedStories


# fetch the story with passed id and open its url in the browser
def openInBrowser(itemID: int):
    """
        Opens the passed story id in the browser
        Tries to first load the story from the history. If not present in
        history, will reach out to the hn service
    """
    urlToLoad = ""
    story = history.getStory(itemID)
    if story is None:
        item = fetchStory(itemID)
        urlToLoad = item.url
    else:
        urlToLoad = story.url
        history.incrementOpenCountInHistory(story.id)

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
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(fetchTopStoriesParallel())
    loop.run_until_complete(future)

    stories = future.result()

    history.appendToHistory(list(filter(lambda s: s.loadedFromHist is False, stories)))

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
    printStoriesWithRich(history.stories[:config.n], cons)
