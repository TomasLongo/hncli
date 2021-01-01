import os

from story import Story, copyStory


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
                os.makedirs(path)
            except FileExistsError:
                print(f'{path} already exists')
            finally:
                hf = open(pathToHistfile, 'w')
                hf.close()

        return pathToHistfile

    def updateStoryInHistory(self, newVersion):
        """
            Updates a story in the history by replacing the existing entry
            with the passed entry
        """

        oldVersion = self.getStory(newVersion.id)
        if (oldVersion is None):
            raise LookupError(f'Can not update story. Id {newVersion.id} was not found in history')

        self.stories.remove(oldVersion)
        self.stories.append(newVersion)
        self._overwriteHistoryFile(self.stories)
        self._reloadHistory()

    def incrementOpenCountInHistory(self, storyID: int):
        story = self.getStory(storyID)
        story.openCount = story.openCount + 1
        self.updateStoryInHistory(story)

    def _loadFromHistoryFile(self):
        """ Loads all stories from the history file """

        loadedStories = []
        with open(self.histPath, 'r') as historyFile:
            for line in historyFile:
                stripped = line.strip('\n ')
                if stripped == "":
                    continue

                tokens = stripped.split(";")

                starred = False if tokens[4] == 'False' else True

                story = Story(url=tokens[2].rstrip(),
                              loadedFromHist=True,
                              id=int(tokens[0]),
                              title=tokens[1],
                              openCount=int(tokens[3]),
                              starred=starred)

                loadedStories.append(story)

        return loadedStories

    def _reloadHistory(self):
        self.stories = self._loadFromHistoryFile()

    def appendToHistory(self, stories):
        """
            Appends the passed list of stories to a file
            converting its fields into csv format
        """

        with open(self.histPath, 'a') as historyFile:
            for story in stories:
                csv = self._convertStoryToCSV(story)
                historyFile.write(csv)

        self._reloadHistory()

    def _overwriteHistoryFile(self, stories):
        """ Replaces the history file with the passed stories """

        with open(self.histPath, 'w') as historyFile:
            for story in stories:
                csv = self._convertStoryToCSV(story)
                historyFile.write(csv)

        self._reloadHistory()

    def isStoryInHistory(self, storyID):
        for s in self.stories:
            if s.id == storyID:
                return True

        return False

    def getStory(self, storyID: int):
        """
            Fetches a specific story from the history and returns a copy of
            the story. Returns None if not found.
        """

        for h in self.stories:
            if h.id == storyID:
                return copyStory(h)

        return None

    def _convertStoryToCSV(self, story):
        return f'{story.id};{story.title};{story.url};{story.openCount};{story.starred}\n'


class NoOpHistory:
    def getStory(self, story):
        return None

    def isStoryInHistory(self, storyID):
        return False

    def appendToHistory(self, stories):
        pass

    def incrementOpenCountInHistory(self, storyID):
        pass
