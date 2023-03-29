import sys
import xml.etree.ElementTree as ET
import os
import csv
from io import StringIO

def main(): 
    tree = ET.parse(sys.argv[1])
    root = tree.getroot()
    element_list = root.findall("./FieldBook/PointRecord")
    with open(sys.argv[2], 'w', newline='') as csvfile: 
        writer = csv.writer(csvfile)
        writer.writerow(['point_no', 'northing', 'easting', 'elev', 'code', 'start_time', 'duration (sec)', 'horiz_prec', 'vert_prec', 'no_sats', 'pdop', 'gdop', 'hdop', 'vdop'])
        for element in element_list: 
            try: 
                start_time = str(element.get('TimeStamp'))
                name = str(element.find('Name').text)
                code = str(element.find('Code').text)
                northing = str(element.find("./ComputedGrid/North").text)
                easting = str(element.find("./ComputedGrid/East").text)
                elev = str(element.find("./ComputedGrid/Elevation").text)
                horiz_prec = str(element.find("./Precision/Horizontal").text)
                vert_prec = str(element.find("./Precision/Vertical").text)
                no_sats = str(element.find("./QualityControl1/NumberOfSatellites").text)
                pdop = str(element.find("./QualityControl1/PDOP").text)
                gdop = str(element.find("./QualityControl1/GDOP").text)
                hdop = str(element.find("./QualityControl1/HDOP").text)
                vdop = str(element.find("./QualityControl1/VDOP").text)
                start = int(element.find('./QualityControl1/StartTime/Seconds').text)
                end = int(element.find('./QualityControl1/EndTime/Seconds').text)
                duration = end - start
                writer.writerow([name, northing, easting, elev, code, start_time, duration, horiz_prec, vert_prec, no_sats, pdop, gdop, hdop, vdop])
            except AttributeError: 
                continue
    
if __name__ == "__main__": 
    main()
