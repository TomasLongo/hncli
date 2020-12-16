import os

class ReadLater:
    def __init__(self, config):
        self.readLaterFile = self._checkLaterfileAndCreateIfNeccessary(config)

    def _checkLaterfileAndCreateIfNeccessary(self, config):
        """
            Checks if the historyfile exists. If not construct it.
            Returns the path to the histfile
        """

        pathToReadLaterFile = config.readLaterFile
        if "~" in pathToReadLaterFile:
            pathToReadLaterFile = os.path.expanduser(pathToReadLaterFile)

        if os.path.isfile(pathToReadLaterFile) is False:
            [path, f] = os.path.split(pathToReadLaterFile)
            try:
                os.mkdirs(path)
            except FileExistsError:
                print(f'{path} already exists')
            finally:
                hf = open(pathToReadLaterFile, 'w')
                hf.close()

        return pathToReadLaterFile

    # StoryID und wir ziehen es uns aus der History. Oder wir
    # geben die Story hier komplett rein. --> Keine Abhängigkeit zu externem
    # Modul
    def addToReadLater(self, story):
        with open(self.readLaterFile, 'a') as readLaterFile:
            readLaterFile.write(f'{story.id};{story.title};{story.url}')

    def getReadLaterItems():
        """ Returns a list of all items that were marked for later reading """
        items = []
        with open(self.readLaterFile) as readLaterFile:
            for line in readLaterFile:

       pass
