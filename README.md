WRE Utilities

This is a collection of Python scripts I've created to automate some parts of my job as a Water Resource Engineer.

As of this commit (10/28/22), all of these utilities operate on all matching files in a particular directory
without taking any arguments.

ANINT.py  return
    This script doesn't work (or do anything, really) at this time. Eventually it will be a script to perform an
    anisotropic interpolation on raw bathymetric data. More details when it gets going.

CONVERTMM.py  return
    Simple script to convert .asc files from mm (millimeters) to in (inches).

CONVERTNEGATIVE.py  return
    Removes negative values from an .asc raster (converts them to zero).

DSSTOASC.py  return
    Converts all .dss files in a directory to .asc. Requires the "dsstoasc.exe" executable from the US Army Corps
    of Engineers (USACE) Hydraulic Engineering Center (HEC). This executable is distributed as part of the HEC-RAS
    download package.

DSSTOASC_BMOSAIC.py  return
    Similar to the above, but because the Weather Center publishes its .dss files in some different name formats,
    the above (dsstoasc.py) doesn't work on all formats. At some point I'll merge these and either make them smart,
    or create some commandline switches.

JOINASC.py  return
    Merges all .asc files in a directory.

MASSMOVER.py  return
    Moves all files in a directory to a new directory. Doesn't work right now because I haven't done anything with
    it lol.

XMRG_EXTRACT.py  return
    Extracts files in a directory from XMRG format to .dss format. Commandline arguments to specify method:  return
    -e flag extracts each file to a separate .dss file.  return
    -c flag extracts all files in directory to a combined .dss record.  return
    -h flag shows help menu.
