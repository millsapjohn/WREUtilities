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
    if i.endswith(tar):
        continue
    elif i.endswith(gz):
        continue
    elif i.endswith(py):
        continue
    elif i.startswith("bmosaic"):
        files.append(i)
    elif i.startswith('xmrg'):
        files.append(i)
if len(files) == 0:
    sys.exit("No XMRG files found in this directory")

# call the xmrg2dss.exe process on every file
# values hardcoded for the time being
if sys.argv[1] == '-e':
    for i in files:
        subprocess.run([r'C:\Program Files (x86)\HEC\HEC-GridUtil\2.0\grid\gridloadXMRG.exe', f'xmrg={i}', f'dss={i}.dss', 'grid=SHG', 'site=WGRFC', 'fpart=PRECIP'])
elif sys.argv[1] == '-c':
    for i in files:
        subprocess.run([r'C:\Program Files (x86)\HEC\HEC-GridUtil\2.0\grid\gridloadXMRG.exe', f'xmrg={i}', f'dss={sys.argv[2]}.dss', 'grid=SHG', 'site=WGRFC', 'fpart=PRECIP'])
elif sys.argv[1] == '-h':
    print('xmrg_extract.py Help Menu')
    print('Arguments')
    print('-e: extract all files in directory into individual .dss records')
    print('c: combine all files in directory into a single .dss record. Requires second argument specifying .dss file name')
    print('-h: launch help menu')
    print('Example Usage')
    print('python xmrg_extract.py -e')
    print('python xmrg_extract.py -c sample_file_name.dss')
    print('python xmrg_extract.py -h')
else:
    print('incorrect arguments. type \'python xmrg_extract.py -h\' for help')
