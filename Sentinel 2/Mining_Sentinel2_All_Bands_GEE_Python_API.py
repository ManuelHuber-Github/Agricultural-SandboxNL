# -*- coding: utf-8 -*-
"""
Created on Mon Sep 20 15:26:56 2021

@author: Manuel Huber
"""

import ee
import geemap
import math
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
import os

Map = geemap.Map()
ee.Initialize()


#############################################################################
#############################################################################
#############################################################################
#############################################################################
#%% Functions for cloud and shadow masks

def get_s2_sr_cld_col(aoi, start_date, end_date):
    # Import and filter S2 SR.
    s2_sr_col = (ee.ImageCollection('COPERNICUS/S2_SR')
        .filterBounds(aoi)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', CLOUD_FILTER)))

    # Import and filter s2cloudless.
    s2_cloudless_col = (ee.ImageCollection('COPERNICUS/S2_CLOUD_PROBABILITY')
        .filterBounds(aoi)
        .filterDate(start_date, end_date))

    # Join the filtered s2cloudless collection to the SR collection by the 'system:index' property.
    return ee.ImageCollection(ee.Join.saveFirst('s2cloudless').apply(**{
        'primary': s2_sr_col,
        'secondary': s2_cloudless_col,
        'condition': ee.Filter.equals(**{
            'leftField': 'system:index',
            'rightField': 'system:index'
        })
    }))

def add_cloud_bands(img):
    # Get s2cloudless image, subset the probability band.
    cld_prb = ee.Image(img.get('s2cloudless')).select('probability')

    # Condition s2cloudless by the probability threshold value.
    is_cloud = cld_prb.gt(CLD_PRB_THRESH).rename('clouds')

    # Add the cloud probability layer and cloud mask as image bands.
    return img.addBands(ee.Image([cld_prb, is_cloud]))

def add_shadow_bands(img):
    # Identify water pixels from the SCL band.
    not_water = img.select('SCL').neq(6)

    # Identify dark NIR pixels that are not water (potential cloud shadow pixels).
    SR_BAND_SCALE = 1e4
    dark_pixels = img.select('B8').lt(NIR_DRK_THRESH*SR_BAND_SCALE).multiply(not_water).rename('dark_pixels')

    # Determine the direction to project cloud shadow from clouds (assumes UTM projection).
    shadow_azimuth = ee.Number(90).subtract(ee.Number(img.get('MEAN_SOLAR_AZIMUTH_ANGLE')));

    # Project shadows from clouds for the distance specified by the CLD_PRJ_DIST input.
    cld_proj = (img.select('clouds').directionalDistanceTransform(shadow_azimuth, CLD_PRJ_DIST*10)
        .reproject(**{'crs': img.select(0).projection(), 'scale': 100})
        .select('distance')
        .mask()
        .rename('cloud_transform'))

    # Identify the intersection of dark pixels with cloud shadow projection.
    shadows = cld_proj.multiply(dark_pixels).rename('shadows')

    # Add dark pixels, cloud projection, and identified shadows as image bands.
    return img.addBands(ee.Image([dark_pixels, cld_proj, shadows]))

def add_cld_shdw_mask(img):
    # Add cloud component bands.
    img_cloud = add_cloud_bands(img)

    # Add cloud shadow component bands.
    img_cloud_shadow = add_shadow_bands(img_cloud)

    # Combine cloud and shadow mask, set cloud and shadow as value 1, else 0.
    is_cld_shdw = img_cloud_shadow.select('clouds').add(img_cloud_shadow.select('shadows')).gt(0)

    # Remove small cloud-shadow patches and dilate remaining pixels by BUFFER input.
    # 20 m scale is for speed, and assumes clouds don't require 10 m precision.
    is_cld_shdw = (is_cld_shdw.focal_min(2).focal_max(BUFFER*2/20)
        .reproject(**{'crs': img.select([0]).projection(), 'scale': 20})
        .rename('cloudmask'))

    # Add the final cloud-shadow mask to the image.
    return img_cloud_shadow.addBands(is_cld_shdw)


def apply_cld_shdw_mask(img):
    # Subset the cloudmask band and invert it so clouds/shadow are 0, else 1.
    not_cld_shdw = img.select('cloudmask').Not()

    # Subset reflectance bands and update their masks, return the result.
    return img.updateMask(not_cld_shdw) #select('B.*')


def creating_csv_S1(inp,path_year, Start, End,year,string,shp):
    
    brp = ee.FeatureCollection('users/manuelhuberde/{}'.format(shp))
    select = brp.filter(ee.Filter.inList('OBJECTID',inp))
    StartDate = Start; #Input start date of Sentinel-1 data acquistion
    EndDate = End; # Input end date of Sentinel-1 data acquisition
    
    
    #*********** Create a Buffer around the BRP parcels************ #
    
    def buffer_field(feature):
       return feature.buffer(-10)
      
    
    roi_crop_buffer = select.map(buffer_field) # Input Buffer size in meters #
    
    #************** Find Centroid of each Parcel ***********#
    
    def func_qzr(f):
    
      PolyCentroid = f.geometry().centroid()
    
      # A new property called 'area' will be set on each feature.
      return f.set({'Polygon_Centroid': PolyCentroid})
    
    AOI = roi_crop_buffer.map(func_qzr)

    
    bands = [['B2', 'B3','B4', 'B8'],['B5', 'B6','B7', 'B8A','B11','B12','probability' ]]  # 2 Different resolutions; 10 and 20m 
    bres =  [10,20]
    
    #bands = ['B2', 'B3','B4', 'B8','B5', 'B6','B7', 'B8A','B11','B12','probability']
   # bstr = ['Bands10','Bands20']
    for b in range(len(bands)):
            if not os.path.exists('{}/{}/S2_Res_{}_Year_{}_{}.csv'.format(path_year,'Bands{}'.format(bres[b]),bres[b],year,string)):
                print(b+1,len(bands),'bands')
                out_file = open("{}/Headers/{}_Headers.txt".format(path_year,bres[b]), "a")
                out_file.write('S2_Res_{}_Year_{}_{}.csv,\n'.format(bres[b],year,string))
                out_file.close()
                   
                s2_sr_cld_col = get_s2_sr_cld_col(AOI, START_DATE, END_DATE)
                s2_sr = s2_sr_cld_col.map(add_cld_shdw_mask).map(apply_cld_shdw_mask)
                   	        #all_stack  = ee.ImageCollection(s2_sr.select(['B4'])).toBands()
                all_stack  = ee.ImageCollection(s2_sr.select(bands[b])).toBands()
                   
                   	        # Determine the scale to perform reduce Region operation 
                scale = bres[b] # all_stack.projection().nominalScale()
                   
                   	        # Combine the mean and standard deviation reducers.
                reducers = ee.Reducer.mean().combine(
                   		          reducer2=ee.Reducer.stdDev(),  sharedInputs=True).combine(
                   		          reducer2=ee.Reducer.count(),  sharedInputs=True)
                   	        # Calculate the S1 mean backscatter or pixel values for a given shape file over a period of time #
                   
                   	        #all_var = S1_st_var.addBands(angles_all_stack)
                all_comb = all_stack.reduceRegions(**{'collection': AOI, 'reducer': reducers, 'scale': scale, 'tileScale': 8})
                   	        #all_comb = all_comb.map(func_qzr)
                geemap.ee_to_csv(all_comb, '{}/{}/S2_Res_{}_Year_{}_{}.csv'.format(path_year,'Bands{}'.format(bres[b]),bres[b],year,string))
            
            else:
                print('Duplicate.. Next please..')
    



#############################################################################
#############################################################################
#############################################################################
#############################################################################
#%% Selecting year and constraints

year = '2020'
START_DATE = '{}-01-01'.format(year)
END_DATE ='{}-12-31'.format(year)

# Those are set thresholds to filter clouds and cloud shadows!
CLOUD_FILTER = 75
CLD_PRB_THRESH = 50
NIR_DRK_THRESH = 0.15
CLD_PRJ_DIST = 1
BUFFER = 80


shp = "BRP_Proj_{}".format(year)

    
fields = gpd.read_file('/DATA-2/Input_Data/BRP_{}/{}.shp'.format(year,shp)) 
GEM1 = gpd.read_file('/DATA-2/Input_Data/Gem/gem_2018_proj.shp')
polygons_gem = GEM1['geometry']
path_year = '/DATA-2/Sentinel2/{}/'.format(year)

#############################################################################
#############################################################################
#############################################################################

if not os.path.exists('{}Headers'.format(path_year)):
    os.mkdir('{}Headers'.format(path_year))
# Those bands are included in the extraction of Sentinel 2
#bands = ['B2', 'B3','B4', 'B8','B5', 'B6','B7', 'B8A','B11','B12','probability']
bands = ['Bands10', 'Bands20']
for b in range(len(bands)):

    if not os.path.exists('{}{}'.format(path_year, bands[b])):
        os.mkdir('{}{}'.format(path_year, bands[b]))
        
    out_file = open("{}/Headers/{}_Headers.txt".format(path_year, bands[b]), "w")
    out_file.close()


#%% Selecting feature collection


# looping through the fields... 
#Creating a list to loop through all the fields with about 1000 fields at a time
arr = list(range(0, len(fields)))
newarr = np.array_split(arr, 2000)


def getXY(pt):
    return (pt.x, pt.y)
centroidseries = fields['geometry'].centroid



for i in range(len(GEM1)):
#for i in range(1):
    print(i+1, ' out of 380')
    index = fields['OBJECTID'][centroidseries.within(polygons_gem[i])]
    index = index.values
    
    gem = GEM1['GM_NAAM'][i]
    
    # looping through the fields... 
    #Creating a list to loop through all the fields with about 500 fields at a time
    
    if len(index) > 500:
        arr = list(range(0, len(index)))
        newarr = np.array_split(arr, int(np.round(len(index)/500, 0)))

        for j in range(len(newarr)):
            string = '{}_out_{}_{}'.format(j+1, len(newarr), gem)
            inp = index[min(newarr[j]):max(newarr[j])+1]
            inp = [int(y) for y in inp]

            creating_csv_S1(inp,path_year, START_DATE, END_DATE,year,string,shp)
            
    else:
        string = 'all_fields_{}_{}'.format(len(index), gem)
        inp = index
        inp = [int(y) for y in inp]
        creating_csv_S1(inp,path_year, START_DATE, END_DATE,year,string,shp)



