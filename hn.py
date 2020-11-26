#! /usr/bin/python3

import sys
import requests
import webbrowser
from rich.console import Console
from rich.text import Text

options = sys.argv[1:]

topStories = " https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty"
itemBaseURL = " https://hacker-news.firebaseio.com/v0/item/"


def exitPeacefully():
    sys.exit(0)


def fetchStory(id):
    resp = requests.get(f'{itemBaseURL}/{id}.json')
    return resp.json()


def fetchTopStories():
    resp = requests.get(topStories)

    cons = Console()

    itemIDs = resp.json()

    for itemID in itemIDs[:20]:
        itemResponse = requests.get(f'{itemBaseURL}/{itemID}/.json')
        json = itemResponse.json()

        text = Text(str(itemID), style="magenta")
        text.append(f' {json["title"]}', style="yellow")

        cons.print(text)


# fetch the story with passed id and open its url in the browser
def openInBrowser(itemID):
    item = fetchStory(itemID)
    webbrowser.open_new_tab(item["url"])
    exitPeacefully()


if len(options) == 0:
    fetchTopStories()
    exitPeacefully()

command = options[0]

if command == "open":
    openInBrowser(options[1])
