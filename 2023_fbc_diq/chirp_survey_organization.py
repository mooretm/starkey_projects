""" Organize FBC DiQ raw survey data for 
    app version number 1.1.1.

    Written by: Travis M. Moore
    Last edited: Feb 16, 2024
"""

###########
# Imports #
###########
# Data science
import pandas as pd

# System
import os
import glob
from datetime import date, datetime


#############
# Constants #
#############
SUBJECT = 'P4245'
ORDER = 'm1_m2'
CHANGE_DATE = date(2024, 2, 1)
NUM_COLS = 8


_path = r'\\starfile\Public\Temp\MooreT\2023 FBC DiQ\Phone_Data'
_path = _path + '\\' + SUBJECT
ALL_FILES = glob.glob(os.path.join(_path, "*.csv"))

chirp_files = [file for file in ALL_FILES if os.path.basename(file).split('-')[0] == "Chirp"]

"""Chirp Survey Organization."""
# Create df and include extra rows to catch comments with 
# commas in them leading to multiple columns
df_list = []
for file in chirp_files:
    filename = os.path.basename(file)
    print(filename)

    # Read CSV
    temp = pd.read_csv(file, header=None, names=range(NUM_COLS))

    # Drop extra columns with all NaNs
    temp = temp.dropna(axis=1, how='all')

    # Get new number of columns
    cols = list(range(1, temp.shape[1]))

    # Join columns 1:end as strings
    temp['combined'] = temp[cols].apply(lambda row: '_'.join(row.values.astype(str)), axis=1)

    # Remove the resulting _nans
    temp['combined'] = temp['combined'].str.replace("_nan", '')

    # Move 'combined' column to position 1
    column_to_move = temp.pop('combined')
    temp.insert(1, 'response', column_to_move)

    # Drop old rows
    temp = temp.drop(temp.columns[range(2, temp.shape[1])], axis=1)

    # Transpose here!!!!!!
    temp = temp.T

    # Use first row as header
    temp.columns = temp.iloc[0]
    temp = temp[1:]

    # Update header names
    temp.columns = ['environment', 'objects', 'activity', 'rating']

    # Insert subject column
    temp.insert(loc=0, column='subject', value=SUBJECT)

    # Insert date/time/datetime columns from file name
    # Remove ".csv" extension
    vals = filename[:-4].split('-') 
    # Remove "Chirp"
    vals.pop(0) 
    # Convert to ints
    vals = [int(x) for x in vals] 
    # Insert date column
    temp['date'] = date(*vals[:3])
    # Insert time column
    #temp['time'] = time(*vals[3:])
    # Insert datetime column
    temp['date_time'] = datetime(*vals)

    df_list.append(temp)

data = pd.concat(df_list)
data.reset_index(drop=True, inplace=True)

# # Replace environment responses with integers
# keys = sorted(list(data['environment'].unique()))
# values = [3,2,1]
# environment_dict = {k:v for k,v in zip(keys, values)}
# print(environment_dict)
# for k, v in environment_dict.items():
#     mask = data['environment'] == k
#     data['environment'][mask] = environment_dict[k]

# Drop comments column
#data = data.drop('activity', axis=1)

# Truncate environment responses
for resp in data['environment'].unique():
    mask = data['environment'] == resp
    data['environment'][mask] = resp.split('(')[0]

# Truncate ratings
data['rating'] = data['rating'].str.replace(" annoying", "")

# Correct spelling of "extremely"
mask = data['rating'] == "Extreamly"
data['rating'][mask] = "Extremely"

# Add which memory was SUPPOSED to be selected
if ORDER == 'm1_m2':
    mask = data['date'] < CHANGE_DATE
    data['memory'] = 999
    data['memory'][mask] = "on"
    data['memory'][-mask] = "off"
elif ORDER == 'm2_m1':
    mask = data['date'] < CHANGE_DATE
    data['memory'] = 999
    data['memory'][mask] = "off"
    data['memory'][-mask] = "on" 

print(data)

data.to_csv(f'{SUBJECT}_chirp_survey.csv', index=False)
