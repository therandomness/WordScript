#!/usr/bin/python3
import argparse
import os
import xml.etree.ElementTree
import glob
import subprocess

MAGIC_SONG_NAMES=["Verse", "Chorus", "Bridge", "CCLI Song #", "Interlude", "Ending"]

def songparse(wordsfile):
    output = {"Title":[],"Order":[]}
    current_block = "Title"

    with open(wordsfile, "r") as songfile:
        for line in songfile:
            line = line.strip()
            if len(line) > 0:
                if any(map(line.startswith, MAGIC_SONG_NAMES)):
                    current_block = line
                    output[current_block] = []
                    output["Order"] += [current_block]
                    continue
                output[current_block] += [line.strip()]

    assert output["Order"][-1].startswith("CCLI"), "Bad parse"
    output["Order"] = output["Order"][:-1]

    return output

class SongPlates:
    def __init__(self, words_template, title_template):
        self.words_et = xml.etree.ElementTree.parse(words_template)
        self.words_lines = []
        # Finding all the tagged things and splitting them up
        for item in self.words_et.findall('.//*[@id]'):
            if (item.attrib['id'] == "words"):
                self.words_lines += [x for x in item]

        self.title_et = xml.etree.ElementTree.parse(title_template)
        self.title_title = None
        self.title_author = None
        # Finding all the tagged things and splitting them up
        for item in self.title_et.findall('.//*[@id]'):
            if (item.attrib['id'] == "SongTitle"):
                self.title_title = item
            elif (item.attrib['id'] == "SongAuthor"):
                self.title_author = item

    def num_lines_per_plate(self):
        return len(self.words_lines)

    def gen_plates(self, parsed_song):

        songTitle = parsed_song["Title"][0]
        if not os.path.exists(songTitle):
            os.makedirs(songTitle)
            
        for section in parsed_song:
            if not any(map(section.startswith, ["Title", "Order", "CCLI"])):
                count = 0
                shortSection = "".join([x[0] for x in section.split(" ")])
                """Yield successive n-sized chunks from lst."""
                for i in range(0, len(parsed_song[section]), self.num_lines_per_plate()):
                    count += 1
                    
                    words_for_plate = parsed_song[section][i:i + self.num_lines_per_plate()]

                    short_words = "".join(words_for_plate)
                    short_words = "".join(short_words.split())
                    short_words = short_words.replace("'", "")
                    
                    filename = "{}-{:02}-{:.15s}".format(shortSection,count,short_words)
                    
                    for element, text in zip(self.words_lines,words_for_plate):
                        element.text = text

                    self.words_et.write("temp.svg")

                    subprocess.check_call(
                        [
                            "inkscape",
                            "-z",
                            "-C",
                            "-e={}.png".format(os.path.join(songTitle, filename)),
                            "-f=temp.svg",
                            "-w=1920",
                        ]
                    )

        self.title_title.text = '"{}"'.format(songTitle)
        self.title_author.text = None
        for i in parsed_song:
            if i.startswith("CCLI"):
                self.title_author.text = parsed_song[i][0].replace("|", "/")

        self.title_et.write("temp.svg")
        subprocess.check_call(
            [
                "inkscape",
                "-z",
                "-C",
                "-e={}.png".format(os.path.join(songTitle, "titleslide")),
                "-f=temp.svg",
                "-w=1920",
            ]
        )
                    




plates = SongPlates("basebackground.svg", "introslide.svg")
for file in glob.glob("*.txt"):
    song_info = songparse(file)
    plates.gen_plates(song_info)
