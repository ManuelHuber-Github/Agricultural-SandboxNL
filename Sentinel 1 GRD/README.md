# Addtional information about the database creation and introduction script

The data base creation is split into three steps:

1) Mining the data from Google Earth Engine 
    - This includes including field buffer zone
    - Calculating Local Incidence Angle
    - Storing all parcel information 
    - Calculating Cross-Pol Ratio VH/VV
    - Doing all processes for six different orbits (ascending [88,161,15] and descending [37,110,139])

2) Creating Pickle files
    - This includes cleaning the data 
    - Flagging flase or potentially false parcels
    - Restructing the data 

3) Creating netCDF files out of pickle files

More information about and explanations for all steps mentioned can be found in the Agricultural SandboxNL publication:
"Agricultural Sandbox NL: A national-scale database of parcel-level, processed Sentinel-1 SAR data"
https://eartharxiv.org/repository/view/2541/


---------------------------------------------------------------------------


# Information and requirements for data base creation scripts

1) Mining_S1GRD_Per_Parcel_GEE_Python_API.py

Python libaries:

- import ee
- import geemap
- import math
- import numpy as np
- import matplotlib.pyplot as plt
- import pandas as pd
- import geopandas as gpd
- import os


Furthermore, a Google Earth Eninge account is required with following shapefiles as assests:
- BRP shapefile (this changes per year) 
- Province and Municipality shapefiles form The Netherlands 
- source: https://data.4tu.nl/articles/dataset/Agricultural_SandboxNL_Database_V1_0/14438750?file=28533669
 
 
