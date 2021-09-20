# -*- coding: utf-8 -*-
"""
Created on Mon Sep 20 15:12:00 2021

@author: Manuel Huber
"""


import netCDF4 as nc4
import numpy as np
import re
import geopandas as gpd

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from netCDF4 import Dataset

import pickle
#import datetime
from datetime import datetime, date, time
import glob
import sys

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
#np.set_printoptions(threshold=sys.maxsize)

import math    
import os



# Here mulitple years can be processed in one go - following has only one year as an example
# paralell computing can be used for muliple years. 

years = [2020]

for y in range(len(years)):
    year = years[y]
    print(year)

    # Reading all pickle files stored 
    if not os.path.exists('/DATA-2/{}_New_2/netCDF'.format(year)):
        os.makedirs('/DATA-2/{}_New_2/netCDF'.format(year))
    files = glob.glob("/DATA-2/{}_New_2/Pickle Final New V8 {}/*".format(year,year))
    
    
    path = '/DATA-2/{}_New_2/'.format(year)
    files = glob.glob("{}Pickle Final New V8 {}/*".format(path,year))
    
    
    arr = os.listdir("{}Pickle Final New V8 {}/".format(path,year))
    names = []
    
    # Settin up all variable names and units, which will be used to strucutre the netcdf
    for i in range(len(files)):
        names.append(arr[i][5:-7])
    var_lables =['vv_mean',
      'vv_std',
      'vh_mean',
      'vh_std',
      'CR_mean',
      'CR_std',
      'lia',
      'ea',
      'aza',
      'OID',
      'pix',
      'MID',
      'RO',
      'time_num']
    
    long_name =['Linear backscatter intensity VV mean - 0','Linear backscatter intensity VV standard deviation - 1','Linear backscatter intensity VH mean - 2','Linear backscatter intensity VV standard deviation - 3','Linear backscatter intensity Cross-Ratio VH/VV mean - 4','Linear backscatter intensity Cross-Ratio VH/VV standard deviation - 5','Local Incidence Angle - 6', 'Elevation Angle - 7','Azimuth Angle - 8','Object Field ID - 9','Pixel Count - 10', 'Mission ID [0=S1A, 1=S1B] - 11','Relavtive Orbit - 12','Time gregorian - 13' ] 
    unit_var = [ 'Linear backscatter intensity','Linear backscatter intensity','Linear backscatter intensity','Linear backscatter intensity','Linear backscatter intensity','Linear backscatter intensity','degrees', 'degrees', 'degrees','[-]','[#]','[-]','[-]','[calendar = gregorian; units = hours since 1900-01-01 00:00:00.0]']
    
    calendar = 'gregorian'
    units = 'hours since 1900-01-01 00:00:00.0'
    
    
    for file in range(len(files)):
    
        if 'NaN' not in files[file]:
            infile = open(files[file],'rb')
            new_dict = pickle.load(infile)
            parcel_info = new_dict['Parcel_Information']
            del new_dict['Parcel_Information']
            
            unique_ID = parcel_info.index
            
            parcel_info.to_csv('{}netCDF/{}_Parcel_Information'.format(path, names[file]))
            
            
            arr = list(range(0, len(unique_ID)))
            newarr = np.array_split(arr, int(np.round(len(unique_ID)/5000, 0)))
            
            for j in range(len(newarr)):
                
                print(j)
                if j == 0:
                    f = nc4.Dataset('{}netCDF/{}.nc'.format(path, names[file]),'w', format='NETCDF4') #'w' stands for write
                    parcel = f.createGroup('Data')
                    parcel.createDimension('Time', None) #len(new_dict[unique_ID[newarr[j][k]]])
                    #parcel.createDimension('Variable', len(var_lables))
                    parcel.createDimension('Parcels', None)
                    
                    parcel_if = f.createGroup('Parcel_ID')
                    parcel_if.createDimension('Parcels', len(unique_ID))
                    temp_if0 = parcel_if.createVariable('ID', 'i4', ['Parcels']) #i4 is integre, wheres f4 are floats..
                    temp_if0[:]= unique_ID
                    temp_if1 = parcel_if.createVariable('lon', 'f4', ['Parcels'])
                    temp_if1[:]= parcel_info['lon'].values
                    temp_if2 = parcel_if.createVariable('lat', 'f4', ['Parcels'])
                    temp_if2[:]= parcel_info['lat'].values          
                    
                    flags = parcel_info.iloc[:,11:]
                    flag_lst = list(flags.columns) 
                    for fl in range(len(flag_lst)):
                        if 'diff' not in flag_lst[fl]: 
                            temp_flag = parcel_if.createVariable('{}'.format(flag_lst[fl]), 'f4', ['Parcels'])
                            temp_flag[:]= parcel_info['{}'.format(flag_lst[fl])].values 
                            temp_flag.unit = '[-]'
                            temp_flag.long_name = 'Flag 1 indicates parcel at azimuth image border and Flag 2 a parcel on the near/far range image border'
                            del temp_flag
                else:
                    f = nc4.Dataset('{}netCDF/{}.nc'.format(path, names[file]),'r+', format='NETCDF4') #'w' stands for write
                    parcel = f['Data']      
                    
                    
                for k in range(len(newarr[j])): #len(unique_ID)
                
                    print(k+1,' out of {}'.format(len(newarr[j])), 'Done: {} % '.format(np.round(((k+1)*100)/len(newarr[j]),2)), names[file], j, 'out of', len(newarr))
        
                    
                    df = new_dict[unique_ID[newarr[j][k]]]
                    dates = df.index
                    for v in range(len(var_lables)):
                        
                        if j == 0 and k ==0:
                            if var_lables[v] in ['pix','OID', 'MID','RO']:
                                temp = parcel.createVariable('{}'.format(var_lables[v]), 'i4', ['Parcels','Time'])
                                temp.unit = unit_var[v]
                                temp.long_name = long_name[v]
                            elif var_lables[v] == 'time_num':
                                temp = parcel.createVariable('{}'.format(var_lables[v]), 'f4', ['Parcels','Time'])
                                temp.unit = units
                                temp.calendar = 'gregorian'
                                temp.long_name = unit_var[v]
                            else:
                                temp = parcel.createVariable('{}'.format(var_lables[v]), 'f4', ['Parcels','Time'])
                                temp.unit = unit_var[v]
                                temp.long_name = long_name[v]
                        else:
                            temp = parcel['{}'.format(var_lables[v])]
        
                    
                        if var_lables[v] == 'time_num':
                            dates = df.index
                            dates_num = []
                            for i in range(len(dates)):
                                dates_num.append(nc4.date2num(dates[i], units = units, calendar = calendar))
                            df['time_num'] = dates_num
                            temp[newarr[j][k],:] =  df['time_num'].values                    
                                
                        else:
                            temp[newarr[j][k],:] =  df['{}'.format(var_lables[v])].values
                            # temp.add_offset = add_offset
                            # temp.scale_factor = scale_factor
                        
                        del temp
                        
                        
                    del df
                del parcel
                
                f.close()
