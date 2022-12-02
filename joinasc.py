# script to merge .asc grid files. Useful when wanting to combine rasters created from hourly rainfall.
import os
import sys
from pathlib import Path

# initialize list of .asc files to be converted.
files = []
path = Path.cwd()
for i in os.listdir(path):
    if i.endswith(".asc"):
        files.append(i)
if len(files) == 0:
    sys.exit("No .asc files found in this directory")

reader = open(files[0], "r")
writer = open("summed.asc", "a")
# .asc grid files have a six-line header. In order to avoid having to skip it every time, I'm choosing to
# skip it at the beginning and only insert it at the end.
for i, line in enumerate(reader):
    if i <= 5:
        continue
    # copying the first file in the list into the new, summed grid.
    else:
        writer.write(line)
reader.close()
writer.close()

# after the initial copy, performing a summing operation with each subsequent file.
for f in files[1:]:
    reader_1 = open("summed.asc", "r")
    reader_2 = open(f, "r")
    # new.asc is an ephemeral file used to store the summed values at each step; it overwrites summed.asc
    # at the end of each step.
    writer = open("new.asc", "a")
    for i, line_1 in enumerate(reader_1):
        if i <= 5:
            continue
        for j, line_2 in enumerate(reader_2):
            if j <= 5:
                continue
            else:
                # splitting each line into a list of all words i.e. raster pixels.
                temp_list_1 = str.split(line_1)
                temp_list_2 = str.split(line_2)
                # sometimes XMRG files have negative values for some reason. Convert negative values
                # to zero to make sure summing is correct.
                temp_list_1 = [0 if float(w) < 0 else w for w in temp_list_1]
                temp_list_2 = [0 if float(w) < 0 else w for w in temp_list_2]
                # sum each pixel value in the line.
                temp_list_1 = [float(w) + float(x) for w, x in zip(temp_list_1, temp_list_2)]
                # re-convert zero values to -9999, the default nodata value.
                temp_list_1 = [-9999 if float(w) <= 0 else w for w in temp_list_1]
                # merge pixels into a single line of text, write into the temporary file
                writer.write(" ".join([str(w) for w in temp_list_1]) + "\n")
    reader_1.close()
    reader_2.close()
    writer.close()
    os.remove("summed.asc")
    os.rename("new.asc", "summed.asc")

# after iterating through the file list, write the header info from the first file in the list.
reader_1 = open("summed.asc", "r")
reader_2 = open(files[0], "r")
writer = open("new.asc", "a")
for i, line in enumerate(reader_2):
    if i <= 5:
        writer.write(line)
    else:
        break
for i, line in enumerate(reader_1):
    writer.write(line)
reader_1.close()
reader_2.close()
writer.close()
os.remove("summed.asc")
os.rename("new.asc", "summed.asc")
