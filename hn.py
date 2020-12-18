#! /usr/bin/python3

import sys
import requests
import webbrowser
import asyncio
from optparse import OptionParser

from concurrent.futures import ThreadPoolExecutor

from rich.console import Console
from rich.text import Text
from rich.markdown import Markdown
from rich.padding import Padding

from readlater import ReadLater
from hnconfig import config
from history import History
from story import Story


parser = OptionParser()
# parser.add_option("-H", "--no-hist", action="store_false", dest="useHist", default=True, help="Do not use the history when fetching stories. E.g. always talk to the api and dont write fetched stries to the history")
parser.add_option("-c", "--open-cnt", dest="openCount", action="store_true", default=False, help="Print the open count for fetched stories")
parser.add_option("-n", "--story-count", type="int", default=20, dest="storyCount", help="Set how many stories should be fetched. Defaults to 20")

parser.add_option("-q",
                  "--quiet",
                  action="store_true",
                  default=False,
                  dest="quiet",
                  help="Only print program output")

parser.add_option("-x",
                  "--debug",
                  action="store_true",
                  default=False,
                  dest="debug",
                  help="Print additional debug output on std error")

(options, args) = parser.parse_args()

topStories = " https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty"
itemBaseURL = " https://hacker-news.firebaseio.com/v0/item/"

STORY_COUNT = options.storyCount
SHOW_OPENCOUNT = options.openCount
QUIET = options.quiet

config.n=options.storyCount
config.showOpenCount=options.openCount
config.quiet=options.quiet
config.debug=options.debug

history = History(config)

def exitPeacefully():
    sys.exit(0)


def exitAngrily():
    sys.exit(1)


def fetchStory(id):
    resp = requests.get(f'{itemBaseURL}/{id}.json')
    return resp.json()


# fetchHistory: liste von stories die aus dem Historyfile geladen wurden
#               Wird verwendet um zu entscheiden ob wir die story von
#               HN laden muessen
def fetchTopStories(fetchHistory):
    resp = requests.get(topStories)

    itemIDs = resp.json()

    idsToProcess = itemIDs[:STORY_COUNT]
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
        for storyID in itemIDs[:STORY_COUNT]:
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
        if story.url != "":
            text.append(" \U0001f517")
            if SHOW_OPENCOUNT:
                text.append(f' ({story.openCount})', style="bright_black")
        text.append(f' {story.title}', style="yellow")

        cons.print(text)

    if (options.quiet is not True):
        errCons = Console(file=sys.stderr)
        errCons.print(Padding(Markdown("To open a story in the browser invoke `hn.py open [storyID]`"), (1, 0, 0, 0)))
        errCons.print(Markdown("To save a story for later reading invoke `hn.py rl [storyID]`"))


def printReadLaterStoriesWithRich(stories, cons):
    for story in stories:
        color = "white"
        text = Text(str(story.id), style=color)
        if story.url != "":
            text.append(" \U0001f517")
            if SHOW_OPENCOUNT:
                text.append(f' ({story.openCount})', style="bright_black")
        text.append(f' {story.title}', style="yellow")

        cons.print(text)

    if (options.quiet is not True):
        errCons = Console(file=sys.stderr)
        errCons.print(Padding(Markdown("To open a story in the browser invoke `hn.py open [stpryID]`"), (1, 0, 0, 0)))


if len(args) == 0:
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(fetchTopStoriesParallel())
    loop.run_until_complete(future)

    stories = future.result()

    history.appendToHistory(list(filter(lambda s: s.loadedFromHist is False, stories)))

    cons = Console()
    printStoriesWithRich(stories, cons)

    exitPeacefully()

command = args[0]

if command == "open":
    if len(args) < 2:
        print(f'no story ID provided to open in browser')
        exitAngrily()

    openInBrowser(int(args[1]))
elif command == "lh":
    cons = Console()
    cons.print(Markdown("## From History"))
    printStoriesWithRich(history.stories[:config.n], cons)
elif command == 'rl':
    readLater = ReadLater(config)
    if len(args) < 2:
        cons = Console()
        cons.print(Markdown("## Stored for later reading"))
        stories = readLater.getReadLaterItems()
        printReadLaterStoriesWithRich(stories, cons)
    else:
        # Argument is the story ID I want to read later
        story = history.getStory(int(args[1]))
        readLater.addToReadLater(story)
