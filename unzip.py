# simple utility to unzip all files in a directory
import os
import sys
from pathlib import Path
from zipfile import ZipFile

path = Path.cwd()
# initialize list of ZIP files in the directory
files = []

# add ZIP files to list
for i in os.listdir(path):
    if i.endswith(".zip"):
        files.append(i)

# check if ZIP files are present, exit if False
if len(files) == 0:
    sys.exit("No ZIP files found in this directory")

for f in files:
    # create a new subdirectory for each ZIP file
    new_dir = f.replace('.zip', '')
    new_dir = os.mkdir('{path}{new_dir}')
    # extract all files in ZIP to new subdirectory
    with ZipFile(r'{path}{f}', 'r') as zObject:
        zObject.extractall(path='{new_dir}')
    zObject.close()
