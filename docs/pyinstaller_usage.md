---
title: pyinstaller_usage
---
# Building from Source
**NOTE**: Make sure you install the latest PyIntstaller directly
`pip install https://github.com/pyinstaller/pyinstaller/archive/develop.zip`

## With spec file
`pyinstaller -y pyinstaller.spec`

## Without spec file, using command line options
* Use --onefile if you don't want a bundle of files
* Make sure to use pyinstaller from directory root
### Windows
`pyinstaller -y --windowed --icon=.\src\media\miles.ico --clean --add-data="src;src" --add-data="LICENSE.txt;." .\merlink.py`
* **--windowed**: Don't use a command prompt
* **--icon=icon.ico**: Icon to use for executable
* **--clean**: Get rid of cruft from previous installs
* **--add-data="X;Y"**: put file/folder X into the executable as file/folder Y
### macOS
### Linux
*Same as Windows, but with : and / instead of ; and \.*

`pyinstaller -y --windowed --icon=./src/media/miles.ico --clean --add-data="src:src" --add-data="LICENSE.txt:." ./merlink.py`
