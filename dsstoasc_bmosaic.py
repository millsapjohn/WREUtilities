import os
import sys
import datetime
from pathlib import Path

try:
    os.remove("hraptab.dss")
except FileNotFoundError:
    print("No hraptab found")

files = []
path = Path.cwd()
for i in os.listdir(path):
    if i.endswith(".dss"):
        files.append(i)
file = open("dss2asc_batch_convert.bat", "a")
file.write("@echo off\n")
file.write("setlocal enabledelayedexpansion\n")
file.write("\n")
file.write(":main")
file.write("setlocal")
file.write("\n")
for f in files:
    filename = f.removesuffix(".dss")
    file_parts = filename.split("_")
    date = file_parts[1]
    year = int(date[0:4])
    if date[4] == "0":
        month = int(date[5])
    else:
        month = int(date[4:6])
    if date[6] == "0":
        day = int(date[7])
    else:
        day = int(date[6:8])
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
    
    file.write(f"dss2ascgrid output={filename}.asc dss={f} pathname={dss_string}")
    file.write("\n")

file.write("endlocal\n")
file.write("goto :eof")
file.close()
    
