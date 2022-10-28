import os
import sys
from pathlib import Path

files = []
path = Path.cwd()
for i in os.listdir(path):
    if i.endswith(".asc"):
        files.append(i)
if len(files) == 0:
    sys.exit("No .asc files found in this directory")

for f in files:
    reader = open(f, "r")
    writer = open("new.asc", "a")
    for i, line in enumerate(reader):
        if i <= 5:
            writer.write(line)
        elif i > 5:
            word_list = str.split(line)
            word_list = [-9999 if float(w) == -9999 else float(w) / 25.4 for w in word_list]
            writer.write(" ".join([str(w) for w in word_list]) + "\n")
    reader.close()
    writer.close()
    os.remove(f)
    os.rename("new.asc", f)
