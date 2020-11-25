import requests
from rich import print


topStories = " https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty"
itemBaseURL = " https://hacker-news.firebaseio.com/v0/item/"
resp = requests.get(topStories)

itemIDs = resp.json()

for itemID in itemIDs[:5]:
    itemResponse = requests.get(f'{itemBaseURL}/{itemID}/.json')
    json = itemResponse.json()
    print(f'[bold magenta]{json["title"]}[/bold magenta]')
