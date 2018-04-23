This setup guide should work for Windows 10. If you experience any problems with setup, ping Ross.

1. Install Git
    1. [Download](https://git-scm.com/download/win) 64-bit git for windows
    2. Install and hit next for everything
2. Install PyCharm 
    1. [Download](https://www.jetbrains.com/pycharm/download/download-thanks.html?platform=windows) community edition for Windows
    2. When prompted, install bash and markdown support
    3. Othrewise hit next for everything
3. Install Python 3
    1. [Download](https://www.python.org/downloads/windows/) and choose the latest python 3 'Windows x86-64 executable installer' 
3. In git, type ```git clone https://github.com/pocc/merlink```
4. Open PyCharm and open a project in the merlink folder you cloned
5. Set Python Intepreter
    1. Go to Edit > Settings > Project > Interpreter > Click on the gear icon in the upper-right-hand corner
    2. Hit "Add..."
    2. Choose New Environment
    3. In base interpreter, click on the ellipses to the right and enter ```%appdata%\local\programs\python``` in open window. You should see an executable you can select.
6. Install missing packages
    1. Click on requirements.txt on the left hand side
    2. Once you click on its text, PyCharm should prompt you to install the missing libraries
    3. OK those installs
7. Run application
    1. Go to the /src folder and click on 'merlink.py'
    2. Click on it and then go to Run > Run 'merlink'
    3. Verify that it loads correctly
8. If you don't have a github account, [set one up](https://github.com/join).
