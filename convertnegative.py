# simple utility to remove small negative values in .asc grids
# some XMRG files from NOAA seem to have small negative values - if you choose, this utility converts them
# to nodata values.
import sys
import os
from pathlib import Path

# initialize files list
files = []
path = sys.argv[1]

# add .asc files to files list
for i in os.listdir(path):
    if i.endswith(".asc"):
        files.append(i)

if len(files) == 0:
    sys.exit('no .asc files found in this directory')

for f in files:
    reader = open(f, "r")
    writer = open("new.asc", "a")
    # .asc grid files have 6 lines of header material. This if statement ensures they get re-written.
    for i, line in enumerate(reader):
        if i <= 5:
            writer.write(line)
        elif i > 5:
            word_list = str.split(line)
            # the default nodata value in .asc grids is -9999; this if statement converts all negatives
            # to nodata
            word_list = [-9999 if float(w) < 0 else w for w in word_list]
            writer.write(" ".join([str(w) for w in word_list]) + "\n")
    reader.close()
    writer.close()
    # remove old file
    os.remove(f)
    # rename new file to same name as old file - essentially replacing it
    os.rename("new.asc", f)
