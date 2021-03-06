#!/usr/bin/python3
"""
Copyright 2020 Dominic J. P. Crutchley

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import os
import xml.etree.ElementTree
import glob
import subprocess
import platform

MAGIC_SONG_NAMES = [
    "Verse",
    "Chorus",
    "Pre-Chorus",
    "Tag",
    "Bridge",
    "CCLI Song #",
    "Interlude",
    "Ending"
]

TSPAN_TAG = ".//{http://www.w3.org/2000/svg}tspan"


def call_inkscape(inputpath, outputpath):
    """Call inkscape to build a PNG

    Keyword arguements:
    inputpath -- string containing the filename of an SVG file.
    outputpath -- string containing the output filename (.png will be added).
    """

    print("Writing {}.png".format(outputpath))

    if platform.system() == "Windows":
        subprocess.check_call(
            [
                "C:\\Program Files\\Inkscape\\bin\\inkscape.exe",
                "-C",
                "-o",
                "{}.png".format(outputpath),
                "-w",
                "1920",
                inputpath,
            ]
        )
    else:
        subprocess.check_call(
            [
                "inkscape",
                "-z",
                "-C",
                "-e={}.png".format(outputpath),
                "-f={}".format(inputpath),
                "-w=1920",
            ]
        )


def songparse(wordsfile):
    """Parse a txt file for song lyrics.
    Returns a dictionary containing each block of lyrics, the title and
    the original order of the blocks.

    Keyword arguements:
    wordsfile -- string containing the filename of a text file.
    """
    output = {"Title": [], "Order": []}
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
    """A class to hold together useful information about a set of song 'plates'
    """

    def __init__(self, words_template, title_template):
        """Build songplates by parsing SVG templates for tagged elements.

        Keyword arguements:
        words_template -- string filename of SVG template for words
        title_template -- string filename of SVG template for the title slide
        """
        self.words_template = words_template
        self.title_template = title_template

    def num_lines_per_plate(self):
        """Return the number of lines available in the words template
        """
        words_et = xml.etree.ElementTree.parse(self.words_template)
        words_lines = []
        # Finding all the tagged things and splitting them up
        for item in words_et.findall(TSPAN_TAG):
            if "<WORDS>" in item.text:
                words_lines += [item]

        return len(words_lines)

    @staticmethod
    def pad_array(array_input, output_size):
        """Pad an array by pre/post-pending empty strings.
        """

        extra_space = output_size - len(array_input)

        while extra_space > 0:
            if extra_space > 1:
                array_input = [""] + array_input + [""]
                extra_space -= 2
            else:
                array_input = array_input + [""]
                extra_space -= 1
        return array_input

    def gen_word_plates(self, parsed_song):
        """Generate the words images for a given song.
        Steps through the various blocks of words creating PNG images.

        Keyword arguements:
        parsed_song -- A dictionary, typcially the output from songparse()
        """

        song_title = parsed_song["Title"][0]
        if not os.path.exists(song_title):
            os.makedirs(song_title)

        for section in parsed_song:
            if not any(map(section.startswith, ["Title", "Order", "CCLI"])):
                count = 0
                short_section = "".join([x[0] for x in section.split(" ")])

                # Yield successive n-sized chunks from lst.
                for i in range(
                        0,
                        len(parsed_song[section]),
                        self.num_lines_per_plate()):
                    count += 1

                    words_for_plate = parsed_song[
                        section][i:i + self.num_lines_per_plate()]

                    words_for_plate = SongPlates.pad_array(
                        words_for_plate,
                        self.num_lines_per_plate()
                        )

                    short_words = "".join(words_for_plate)
                    short_words = "".join(short_words.split())
                    short_words = short_words.replace("'", "")

                    filename = "{}-{:02}-{:.15s}".format(
                        short_section,
                        count,
                        short_words
                        )

                    words_et = xml.etree.ElementTree.parse(
                        self.words_template)

                    words_lines = []
                    # Finding all the tagged things and splitting them up
                    for item in words_et.findall(TSPAN_TAG):
                        if "<WORDS>" in item.text:
                            words_lines += [item]

                    for element, text in zip(
                            words_lines,
                            words_for_plate):
                        element.text = element.text.replace("<WORDS>", text)

                    words_et.write("temp.svg")

                    call_inkscape(
                        "temp.svg",
                        os.path.join(
                            song_title,
                            filename
                        )
                    )

    def gen_title_plate(self, parsed_song):
        """Generate the title image for a given song.

        Keyword arguements:
        parsed_song -- A dictionary, typcially the output from songparse()
        """

        song_title = parsed_song["Title"][0]
        if not os.path.exists(song_title):
            os.makedirs(song_title)

        title_et = xml.etree.ElementTree.parse(self.title_template)

        xml_tags = {
            "<TITLE>": [],
            "<AUTHOR>": [],
            "<CCLIsong>": [],
            "<CCLIlicence>": [],
            }

        # Finding all the tagged things and splitting them up
        for item in title_et.findall(TSPAN_TAG):
            for tag in xml_tags:
                if tag in item.text:
                    xml_tags[tag] += [item]

        assert xml_tags["<TITLE>"] is not None, \
            "The SVG template must contain a text element named 'SongTitle'"
        assert xml_tags["<AUTHOR>"] is not None, \
            "The SVG template must contain a text element named 'SongAuthor'"

        def replace_tags(key, new_value):
            for item in xml_tags[key]:
                item.text = item.text.replace(key, new_value)

        replace_tags("<TITLE>", f"{song_title}")

        for i in parsed_song:
            if i.startswith("CCLI"):
                replace_tags(
                    "<AUTHOR>",
                    parsed_song[i][0].replace("|", "/")
                    )

                if "#" in i:
                    replace_tags(
                        "<CCLIsong>",
                        i.split("#")[1].strip()
                        )

                for j in parsed_song[i]:
                    if j.startswith("CCLI Licence"):
                        replace_tags(
                            "<CCLIlicence>",
                            j.split("No.")[1].strip()
                            )

        title_et.write("temp.svg")

        call_inkscape("temp.svg", os.path.join(song_title, "titleslide"))


plates = SongPlates("basebackground.svg", "introslide.svg")
for file in glob.glob("*.txt"):
    song_info = songparse(file)
    plates.gen_word_plates(song_info)
    plates.gen_title_plate(song_info)
