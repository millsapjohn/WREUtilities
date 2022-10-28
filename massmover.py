import sys
import os
from pathlib import Path

from_path = str.strip(input("Enter the origin file path: "), "\"")
to_path = str.strip(input("Enter the destination file path: "), "\"")
file_type = input("Enter the file extension to be moved: ")

files = []

for i in os.listdir(from_path):
    if i.endswith(file_type):
        files.append(i)

for f in files:
    src = from_path + "\\" + f
    dst = to_path + "\\" + f 
    os.popen(f"copy {src} {dst}")
