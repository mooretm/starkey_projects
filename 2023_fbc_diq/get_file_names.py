""" Get all .wav file paths recursively. Copy all files to new directory.

    Written by: Travis M. Moore
    Created: 10/01/2023
    Last edited: 12/8/2023
"""

###########
# Imports #
###########
# Data science
import pandas as pd

# System
from pathlib import Path
import shutil
import os


#############
# Constants #
#############
path = r'C:\Users\MooTra\Code\Python\Projects\2023_fbc_diq\stimuli'


######################
# Impulse Recordings #
######################
# Matrix file for impulse recordings
files = Path(path + r'\HS_Impulses').rglob('*.wav')
files = [str(x) for x in files]
# Grab just the file name for creating a matrix file
file_names_only = []
for f in files:
    file_names_only.append(os.path.basename(f))
# Create dataframe
m1 = pd.DataFrame(file_names_only, columns=['audio_file'])
m1['pres_level'] = 76

# Write to file
m1.to_csv(path + r'\impulse_recordings\Matrix_Source_Files\matrix_impulses_all.csv', index=False)

# Copy/paste files from sub-folders into single folder
for file in files:
    name = os.path.basename(file)
    dst = path + os.sep + 'impulse_recordings' + os.sep + name
    shutil.copyfile(file, dst)


#####################
# Speech Recordings #
#####################
# Matrix file for impulse recordings
files = Path(path + r'\HS_Speech').rglob('*.wav')
files = [str(x) for x in files]
# Grab just the file name for creating a matrix file
file_names_only = []
for f in files:
    file_names_only.append(os.path.basename(f))
# Create dataframe
m2 = pd.DataFrame(file_names_only, columns=['audio_file'])
m2['pres_level'] = 76

# Write to file
m2.to_csv(path + r'\speech_recordings\Matrix_Source_Files\matrix_speech_all.csv', index=False)

# Copy/paste files from sub-folders into single folder
for file in files:
    name = os.path.basename(file)
    dst = path + os.sep + 'speech_recordings' + os.sep + name
    shutil.copyfile(file, dst)


#######################
# Training Recordings #
#######################
# Matrix file for IMPULSE recordings
files = Path(path + r'\HS_Impulses_Training').rglob('*.wav')
files = [str(x) for x in files]
# Grab just the file name for creating a matrix file
file_names_only = []
for f in files:
    file_names_only.append(os.path.basename(f))
# Create dataframe
m3 = pd.DataFrame(file_names_only, columns=['audio_file'])
m3['pres_level'] = 76
# The number of yes/no values are hard coded here; 
# Make sure this is accurate!
m3['expected_response'] = ['no'] * 5 + ['yes'] * 5
# Write to file
m3.to_csv(path + r'\impulse_recordings\Matrix_Source_Files\matrix_impulse_screening.csv', index=False)

# Matrix file for SPEECH recordings
files = Path(path + r'\HS_Speech_Training').rglob('*.wav')
files = [str(x) for x in files]
# Grab just the file name for creating a matrix file
file_names_only = []
for f in files:
    file_names_only.append(os.path.basename(f))
# Create dataframe
m4 = pd.DataFrame(file_names_only, columns=['audio_file'])
m4['pres_level'] = 76
# The number of yes/no values are hard coded here; 
# Make sure this is accurate!
m4['expected_response'] = ['no'] * 5 + ['yes'] * 5
# Write to file
m4.to_csv(path + r'\speech_recordings\Matrix_Source_Files\matrix_speech_screening.csv', index=False)
