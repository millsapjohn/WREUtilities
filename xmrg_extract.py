# script for extracting all XMRG files in a given directory
# to DSS files

# either add location of xmrg2dss.exe to PATH, or place in 
# current working directory
import os
import sys
from pathlib import Path
import subprocess

# initialize list of valid files in the current working directory
files = []
path = Path.cwd()
for i in os.listdir(path):
    if i.startswith("bmosaic"):
        files.append(i)
if len(files) == 0:
    sys.exit("No XMRG files found in this directory")

# call the xmrg2dss.exe process on every file
# values hardcoded for the time being
for i in files:
    subprocess.run([r'C:\Program Files (x86)\HEC\HEC-GridUtil\2.0\grid\gridloadXMRG.exe', f'xmrg={i}', f'dss={i}.dss', 'grid=SHG', 'site=WGRFC', 'fpart=PRECIP'])
