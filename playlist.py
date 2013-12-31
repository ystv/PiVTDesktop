

class Playlist(object):
    """ Store, load and save a video playlist
    
    """
    def __init__(self):
        self.playlist = []
        self.index = 0
        
    def loadPlaylist(self, filename):
        pass
    
    def savePlaylist(self, filename):
        pass
    
    def getNextItem(self):
        if len(self.playlist) == 0:
            return -1
        
        self.index += 1
        
        if len(self.playlist) > self.index:
            self.index = 0
            return self.playlist[0]
        else:
            return self.playlist[self.index]