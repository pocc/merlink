# Building from Source
*For either of these, first cd to the directory root*
## With spec file
`pyinstaller src/pyinstaller.<OS>.spec`

## Without spec file, using command line options
* Use --onefile if you don't want a bundle of files
### Windows
`pyinstaller --windowed --icon=.\src\media\miles.ico --clean --add-data="src\media\;media" --add-data="src\scripts;scripts" --add-data="LICENSE.txt;." .\src\merlink.py`
* **--windowed**: Don't use a command prompt
* **--icon=icon.ico**: Icon to use for executable
* **--clean**: Get rid of cruft from previous installs
* **--add-data="X;Y"**: put file/folder X into the executable as file/folder Y
### macOS
### Linux
*Same as Windows, but with : and / instead of ; and \.*

`pyinstaller --windowed --icon=./src/media/miles.ico --clean --add-data="src/media/:media" --add-data="src/scripts:scripts" --add-data="LICENSE.txt:." ./src/merlink.py`
