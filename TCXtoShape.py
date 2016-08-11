#-------------------------------------------------------------------------------
# Name:        TCXtoShape.py
# Purpose:     Simple script to convert a TCX file into a point shapefile
#
#               User will need to set the input file, and output filename and
#               directory
#
# Author:      Benjamin Spaulding - @gisdoctor
#
# Created:     August/08/2016

# tcx parser based on https://github.com/jhofman/fitnesshacks
# Shapely and Fiona are also awesome -
#       http://toblerity.org/fiona/manual.html
#       http://toblerity.org/shapely/manual.html
#-------------------------------------------------------------------------------

import os, sys, re
from xml.etree.ElementTree import fromstring
#from time import strptime, strftime
import fiona
from fiona.crs import from_epsg
from shapely.geometry import mapping, Point
import pyproj


#function to return the data in the specific TCX tags - code from https://github.com/jhofman/fitnesshacks
def findtext(e, name, default=None):
    """
    findtext
    helper function to find sub-element of e with given name and
    return text value
    returns default=None if sub-element isn't found
    """
    try:
        return e.find(name).text
    except:
        return default


#Input file TCX file
inputFile = "INPUTTCX.tcx"

#output file name
outputShapefileName = '2016_08_07_Running'

#output folder
outpath =  '//outputFolder/'

istream = open(inputFile,'r')

#initialize an ID counter
idval = 0

# read xml contents
xml = istream.read()

# parse tcx file
xml = re.sub('xmlns=".*?"','',xml)

# parse xml
tcx=fromstring(xml)

#pull the activity type from the TCX file
activity = tcx.find('.//Activity').attrib['Sport']

#output shapefile
outShape = 'rBr_'+outputShapefileName+'_shape.shp'

#output crs
crs = fiona.crs.from_epsg(4326)

#output shapefile schema
schema = {
         'geometry': 'Point',
        'properties': {'id': 'int','Lat':'float','Lon':'float','AltMeters':'float','DistMeters':'float','TimeStamp':'str:50',},
        }

print ("Start TCX Extraction")
#using Fiona, create a new shapefile and then populate it with data from the tcx file
with fiona.open(outpath+outShape, 'w', driver='ESRI Shapefile',crs = crs, schema = schema) as c:

    for lap in tcx.findall('.//Lap/'):

        for point in lap.findall('.//Trackpoint'):

                idval = idval + 1
                timestamp = findtext(point, 'Time')
                AltitudeMeters = float(findtext(point, 'AltitudeMeters'))
                DistanceMeters = float(findtext(point, 'DistanceMeters'))
                LatitudeDegrees = float(findtext(point, 'Position/LatitudeDegrees'))
                LongitudeDegrees = float(findtext(point, 'Position/LongitudeDegrees'))

                #build shapely point
                latlonPoint = Point([LongitudeDegrees,LatitudeDegrees])

                # Write a new Shapefile
                c.write({
                        'geometry': mapping(latlonPoint),
                        'properties': {'id': idval,'Lat':LatitudeDegrees,'Lon':LongitudeDegrees,'AltMeters':AltitudeMeters,'DistMeters':DistanceMeters,'TimeStamp':timestamp },
                        })

c.close()
print ("Extraction Complete")
