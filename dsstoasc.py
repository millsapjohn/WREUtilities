# script for creating .asc grid files from .dss files
# NOTE: I have not tried this on a .dss file containing multiple rasters. That behavior is undefined
# at this time.
import os
import sys
import datetime
from pathlib import Path
import subprocess

# hraptab.dss is a file generated when converting XMRG files to .dss. Remove it from directory
# if it exists to avoid processing it.
try:
    os.remove("hraptab.dss")
except FileNotFoundError:
    print("No hraptab found")

# initialize list of valid files in the current working directory
files = []
path = Path.cwd()
for i in os.listdir(path):
    if i.endswith(".dss"):
        files.append(i)
if len(files) == 0:
    sys.exit('No .dss files found in this directory')

# extraction of datetime from filename. The dsstoascGrid.exe executable is very particular about formatting.
for f in files:
    if f.startswith('bmosaic'):
        filename = f.removesuffix('.dss')
        file_parts = filename.split('_')
        date = file_parts[1]
        year = int(date[0:4])
        if date[4] == '0':
            month = int(date[5])
        else:
            month = int(date[4:6])
        if date[6] == '0':
            day = int(date[7])
        else:
            day = int(date[6:8])
    else:
        filename = f.removesuffix(".dss")
        file_parts = filename.split("_")
        date = file_parts[1]
        year = int(date[4:])
        if date[0] == "0":
            month = int(date[1])
        else:
            month = int(date[0:2])
        if date[2] == "0":
            day = int(date[3])
        else:
            day = int(date[2:4])
    time = int(file_parts[2].removesuffix("z"))
    a_part = "SHG"
    b_part = "WGRFC"
    c_part = "PRECIP"
    f_part = "PRECIP"

    if time != 0:
        e_date_time = datetime.datetime(year, month, day, time, 0, 0)
        e_part = e_date_time.strftime("%d%b%Y") + ":" + e_date_time.strftime("%H") + "00"
    else:
        e_date_time = datetime.datetime(year, month, day, time, 0, 0)
        e_date_time = e_date_time + datetime.timedelta(hours=-1)
        e_part = e_date_time.strftime("%d%b%Y" + ":" + e_date_time.strftime("%H") + "00")
        e_date_time = e_date_time + datetime.timedelta(hours=1)
        e_part = e_part.replace("2300", "2400")
    d_date_time = e_date_time + datetime.timedelta(hours=-1)
    d_part = d_date_time.strftime("%d%b%Y" + ":" + d_date_time.strftime("%H") + "00")
    dss_string = "/" + a_part + "/" + b_part + "/" + c_part + "/" + d_part +"/" + e_part + "/" + f_part + "/"
    
    # call dsstoasc.exe on each file, with the correctly-prepared pathname string
    # note: the pathname for a .dss file is different from the system path; this
    # references the variables that are already stored in the .dss header.
    # file.write(f"dss2ascgrid output={filename}.asc dss={f} pathname={dss_string}")
    subprocess.run([r'C:\Program Files (x86)\HEC\HEC-GridUtil\2.0\grid\dss2ascGrid.exe', f'output={filename}.asc', f'dss={f}', f'pathname={dss_string}'])
