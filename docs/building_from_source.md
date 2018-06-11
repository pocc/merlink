# Building from Source
## Windows
1. Go to directory root

`pyinstaller --windowed --icon=.\src\media\miles.ico --clean --add-data="src\media\;media" --add-data="src\scripts;scripts" --add-data="LICENSE.txt;." .\src\merlink.py`
* **--windowed**: Don't use a command prompt
* **--icon=icon.ico**: Icon to use for executable
* **--clean**: Get rid of cruft from previous installs
* **--add-data="X;Y"**: put file/folder X into the executable as file/folder Y
## macOS
## Linux
pyinstaller --windowed --icon=./src/media/miles.ico --clean --add-data="src/media/:media" --add-data="src/scripts:scripts" --add-data="LICENSE.txt:." ./src/merlink.py
