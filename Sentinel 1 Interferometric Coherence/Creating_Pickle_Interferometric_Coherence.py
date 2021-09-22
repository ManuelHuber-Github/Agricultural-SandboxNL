import numpy as np
import re
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pickle
from datetime import datetime, date, time
import glob
import sys
import os
import pickle
import datetime as datetime2
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import math


# For example for one year... can be adjusted to loop over muliptle years.
years = [2020]
for x in range(len(years)):
    year = years[x]
    fields = gpd.read_file("/data/shp_buffered_{}/fields_buffer_{}.shp".format(year, year))
    path = '/data/CSV_per_Tif/{}_88_GDAL/'.format(year)
    
    
    files = glob.glob(path+'*.csv')
    names = os.listdir(path)
    
    mean = []
    std = []
    count =[]
    
    
    for i in range(len(files)):
        print(i+1, 'out of', len(files))
        date_st = names[i][13:-17]
        date = datetime(year=int(date_st[:4]), month=int(date_st[4:6]), day=int(date_st[6:8]))
        df = pd.read_csv(files[i])
        df.index = df['Unnamed: 0'].values
        df = df.drop('Unnamed: 0', axis=1)
        
        
        dfib = pd.DataFrame()
        dfib['{}'.format(date)] = df['mean']
        dfib.index = df.index
        dfib = dfib.dropna()
        mean.append(dfib)
        
        dfib = pd.DataFrame()
        dfib['{}'.format(date)] = df['std']
        dfib.index = df.index
        std.append(dfib)
        
        dfib = pd.DataFrame()
        dfib['{}'.format(date)] = df['count']
        dfib.index = df.index
        count.append(dfib)
    
    df_mean = pd.concat(mean, axis=1)
    df_std = pd.concat(std, axis=1)
    df_count = pd.concat(count, axis=1)
    
    
    #%% DELETE ALL ROWS WHICH HAVE CONSTANT 0 VALUES OVER TIME
    
    df_meanC = df_mean
    ids_0  =  []
    ids_No_0 =[]
    for i in range(len(df_meanC)):
        print(i)
        ib = df_meanC.iloc[i].replace('--', '0')
        ib = ib.astype(float)
        if sum(ib) == 0:
            ids_0.append(ib)
        else:
            ids_No_0.append(ib)    
    
    zerosC = pd.concat(ids_0, axis=1).T
    NozerosC = pd.concat(ids_No_0, axis=1).T
    
    
    
    #%% Filtered datasets depened on the mean masked values
    df = NozerosC.dropna()
    count_select = df_count[df_count.index.isin(df.index)]
    std_select = df_std[df_std.index.isin(df.index)]
    mean_select = df
    
    info = fields[fields.OBJECTID.isin(df.index)]
    
    df_all = {}
    df_all['mean']= mean_select
    df_all['std']= std_select
    df_all['count']= count_select
   # df_all['geometry'] = info.geometry
   # df_all['crop'] = info.GWS_GEWAS
    
    path_save ='/data/Coherence Pickel/'
    with open('{}Dict_Coherence_88_VV_{}_small.pickle'.format(path_save,year), 'wb') as handle:
            pickle.dump(df_all, handle, protocol=pickle.HIGHEST_PROTOCOL)