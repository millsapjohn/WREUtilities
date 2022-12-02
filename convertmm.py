# simple utility to convert .asc grids from millimeters to inches.
import os
import sys
from pathlib import Path

# initialize files list
files = []
path = Path.cwd()
# add all .asc files in the current working directory to files list
for i in os.listdir(path):
    if i.endswith(".asc"):
        files.append(i)
# if no .asc files are found, exit
if len(files) == 0:
    sys.exit("No .asc files found in this directory")

for f in files:
    reader = open(f, "r")
    writer = open("new.asc", "a")
    for i, line in enumerate(reader):
        # .asc grids have five lines of header material. This if statement ensures they stay the same.
        if i <= 5:
            writer.write(line)
        # this if statement performs a conversion on each grid pixel (mm to in)
        elif i > 5:
            word_list = str.split(line)
            # -9999 is used as the default nodata value in .asc grids - make sure they stay the same.
            # .asc grids are literally just text files with the same number of words (pixels) in each line.
            # Because of this each "word" in the line has to be converted to float.
            word_list = [-9999 if float(w) == -9999 else float(w) / 25.4 for w in word_list]
            writer.write(" ".join([str(w) for w in word_list]) + "\n")
    reader.close()
    writer.close()
    # delete the old file
    os.remove(f)
    # rename the new file with the same name (in effect, replace the old file with the new, converted file)
    os.rename("new.asc", f)
