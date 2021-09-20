# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 15:54:38 2020

@author: Manuel Huber.


Geemap is used to make use of Google earth engine and its functions. 

https://pypi.org/project/geemap/

"""


#  All libaries needed for this script
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


#%% Function to export Sentinel 1 variables as a csv file for specific fields



def creating_csv_S1(inp,save, Start, End,relOrbit, passType, azi, rotation,year,string,out_file,shp):
    
    


    brp = ee.FeatureCollection('users/manuelhuberde/{}'.format(shp)) # This asset needs to be uploaded before excecuting the script! 
    

    select = brp.filter(ee.Filter.inList('OBJECTID',inp))
    
    StartDate = Start; #Input start date of Sentinel-1 data acquistion
    EndDate = End; # Input end date of Sentinel-1 data acquisition
    
    #***The List of province, Municipalities and BRP crop parcels of Netherlands in Console Panel**#
    dataset = ee.Image('USGS/SRTMGL1_003')
    srtm = dataset.select('elevation')
    PassType = passType; #Input "ASCENDING" or "DESCENDING" Passtype of Sentinel-1
    relOrbit = relOrbit; #Relative Orbit of Acquisitions {Ascending (88, '161': 15); Descending (37, '110': 139)}
    azimuth_val = azi # Use add(180.0) for DESCENDING and add(270.0) ASCENDING image':
    rotation_val = rotation # Use subtract(180.0) for DESCENDING and subtract(360.0) for ASCENDING image.
    
    #*********** Create a Buffer around the BRP parcels************ #
    
    def buffer_field(feature):
       return feature.buffer(-10)
      
    
    roi_crop_buffer = select.map(buffer_field) # Input Buffer size in meters #
    
    #************** Find Centroid of each Parcel ***********#
    
    def func_qzr(f):
    
      PolyCentroid = f.geometry().centroid()
    
      # A new property called 'area' will be set on each feature.
      return f.set({'Polygon_Centroid': PolyCentroid})
    
    roi_crop_buffer_new = roi_crop_buffer.map(func_qzr)
    #*** Function to remove border noise/edges and garbage values of 2017 and 2018 data ***#
    
    # Mask out using backscatter value threshold for VV and VH-Pol

    
    def BorderNoisefilter(image):
         im = image.select(['angle'])
         im2 = im.gt(30)
         im3 = im2.lt(45)
         im4 = image.updateMask(im3)
         all_var = image.updateMask(im4.select(['VV']).gt(0.0003))
         return all_var
    
    #*** Functions to convert S-1 Backscatter in dB/linear scale ***#
    
    def toNatural(i):
      return ee.Image(ee.Image.constant(10.0).pow(i.divide(10.0)).copyProperties(i, ['system:time_start']))
    
    def toDB(i):
      return ee.Image(i.select(0)).log10().multiply(10.0).copyProperties(i, ['system:time_start'])   
    
    #** Sentinel-1 GRD data select, import and metadata filtering operations.
    #S1_GRD_FLOAT data is sleced to avoid mathematical operations at logarithmic scale **#
    S1Pol = ee.ImageCollection('COPERNICUS/S1_GRD_FLOAT') \
            .filterBounds(roi_crop_buffer)\
            .filterDate(StartDate, EndDate) \
            .filter(ee.Filter.listContains('transmitterReceiverPolarisation','VV')) \
            .filter(ee.Filter.listContains('transmitterReceiverPolarisation','VH')) \
            .filter(ee.Filter.eq('instrumentMode', 'IW')) \
            .filter(ee.Filter.eq('orbitProperties_pass', PassType)) \
            .filter(ee.Filter.eq('relativeOrbitNumber_start', relOrbit)) \
            .sort('system:time_start') \
            .map(BorderNoisefilter) \
                
    if S1Pol.size().getInfo() != 0:
        out_file.write('S1_RO_{}_Pass_{}_Year_{}_{}.csv,\n'.format(relOrbit, passType[:3],year,string))
        out_file.close()
        S1VV = S1Pol.select('VV')
        S1VH = S1Pol.select('VH')
        #Calculate Cross Pol ratio VH/VV for Sentinel-1 SAR data #
        def CrossPolRatio (image):
            return image.addBands(image.expression(
            'VH/VV', {
              'VH': image.select(['VH']),
              'VV': image.select(['VV'])
            }
              ))
        
        S1var = S1Pol.map(CrossPolRatio)
            
        #======================== Local Incidence Angle (LIA) calculation ==================\
        
        
        def get_angle(image):
            S1angle = image.select('angle')
            #We can use the gradient of the "angle" band of the S1 image to derive the S1 azimuth angle.
            S1_azimuth = ee.Terrain.aspect(S1angle) \
                                    .reduceRegion(ee.Reducer.mean(), S1angle.geometry(), 100) \
                                    .get('aspect')
            # Attention, this is not actually azimuth, but the look direction across range, which is NOT
            # yet corrected for the angle with which s1_inc is rotated relative to North!!!
            # Calculate True azimuth direction for the near range image edge
            def getCorners(f):
              # Get the coords as a transposed array
              coords = ee.Array(f.geometry().coordinates().get(0)).transpose()
              crdLons = ee.List(coords.toList().get(0))
              crdLats = ee.List(coords.toList().get(1))
              minLon = crdLons.sort().get(0)
              maxLon = crdLons.sort().get(-1)
              minLat = crdLats.sort().get(0)
              maxLat = crdLats.sort().get(-1)
              azimuth = ee.Number(crdLons.get(crdLats.indexOf(minLat))).subtract(minLon).atan2(ee.Number(crdLats.get(crdLons.indexOf(minLon))).subtract(minLat)) \
                        .multiply(180.0/math.pi).add(azimuth_val) 
              return ee.Feature(ee.Geometry.LineString([crdLons.get(crdLats.indexOf(minLat)), minLat,
            minLon, crdLats.get(crdLons.indexOf(minLon))]), { 'azimuth': azimuth}).copyProperties(f)
            
            azimuthEdge = getCorners(image)
            
            TrueAzimuth = azimuthEdge.get('azimuth')   # This should be some degree off the North direction, due to Earth rotation
            rotationFromNorth_or_South = ee.Number(TrueAzimuth).subtract(rotation_val) # Use subtract(180.0) for DESCENDING and subtract(360.0) for ASCENDING image.
            
            # Correct the across-range-look direction
            S1_azimuth = ee.Number(S1_azimuth).add(rotationFromNorth_or_South)  
            # Here we derive the terrain slope and aspect
            
            srtm_slope = ee.Terrain.slope(srtm).select('slope')
            srtm_aspect = ee.Terrain.aspect(srtm).select('aspect')
        
            # And finally the local incidence angle
            slope_projected2 = srtm_slope.multiply(ee.Image.constant(TrueAzimuth).subtract(90.0).subtract(srtm_aspect).multiply(math.pi/180).cos())
            lia2 = S1angle.subtract(ee.Image.constant(90).subtract(ee.Image.constant(90).subtract(slope_projected2))).abs()
            angles = lia2.addBands(S1_azimuth) # add azimuth angle to the lia image... this new band is called constant
            angles = angles.select(['angle','constant']).rename(['LIA','AZI']) # REnaming the bands in order to merge it together with the VH and VV datasets (they need to have the same coloumn names in order to)
            return angles
        
        angles_all  = S1var.map(get_angle) # Including the azimuth angle
        
        angles_all_stack  = ee.ImageCollection(angles_all).toBands()
        S1_st_var = ee.ImageCollection(S1var).toBands()
        
        # Determine the scale to perform reduce Region operation #
        scale = S1VV.first().projection().nominalScale()
        
        # Combine the mean and standard deviation reducers.
        reducers = ee.Reducer.mean().combine(
          reducer2=ee.Reducer.stdDev(),  sharedInputs=True).combine(
          reducer2=ee.Reducer.count(),  sharedInputs=True)
        # Calculate the S1 mean backscatter or pixel values for a given shape file over a period of time #
        
        all_var = S1_st_var.addBands(angles_all_stack)
        all_comb = all_var.reduceRegions(**{'collection': roi_crop_buffer_new, 'reducer': reducers, 'scale': scale, 'tileScale': 8}) #Tilescale 8 is used to reduce the chance of memory error
        all_comb = all_comb.map(func_qzr)
                    
        geemap.ee_to_csv(all_comb, '{}S1_RO_{}_Pass_{}_Year_{}_{}.csv'.format(save,relOrbit, passType[:3],year,string))
        
    else:
        print('empty image collection')        
                
        


#%% Loading the fields shapefile!

relOrbit_As = [88,161,15]
relOrbit_Des = [37,110,139]
#########################################
#########################################
#THOSE VALUES NEED TO BE ADJUSTED FOR CASE (ORBIT AND YEAR)


relOrbit = 37 # Here an orbit needs to be filled in. This case it is the relative oribt 37

year = '2020'



##########################################
##########################################
shp = "BRP_Proj_{}".format(year)

    
if relOrbit in relOrbit_Des:
    # Select for desending orbit...:
    passType = "DESCENDING"
    azi = 180
    rotation = 180
else:    
    # Select for ascending orbits...:
    passType = "ASCENDING"
    azi = 270
    rotation = 360 


# Path where to store the data (for the named year per orbit)

path_year = '/DATA-2/{}_New_2/'.format(year)

# The following shape file needs to be uploaded on Gooogle Earth Engine in the assets folder with the same
# name as the shp name (for example BRP_Proj_2020)
fields = gpd.read_file('/DATA-2/Input_Data/BRP_{}/{}.shp'.format(year,shp)) 
# Path to store the intermidiate shp files // Hence this needs to be created
# Those shp files are needed to strucutre the mining process
GEM1 = gpd.read_file('/DATA-2/Input_Data/Gem/gem_2018_proj.shp')
polygons_gem = GEM1['geometry']

StartDate = '{}-01-01'.format(year); #Input start date of Sentinel-1 data acquistion
EndDate = '{}-12-31'.format(year); # Input end date of Sentinel-1 data acquisition
# Orbits over the Netherlands


if not os.path.exists('{}Orbit_{}'.format(path_year,relOrbit)):
    os.mkdir('{}Orbit_{}'.format(path_year,relOrbit))
    
    
if not os.path.exists('{}Headers'.format(path_year)):
    os.mkdir('{}Headers'.format(path_year))



def getXY(pt):
    return (pt.x, pt.y)
centroidseries = fields['geometry'].centroid


out_file = open("{}/Headers/Headers_Orbit_{}.txt".format(path_year,relOrbit), "w")
out_file.close()

for i in range(len(GEM1)):
    print(i+1, ' out of 380')
    index = fields['OBJECTID'][centroidseries.within(polygons_gem[i])]
    index = index.values
    
    gem = GEM1['GM_NAAM'][i]
    
    # looping through the fields... 
    #Creating a list to loop through all the fields with about 500 fields at a time, to reduce memory issues. 
    
    if len(index) > 500:
        arr = list(range(0, len(index)))
        newarr = np.array_split(arr, int(np.round(len(index)/500, 0)))

        for j in range(len(newarr)):
            out_file = open("{}/Headers/Headers_Orbit_{}.txt".format(path_year,relOrbit), "a")
            string = '{}_out_{}_{}'.format(j+1, len(newarr), gem)
            inp = index[min(newarr[j]):max(newarr[j])+1]
            inp = [int(y) for y in inp]
            save_des = '{}Orbit_{}/'.format(path_year,relOrbit)
            creating_csv_S1(inp,save_des,StartDate,EndDate, relOrbit,passType, azi, rotation,year, string,out_file,shp)
            
    else:
        out_file = open("{}/Headers/Headers_Orbit_{}.txt".format(path_year,relOrbit), "a")
        string = 'all_fields_{}_{}'.format(len(index), gem)
        inp = index
        inp = [int(y) for y in inp]
        save_des = '{}Orbit_{}/'.format(path_year,relOrbit)
        creating_csv_S1(inp,save_des,StartDate,EndDate, relOrbit,passType, azi, rotation,year, string,out_file,shp)
        
