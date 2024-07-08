""" Script to extract measured REUG from MedRx .csv files
    and plot the difference from a given average REUG.

    Jumana requested the REUG data and this seemed like
    a good place to store this script. Otherwise, unrelated
    to the other scripts in this directory.

    Written by: Travis Moore
    Created: 02/08/2023
    Last edited: 02/08/2023
"""

###########
# Imports #
###########
import numpy as np
import pandas as pd
import sklearn.metrics
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})
from pathlib import Path
import os


#################
# Organize Data #
#################
# Average REUG
AVG_REUG = [0, 2, 1, 3, 4, 7, 12, 15, 16, 17, 16, 15, 15, 14, 13, 12, 10, 7, 3, 3, 2, 2, 2, 2]

# Get list of files
_path = Path(r'\\starfile\Dept\Research and Development\HRT\Users\CR Studies\G23 Validation\REM Target Match')
files = _path.glob('*.csv')
files = list(files)

# Create a list of dataframes with columns: filename, freq, reug_measured
df_list = []
for file in files:
    df = pd.read_csv(file)
    df = df[['Frequency', 'Real ear unaided gain']]

    df.insert(loc=0, column='file_name', value=os.path.basename(file))
    #df[['file_name', 'rem_device', 'side', 'ha_style']] = df['file_name'].str.split('_', expand=True)
    #df = df[['file_name', 'rem_device', 'side', 'ha_style', 'Frequency', 'Real ear unaided gain']]
    #df['ha_style'] = df.iloc[0, 3][:-4]
    df.insert(loc=2, column='reug_avg', value=AVG_REUG)

    df.rename(columns={
        'Frequency': 'freq',
        'Real ear unaided gain': 'reug_measured',
        #'file_name': 'sub'
        },
        inplace=True
    )

    df_list.append(df)

# Row-wise concatenation
data = pd.concat(df_list, axis=0, ignore_index=False)
freqs = data['freq'].unique()
data.to_csv('REUG_Data.csv', index=False)
print(data)


#####################
# Create Empty Plot #
#####################
# Style and fonts
plt.style.use('seaborn-v0_8')
plt.rc('font', size=16)
plt.rc('axes', titlesize=14)
plt.rc('axes', labelsize=14)
plt.rc('xtick', labelsize=14)
plt.rc('ytick', labelsize=14)

# Create figure and axes
fig, axs = plt.subplots(nrows=1, ncols=1)

#plot_freqs = [200, "", "", 1100, "", "", 2000, "", "", 3000, "", "", "", 4200, "", "", "", "", 6300, "", "", 8100, "", 9400]
plot_freqs = [200, "", "", "", "", "", 2000, "", "", "", "", "", "", 4200, "", "", "", "", "", "", "", "", "", 9400]
# Create ticks and labels
#kHz = [x/1000 for x in freqs]
#for ii in [0, 2, 4, 6, 8]:
#    kHz[ii] = ""

axs.set(
    title="Measured REUG - Average REUG",
    ylabel="Deviation from Average (dB SPL)",
    xscale='log',
    xticks=freqs,
    xticklabels=plot_freqs,
    xlabel="Frequency (Hz)"
)
#plt.xticks(rotation=45)


#############
# Plot Data #
#############
# Plot individual difference
diffs = pd.DataFrame()
for record in data['file_name'].unique():
    reug = data[data['file_name']==record]['reug_measured']
    diff = reug - AVG_REUG
    diffs[record] = diff
    axs.plot(freqs, diff, lw=0.5)

# Plot grand average difference
axs.plot(freqs, diffs.mean(axis=1), color='blue', lw=4, label="Mean Difference")

# Plot RMSE
rmse_list = []
for f in freqs:
    temp = data[data['freq'] == f]
    mse = sklearn.metrics.mean_squared_error(
        temp['reug_measured'], 
        temp['reug_avg']
    )
    rmse = np.sqrt(mse)
    rmse_list.append(rmse)
axs.plot(freqs, rmse_list, 'ro', label="RMSE")
plt.legend()

# Add 0 line for reference
axs.axhline(y=0, color='k', lw=2)

plt.xscale='log'

plt.show()

