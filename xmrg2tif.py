# script for converting all XMRG files in a given directory
# to geotiff
import sys
import os
from pathlib import Path
import subprocess

# initialize list of valid files in the current working directory
files = []
path = Path.cwd()
for i in os.listdir(path):
    # exclude subdirectories
    if os.path.isdir(i) == True:
        continue
    # exclude anything with a file extension - XMRG don't have extensions
    elif os.path.splitext(i)[1] != '':
        continue
    else:
        files.append(i)

if len(files) == 0:
    sys.exit('No XMRG files found in this directory')


