# CLI client for news.ycombinator.com

This little app provied access to the top stories from hackernews in the command line

[[image]]

## Usage

`hn.py -h` prints a some hints on how to use the app

### Get latest top stories

A simple invocation of `hn.py` fetches the latest 20 top stories. To tweak how many stories are fetched change the `n` parameter in the config.

The stories are printed as a list, showing the id, the title, and a little marker telling if the story is an external link.

![Fechting the latest top stories](readme-assets/fetch-stories.png)

### Open a story in the browser

`hn.py` outputs the story-id of every fetched story. To open a story in the browser use the `open` command with a story id

```shell
hn.py open [storyid]
```

The history file will track how many times a story has been opened in the browser

### Print a list of the history

`hn.py lh` shows the last n history entries

## Inner life

The script fetches top stories in two steps from the api:

1. The latest 500 top story ids are fetched
1. Out the 500 top notch stories, the first x IDs are picked and used to fetch the actual story (x can be configured)

Stories that are actually downloaded are cached in a history file


## History

Fetched stories are written into a history file to prevent unnecessary repeated invocations of the hackernews api. So, every story is fetched only once from the api. Subsequent invocations of the script will load old stories from the history.

StoryIDs that have been loaded from the history are printed in green when executing the script. Stories loaded from the api, are printed in magenta.
