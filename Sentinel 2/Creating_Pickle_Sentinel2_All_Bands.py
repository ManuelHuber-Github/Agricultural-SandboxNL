# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 11:24:14 2021

@author: Manuel Huber
"""


import numpy as np
import re
import geopandas as gpd

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import pickle
#import datetime
from datetime import datetime, date, time
import glob
import sys
import os
import pickle
import datetime as datetime2
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
#np.set_printoptions(threshold=sys.maxsize)

import math



#%% Path for Sentinel 2 csv data.... 2019

years = ['2020']

for x in range(len(years)):
    print(years[x])
    year = years[x]
    path = '/DATA-2/Sentinel2/'
    
    shp = "BRP_Proj_{}".format(year)
    
    fields = gpd.read_file('/DATA-2/Input_Data/BRP_{}/{}.shp'.format(year,shp))
    
    GEM = gpd.read_file('/DATA-2/Input_Data/Gem/gem_2018_proj.shp')
    PROV =  gpd.read_file('/DATA-2/Input_Data/Prov/Province_van_nederland_proj.shp')
    
    files10 = glob.glob("{}/{}/Bands10/*.csv".format(path, year))
    files20 = glob.glob("{}/{}/Bands20/*.csv".format(path, year))
    
    files = [files20]# [files10, files20]
    
    bands_mean = []
    bands_std = []
    
    parcelID = []
    mission_details = []
    
    #bands = [['B2', 'B3','B4', 'B8'],['B5', 'B6','B7', 'B8A','B11','B12','probability' ]]
    #bands_strings = [['B2_mean', 'B3_mean','B4_mean', 'B8_mean','B2_std', 'B3_std','B4_std', 'B8_std', 'B2_count'],['B5_mean', 'B6_mean','B7_mean', 'B8A_mean','B11_mean','B12_mean','probability_mean','B5_std', 'B6_std','B7_std', 'B8A_std','B11_std','B12_std','probability_std','B5_count' ]]
    
    bands = [['B5', 'B6','B7', 'B8A','B11','B12','probability' ]]
    bands_strings = [['B5_mean', 'B6_mean','B7_mean', 'B8A_mean','B11_mean','B12_mean','probability_mean','B5_std', 'B6_std','B7_std', 'B8A_std','B11_std','B12_std','probability_std','B5_count' ]]
    resolution = [20]
    
    # For loop to go through all files within an orbit folder
    
    
        
    for f in range(len(files)):
    
        df_files = []
        parcelID = []
        #f= 0    
        for l in range(len(files[f])):   
        #for l in range(10):
            #l = l + 1680
            print(l, 'out of', len(files[f])) 
            #print(files[f][l])
            df = pd.read_csv(files[f][l])
            # Get the OBject id as index, so we can sort it accordingly
            #print(df.info())
            lst_head = list(df.columns)
            if 'OBJECTID'in lst_head:
              df.index = df['OBJECTID']
              print(np.shape(df))
              df = df.sort_index()
              
              londf = []
              latdf = []
              faults = []
              for p in range(len(df)):
                  if str(df['Polygon_Centroid'].iloc[p])!= 'nan':
                      
                      londf.append(eval(df['Polygon_Centroid'].iloc[p])["coordinates"][0])
                      latdf.append(eval(df['Polygon_Centroid'].iloc[p])["coordinates"][1])
                  else:
                      print('MISSING FIELD (ROW: {} ) in File: {}'.format(p,files[f][l]))
                      faults.append(df.index[p])
              
              
              # Here I create columns to later delete empty rows (field IDs without lon/lat..)
              df = df.drop(faults)
              df['lon'] = londf
              df['lat'] = latdf   
              
              #Function to delete the empty rows and below deleting these.. 
              def del_0(df):
                  df = df[df['lon']!=0]
                  df = df[df['lat']!=0]
                  return df
              
              df = del_0(df)
              
              df = df[~df.index.duplicated(keep='first')]
                
              
              # Creating a list of headers for each variable ... 
              lables_raw = list(df.columns.values)
          
          
              # Create a dataframe saving all the parcel informations /deleting empty roles 
              ID = df[['Polygon_Centroid','lon','lat']]
          
              # Save the parcel informations.. 
              parcelID.append(ID)
          
              strings = bands_strings[f]
              
              all_headers = []
              for k in range(len(strings)):
                  res = [i for i in lables_raw if strings[k] in i]
                  all_headers.append(res)
                  
              # Function to extract the dates from the headers
              all_dates = []
              for k in range(len(all_headers)):
                  dates = []
                  for i in range(len(all_headers[k])):
                      date = all_headers[k][i] #Selecting only the frist date once it is started to record
                      date_for_file = datetime(year=int(date[:4]), month=int(date[4:6]), day=int(date[6:8]), hour=(int(date[9:11])), minute=(int(date[11:13])),second=(int(date[13:15])))
                      dates.append(date_for_file)
                  all_dates.append(dates)
              
              
              df_all = []
              
              
              for r in range(len(all_headers)):
                  
                  xy = pd.DataFrame()
                  xy['head'] = all_headers[r]
                  xy['date'] = all_dates[r]
                  xy = xy.drop_duplicates(subset=['date'], keep='first')
                  
                  sel = df[xy['head']]     
                  sel.columns = xy['date']  
                  df_all.append(sel)
                          
              df_files.append(df_all)
              
              del df, df_all, ID 
            else:
                 print('empty')
                       
        print('done with reading the files...')
        
        df_per_var = []
        for var in range(len(bands_strings[f])):
           # print(var+1, len(bands_strings[f]))
            df_sep = []
            for j in range(len(df_files)):
              #  print(df_files[j][var])
              #  print(j+1, len(df_files))
                df_sep.append(df_files[j][var])
            #print(df_sep)
            df_conc = pd.concat(df_sep)
            df_per_var.append(df_conc)
            
        
        parcel_c = pd.concat(parcelID)
        print(parcel_c)
        #del df_files, parcelID
        print('puuh, created the dataframes...')
        
        #bands_names = [['B2_mean', 'B3_mean','B4_mean', 'B8_mean','B2_std', 'B3_std','B4_std', 'B8_std', 'Pix_count'],['B5_mean', 'B6_mean','B7_mean', 'B8A_mean','B11_mean','B12_mean','probability_mean','B5_std', 'B6_std','B7_std', 'B8A_std','B11_std','B12_std','probability_std','Pix_count' ]]
        bands_names = [['B5_mean', 'B6_mean','B7_mean', 'B8A_mean','B11_mean','B12_mean','probability_mean','B5_std', 'B6_std','B7_std', 'B8A_std','B11_std','B12_std','probability_std','Pix_count' ]]
        df_all = {}
        parcel_select = []
        GEM_lst = []
        PROV_lst = []
        for i in range(len(parcel_c)):
            #print(i, len(parcel_c))
            df_per_ID  = pd.DataFrame()
            
            for j in range(len(bands_names[f])):
                
                df_per_ID[bands_names[f][j]] = df_per_var[j].iloc[i]
                df_per_ID['OID'] = [parcel_c.index[i]]*len(df_per_ID)
            df_per_ID = df_per_ID.dropna()  
            if len(df_per_ID)!= 0:
                #print(i+1, 'out of', len(vv_m_c), ((i+1)*100/len(vv_m_c)))
                df_all[parcel_c.index[i]]  = df_per_ID
                       
                point = Point(parcel_c['lon'].iloc[i],parcel_c['lat'].iloc[i])
            
                x_gem =GEM['geometry'].contains(point)
                x_prov =PROV['geometry'].contains(point)
                
                if any(x_prov) == True:
                    string = PROV['PROV_NAAM'][x_prov].values[0]
                    PROV_lst.append(''.join(e for e in string if e.isalnum()).replace('-', ' '))
                else: 
                    print("nan prov")
                    PROV_lst.append('NaN')
            
                    
                if any(x_gem) == True:
                    string = GEM['GM_NAAM'][x_gem].values[0]
                    GEM_lst.append(''.join(e for e in string if e.isalnum()).replace('Ãº', 'u').replace('Ã¢', 'a'))
                else: 
                    print("nan gem")
                    
                    GEM_lst.append('NaN')
                unique_field_geo = fields[fields["OBJECTID"]==parcel_c.index[i]]
                pa = gpd.GeoDataFrame(parcel_c.iloc[i]).T
                pa['polygon'] = unique_field_geo['geometry'].values
                #print(pa)
                parcel_select.append(pa)
            del df_per_ID
        
        print('yeah, dictonary is created... getting there')
        print(parcel_select)
        parcel_c = pd.concat(parcel_select)
        
        parcel_c['gem'] = GEM_lst
        parcel_c['prov'] = PROV_lst
        
        prov = np.unique(PROV_lst)
        
        
        del GEM_lst, PROV_lst
        
        if not os.path.exists('{}Pickle_{}'.format(path,year)):
            os.makedirs('{}Pickle_{}'.format(path,year))
                
        for i in range(len(prov)):
            if not os.path.exists('{}Pickle_{}/Prov_{}'.format(path,year,prov[i])):
                os.makedirs('{}Pickle_{}/Prov_{}'.format(path,year,prov[i]))
                
        #Creating picles per province... 
        
        list_df = []
        
        for i in range(len(prov)):
            print(prov[i], 'Creating the pickles...')
            IDs = parcel_c[parcel_c['prov']==prov[i]].index.values
            
            new_list =  { your_key: df_all[your_key] for your_key in IDs }
            
            new_list['Parcel_Information'] =gpd.GeoDataFrame(parcel_c[parcel_c['prov']==prov[i]])
        
            list_df.append(new_list)
            with open('{}Pickle_{}/Prov_{}/Prov_{}_S2_Res_{}m.pickle'.format(path,year,prov[i],prov[i], resolution[f]), 'wb') as handle:
                pickle.dump(new_list, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
        print('yeah finished with a year...')