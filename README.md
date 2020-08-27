# WordScript

Designed to convert words from systems such as CCLI SongSelect into PNG slides to be used in pre-recorded songs.

**Note: You should ensure you have the appropriate licenses before reproducing lyrics from CCLI SongSelect in any form.  This script does not provide lyrics, it is intended to aid those who work with them regularly.**

Place text files in the root directory and run the script.  It will create a folder per text file and populate it with PNG files.

`ExampleSong.txt` is provided to help you test the system is working.

## Customisation

You can customise the slide templates by directly editing them in Inkscape.  The script uses 'well known tags' in the text fields to identify and alter the text, so actions like: adding elements, changing colors, fonts and sizing should all work seemlessly.

The tags matched in introslide.svg are:
* <TITLE> - Replaced with the song title
* <AUTHOR> - Replaced with the authors names
* <CCLIsong> - Replaced with the CCLI Song number
* <CCLIlicence> - Replaced with the CCLI Licence number

The tags matched  in basebackground.svg are:
* <WORDS> - Each instance found is replaced with the next  line of a song.
    * So if there's  3 instances of <WORDS> in the template, 3 lines of song will print per image.

Also, you can edit the sample text to have the number of lines you want per slide and the script should follow you.

## Usage
### Usage on Linux

Install python3 and inkscape.  For Ubuntu try

    sudo apt install python3 inkscape

Excute script from root folder of repo.

    python3 auto_lyrics.py

### Usage on Windows

Install [Python3 for windows](https://www.python.org/downloads/release/python-385/)

Install [Inkscape for windows](https://inkscape.org/release/inkscape-1.0/)

Run by either:
* Running by double-clicking `auto_lyrics.py`, a window should print progress as the slides are created
* Enter the console, navigate to the root of this repo and execute `py auto_lyrics.py`
