# WordScript

Designed to convert words from systems such as CCLI SongSelect into PNG slides to be used in pre-recorded songs.

Place text files in the root directory and run the script.  It will create a folder per text file and populate it with PNG files.

`ExampleSong.txt` is provided to help you test the system is working.

## Usage on Linux

Install python3 and inkscape.  For Ubuntu try

    sudo apt install python3 inkscape

Excute script from root folder of repo.

    python3 autoLyrics.py

## Usage on Windows

Install Python3 for windows https://www.python.org/downloads/release/python-385/

Install Inkscape for windows https://inkscape.org/release/inkscape-1.0/

Run by either:
* Running by double-clicking `autoLyrics.py`, a window should print progress as the slides are created
* Enter the console, navigate to the root of this repo and execute `py autoLyrics.py`
