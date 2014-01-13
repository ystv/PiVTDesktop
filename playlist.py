import xml.etree.ElementTree as ElTree

class Playlist(object):
    """ Store, load and save a video playlist
    
    """
    def __init__(self):
        self.playlist = []
        self.index = 0
        
    def loadPlaylist(self, filename):
        tree = ElTree.parse(filename)
        root = tree.getroot()
        
        # Clear current playlist
        self.playlist = []
        for item in root:
            name = item[0].text
            length = item[1].text
            self.playlist.append((name, length))
        
    
    def savePlaylist(self, filename):
        root = ElTree.Element("playlist")
        
        for name, length in self.playlist:
            item = ElTree.SubElement(root, "item")
            itemname = ElTree.SubElement(item, "filename")
            itemname.text = name
            itemlen = ElTree.SubElement(item, "length")
            itemlen.text = str(length)
        
        tree = ElTree.ElementTree(root)
        tree.write(filename)
        
    def getCurrentItemName(self):
        item, duration = self.playlist[self.index]
        
        return item
    
    def getNextItem(self):
        if len(self.playlist) == 0:
            return -1
            self.index = -1
        
        self.index = self.index + 1
        
        if len(self.playlist) <= self.index:
            self.index = 0
            return self.playlist[0]
        else:
            return self.playlist[self.index]
        
    def addItem(self, filename, length, index=-1):
        if index == -1:
            index = len(self.playlist)
        self.playlist.insert(index, (filename, length))  
      
    def moveUp(self, ind):
        if (ind + 1) > len(self.playlist):
            raise ValueError
        
        if self.index == ind:
            changecurrent = True
        else:
            changecurrent = False
            
        item = self.playlist.pop(ind)
        
        if ind == 0:
            ind = len(self.playlist) + 1
           
        self.playlist.insert(ind-1, item)
        
        if changecurrent == True:
            self.index = ind - 1
        
    def moveDown(self, ind):
        if (ind + 1) > len(self.playlist):
            raise ValueError
        
        if self.index == ind:
            changecurrent = True
        else:
            changecurrent = False
            
        item = self.playlist.pop(ind)
        
        if ind >= len(self.playlist):
            ind = -1
            
        self.playlist.insert(ind+1, item)
        
        if changecurrent == True:
            self.index = ind + 1  
        
    def removeItem(self, index):
        if (index + 1) > len(self.playlist):
            raise ValueError
        
        if self.index == index:
            self.getNextItem()
            
        self.playlist.pop(index)