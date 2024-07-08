""" Verifit data class

    Extract and organze Verifit session .xml files.

    Extracts:
        1. Aided SII (NOTE: unaided SII not available from session file!)
        2. REM measured SPL values
        3. REM target SPL values

    Written by: Travis M. Moore
    Created: Nov. 17, 2022
    Last edited: Dec. 02, 2022
"""

###########
# Imports #
###########
# Import data science packages
import numpy as np
import pandas as pd
import xml.etree.ElementTree as ET

import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

# Import system packages
import os
from pathlib import Path

# Import GUI packages
import tkinter as tk
from tkinter import filedialog


class VerifitModel:
    def __init__(self, path=None, freqs=None):
        if not path:
            # Show file dialog to get path
            root = tk.Tk()
            root.withdraw()
            path = filedialog.askdirectory()
            print(path)

        files = Path(path).glob('*.xml')
        self.files = list(files)

        # Desired frequencies for index
        if freqs:
            self.desired_freqs = freqs
        else:
            self.desired_freqs = [250, 500, 750, 1000, 1500, 2000, 
                3000, 4000, 6000, 8000]

        # Automatically import all data upon instantiation
        self.get_all()
            

    def get_all(self):
        print('')
        print('-' * 50)
        print("Verifit Data")
        print('-' * 50)
        self.get_aided_sii()
        self.get_measured_spls()
        self.get_target_spls()
        self.get_diffs()
        print('-' * 50)
        print('')


    def write_to_csv(self):
        self.get_all()
        #self.all_data.sort_values(by='filename')
        self.aided_sii.to_csv('aided_sii.csv', index=False)
        self.target_spls.to_csv('target_spls.csv', index=False)
        self.measured_spls.to_csv('measured_spls.csv', index=False)
        print("verifitmodel: .csv files created successfully!\n")


    def _get_root(self, file):
        # Get XML tree structure and root
        tree = ET.parse(file)
        self.root = tree.getroot()
        
        # Get tag with 12th-octave frequency list
        freqs = self.root.find("./test[@name='frequencies']/data[@name='12ths']").text
        freqs = freqs.split()
        self.twelfth_oct_freqs = [int(float(freq)) for freq in freqs]

        # Get tag with 12th-octave frequency list
        freqs = self.root.find("./test[@name='frequencies']/data[@name='audiometric']").text
        freqs = freqs.split()
        audiometric_freqs = [int(float(freq)) for freq in freqs]
        self.audiometric_freqs = audiometric_freqs[:-2]

        # Get file name
        filename = os.path.basename(file)
        self.filename = filename[:-4]


    ####################
    # AIDED SII VALUES #
    ####################
    # NOTE: Verifit session file does not include unaided SII!
    def get_aided_sii(self):
        print("verifitmodel: Fetching aided SII data...")
        sii_list = []
        sii_dict = {}

        for file in self.files:
            self._get_root(file)

            try:
            # Left
                sii_dict['sii_L1'] = float(self.root.find("./test[@side='left']/data[@internal='map_rear_sii1']").text)
                sii_dict['sii_L2'] = float(self.root.find("./test[@side='left']/data[@internal='map_rear_sii2']").text)
                sii_dict['sii_L3'] = float(self.root.find("./test[@side='left']/data[@internal='map_rear_sii3']").text)
                #sii_dict['sii_L4'] = float(self.root.find("./test[@side='left']/data[@internal='map_rear_sii4']").text)
                # Right
                sii_dict['sii_R1'] = float(self.root.find("./test[@side='right']/data[@internal='map_rear_sii1']").text)
                sii_dict['sii_R2'] = float(self.root.find("./test[@side='right']/data[@internal='map_rear_sii2']").text)
                sii_dict['sii_R3'] = float(self.root.find("./test[@side='right']/data[@internal='map_rear_sii3']").text)
                #sii_dict['sii_R4'] = float(self.root.find("./test[@side='right']/data[@internal='map_rear_sii4']").text)
            except AttributeError:
                print(f"\n{self.filename} is missing data! Aborting!\n")
                exit()

            sii_list.append(pd.DataFrame(sii_dict, index=[str(self.filename)]))

        aided_sii = pd.concat(sii_list)
        aided_sii.reset_index(inplace=True)
        self.aided_sii = aided_sii.rename(columns={'index':'filename'})

        print("verifitmodel: Completed!\n")


    #######################
    # MEASURED SPL VALUES #
    #######################
    def get_measured_spls(self):
        print("verifitmodel: Fetching measured SPL data...")
        spls_list = []

        for file in self.files:
            self._get_root(file)

            spls_dict = {}

            # Measured SPL REM values
            try:
                # Left MEASURED spls
                spls_dict['spl_L1'] = self.root.find("./test[@side='left']/data[@internal='map_rearspl1']").text
                spls_dict['spl_L2'] = self.root.find("./test[@side='left']/data[@internal='map_rearspl2']").text
                spls_dict['spl_L3'] = self.root.find("./test[@side='left']/data[@internal='map_rearspl3']").text
                # Right MEASURED spls
                spls_dict['spl_R1'] = self.root.find("./test[@side='right']/data[@internal='map_rearspl1']").text
                spls_dict['spl_R2'] = self.root.find("./test[@side='right']/data[@internal='map_rearspl2']").text
                spls_dict['spl_R3'] = self.root.find("./test[@side='right']/data[@internal='map_rearspl3']").text
            except AttributeError:
                print(f"\n{self.filename} is missing MEASURED REM data! Aborting!\n")
                exit()

            # Split numbers into list
            for key in spls_dict:
                spls_dict[key] = spls_dict[key].split()
                spls_dict[key] = [float(x) for x in spls_dict[key]]

            df = pd.DataFrame(spls_dict, index=self.twelfth_oct_freqs)
            # Get only specified frequencies
            df = df.loc[self.desired_freqs]
            df.reset_index(inplace=True)
            df = df.rename(columns={'index':'freq'})
            df.insert(loc=0, column='filename', value=self.filename)

            spls_list.append(df)
        
        self.measured_spls = pd.concat(spls_list)
        
        print("verifitmodel: Completed!\n")


    #####################
    # TARGET SPL VALUES #
    #####################
    def get_target_spls(self):
        print("verifitmodel: Fetching target SPL data...")
        target_list = []

        for file in self.files:
            self._get_root(file)
            
            target_dict = {}

            # TARGET spl values
            try:
                # Left TARGET spls
                target_dict['target_L1'] = self.root.find("./test[@side='left']/data[@internal='map_rear_targetspl1']").text
                target_dict['target_L2'] = self.root.find("./test[@side='left']/data[@internal='map_rear_targetspl2']").text
                target_dict['target_L3'] = self.root.find("./test[@side='left']/data[@internal='map_rear_targetspl3']").text
                # Right TARGET spls
                target_dict['target_R1'] = self.root.find("./test[@side='right']/data[@internal='map_rear_targetspl1']").text
                target_dict['target_R2'] = self.root.find("./test[@side='right']/data[@internal='map_rear_targetspl2']").text
                target_dict['target_R3'] = self.root.find("./test[@side='right']/data[@internal='map_rear_targetspl3']").text
            except AttributeError:
                print(f"\n{self.filename} is missing TARGET REM data! Aborting!\n")
                exit()

            # Split numbers into list
            for key in target_dict:
                target_dict[key] = target_dict[key].split()
                # There aren't targets above 8 kHz, just an underscore
                target_dict[key] = [x for x in target_dict[key] if x != '_']
                target_dict[key] = [float(x) for x in target_dict[key]]

            # Targets are only provided at audiometric frequencies,
            # not the full 12th octave list. Here we are just labeling
            # the frequencies, not selecting like with measured SPLs
            df = pd.DataFrame(target_dict, index=self.audiometric_freqs)
            df.reset_index(inplace=True)
            df = df.rename(columns={'index':'freq'})
            df.insert(loc=0, column='filename', value = self.filename)
            
            target_list.append(df)
        
        self.target_spls = pd.concat(target_list)

        print("verifitmodel: Completed!\n")


    ###############################
    # Data Organization Functions #
    ###############################
    def _to_long_format(self):
        """ Create a wide format dataframe for each measure
        """
        self.aided_sii_long = pd.melt(
            self.aided_sii,
            id_vars=['filename'],
            value_vars=list(self.aided_sii.columns[1:])
        )
        self.measured_spls_long = pd.melt(
            self.measured_spls,
            id_vars=['filename', 'freq'], 
            value_vars=list(self.measured_spls.columns[1:])
        )
        self.target_spls_long = pd.melt(
            self.target_spls,
            id_vars=['filename', 'freq'], 
            value_vars=list(self.target_spls.columns[1:])
        )

    
    def get_diffs(self):
        """ Create a new dataframe with target and measured spls as 
            columns. Include a columns of differences.
        """
        # Transform dataframe to long format
        self._to_long_format()

        # Create new dataframe of diffs
        y = pd.DataFrame(self.measured_spls_long[['filename', 'freq']])
        levels = [x.split('_')[1] for x in self.measured_spls_long['variable']]
        y['level'] = levels
        y['targets'] = self.target_spls_long[['value']]
        y['measured'] = self.measured_spls_long[['value']]
        y['measured-target'] = y['measured'] - y['targets']
        self.diffs = y.copy()


    ######################
    # Plotting Functions #
    ######################
    def _set_up_plot(self):
        """ Create empty plotting space for measured-target diffs
        """
        # Set style
        plt.style.use('seaborn-v0_8')

        # Create tick labels
        kHz = [x/1000 for x in self.desired_freqs]
        for ii in [0, 2, 4, 6, 8]:
            kHz[ii] = ""

        self.fig, self.axs = plt.subplots(nrows=3, ncols=2)

        for pair in self.axs:
            for ax in pair:
                ax.set(
                    xticks=self.desired_freqs,
                    xticklabels=kHz)

        self.axs[0,0].set(
            title="Soft (50 dB SPL): Left",
            ylabel="Difference (Measured - Target)",
            )
        self.axs[1,0].set(
            title="Average (60 dB SPL): Left",
            ylabel="Difference (Measured - Target)",
        )
        self.axs[2,0].set(
            title="Loud (80 dB SPL): Left",
            ylabel="Difference (Measured - Target)",
            xlabel="Frequency (kHz)"
        )

        self.axs[0,1].set(title="Soft (50 dB SPL): Right")
        self.axs[1,1].set(title="Average (60 dB SPL): Right")
        self.axs[2,1].set(title="Loud (80 dB SPL): Right", xlabel="Frequency (kHz)")


    def plot_diffs(self, title=None):
        """ Plot the individual differences between measured and 
            target SPLs
        """
        self._set_up_plot()
        if not title:
            self.fig.suptitle('Measured SPLs - NAL-NL2 Target SPLs')
        else:
            self.fig.suptitle(title)

        # Plot the individual data
        for file in self.diffs['filename'].unique():
            for ii in range(1,4):
                temp = self.diffs[(self.diffs['filename']==file) & (self.diffs['level']=='L' + str(ii))]
                self.axs[ii-1,0].plot(temp['freq'], temp['measured-target'])
                self.axs[ii-1,0].axhline(y=0, color='k')
                self.axs[ii-1,0].set_ylim(
                    np.min(self.diffs['measured-target']+(-5)),
                    np.max(self.diffs['measured-target']+5)
                ) 

                temp = self.diffs[(self.diffs['filename']==file) & (self.diffs['level']=='R' + str(ii))]
                self.axs[ii-1,1].plot(temp['freq'], temp['measured-target'])
                self.axs[ii-1,1].axhline(y=0, color='k')
                self.axs[ii-1,1].set_ylim(
                    np.min(self.diffs['measured-target']+(-5)),
                    np.max(self.diffs['measured-target']+5)
                )
            
        # Calculate and plot grand average curve for each level
        # Get values at all freqs for a single level
        for ii in range(1,4):
                # Filter diffs by level
                temp = self.diffs[self.diffs['level']=='L' + str(ii)]
                vals_by_freq = temp.groupby(['freq'])['measured-target'].mean()
                self.axs[ii-1,0].plot(temp['freq'].unique(), vals_by_freq, 'ko')

                temp = self.diffs[self.diffs['level']=='R' + str(ii)]
                vals_by_freq = temp.groupby(['freq'])['measured-target'].mean()
                self.axs[ii-1,1].plot(temp['freq'].unique(), vals_by_freq, 'ko')

        plt.show()
