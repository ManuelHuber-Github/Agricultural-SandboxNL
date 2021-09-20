# SandboxNL
Agricultural Monitoring exploiting Sentinel 1 and Sentinel 2. SandboxNL contains detailed explanations about the creation and usage of the parcel based Sentinel datasets. 

In the Agricultural SandboxNL, consecutive years (strating from 2017) of Snetinel-1A/B synthetic aperture radar (SAR) scenes as well as Sentinel 2 images, are used to generated the Basisregestratie GewasPercelen (BRP) parcel-level database of the Netherlands. The database is consists of parcel-level spatially averaged VV, VH and VH/VV backscatter values, corresponding standard deviation, viewing incidence angle, local incidence angle, azimuth angle, pixel count and data quality flag for each parcel. Each parcel can be identified with an unique Object ID. The same counts for the processing steps applied onto the Sentinel 2 images. All spectral bands have been processed and stored using the same BRP parcel information.

The databases (Sentinel 1 and 2)  provide time series for approximately  770,000  crop  parcels  over  the  Netherlands  annually. The  database  can  be queried for Sentinel-1 /2 system parameter (e.g. relative orbit) or user application-specific parameter (e.g. crop type, spatial extent, time period) for individual parcel level assessment or aggregated at administrative boundaries.

These unique datasets allow non-expert and expert users to directly utilize agricultural parcel information in space and time using SAR and optical data without undergoing complex and computationally intensive data handling and processing steps. The extracted spatially tagged parcel-level information is scalable at various administrative (e.g., municipalities, water boards and provinces) and user defined boundaries.

What does the Agricultural SandboxNL contain?

-	A national scale database
-	Parcel level, processed SAR (Sentinel-1) data / six relative orbits
-	Parcel level, processed Optical (Sentinel-2) data / 12 spectral bands
-	Parcel level, processed SAR (Sentinel-1) Interferometric Coherence / one relative orbit
-	770.000 crop parcels containing 312 different crop types
-	Up to 3 years of continuous data


------------------------------------------------------------------------------
# Authors:

Vineet Kumar (V.Kumar-1@tudelft.nl), Department of Water Management, Delft University of Technology, Delft, The Netherlands,
Manuel Huber (manuel.huber@esa.int), European Space Agency (ESA-ESTEC), Noordwijk,The Netherlands,
Susan Steele-Dunne (s.c.steele-dunne@tudelft.nl), Department of Geoscience and Remote Sensing, Delft University of Technology, Delft, The Netherlands,
Björn Rommen (Bjorn.Rommen@esa.int), European Space Agency (ESA-ESTEC), Noordwijk,The Netherlands

------------------------------------------------------------------------------

The following figure illustrates multiple images in from of a GIF, showing the spatial and temporal extension of the Sentinel 1 GRD and Interferometric Coherence as well as the Sentinel 2 datasets. The VH/VV is representing the Sentinel 1 GRD database using only one relative orbit out of the six different orbits covering the Netherlands. In all three subplots, the monthly averages are shown, highlighting the main crop dynamics such as emergence, growth and harvest. The time series plots show the variation of all maize fields within Dronten as an example to illustrate the average growing cycle of maize indicating emergence around June and harvest in the beginning of October. Still, below the monthly averages much more information is hidden, containing crop specific anomalies and patterns depending on environmental factors, individual famer practices, crop type and viewing geometries of the satellites. 

![GIF_Article](https://user-images.githubusercontent.com/62883629/133793704-d9fb53a5-7caa-4ad1-879e-c07131569330.gif)

------------------------------------------------------------------------------
# Git Repository Structure 

This git-hub repository shall give all information about this project, starting from database creation and data minining to concrete retrieval examples. 
All information is openly avialable and should give the opportunity to enhance research for agricultural monitoring and to create operational applications. 




