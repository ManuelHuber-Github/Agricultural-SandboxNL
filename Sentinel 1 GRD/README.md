# Addtional information about the dataset creation and introduction script

1) Mining the data from Google Earth Engine 
    - This includes including field buffer zone
    - Border Noise Removal
    - Calculating Local Incidence Angle
    - Storing all parcel information 
    - Calculating Cross-Pol Ratio VH/VV
    - Processing for six different relative orbits (ascending [88,161,15] and descending [37,110,139])
    - Downloading all processed data per relative orbit

2) Creating Pickle files
    - This includes cleaning the data 
    - Flagging flase or potentially false parcels
    - Structuring and formating the data 

3) Creating netCDF files out of pickle files

4) Introduction python script to access, manipulate and visualize the database

More information about and explanations for all steps mentioned can be found in the Agricultural SandboxNL publication:
"Agricultural Sandbox NL: A national-scale database of parcel-level, processed Sentinel-1 SAR data"
https://eartharxiv.org/repository/view/2541/


---------------------------------------------------------------------------


# Information and requirements 

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
 
---------------------------------------------------------------------------
2) Creating_Pickle_Files_Per_Province_Clean_Sort.py

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
---------------------------------------------------------------------------
3) Creating_netCDF_from_pickle_files.py

- import netCDF4 as nc4
- import numpy as np
- import re
- import geopandas as gpd
- import numpy as np
- import matplotlib.pyplot as plt
- import pandas as pd
- from netCDF4 import Dataset
- import pickle
- from datetime import datetime, date, time
- import glob
- import sys
- from shapely.geometry import Point
- from shapely.geometry.polygon import Polygon
- import math    
- import os
 
 
 
 ---------------------------------------------------------------------------
4) SandBoxNL_Introduction_Script_GRD.ipynb

Python libaries:

- import netCDF4 as nc4
- import numpy as np
-import geopandas as gpd
- import matplotlib.pyplot as plt
- import pandas as pd
- from netCDF4 import Dataset
- import pickle as pickle
- import xlrd
- from datetime import datetime, date, time
- import glob
- import math    
- import os
- from shapely.geometry import Point
- from shapely.geometry.polygon import Polygon
- from shapely import wkt
- import shapely

This code is written in Python (3.6>) within Jupyter Notebook. It gives examples how to use and work with the Sentinel 1 GRD database. A detailed explanation for every step is included in this code. 

