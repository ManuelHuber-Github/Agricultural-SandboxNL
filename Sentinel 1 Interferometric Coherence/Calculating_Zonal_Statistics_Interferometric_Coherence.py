# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 10:52:08 2021

@author: Manuel Huber
"""

import glob
import os
import numpy as np
import pandas as pd

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from osgeo import gdal, ogr, osr

import geopandas as gpd

def zonal_stats(feat, shp, raster, transform):

    # Open data
    #raster = gdal.Open(input_value_raster)
    #shp = ogr.Open(input_zone_polygon)
    lyr = shp.GetLayer()

    # Get raster georeference info
    #transform = raster.GetGeoTransform()
    xOrigin = transform[0]
    yOrigin = transform[3]
    pixelWidth = transform[1]
    pixelHeight = transform[5]

    # Get extent of feat
    geom = feat.GetGeometryRef()
    if (geom.GetGeometryName() == 'MULTIPOLYGON'):
        count = 0
        pointsX = []; pointsY = []
        for polygon in geom:
            geomInner = geom.GetGeometryRef(count)    
            ring = geomInner.GetGeometryRef(0)
            numpoints = ring.GetPointCount()
            for p in range(numpoints):
                    lon, lat, z = ring.GetPoint(p)
                    pointsX.append(lon)
                    pointsY.append(lat)    
            count += 1
    elif (geom.GetGeometryName() == 'POLYGON'):
        ring = geom.GetGeometryRef(0)
        numpoints = ring.GetPointCount()
        pointsX = []; pointsY = []
        for p in range(numpoints):
                lon, lat, z = ring.GetPoint(p)
                pointsX.append(lon)
                pointsY.append(lat)

    else:
        sys.exit()

    xmin = min(pointsX)
    xmax = max(pointsX)
    ymin = min(pointsY)
    ymax = max(pointsY)

    # Specify offset and rows and columns to read
    xoff = int((xmin - xOrigin)/pixelWidth)
    yoff = int((yOrigin - ymax)/pixelWidth)
    xcount = int((xmax - xmin)/pixelWidth)+1
    ycount = int((ymax - ymin)/pixelWidth)+1

    # Create memory target raster
    target_ds = gdal.GetDriverByName('MEM').Create('', xcount, ycount, gdal.GDT_Byte)
    target_ds.SetGeoTransform((
        xmin, pixelWidth, 0,
        ymax, 0, pixelHeight,
    ))

    # Create for target raster the same projection as for the value raster
    raster_srs = osr.SpatialReference()
    raster_srs.ImportFromWkt(raster.GetProjectionRef())
    target_ds.SetProjection(raster_srs.ExportToWkt())

    # Rasterize zone polygon to raster
    gdal.RasterizeLayer(target_ds, [1], lyr, burn_values=[1])

    # Read raster as arrays
    banddataraster = raster.GetRasterBand(1)
    if banddataraster.ReadAsArray(xoff, yoff, xcount, ycount) is not None:
        dataraster = banddataraster.ReadAsArray(xoff, yoff, xcount, ycount).astype(float)

        bandmask = target_ds.GetRasterBand(1)
        datamask = bandmask.ReadAsArray(0, 0, xcount, ycount).astype(float)
    
        # Mask zone of raster
        zoneraster = np.ma.masked_array(dataraster,  np.logical_not(datamask))
    
        # Calculate statistics of zonal raster
        return [np.mean(zoneraster),len(zoneraster),np.std(zoneraster)]
    else:
        #print('nope')
        return [0,0,0]


def loop_zonal_stats(input_zone_polygon,raster):

    shp = ogr.Open(input_zone_polygon)
    if shp is not None:
        lyr = shp.GetLayer()
        featList = range(lyr.GetFeatureCount())
        statDict = {}
        inp = gpd.read_file(input_zone_polygon)
        #raster = gdal.Open(input_value_raster)
        transform = raster.GetGeoTransform()
        
        for FID in featList:
    
            feat = lyr.GetFeature(FID)
            meanValue = zonal_stats(feat, shp, raster, transform)
            statDict[inp.OBJECTID[FID]] = meanValue
            #statDict[FID] = meanValue
        df = pd.DataFrame(statDict).T
        df = df.rename(columns={0: "mean", 1: "count",2: "std"})
        return df
    print('There is is something going on')
     


#############################################################################

year = 2020

############################################################################

fields = gpd.read_file("/data/shp_buffered_{}/fields_buffer_{}.shp".format(year, year))
arr = np.array_split(np.arange(len(fields)), 10000)
print(np.shape(arr))



files = glob.glob("/data/Images_2019_88/Output_Tiffs_88_20/*.tif")
names = os.listdir('/data/Images_2019_88/Output_Tiffs_88_20')


for j in range(len(files)):
    name = names[j]
    input_value_raster = files[j]
    raster = gdal.Open(input_value_raster)
    
    
    df_fields = []    
    for i in range(len(arr)):
        print(i+1, ' out of', len(arr), 'from tif', j+1, 'out of', len(files))
        ib = fields.iloc[min(arr[i]):max(arr[i])]
        ib = ib.dropna()
        if len(ib)!=0:
            ib.to_file("/data/inbetween_shp/inbetween.shp")
            input_zone_polygon = "/data/inbetween_shp/inbetween.shp"
            df_fields.append(loop_zonal_stats(input_zone_polygon, raster))
        else:
            print('empty')
    df_c = pd.concat(df_fields)
    df_c.to_csv('/data/CSV_per_Tif/{}_88_GDAL/{}.csv'.format(year, name))	