""" Estat targets data class

    Create a dataframe of desired values from tech toolbox
    .csv file. 

    Written by: Travis M. Moore
    Created: Nov. 28, 2022
    Last edited: Dec 23, 2022
"""

###########
# Imports #
###########
# Import GUI packages
import tkinter as tk
from tkinter import filedialog

# Import system packages
import os
from pathlib import Path

# Import data science packages
import numpy as np
import pandas as pd


#########
# BEGIN #
#########
class Estatmodel:
    def __init__(self, path=None):
        # Check for provided path
        if not path:
            # Show file dialog to get path
            root = tk.Tk()
            root.withdraw()
            path = filedialog.askdirectory()
            print(path)

        # Get list of files
        files = Path(path).glob('*.csv')
        files = list(files)

        # Grab files containing "CorrectCouplingVR" in the name
        self.files = []
        for file in files:
            if 'CorrectCouplingVR' in os.path.basename(file):
                self.files.append(file)

        # Create list of frequencies for indexing
        freqs = [200, 500, 800, 1000, 1500, 2000, 3000, 4000, 6000, 8000]
        self.freqs = [str(val) for val in freqs]

        # Automatically fetch data on instantiation
        print('-' * 60)
        print("e-STAT Data")
        print('-' * 60)
        self.get_targets()
        print('-' * 60 + '\n')


    def _get_rows_cols(self, df):
        """ Tech toolbox data export files are organized differently 
            based on form factor. This function assigns the header 
            row (-1) and starting target column by form factor. 
        """
        device_info = str(df.iloc[0,0])
        if "MicroRIC" in device_info:
            self.form_factor = "mRIC"
            self.header_row = 20
            self.target_col = 46
        elif " RIC" in device_info:
            self.form_factor = "RIC"
            self.header_row = 20
            self.target_col = 48
        elif "ITE" in device_info:
            self.form_factor = "ITE"
            self.header_row = 20
            self.target_col = 46
        elif "ITC" in device_info:
            self.form_factor = "ITC"
            self.header_row = 20
            self.target_col = 46
        elif "CIC" in device_info:
            self.form_factor = "CIC"
            self.header_row = 19
            self.target_col = 46
        elif "IIC" in device_info:
            self.form_factor = "IIC"
            self.header_row = 19
            self.target_col = 46
        else:
            self.form_factor = "OTHER"


    def get_targets(self):
        """ Create e-STAT prescribed targets dataframe
        """
        print("estatmodel: Fetching e-STAT targets...")
        df_list = []

        for file in self.files:
            # Read in .csv file as dataframe          
            df = pd.read_csv(file, header=None)

            # Get header row, starting target column, 
            # and form factor
            self._get_rows_cols(df)
        
            # Grab appropriate rows/columns from df
            # based on form factor
            vals_df = df.iloc[self.header_row-1:, :]

            # Set column headers
            names = list(vals_df.iloc[0])
            names[0] = 'freq'
            vals_df.columns = names
            vals_df = vals_df[1:]
        
            # Set frequencies as index
            vals_df = vals_df.set_index(['freq'])
            
            # Find column with second occurrence of Soft 50 Left
            targ_col = [i for i, value in enumerate(vals_df.columns) if value == "Soft Response 50 dB Speech (Left)"]
            if len(targ_col) != 3:
                print(f"\n\nWrong number of target columns for {file}")
            # Subset by desired target columns
            x = list(range(targ_col[1], targ_col[1]+6))
            vals_df = vals_df.iloc[:, x]
            # Rename columns
            vals_df.columns = ['L1', 'R1', 'L2', 'R2', 'L3', 'R3']
            # Subset by desired frequencies
            vals_df = vals_df.loc[self.freqs, :]

            # Convert freq index to column
            vals_df.reset_index(level=0, inplace=True)
            # Add filename column
            vals_df.insert(loc=0, column='filename', value=os.path.basename(file)[:-4])
            # Add form factor column
            vals_df.insert(loc=1, column='form_factor', value=self.form_factor)

            
            # Append df to list
            df_list.append(vals_df)

            ####################################
            # TEST: which columns have soft 50 #
            ####################################
            # print(f"\n{os.path.basename(file)}")
            # #print(vals_df.iloc[0])
            # x = [i for i, value in enumerate(vals_df.columns) if value == "Soft Response 50 dB Speech (Left)"]
            # print("Soft 50 Columns")
            # print(x)
            # print(f"Assigned column: {self.target_col}")
            ####################################

        self.estat_targets = pd.concat(df_list)
        self.estat_targets['form_factor'] = self.estat_targets['form_factor'].str.upper()
        print("estatmodel: Done!")


    def _to_long_format(self):
        self.estat_targets_long = pd.melt(self.estat_targets, 
            id_vars=['filename', 'form_factor', 'freq'], 
            value_vars=list(self.estat_targets.columns[3:]))

        self.estat_targets_long.rename(columns={
            'variable': 'level',
            'value': 'estat_target'
            }, 
            inplace=True
        )

        # Convert values to floats and round to one decimal place
        self.estat_targets_long['estat_target'] = np.round(self.estat_targets_long['estat_target'].astype(float), 1)
