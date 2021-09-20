# -*- coding: utf-8 -*-
"""
Created on Mon Sep 20 14:54:52 2021

@author: Manuel Huber
"""


import numpy as np
import re
import geopandas as gpd
import scipy as sc

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

#%% Splitting the dataset and then concatenating it.


'''
This script builds on the data structure constructed by the mining script:
    
Git: Agricultural-SandboxNL/Sentinel 1 GRD/Mining_S1GRD_Per_Parcel_GEE_Python_API.py


The purpose is to merge all individual csv files together to a national dataset

'''
def get_pickle_per_orbit(path,orbit):
    files = glob.glob("{}Orbit_{}/*.csv".format(path,orbit))
    print('start with Orbit {}'.format(orbit))
    vv_m2 = []
    vv_std2 = []
    vh_m2 = []
    vh_std2 = []
    vh1_m2 = []
    vh1_std2 = []
    
    lia_m2= []
    ea_2 = []
    aza_2 = []
    pix_m2 =[]
    
    #dates_all = []
    parcelID = []
    mission_details = []
    
# For loop to go through all files within an orbit folder (csv files)

    for l in range(len(files)):
        
        df = pd.read_csv(files[l])
        # Get the OBject id as index, so we can sort it accordingly
           
        df.index = df['OBJECTID']
        df = df.sort_index()
        
        londf = []
        latdf = []
        faults = []
        for p in range(len(df)):
            if str(df['Polygon_Centroid'].iloc[p])!= 'nan':
                
                londf.append(eval(df['Polygon_Centroid'].iloc[p])["coordinates"][0])
                latdf.append(eval(df['Polygon_Centroid'].iloc[p])["coordinates"][1])
            else:
                print('MISSING FIELD (ROW: {} ) in File: {}'.format(p,files[l]))
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
        lables_end = []
        for i in range(len(lables_raw)):
            lables_end.append(lables_raw[i][-2:])
        strings = ['VV_mean','VV_stdDev', 'VH_mean', 'VH_stdDev','VH_1_mean','VH_1_stdDev','angle_count', 'angle_mean','angle_stdDev','AZI_mean','AZI_stdDev','LIA_mean', 'LIA_stdDev' ]
        
        
        
        
        all_headers = []
        for k in range(len(strings)):
            res = [i for i in lables_raw if strings[k] in i]
            all_headers.append(res)
        
        # Function to extract the MIssioID from the header... 
        def get_missionID(header_vv):
            ID = []
            for i in range(len(header_vv)):
                if header_vv[i][:3] =='S1A':
                    ID.append(0)    #0 == S1A Mission
                else:
                    ID.append(1)    #1 == S1B Mission
            return ID
        
        # Extract the header strings
        
        # FUnction to extract the relative orbit
        def find_number(text, c):
            return re.findall(r'%s(\d+)' % c, text)
        
        # Function to extract the dates from the headers
        all_dates = []
        for k in range(len(all_headers)):
            dates = []
            for i in range(len(all_headers[k])):
                date = all_headers[k][i] #Selecting only the frist date once it is started to record
                date_for_file = datetime(year=int(date[17:21]), month=int(date[21:23]), day=int(date[23:25]), hour=(int(date[26:28])), minute=(int(date[28:30])),second=(int(date[30:32])))
                dates.append(date_for_file)
            all_dates.append(dates)
        
        
        # Store the mission ID and Relative orbit, Pass Type
        df_ID_RO_P = pd.DataFrame()
        df_ID_RO_P['ID'] = get_missionID(all_headers[0])
        df_ID_RO_P['RO'] = [int('{}'.format(orbit))]*len(all_headers[0])
        
        
        
        if  re.findall('DESENDING', files[l]) == 'DES':
            df_ID_RO_P['PASS'] = [0] *len(all_headers[0])       # 0 == 'DESENDING'
        else: 
            df_ID_RO_P['PASS'] = [1] *len(all_headers[0]) # 1== 'ASCENDING'
        df_ID_RO_P.index = all_dates[0]
        
        mission_details.append(df_ID_RO_P)
        
        # Next lines are to create the dataframes per variable and lable/index it with the excat date
        # Order of the array:
        #   strings = ['VV_mean','VV_stdDev', 'VH_mean', 'VH_stdDev','VH_1_mean','VH_1_stdDev','angle_count', 'angle_mean','angle_stdDev','AZI_mean','AZI_stdDev','LIA_mean', 'LIA_stdDev' ]
        vv_m=df[all_headers[0]]
        vv_m.columns = all_dates[0]
        
        vv_std=df[all_headers[1]]
        vv_std.columns = all_dates[1]
        
        vh_m=df[all_headers[2]]
        vh_m.columns = all_dates[2]
        
        vh_std=df[all_headers[3]]
        vh_std.columns = all_dates[3]
        
        vh1_m=df[all_headers[4]]
        vh1_m.columns = all_dates[4]
        
        vh1_std=df[all_headers[5]]
        vh1_std.columns = all_dates[5]
        
        ea=df[all_headers[7]]
        ea.columns = all_dates[7]    
        
        aza=df[all_headers[9]]
        aza.columns = all_dates[9]
        
        lia_m=df[all_headers[11]]
        lia_m.columns = all_dates[11]
        
        pix=df[all_headers[6]]
        pix.columns = all_dates[6]
        
        
        
        flag_pix = []
        flag_diff = []
        for i in range(len(pix)):
            val = list(filter(None,np.unique(pix.iloc[i])))
            dates_uni = pd.to_datetime(vv_std.iloc[i].dropna().index.strftime('%d-%m-%y').unique())
            dates_all = pd.to_datetime(vv_std.iloc[i].dropna().index.strftime('%d-%m-%y'))
            
            if len(val) != 0:
                dif = np.max(val)-np.min(val)
                
            else:
                dif = 0
                        
            if  abs(len(dates_uni)-len(dates_all)) > 0:
                flag_pix.append(1) # if the leng differs more then the trheshold then it means the field covers 2 consecutive time stamps
                flag_diff.append(dif)
                
            elif dif > 3 and np.min(ea.iloc[i]) < 30.1 and len(dates_uni) == len(dates_all):
                 flag_pix.append(2) #Flagging fields which diverge in pixel count caused by near, far range border effects
                 flag_diff.append(dif)
            
            elif dif > 3 and np.max(ea.iloc[i])>44.9 and len(dates_uni) == len(dates_all):
                flag_pix.append(2) #Flagging fields which diverge in pixel count caused by near, far range border effects
                flag_diff.append(dif)
                    
            else: 
                flag_pix.append(0) # No overlap etc, hence no processing needed
                flag_diff.append(0)
        
        # Create a dataframe saving all the parcel informations /deleting empty roles 
        ID = df[['Polygon_Centroid','lon','lat',
        'GWS_GEWAS',
        'CAT_GEWASC',
        'GWS_GEWASC',
        'GEOMETRIE_',
        'GEOMETRIE1']]
        pd.options.mode.chained_assignment = None  
        ID['flag_{}'.format(orbit)] = flag_pix
        ID["flag_diff_{}".format(orbit)]= flag_diff
        
        # Save the parcel informations.. 
        parcelID.append(ID)
        
        
        ea_2.append(ea)
        vv_m2.append(vv_m)
        vv_std2.append(vv_std)
        vh_m2.append(vh_m)
        vh_std2.append(vh_std)
        vh1_m2.append(vh1_m)
        vh1_std2.append(vh1_std)
        pix_m2.append(pix)
        lia_m2.append(lia_m)
        aza_2.append(aza)
    
    del ea, vv_m, vv_std, vh_m, vh_std, vh1_m, vh1_std, pix, lia_m, aza, df_ID_RO_P, df, all_dates, all_headers, lables_raw, londf, latdf
    
    # Concat all the different files together... 
    vv_m_c =pd.concat(vv_m2).sort_index()
    vv_std_c = pd.concat(vv_std2).sort_index()
    vh_m_c = pd.concat(vh_m2).sort_index()
    vh_std_c = pd.concat(vh_std2).sort_index()
    vh1_m_c = pd.concat(vh1_m2).sort_index()
    vh1_std_c = pd.concat(vh1_std2).sort_index()
    
    pix_c = pd.concat(pix_m2).sort_index()
    
    lia_m_c=pd.concat(lia_m2).sort_index()
    aza_c= pd.concat(aza_2).sort_index()
    ea_c = pd.concat(ea_2).sort_index()
    
    mission_details_c = pd.concat(mission_details)
    mission_details_c = mission_details_c[~mission_details_c.index.duplicated(keep='first')].sort_index()
    
    parcel_c = pd.concat(parcelID)
    parcel_c= pd.DataFrame(parcel_c).sort_index()
    
    print('appending {} .. getting to correction'.format(orbit))
    
    # Function to correct for parcels which have a double timestep as these occure on two images! 
    # This can happen if the parcel boundaries reach over two consecutive images
    
    def correct_for_double_timest(vv_m_c, pix_c,fl):
    
        df_ib = pd.DataFrame()
        df_ib['var'] =vv_m_c.values
        df_ib['pix'] =pix_c.values
        df_ib.index = vv_m_c.index
        df_ib = df_ib.dropna()
        
        
        dates = pd.to_datetime(df_ib.index.strftime('%d-%m-%y').unique())
    
        date_out = []
        var = []
        for i in range(len(dates)):
            
            xy = df_ib[pd.to_datetime(df_ib.index.strftime('%d-%m-%y'))==dates[i]]
            if len(xy) ==2:
                x = ((xy.iloc[0]['var']*xy.iloc[0]['pix'])+(xy.iloc[1]['var']*xy.iloc[1]['pix']))/(xy.iloc[1]['pix']+xy.iloc[0]['pix'])
                date_out.append(pd.to_datetime(xy.index[0]))
                var.append(x)
          
            else:
                date_out.append(pd.to_datetime(xy.index[0]))
                var.append(xy['var'].values[0])
        df_out = pd.DataFrame()
        df_out['var'] = var
        df_out.index = date_out
        df_out = df_out.sort_index()
    
        
        return df_out['var']
    
    # Sort the data per ID and time date // Primary structure is with the OBJECT ID
    
    df_all = {}
    parcel_select = []
    GEM_lst = []
    PROV_lst = []
    
    for i in range(len(vv_m_c)):
    #print(i)
        
        if parcel_c.iloc[i]['flag_{}'.format(orbit)] == 1:
            df_per_ID = pd.DataFrame()
            
            df_per_ID['vv_mean'] = correct_for_double_timest(vv_m_c.iloc[i], pix_c.iloc[i],1)
            df_per_ID['vv_std'] = correct_for_double_timest(vv_std_c.iloc[i], pix_c.iloc[i],1)
            df_per_ID['vh_mean'] = correct_for_double_timest(vh_m_c.iloc[i], pix_c.iloc[i],1)
            df_per_ID['vh_std'] = correct_for_double_timest(vh_std_c.iloc[i], pix_c.iloc[i],1)
            df_per_ID['CR_mean'] = correct_for_double_timest(vh1_m_c.iloc[i], pix_c.iloc[i],1)
            df_per_ID['CR_std'] = correct_for_double_timest(vh1_std_c.iloc[i], pix_c.iloc[i],1)
            df_per_ID['lia'] =correct_for_double_timest(lia_m_c.iloc[i], pix_c.iloc[i],1)
            df_per_ID['ea'] =correct_for_double_timest(ea_c.iloc[i], pix_c.iloc[i],1)
            df_per_ID['aza'] = aza_c.iloc[i][aza_c.iloc[i].index.isin(df_per_ID.index)]
            df_per_ID['pix'] = pix_c.iloc[i][pix_c.iloc[i].index.isin(df_per_ID.index)]
            df_per_ID['OID'] = [vv_m_c.index[i]]*len(df_per_ID)
            df_per_ID['MID'] = mission_details_c['ID'][mission_details_c['ID'].index.isin(df_per_ID.index)]
            df_per_ID['RO'] = mission_details_c['RO'][mission_details_c['RO'].index.isin(df_per_ID.index)]           
        else:           
            df_per_ID = pd.DataFrame()              
            df_per_ID['vv_mean'] = vv_m_c.iloc[i]
            df_per_ID['vv_std'] = vv_std_c.iloc[i]
            df_per_ID['vh_mean'] = vh_m_c.iloc[i]
            df_per_ID['vh_std'] = vh_std_c.iloc[i]
            df_per_ID['CR_mean'] = vh1_m_c.iloc[i]
            df_per_ID['CR_std'] = vh1_std_c.iloc[i]
            df_per_ID['lia'] =lia_m_c.iloc[i]
            df_per_ID['aza'] =aza_c.iloc[i]
            df_per_ID['ea'] =ea_c.iloc[i]
            df_per_ID['OID'] = [vv_m_c.index[i]]*len(df_per_ID)
            df_per_ID['pix'] = pix_c.iloc[i]
            df_per_ID['MID'] = mission_details_c['ID']
            df_per_ID['RO'] = mission_details_c['RO']
            df_per_ID = df_per_ID.dropna()
            
        # Only if the selected ID has data it will be stored in the dictionary
        if len(df_per_ID)!= 0:
            df_all[vv_m_c.index[i]]  = df_per_ID
                   
            point = Point(parcel_c['lon'].iloc[i],parcel_c['lat'].iloc[i])
        
            x_gem =polygons_gem.contains(point)
            x_prov =polygons_prov.contains(point)
            
            if any(x_prov) == True:
                string = PROV['PROV_NAAM'][x_prov].values[0]
                PROV_lst.append(''.join(e for e in string if e.isalnum()).replace('-', ' '))
            else: 
                print("nan prov")
                PROV_lst.append('NaN')
        
                
            if any(x_gem) == True:
                string = GEM1['GM_NAAM'][x_gem].values[0]
                GEM_lst.append(''.join(e for e in string if e.isalnum()).replace('ú', 'u').replace('â', 'a'))
            else: 
                print("nan gem")
                
                GEM_lst.append('NaN')
            unique_field_geo = fields[fields["OBJECTID"]==parcel_c.index[i]]
            pa = gpd.GeoDataFrame(parcel_c.iloc[i]).T
            pa['polygon'] = unique_field_geo['geometry'].values
            parcel_select.append(pa)
        
    del ea_c, vv_m_c, vv_std_c, vh_m_c, vh_std_c, vh1_m_c, vh1_std_c, lia_m_c, aza_c, mission_details_c, df_per_ID, pa, unique_field_geo, parcel_c
    
    
      
    print('Corrected {}, now getting into final preps... '.format(orbit))
    
    # Concatenating the parcel information to one file and add information about province and municipality
    parcel_c = pd.concat(parcel_select)
    parcel_c['gem'] = GEM_lst
    parcel_c['prov'] = PROV_lst
    
    prov = np.unique(PROV_lst)
    
    
    del GEM_lst, PROV_lst
    
    if not os.path.exists('{}Pickle'.format(path)):
        os.makedirs('{}Pickle'.format(path))
            
    for i in range(len(prov)):
        if not os.path.exists('{}Pickle/Prov_{}'.format(path,prov[i])):
            os.makedirs('{}Pickle/Prov_{}'.format(path,prov[i]))
    
    #Creating pickles per province... 
    
    list_df = []
    
    for i in range(len(prov)):
        
        print('{}_Orbit {}; {} out of {} '.format(prov[i],int(orbit),i, len(prov)))
        
        IDs = parcel_c[parcel_c['prov']==prov[i]].index.values
        
        new_list =  { your_key: df_all[your_key] for your_key in IDs }
        
        new_list['Parcel_Information'] =gpd.GeoDataFrame(parcel_c[parcel_c['prov']==prov[i]])
    
        list_df.append(new_list)
        with open('{}Pickle/Prov_{}/Prov_{}_Orbit_{}.pickle'.format(path,prov[i],prov[i], orbit), 'wb') as handle:
            pickle.dump(new_list, handle, protocol=pickle.HIGHEST_PROTOCOL)
            
        del IDs, new_list
    print('Finished pickle creation Orbit {}'.format(orbit))   
    
    del df_all, parcel_c





