import sys
import os
import datetime

from story import Story
from logger import logDebug


class ReadLater:
    def __init__(self, config):
        self.readLaterFile = self._checkLaterfileAndCreateIfNeccessary(config)

    def _checkLaterfileAndCreateIfNeccessary(self, config):
        """
            Checks if the read later file exists. If not construct it.
            Returns the path to the read later file.
            Also, deletes the present file if it is older than one day
            and creates a fresh one
        """

        pathToReadLaterFile = config.readLaterFile
        logDebug(f'Checking existence of {config.readLaterFile}')
        if "~" in pathToReadLaterFile:
            pathToReadLaterFile = os.path.expanduser(pathToReadLaterFile)

        if os.path.isfile(pathToReadLaterFile) is False:
            [path, f] = os.path.split(pathToReadLaterFile)
            try:
                os.makedirs(path)
            except FileExistsError:
                print(f'{path} already exists', file=sys.stderr)
            finally:
                print(f'creating read later file under {pathToReadLaterFile}', file=sys.stderr)
                hf = open(pathToReadLaterFile, 'w')
                hf.close()
        else:
            creationTime = datetime.date.fromtimestamp(os.stat(pathToReadLaterFile).st_birthtime)
            today = datetime.date.today()
            expiration = creationTime + datetime.timedelta(days=config.rlTTL)
            if (today > expiration):
                logDebug(f'read later is older than {config.rlTTL}d')
                os.remove(pathToReadLaterFile)
                hf = open(pathToReadLaterFile, 'w')
                hf.close()
            else:
                logDebug('read later is still fresh')

        return pathToReadLaterFile

    # StoryID und wir ziehen es uns aus der History. Oder wir
    # geben die Story hier komplett rein. --> Keine Abhängigkeit zu externem
    # Modul
    def addToReadLater(self, story):
        print(f'Adding {story.id} to read later', file=sys.stderr)
        with open(self.readLaterFile, 'a') as readLaterFile:
            readLaterFile.write(f'{story.id};{story.title};{story.url}')

    def getReadLaterItems(self):
        """ Returns a list of all items that were marked for later reading """
        stories = []
        logDebug(f'Reading later file from {self.readLaterFile}')
        with open(self.readLaterFile, 'r') as readLaterFile:
            for line in readLaterFile:
                stripped = line.strip('\n ')
                if stripped == '':
                    continue

                tokens = line.split(';')
                if len(tokens) != 3:
                    print(f'Erro reading read later file. Line has {len(tokens)} tokens', file=sys.stderr)
                    continue

                story = Story(id=tokens[0], title=tokens[1], url=tokens[2])
                stories.append(story)

            return stories

