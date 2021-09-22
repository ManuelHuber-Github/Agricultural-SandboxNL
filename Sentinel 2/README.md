# Addtional information about the database creation and introduction script

The whole database was mined via Google Earth Engine using a Python API. Following database in Goolge Earth Engine is used to crate this parcel based dataset:
https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR


# Requirements 

1) Mining_Sentinel2_All_Bands_GEE_Python_API.py

- import ee
- import geemap
- import math
- import numpy as np
- import matplotlib.pyplot as plt
- import pandas as pd
- import geopandas as gpd
- import os

This script requires the user to have an active Google Earth Engine account. Username still needs to be changed to the individual case. 

-------------------------------------------------------------------

2) Creating_Pickle_Sentinel2_All_Bands.py

- import numpy as np
- import re
- import geopandas as gpd
- import numpy as np
- import matplotlib.pyplot as plt
- import pandas as pd
- import pickle
- from datetime import datetime, date, time
- import glob
- import sys
- import os
- import pickle
- import datetime as datetime2
- from shapely.geometry import Point
- from shapely.geometry.polygon import Polygon
- import math

-------------------------------------------------------------------

3) SandBoxNL_Code_Introduction_Sentinel2.py

- import netCDF4 as nc4
- import numpy as np
- import geopandas as gpd
- import matplotlib.pyplot as plt
- import pandas as pd
- from netCDF4 import Dataset
- #import pickle
- import pickle5 as pickle
- from datetime import datetime, date, time
- import glob
- import math    
- import os
- from shapely.geometry import Point
- from shapely.geometry.polygon import Polygon
- from shapely import wkt
- import shapely
- import calendar
