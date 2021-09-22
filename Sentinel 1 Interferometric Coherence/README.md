# Addtional information about the database creation and introduction script

As the computational effort is very large coherence datasets have only be processed for one relative orbit 88 (as this has the best coverage over The Netherlands). 
Still, in the future more orbits will be added to this database. 

---------------------------------------------------------------------

1) Calculating_Interferometric_Coherence_Batch_Script_SNAP_Python.py

- from os import path
- import os
- import pandas as pd
- from datetime import datetime, date, time

This program utilizes the SNAP software using a Python API. The execution of the script is done with the ./gpt (graphical processing tool) of SNAP.
More information about the gpt-SNAP can be found here: http://step.esa.int/docs/tutorials/SNAP_CommandLine_Tutorial.pdf

The processing chain to calculate the interferometric coherence is illustrate here and stored in the 4_CCD_Graph_param_coherence_TIF.xml:

<img width="571" alt="GPT_Chain" src="https://user-images.githubusercontent.com/62883629/134313667-aa17db5f-7116-4be4-bf7c-6ca92c170934.PNG">

The Interferometric Cohernce pairs are stored as tiff files. As a next step field averages and standard deviations are calcuated using the BRP files from PDOK (same as for Sentinel 1 GRD and Sentinel 2). However, this step needs to be done manually as Google Earth Engine can not be utilized for this efficiently. 

-------------------------------------------------------------------------

2) Calculating_Zonal_Statistics_Interferometric_Coherence.py

- import glob
- import os
- import numpy as np
- import pandas as pd
- from shapely.geometry import Point
- from shapely.geometry.polygon import Polygon
- from osgeo import gdal, ogr, osr
- import geopandas as gpd

This script is needed to calculate the zonal statistics. The output is stored as csv file per image. As a next step all information is concatenated to one file (pickle) 
containing all infromation. 

---------------------------------------------------------------------------

3) Creating_Pickle_Interferometric_Coherence.py

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

The output is ready for analysis and visualization. 

-----------------------------------------------------------------------------

4) SandBoxNL_Code_Introduction_Coherence.ipynb

- import netCDF4 as nc4
- import numpy as np
- import geopandas as gpd
- import matplotlib.pyplot as plt
- import pandas as pd
- from netCDF4 import Dataset
- import pickle
- from datetime import datetime, date, time
- import glob
- import math    
- import os
- from shapely.geometry import Point
- from shapely.geometry.polygon import Polygon

This example script works with the interferometric coherence dataset used in the SanboxNL publication covering Flevoland for the relative orbit 110. 
