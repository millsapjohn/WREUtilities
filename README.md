# WRE Utilities

This is a collection of Python scripts I've created to automate some parts of my job as a Water Resource Engineer.

As of this commit (12/1/2022), all of these utilities operate on all matching files in a particular directory.
All utilities other than xmrg_extract.py do not take any arguments.

## anint.py
Performs anisotropic inverse-distance weighted interpolation from irregular points to a generated grid. This
algorithm was proposed by Tim D. Osting as a method of generating surfaces from bathymetric data. The script
is set up as a QGIS processing script at this time, and as of this commit (28-12-2022) doesn't work yet.

## anint2.py
While the above module is intended to be a QGIS plugin, dealing with all the extraneous functionality is
annoying while I'm trying to work out the logic. This one is a standalone Python module. As of this commit
(12-01-2023) it doesn't work yet, but I'm getting close.

## convertmm.py
Simple script to convert .asc files from mm (millimeters) to in (inches).

## convertnegative.py
Removes negative values from an .asc raster (converts them to zero).

## dsstoasc.py
Converts all .dss files in a directory to .asc. Requires the "dss2ascGrid.exe" executable from the US Army Corps
of Engineers (USACE) Hydraulic Engineering Center (HEC). This executable is distributed as part of the HEC-RAS
download package. This now supports the two filename formats I've come across.

## joinasc.py
Merges all .asc files in a directory.

## massmover.py
Moves all files in a directory to a new directory. Doesn't work right now because I haven't done anything with
it.

## unzip.py
Unzips all zip files in a directory.

## xmrg2tif.py
Working on a python-native script for extracting XMRG files. Still in the beginning phase of this project.

## xmrg_extract.py
Requires the "gridloadXMRG.exe" executable from the US Army Corps of Engineers (USACE) Hydraulic Engineering
Center (HEC). This executable is distributed as part of the HEC-RAS download package.<br/>
Extracts files in a directory from XMRG format to .dss format. Commandline arguments to specify method:<br/>
    -e flag extracts each file to a separate .dss file.<br/>
    -c flag extracts all files in directory to a combined .dss record.<br/>
    -h flag shows help menu.
