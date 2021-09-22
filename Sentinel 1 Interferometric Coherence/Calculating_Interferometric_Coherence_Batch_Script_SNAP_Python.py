# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 10:41:44 2021

@author: Manuel Huber
"""


from os import path
import os
import pandas as pd
from datetime import datetime, date, time


# Here the diretory of the SLC needs to be adjusted
files = os.listdir("/data/Images_2019_88/SLC/")
dates = []
for k in range(len(files)):
    date = files[k]
    # Extracting the dates from the file name
    date_for_file = datetime(year=int(date[17:21]), month=int(date[21:23]), day=int(date[23:25]))
    dates.append(date_for_file)


df = pd.DataFrame()
df['labels'] = files
df.index = dates
df = df.sort_index()
#print(df)


for i in range(len(files)-1):
    #print(i, 'out of', len(files)-1)
    output = 'Coherence_VV_{}_{}'.format(df.labels[i][17:25],df.labels[i+1][17:25])
    inp1 = df.labels[i]
    inp2 = df.labels[i+1]
    #print('Start with',output)
    if not path.exists('/data/Images_2019_88/Output_Tiffs_88_20/{}.tif'.format(output)):
        #print(i, 'out of', len(files)-1)
        print(files[i])
	#print(files[i])
        # Executing the os commands to batch script the coherence calculations for all pairs within the given time frame
        # XMS and Xmx are set for the avialable memory for the system, the xml file is the batch script created using SNAP
        os.system('./gpt /data/Images_2019_88/Scihub/4_CCD_Graph_param_coherence_TIF.xml -J-Xms8G -J-Xmx35G -PInputFile1=/data/Images_2019_88/SLC/{} -PInputFile2=/data/Images_2019_88/SLC/{}  -POutputFile=/data/Images_2019_88/Output_Tiffs_88_20/{}'.format(inp1, inp2, output))