#%% Run it for all the orbits...

#####################################################################################################
#####################################################################################################
#####################################################################################################
#####################################################################################################
'''
The following inputs have to be changed according to the year 
'''
#####################################################################################################

year = 2020

shp = "BRP_Proj_{}".format(year)
        
PROV =gpd.read_file('/DATA-2/Input_Data/Prov/Province_van_nederland_proj.shp')
polygons_prov = PROV['geometry']
GEM1 = gpd.read_file('/DATA-2/Input_Data/Gem/gem_2018_proj.shp')
polygons_gem = GEM1['geometry']

fields = gpd.read_file('/DATA-2/Input_Data/BRP_{}/{}.shp'.format(year,shp))
path = '/DATA-2/{}_New_2/'.format(year)


relOrbits = [88,161,15,37,110,139]


#####################################################################################################
#####################################################################################################
#####################################################################################################
#####################################################################################################
#####################################################################################################



for i in range(len(relOrbits)):
    get_pickle_per_orbit(path,'{}'.format(relOrbits[i]))
    

# Path where to store the final dataset.....

if not os.path.exists('{}Pickle Final New V8 {}'.format(path,year)):
        os.makedirs('{}Pickle Final New V8 {}'.format(path,year))
    
path_save = '{}Pickle Final New V8 {}/'.format(path,year)


