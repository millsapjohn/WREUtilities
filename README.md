# WRE Utilities

This is a collection of Python scripts I've created to automate some parts of my job as a Water Resource Engineer.

Most utilities do not take arguments; those that do are explained below.

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

## jxlparse.py 
Converts a Trimble .jxl (JobXML) file to .csv of points, listing pertinent info such as precision.

Arguments: (source file) (destination file)

## linesnap.py 
Takes a collection of disconnected line segments and joins them. No vertices are moved; rather a new segment is 
added between endpoints. Searches by location rather than index, and dynamically updates as it goes. This should 
make joining less error-prone than methods currently available in GRASS, QGIS, etc.

Arguments: (source file) (destination file) (search radius)

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
