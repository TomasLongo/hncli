import requests
from rich.console import Console
from rich.text import Text


topStories = " https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty"
itemBaseURL = " https://hacker-news.firebaseio.com/v0/item/"

resp = requests.get(topStories)

cons = Console()

itemIDs = resp.json()

for itemID in itemIDs[:15]:
    itemResponse = requests.get(f'{itemBaseURL}/{itemID}/.json')
    json = itemResponse.json()

    text = Text(str(itemID), style="magenta")
    text.append(f' {json["title"]}', style="yellow")

    cons.print(text)
