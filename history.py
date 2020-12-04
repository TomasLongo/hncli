import os

from story import Story


class History:

    def __init__(self, config):
        self.histPath = self._checkHistfileAndCreateIfNeccessary(config)
        self.stories = self._loadFromHistoryFile()

    def _checkHistfileAndCreateIfNeccessary(self, config):
        """
            Checks if the historyfile exists. If not construct it.
            Returns the path to the histfile
        """

        pathToHistfile = config.histfile
        if "~" in pathToHistfile:
            pathToHistfile = os.path.expanduser(pathToHistfile)

        if os.path.isfile(pathToHistfile) is False:
            [path, f] = os.path.split(pathToHistfile)
            try:
                os.mkdirs(path)
            except FileExistsError:
                print(f'{path} already exists')
            finally:
                hf = open(pathToHistfile, 'w')
                hf.close()

        return pathToHistfile

    def incrementOpenCountInHistory(self, storyID: int):
        story = self.getStory(storyID)
        story.openCount = story.openCount + 1
        self._overwriteHistoryFile(self.stories)
        self._reloadHistory()

    def _loadFromHistoryFile(self):
        """ Loads all stories from the history file """

        loadedStories = []
        with open(self.histPath, 'r') as historyFile:
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

    def _reloadHistory(self):
        self.stories = self._loadFromHistoryFile()

    def appendToHistory(self, stories):
        """ Appends the passed list of stories to a file concverting ist fields into csv format """

        with open(self.histPath, 'a') as historyFile:
            for story in stories:
                historyFile.write(f'{story.id};{story.title};{story.url};{story.openCount}\n')

        self._reloadHistory()

    def _overwriteHistoryFile(self, stories):
        """ Replaces the history file with the passed stories """

        with open(self.histPath, 'w') as historyFile:
            for story in stories:
                historyFile.write(f'{story.id};{story.title};{story.url};{story.openCount}\n')

        self._reloadHistory()

    def isStoryInHistory(self, storyID):
        for s in self.stories:
            if s.id == storyID:
                return True

        return False

    def getStory(self, storyID: int):
        """
            Fetches a specific story from the history. Returns None if not
            found
        """

        for h in self.stories:
            if h.id == storyID:
                return h

        return None
