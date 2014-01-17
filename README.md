PiVTDesktop
=========

PiVTDesktop is a client to control the PiVT video server available at 
https://github.com/YSTV/PiVT in order to use the VT server functionality.

Playlists can be created from within the client and played using the server,
with a countdown of time remaining on the video and features to automatically
play the list.

Downloading PiVTDesktop
---------------------
Binaries are available from http://ystv.co.uk/PiVT or get the source from:

    git clone git://github.com/YSTV/PiVTDesktop.git
    
Prerequisites
------------------
PiVTDesktop uses the wxPython widget framework and YAML for configuration files,
however these are already included in the binaries.

The client was developed and tested on Windows, however should work on most
other platforms where wxPython is available.

Using PiVTDesktop
--------------------
Fire up the client and hit Connect->Connection Options and fill in some details

Then click the Add button and add a few files which will appear in the playlist

Finally select one of the files, wait for it to load and hit play.

Rejoice!

Configuration
-----------------
A configuration file is provided and will be updated internally by the system

