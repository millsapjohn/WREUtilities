WRE Utilities

This is a collection of Python scripts I've created to automate some parts of my job as a Water Resource Engineer.

As of this commit (10/28/22), all of these utilities operate on all matching files in a particular directory
without taking any arguments.

ANINT.py /cr
    This script doesn't work (or do anything, really) at this time. Eventually it will be a script to perform an
    anisotropic interpolation on raw bathymetric data. More details when it gets going.

CONVERTMM.py
    Simple script to convert .asc files from mm (millimeters) to in (inches).

CONVERTNEGATIVE.py
    Removes negative values from an .asc raster (converts them to zero).

DSSTOASC.py
    Converts all .dss files in a directory to .asc. Requires the "dsstoasc.exe" executable from the US Army Corps
    of Engineers (USACE) Hydraulic Engineering Center (HEC). This executable is distributed as part of the HEC-RAS
    download package.

DSSTOASC_BMOSAIC.py
    Similar to the above, but because the Weather Center publishes its .dss files in some different name formats,
    the above (dsstoasc.py) doesn't work on all formats. At some point I'll merge these and either make them smart,
    or create some commandline switches.

JOINASC.py
    Merges all .asc files in a directory.

MASSMOVER.py
    Moves all files in a directory to a new directory. Doesn't work right now because I haven't done anything with
    it lol.
