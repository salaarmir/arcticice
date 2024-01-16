#!/usr/bin/env python
# coding: utf-8

# # Arctic Ice
# 
# ### Data Scrub
# 
# * imports csv and convert to pandas dataframes
# * remove awkward characters from columns
# * removes unnecessary columns
# * merges dataframes
# * changd code to systematically find csvs
# 
#  ### Merging
#  
#  * merges dataframes into single
#  * remove unwanted columns
#  * remove unwanted years / rows
#  
#  ### Error removal
#  
#  * Errors identified and replaced with nans
#  * nans replaced using highlighed code, default is linear interpolation
#  

# ## Imports

import pandas as pd
import glob
import numpy as np
import seaborn as sns
import matplotlib as plt
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

#Arctic Ice


#implemented using salaars code
filepath = '../Data/Arctic_Ice_Monthly/*.csv'
csv_files = glob.glob(filepath)

for i in range(len(csv_files)):
    csv_files[i] = csv_files[i][27:]
    
raw_ds = pd.concat([pd.read_csv(file) for file in csv_files ], ignore_index=True)


#I change some column headings to remove special characters
import pandas as pd

raw_ds.columns = raw_ds.columns.str.replace('-', '')
raw_ds.columns = raw_ds.columns.str.replace(' ', '')


# The dataframe is sorted by year, then month. Reorganizing the data month by month. 
raw_ds = raw_ds.sort_values(by=['year', 'mo'])
raw_ds = raw_ds.reset_index(drop=True)


#seperates into analysis_df, which is to be used for analysis, and 2023_df.
#2023 data was seperated into as it uses a new datatype this could
#prove an issue as all other data is Godddard type

a = raw_ds.loc[62:529]
df_2023 = raw_ds.loc[530:]

#Temp
#takes temp data from csv file and drops irrelvant columns
t = pd.read_csv('../Data/Temps.csv')
t = t[['TAVG']]
t = t.rename(columns={"TAVG": "temp"})

#cuts down the data to the years and months covered by arctiv ice data
t =  t.loc[822:1289]


#Methane

#takes temp data from csv file and drops irrelvant columns
m = pd.read_csv('../Data/Methane.csv')
m = m[['average']]
m = m.rename(columns={"average": "methane"})

#cuts down the data to the years and months covered by arctiv ice data
m =  m.loc[6:473] 



#takes temp data from csv file and drops irrelvant columns
c = pd.read_csv('../Data/Carbon_Dioxide.csv')
c = c[['average']]
c = c.rename(columns={"average": "CO2"})

#cuts down the data to the years and months covered by arctiv ice data
#m =  m.loc[6:473] 
c =  c.loc[60:527]

 #Merging


a, m, t, c = a.reset_index(), m.reset_index(), t.reset_index(), c.reset_index()

all_data = pd.concat([a, t, m, c,], axis=1, join="inner")
all_data = all_data.drop(['index','datatype', 'region'], axis=1)

all_data

all_data = all_data.rename(columns={"mo": "month"})
all_data

# replaces errors with nans


all_data.loc[43, 'area'] = pd.NA
all_data.loc[47, 'area'] = pd.NA
all_data.loc[47, 'extent'] = pd.NA
all_data.loc[48, 'area'] = pd.NA
all_data.loc[48, 'extent'] = pd.NA


# Uses linear interpolation to replace the nans
# This line replaces the errors currently set to use linear interpolation. To change, simply change `method=linear`


all_data.interpolate(method='linear', axis=0, limit=None, inplace=True)


# This new dataframe contains the yearly means for all columns


annual_means =  all_data.groupby(['year']).mean().drop(["month"], axis=1)


# This new dataframe contains the mean for each month across the years



month_means =  all_data.groupby(['month']).mean().drop(["year"], axis=1)



# This dataframe contains the data for each individual month, across all the years. For exaple all the Januaries across the recorded years


m_names = list(range(1,13))
m_data = []

for i in range(len(m_names)):
    appended = all_data.loc[lambda df: df['month'] == m_names[i]]
    m_data.append(appended)
    
single_month_data = dict(zip(m_names, m_data));


# Use this function to get the data for individual months. For example
# `month_getter(1)` will return all January data across all years


def month_getter(m):
    result = single_month_data[m].drop(["month"], axis=1)
    return result

# # Youssef Salaar Bridge

# This just changes some column and variable names so my preprocessed data works with salaars model


def YS_bridge(ydf):
    sdf = ydf.copy(deep=True).reset_index()
    sdf = sdf.rename(columns={'extent': 'extent_avg', 'area': 'area_avg', 'temp': 'temp_avg', 'methane': 'CH4_avg', 'CO2': 'CO2_avg'})
    
    return sdf

Processed_Dataset = YS_bridge(annual_means);