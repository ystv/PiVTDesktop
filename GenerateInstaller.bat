rmdir dist /Q /S
del PiVTDesktopSetup.exe
C:\Python27\Scripts\pyinstaller.exe PiVTDesktop.py --noconsole -i PiVT_icon.ico --onefile
copy README.md dist
copy COPYING.txt dist
copy config.yaml dist
copy PiVT_icon.ico dist
"D:\Programs\NSIS\makensis.exe" PiVTDesktop.nsi
rmdir build /Q /S
del *.pyc /Q