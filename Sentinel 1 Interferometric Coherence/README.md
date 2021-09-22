# Addtional information about the database creation and introduction script

---------------------------------------------------------------------

1) Calculating_Interferometric_Coherence_Batch_Script_SNAP_Python

- from os import path
- import os
- import pandas as pd
- from datetime import datetime, date, time

This program utilizes the SNAP software using a Python API. The execution of the script is done with the ./gpt (graphical processing tool) of SNAP.
More information about the gpt-SNAP can be found here: http://step.esa.int/docs/tutorials/SNAP_CommandLine_Tutorial.pdf

The processing chain to calculate the interferometric coherence is illustrate here and stored in the 4_CCD_Graph_param_coherence_TIF.xml:

<img width="571" alt="GPT_Chain" src="https://user-images.githubusercontent.com/62883629/134313667-aa17db5f-7116-4be4-bf7c-6ca92c170934.PNG">

The Interferometric Cohernce pairs are stored as tiff files. As a next step field averages and standard deviations are calcuated using the BRP files from PDOK (same as for Sentinel 1 GRD and Sentinel 2). However, this step needs to be done manually as Google Earth Engine can not be utilized for this efficiently. 




