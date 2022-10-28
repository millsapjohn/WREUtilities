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

reader = open(files[0], "r")
writer = open("summed.asc", "a")
for i, line in enumerate(reader):
    if i <= 5:
        continue
    else:
        writer.write(line)
reader.close()
writer.close()

for f in files[1:]:
    reader_1 = open("summed.asc", "r")
    reader_2 = open(f, "r")
    writer = open("new.asc", "a")
    for i, line_1 in enumerate(reader_1):
        if i <= 5:
            continue
        for j, line_2 in enumerate(reader_2):
            if j <= 5:
                continue
            else:
                temp_list_1 = str.split(line_1)
                temp_list_2 = str.split(line_2)
                temp_list_1 = [0 if float(w) < 0 else w for w in temp_list_1]
                temp_list_2 = [0 if float(w) < 0 else w for w in temp_list_2]
                temp_list_1 = [float(w) + float(x) for w, x in zip(temp_list_1, temp_list_2)]
                temp_list_1 = [-9999 if float(w) <= 0 else w for w in temp_list_1]
                writer.write(" ".join([str(w) for w in temp_list_1]) + "\n")
    reader_1.close()
    reader_2.close()
    writer.close()
    os.remove("summed.asc")
    os.rename("new.asc", "summed.asc")

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