folders = glob.glob("{}Pickle/*/".format(path))

for f in range(len(folders)):
    
    print('Folder: {} out of {}'.format(f, len(folders)))
    path_prov = folders[f]
    files = glob.glob("{}*".format(path_prov))
    
    # Information stored in the parce file
    static = ['Polygon_Centroid',
                   'lon',
                   'lat',
                   'GWS_GEWAS',
                   'CAT_GEWASC',
                   'GWS_GEWASC',
                   'GEOMETRIE_',
                   'GEOMETRIE1',
                   'polygon',
                   'gem',
                   'prov']
    
    parcel_info = []
    pickles = []
    orbits = []
    parcel_static = []
    
    for i in range(len(files)):
        orbits.append(re.findall('\d+', files[i][-18:])[0])
        infile = open(files[i],'rb')
        new_dict = pickle.load(infile)
        parcel_info.append(new_dict['Parcel_Information'])
        parcel_static.append(new_dict['Parcel_Information'][static])
        
        del new_dict['Parcel_Information']
        pickles.append(new_dict)
        del new_dict
        infile.close()

                       
    parcel = pd.concat(parcel_static).sort_index()
    parcel_c = parcel[~parcel.index.duplicated(keep='first')]
    
    # Include all the flagging information in the parcel information file
    for i in range(len(orbits)):
        parcel_c = pd.concat([parcel_c, parcel_info[i][['flag_{}'.format(orbits[i]),'flag_diff_{}'.format(orbits[i])]]], axis=1)
    
    del parcel
    
    unique_ID =parcel_c.index
    
    # Concat the dataframes together which have the same ObjectID and store each dataframe in a list under the ObjectID
    def get_df_list(df_37):
        key = list(df_37.keys())
        dfib = []
        for i in range(len(key)):
            df1 = df_37[key[i]]
            dfib.append(df1)
        df = pd.concat(dfib)
        return df
    
    df_all_c = []
    
    for i in range(len(pickles)):
        df_all_c.append(get_df_list(pickles[i]))
           
    df_all = pd.concat(df_all_c)
    
    del df_all_c, pickles

    # Creating a dictonary which is sorted per parcel ID
    list_ID = {}
    for i in range(len(unique_ID)):
         list_ID[unique_ID[i]] = df_all[df_all['OID']==unique_ID[i]].sort_index()
    list_ID["Parcel_Information"]= parcel_c
    
    
    # Storing the dictonary
    with open('{}Dict_Prov_{}.pickle'.format(path_save,parcel_c['prov'].iloc[0]), 'wb') as handle:
            pickle.dump(list_ID, handle, protocol=pickle.HIGHEST_PROTOCOL)

    del list_ID, df_all, parcel_c

