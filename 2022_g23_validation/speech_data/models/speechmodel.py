""" Class for analyzing data from the Speech Task Controller

    Gather all data, organize, analyze, plot.

    Written by: Travis M. Moore
    Created: Dec 06, 2022
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

import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})


#########
# BEGIN #
#########
class SpeechModel:
    def __init__(self, path=None):
        """ Import all data files as single dataframe
        """
        if not path:
            # Show file dialog to get path
            root = tk.Tk()
            root.withdraw()
            path = filedialog.askdirectory()
            print(f"Path of selected folder: {path}")

        # Get list of file paths
        files = Path(path).glob('*.csv')
        self.files = list(files)

        # List for catching outliers in func: get_outliers()
        # Putting it here so it doesn't reset when plot funcs
        # are called multiple times
        self.outliers = []


    ###########################
    # Data Organization Funcs #
    ###########################
    def words_to_percent(self, num):
        return (num / 5) * 100


    def organize_data(self):
        """ Prepare data for use
        """
        print('')
        print('-' * 60)
        print("speechmodel: Organizing data...")
        #print(f"Number of files: {len(self.files)}")
        df = pd.concat((pd.read_csv(f) for f in self.files), 
            ignore_index=True)

        df[['environment', 'condition', 'form_factor']] = df['Condition'].str.split('_', expand=True)
        df = df[['Subject', 'environment', 'condition', 'form_factor', 'new_db_lvl', 'Num Words Correct', 'Outcome']]
        df.rename(columns={
            'Subject': 'sub', 
            'new_db_lvl': 'level', 
            'Num Words Correct': 'word_pc',
            'Outcome': 'sentence_pc'},
            inplace=True)

        # Convert number of words to percent
        df['word_pc'] = df['word_pc'].apply(self.words_to_percent)

        # Remove 'P' from subject IDs and convert to int
        sub_list = list(df['sub'])
        for ii, sub in enumerate(sub_list):
            if isinstance(sub, str):
                try:
                    sub_list[ii] = int(sub[1:])
                except:
                    print(f"Subject: {sub}; First char: {sub[0]}")
        df['sub'] = sub_list

        # Make all form factors uppercase
        df['form_factor'] = df['form_factor'].str.upper()

        # Change 'aidednroff' to 'omnioff'
        bools = df['condition']=='aidednroff'
        df.loc[bools,'condition'] = 'omnioff'

        # Drop SNR50
        bools = df['condition'] == 'snr50'
        df = df[~bools]

        # Drop subject P2050
        sub_bools = df['sub'] == 2050
        df = df[~sub_bools]

        # Get list of all conditions
        self.conditions = df['condition'].unique()
        self.conditions.sort()

        self.data = df.copy()

        print("speechmodel: Complete!")
        print('-' * 60)
        print('')


    def _to_wide_format(self, data, title=None):
        df = data.copy()
        df.reset_index(inplace=True)
        df = df.pivot(index=['sub', 'environment', 'form_factor'], 
            columns='condition', values=['sentence_pc', 'word_pc'])
        df.reset_index(inplace=True)
        df.sort_values(by=['environment', 'form_factor'], 
            ascending=[False, False],inplace=True)

        if not title:
            title = 'wide_format.csv'    
        df.to_csv('./G23 Speech Data/' + title, index=False)


    def get_ind_means(self):
        # Group by sub/env/cond and get individual means
        self.ind_means = self.data.groupby(['sub', 'environment', 'condition', 'form_factor']).mean()
        # Convert percent from decimal
        self.ind_means.loc[:, 'sentence_pc'] = np.round(self.ind_means.loc[:, 'sentence_pc'] * 100, 2)


    def get_group_means(self):
        self.get_ind_means()
        self.group_means = self.ind_means.groupby(['environment', 'condition', 'form_factor']).mean()
        self.group_sds = self.ind_means.groupby(['environment', 'condition', 'form_factor']).apply(np.std)


    def find_outliers(self, df, boxdata, conds):
        self.boxdata = boxdata
               
        # Get outliers per condition
        fliers = []
        for ii, item in enumerate(self.boxdata['fliers']):
            vals = item.get_data()[1]
            fliers.append(vals)

        # Get index of outlier values
        for ii in range(0, len(conds)):
            #print(f"{conds[ii]}: {fliers[ii]}")
            for outlier in fliers[ii]:
                #print(f"Outlier: {outlier}")
                bools = df.index.get_level_values('condition')==conds[ii]
                temp = df[bools]
                #print(temp)
                idx = np.where(temp==outlier)[0]
                #print(idx)
                
                # Multiple subjects with the same outlier value
                # must be separated manually and appended to 
                # outlier list
                # if len(idx) > 1:
                #     for val in idx:
                #         sub='MULTIPLE'
                #         print(f"Duplicate outlier data type: {type(temp.index[idx])}")
                #         self.outliers.append(temp.index[val])
                #         #self.outliers.append(list(temp.index[val]))
                #         print(temp.index[val])
                # else:
                #     sub = temp.index[idx][0]
                #     print(f"Typical outlier data type: {type(temp.index[idx])}")
                #     self.outliers.append(temp.index[idx])
                #     #self.outliers.append(list(temp.index[idx]))
                #     print(temp.index[idx])


                sub = temp.index[idx][0]
                #print(f"Typical outlier data type: {type(temp.index[idx])}")
                self.outliers.append(temp.index[idx])
                #self.outliers.append(list(temp.index[idx]))
                #print(temp.index[idx])

                #print(f"Value of {outlier} is an outlier for subject {sub} at index {idx}")

        #print(self.outliers)
        #self.outliers.to_csv('./G23 Speech Data/outliers.csv')


    def remove_outliers(self, df, show=None, save=None):
        self.clean = df.copy()

        print('')
        print('-'*60)
        print('speechmodel: Removing outliers...\n')

        # # Remove duplicates from outlier list
        # # Occurrs from calling the plotting function multiple times
        # res = []
        # [res.append(x) for x in self.outliers if x not in res]
        # self.outliers = res

        # # Drop outlier rows
        # for outlier_row in self.outliers:
        #     self.clean.drop(outlier_row, inplace=True)
        # #return df.drop(self.outliers)
        # print(f"speechmodel: Cleaned df length: {len(self.clean)}")

        # Drop outlier rows
        dups = []
        for outlier in self.outliers:
            try:
                self.clean.drop(outlier, inplace=True)
            except:
                dups.append(list(outlier))
                #print("Duplicate outlier found!")
                print(list(outlier))
                #pass

        #print("")
        print(f"\nspeechmodel: Number of outliers found: {len(self.outliers)}")
        print(f"speechmodel: Number of duplicate outliers found: {len(dups)}")
        print(f"speechmodel: Unique outliers: {len(self.outliers) - len(dups)}")
        print(f"speechmodel: Length of uncleaned data: {len(df)}")
        print(f"speechmodel: Cleaned df length: {len(self.clean)}")
        print("speechmodel: NOTE: the difference between the clean and " +
            "raw data lengths may differ slightly due to multiple " +
            "outliers in a single list element.")

        # Print to console
        if show:
            for ii in range(0, len(self.outliers)):
                print(list(self.outliers[ii]))

        if save:
            #self.clean.to_csv('./G23 Speech Data/clean_sub_means.csv')
            pd.DataFrame(self.outliers).to_csv('./G23 Speech Data/outliers.csv')

        print('speechmodel: Complete!')
        print('-'*60)
        print('')


    def collapse_form_factors(self, data):
        # Make copy of provided dataframe
        self.collapsed = data.copy()

        # Get current form factor index values
        current_index_vals = self.collapsed.index.get_level_values('form_factor')
        
        # Create list of new index vals
        new_index_vals = []
        for val in current_index_vals:
            if val == 'RIC':
                new_index_vals.append('RIC')
            elif val == 'MRIC':
                new_index_vals.append('RIC')
            elif val == 'ITC':
                new_index_vals.append('Custom')
            elif val == 'ITE':
                new_index_vals.append('Custom')
            elif val == 'CIC':
                new_index_vals.append('Wired')
            elif val == 'IIC':
                new_index_vals.append('Wired')
            else: 
                print('Invalid form factor!!')
                return

        # Replace old index vals with new index vals
        # Drop original form factor index column
        self.collapsed.index = self.collapsed.index.droplevel(3)
        # Add new form factors values as index
        self.collapsed = self.collapsed.assign(form_factor=new_index_vals).set_index('form_factor', append=True).copy()
        #self.collapsed.drop('level', axis=1, inplace=True)
        #temp = self.collapsed.copy()
        #temp.reset_index(inplace=True)
        self.collapsed.to_csv('./G23 Speech Data/collapsed_speech_data.csv')


    def final_plot_format(self, data):
        d = data.copy()
        d.reset_index(inplace=True)

        for ii in range(0, len(d)):
            # Form factors
            if d.iloc[ii, 3] == 'Wired':
                d.iloc[ii, 3] = 'Wired Custom'
            elif d.iloc[ii, 3] == 'Custom':
                d.iloc[ii, 3] = 'Wireless Custom'

            # Conditions
            if (d.iloc[ii, 2] == 'aided') and (d.iloc[ii, 1]=='n') and (d.iloc[ii, 3] != 'Wired Custom'):
                d.iloc[ii, 2] = 'NR On + Dir'
            elif (d.iloc[ii, 2] == 'aided') and (d.iloc[ii, 1]=='n') and (d.iloc[ii, 3] == 'Wired Custom'):
                d.iloc[ii, 2] = 'NR On + Omni'
            elif (d.iloc[ii, 2] == 'aided') and (d.iloc[ii, 1]=='q'):
                d.iloc[ii, 2] = 'Aided'
            elif d.iloc[ii, 2] == 'unaided':
                d.iloc[ii, 2] = 'Unaided'
            elif d.iloc[ii, 2] == 'omnioff':
                d.iloc[ii, 2] = 'NR Off + Omni'
            elif d.iloc[ii, 2] == 'omnion':
                d.iloc[ii, 2] = 'NR On + Omni'
            elif (d.iloc[ii, 2] == 'embs') and (d.iloc[ii, 1]=='n'):
                d.iloc[ii, 2] = 'Edge Mode'
            elif (d.iloc[ii, 2] == 'embs') and (d.iloc[ii, 1]=='q'):
                d.iloc[ii, 2] = 'EM - Best Sound'
            elif (d.iloc[ii, 2] == 'emes') and (d.iloc[ii, 1]=='n'):
                d.iloc[ii, 2] = 'Edge Mode'
            elif (d.iloc[ii, 2] == 'emes') and (d.iloc[ii, 1]=='q'):
                d.iloc[ii, 2] = 'EM - Enhanced Speech'
 
        d.set_index(['sub', 'environment', 'condition', 'form_factor'], inplace=True)
        return d


    ##################
    # Plotting Funcs #
    ##################
    def multi_barplot(self, form_factors, show=None, save=None):
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

        # Get INDIVIDUAL mean outcome values
        #self.get_ind_means()

        X = np.arange(len(self.conditions))
        X = X * 3

        # Create dict of data by form factor
        self.form_dict = {}
        for form in form_factors:
            # Subset data by specified form factor
            bools = self.ind_means.index.get_level_values('form_factor') == form
            # Get GROUP mean outcome values
            temp = self.ind_means[bools].groupby(['environment', 'condition']).mean()
            self.form_dict[form] = temp

        # Multi-barplot
        plt.style.use('seaborn-v0_8')
        fig, axs = plt.subplots(nrows=2, ncols=1)
        fig.suptitle(f"Word Recognition Scores for All Form Factors")
        
        # QUIET data
        self.data_dict = {}
        for ii, form in enumerate(form_factors):
            quiet = self.form_dict[form].loc['q']
            quiet.reset_index(inplace=True)
            missing = list(set(self.conditions) - set(quiet['condition']))
            if missing:
                for miss in missing:
                    quiet.loc[len(quiet.index)] = [miss, 1, 1, 1]
            quiet.sort_values(by=['condition'], inplace=True)

            self.data_dict[form] = quiet

        offset = 0.4
        for form in (form_factors):
            print(f"\nQuiet: {form}")
            print(self.data_dict[form])
            axs[0].bar(X+offset, self.data_dict[form]['sentence_pc'], width=0.4)
            axs[0].set_title('Quiet')
            offset = offset + 0.4

        # NOISE data
        for ii, form in enumerate(form_factors):
            try:
                noise = self.form_dict[form].loc['n']
                noise.reset_index(inplace=True)
            except KeyError:
                    missing_dict = {
                        'condition': ['aided', 'emes', 'embs', 'omnioff', 'omnion', 'unaided'],
                        'level': np.repeat(1,6),
                        'words_correct': np.repeat(1,6),
                        'sentence_pc': np.repeat(1,6)
                    }
                    noise = pd.DataFrame(missing_dict)

            missing = list(set(self.conditions) - set(noise['condition']))
            if missing:
                for miss in missing:
                    noise.loc[len(noise.index)] = [miss, 1, 1, 1]
            noise.sort_values(by=['condition'], inplace=True)

            self.data_dict[form] = noise

        offset = 0.4
        for form in (form_factors):
            print(f"\nNoise: {form}")
            print(self.data_dict[form])
            axs[1].bar(X+offset, self.data_dict[form]['sentence_pc'], width=0.4)
            axs[1].set_title('Noise')
            offset = offset + 0.4

        # Axis info for both plots
        for ii in [0, 1]:
            axs[ii].set_xticks(X+1.4, self.conditions)
            axs[ii].set_yticks(np.arange(0,110,10))
            axs[ii].set(
                xlabel='Condition',
                ylabel='Percent Correct',
                ylim=(0,100),
                xlim=(0,20))
            axs[ii].legend(form_factors, loc='upper right')

        # Save figure
        if save:
            plt.savefig("./G23 Speech Data/ALL.png")

        # Show plot
        if show:
            plt.show()


    def single_env_boxplot(self, data, form_factor, env, data_col, show=None, save=None, **kwargs):
        """ Make boxplots for a single form factor, all conditions.
        """
        # Set up figure
        plt.style.use('seaborn-v0_8')
        
        plt.rc('font', size=12)
        plt.rc('axes', titlesize=12)
        plt.rc('axes', labelsize=12)
        plt.rc('xtick', labelsize=12)
        plt.rc('ytick', labelsize=12)

        fig, axs = plt.subplots(nrows=1, ncols=1)


        #########
        # QUIET #
        #########
        if env == 'q':
            try:
                # Custom sort group means
                quiet_means = data.loc[(slice(None), ['q'], slice(None), [form_factor]), [data_col]]
                quiet_xlabs = kwargs.get('quiet_xlabs', quiet_means.index.get_level_values('condition'))
                quiet_means = quiet_means.iloc[pd.Categorical(quiet_means.index.get_level_values('condition'), quiet_xlabs).argsort()]
                
                fig.suptitle(f"Word Recognition Scores for {form_factor} Group (n$\u2248${len(quiet_means.index.get_level_values('sub').unique())})")

                # Put data into list for boxplot with matplotlib (_)
                conds = list(quiet_means.index.get_level_values('condition').unique())
                quiet = []
                for cond in conds:
                    x = quiet_means.loc[(slice(None), slice(None), [cond], slice(None))][data_col]
                    quiet.append(x)

                # Plot data
                qboxdata = axs.boxplot(quiet, labels=conds)

                self.find_outliers(quiet_means, qboxdata, conds)

                #axs.set(title=f"Quiet ({data_col})", ylabel="Percent Correct", ylim=(-5,105))
                axs.set(title="Quiet", ylabel="Percent Correct", ylim=(-5,105))
                axs.title.set_size(14)
            except KeyError:
                print(f"speechmodel: Missing quiet data for {form_factor}; skipping!")
                axs.set(title=f"Quiet")

        #########
        # NOISE #
        #########
        if env == 'n':
            try:
                # Custom sort
                noise_means = data.loc[(slice(None), ['n'], slice(None), [form_factor]), [data_col]]
                noise_xlabs = kwargs.get('noise_xlabs', noise_means.index.get_level_values('condition'))
                noise_means = noise_means.iloc[pd.Categorical(noise_means.index.get_level_values('condition'), noise_xlabs).argsort()]
                #print(f"\nIndividual Means:\n{noise_means}")

                fig.suptitle(f"Word Recognition Scores for {form_factor} Group (n$\u2248${len(noise_means.index.get_level_values('sub').unique())})")

                # Put data into list for boxplot with matplotlib (_)
                conds = list(noise_means.index.get_level_values('condition').unique())
                noise = []
                for cond in conds:
                    x = noise_means.loc[(slice(None), slice(None), [cond], slice(None))][data_col]
                    noise.append(x)

                # Plot data
                nboxdata = axs.boxplot(noise, labels=conds)

                self.find_outliers(noise_means, nboxdata, conds)

                #axs.set(title=f"Noise ({data_col})", ylim=(-5, 105),
                axs.set(title=f"Noise", ylim=(-5, 105),
                    #ylabel="Percent Correct", xlabel="Condition")
                    ylabel="Percent Correct")
                axs.title.set_size(14)
            except KeyError:
                print(f"speechmodel: Missing noise data for {form_factor}; skipping!")
                axs.set(title=f"Noise")

        # Save figure
        if save:
            plt.savefig(f"./G23 Speech Data/{form_factor}_{env}_{data_col}.png")

        # Display figure
        if show:
            plt.show()      

        plt.close()


    def single_device_boxplot(self, data, form_factor, data_col, show=None, save=None, **kwargs):
        """ Make barplot with error bars for a single form factor, 
            all conditions.
        """

        # Set up figure
        plt.style.use('seaborn-v0_8')
        fig, axs = plt.subplots(nrows=2, ncols=1)
        fig.suptitle(f"Word Recognition Scores for {form_factor} Group ({data_col})")

        #########
        # QUIET #
        #########
        try:
            # Custom sort group means
            quiet_means = data.loc[(slice(None), ['q'], slice(None), [form_factor]), [data_col]]
            quiet_xlabs = kwargs.get('quiet_xlabs', quiet_means.index.get_level_values('condition'))
            quiet_means = quiet_means.iloc[pd.Categorical(quiet_means.index.get_level_values('condition'), quiet_xlabs).argsort()]
            
            # Put data into list for boxplot with matplotlib (_)
            conds = list(quiet_means.index.get_level_values('condition').unique())
            quiet = []
            for cond in conds:
                x = quiet_means.loc[(slice(None), slice(None), [cond], slice(None))][data_col]
                quiet.append(x)

            # Plot data
            qboxdata = axs[0].boxplot(quiet, labels=conds)

            self.find_outliers(quiet_means, qboxdata, conds)

            axs[0].set(title=f"{form_factor}: Quiet", ylabel="Percent Correct", ylim=(-5,105))
        except KeyError:
            print(f"speechmodel: Missing quiet data for {form_factor}; skipping!")
            axs[0].set(title=f"{form_factor}: Quiet")

        #########
        # NOISE #
        #########
        try:
            # Custom sort
            noise_means = data.loc[(slice(None), ['n'], slice(None), [form_factor]), [data_col]]
            noise_xlabs = kwargs.get('noise_xlabs', noise_means.index.get_level_values('condition'))
            noise_means = noise_means.iloc[pd.Categorical(noise_means.index.get_level_values('condition'), noise_xlabs).argsort()]
            #print(f"\nIndividual Means:\n{noise_means}")

            # Put data into list for boxplot with matplotlib (_)
            conds = list(noise_means.index.get_level_values('condition').unique())
            noise = []
            for cond in conds:
                x = noise_means.loc[(slice(None), slice(None), [cond], slice(None))][data_col]
                noise.append(x)

            # Plot data
            nboxdata = axs[1].boxplot(noise, labels=conds)

            self.find_outliers(noise_means, nboxdata, conds)

            axs[1].set(title=f"{form_factor}: Noise", ylim=(-5, 105),
                ylabel="Percent Correct", xlabel="Condition")
        except KeyError:
            print(f"speechmodel: Missing noise data for {form_factor}; skipping!")
            axs[1].set(title=f"{form_factor}: Noise")

        # Save figure
        if save:
            plt.savefig(f"./G23 Speech Data/{form_factor}_{data_col}.png")

        # Display figure
        if show:
            plt.show()      

        plt.close()


    def single_device_barplot(self, form_factor, data_col, show=None, save=None, **kwargs):
        """ Make barplot with error bars for a single form factor, 
            all conditions.
        """
        # Get data
        self.get_group_means()
        
        # Set up figure
        plt.style.use('seaborn-v0_8')
        fig, axs = plt.subplots(nrows=2, ncols=1)
        fig.suptitle(f"Word Recognition Scores for {form_factor.upper()} Group ({data_col})")

        #########
        # QUIET #
        #########
        try:
            # Custom sort group means
            quiet_means = self.group_means.loc[(['q'], slice(None), [form_factor]), [data_col]]
            quiet_sds = self.group_sds.loc[(['q'], slice(None), [form_factor]), [data_col]]
            quiet_xlabs = kwargs.get('quiet_xlabs', quiet_means.index.get_level_values('condition'))
            quiet_means = quiet_means.iloc[pd.Categorical(quiet_means.index.get_level_values('condition'), quiet_xlabs).argsort()]
            quiet_sds = quiet_sds.iloc[pd.Categorical(quiet_sds.index.get_level_values('condition'), quiet_xlabs).argsort()]
            print(f"Group Means:\n{quiet_means}")
            print(f"Group SD:\n{quiet_sds}")

            # Plot data
            axs[0].bar(quiet_means.index.get_level_values('condition'), 
                quiet_means[data_col])
            axs[0].set(title="Quiet", ylim=(0,115), ylabel="Percent Correct")
            # Plot error bars
            axs[0].errorbar(
                quiet_means.index.get_level_values('condition'), 
                quiet_means[data_col],
                yerr=quiet_sds[data_col],
                fmt='o',
                color='k'
            )
        except KeyError:
            print(f"speechmodel: Missing quiet data for {form_factor}; skipping!")
            axs[0].set(title="Quiet", ylim=(0,100))

        #########
        # NOISE #
        #########
        try:
            # Custom sort
            noise_means = self.group_means.loc[(['n'], slice(None), [form_factor]), [data_col]]
            noise_sds = self.group_sds.loc[(['n'], slice(None), [form_factor]), [data_col]]
            noise_xlabs = kwargs.get('noise_xlabs', noise_means.index.get_level_values('condition'))
            noise_means = noise_means.iloc[pd.Categorical(noise_means.index.get_level_values('condition'), noise_xlabs).argsort()]
            noise_sds = noise_sds.iloc[pd.Categorical(noise_sds.index.get_level_values('condition'), noise_xlabs).argsort()]
            print(f"Group Means:\n{noise_means}")
            print(f"Group SD:\n{noise_sds}")

            # Plot data
            axs[1].bar(noise_means.index.get_level_values('condition'), 
                noise_means[data_col])
            axs[1].set(title="Noise", ylim=(0,115), 
                ylabel="Percent Correct", xlabel="Condition")
            # Plot error bars
            axs[1].errorbar(
                noise_means.index.get_level_values('condition'), 
                noise_means[data_col],
                yerr=noise_sds[data_col],
                fmt='o',
                color='k'
            )
        except KeyError:
            print(f"speechmodel: Missing noise data for {form_factor}; skipping!")
            axs[1].set(title="Noise", ylim=(0,100))

        # Save figure
        if save:
            plt.savefig(f"./G23 Speech Data/{form_factor}_{data_col}.png")

        # Display figure
        if show:
            plt.show()
        

    def single_barplot_OLD(self, form_factor, show=None, save=None, **kwargs):
        # Get INDIVIDUAL mean outcome values
        self.get_ind_means()
        # Subset data by specified form factor
        bools = self.ind_means.index.get_level_values('form_factor') == form_factor
        # Get GROUP mean outcome values
        self.form = self.ind_means[bools].groupby(['environment', 'condition']).mean()

        # Get quiet environment values
        try:
            quiet = self.form.loc['q']
            #print(f"Quiet: {form_factor}")
            #print(quiet)
            quiet_xlabs = kwargs.get('quiet_xlabs', quiet.index.get_level_values('condition'))
            quiet = quiet.iloc[pd.Categorical(quiet.index, quiet_xlabs).argsort()]
            print(f"Quiet: {form_factor}")
            print(quiet)
        except KeyError as e:
            print(f"speechmodel: Missing value: {e}")

        # Get noise environment values
        try:    
            noise = self.form.loc['n']
            noise_xlabs = kwargs.get('noise_xlabs', quiet.index.get_level_values('condition'))
            noise = noise.iloc[pd.Categorical(noise.index, noise_xlabs).argsort()]
            print(f"Noise: {form_factor}")
            print(noise)
        except KeyError as e:
            print(f"speechmodel: Missing value: {e}")

        # Make barplot
        plt.style.use('seaborn-v0_8')
        fig, axs = plt.subplots(nrows=2, ncols=1)
        fig.suptitle(f"Word Recognition Scores for {form_factor.upper()} Group")
        
        # Plot quiet data
        try:
            #axs[0].bar(quiet.index.get_level_values('condition'), 
            #    quiet['outcome'], color=['blue'])
            axs[0].bar(quiet_xlabs, 
                quiet['sentence_pc'], color=['blue'])
            axs[0].set(title="Quiet")
        except UnboundLocalError as e:
            print(f"speechmodel: {e}.\nspeechmodel: Skipping it.")

        # Plot noise data
        try:
            axs[1].bar(noise_xlabs, 
                noise['sentence_pc'], color=['orange'])
            axs[1].set(title="Noise")
        except UnboundLocalError as e:
            print(f"speechmodel: {e}.\nspeechmodel: Skipping it.")

        # Set axis limits
        for ax in axs:
            ax.set_ylim([0, 100])

        # Save figure
        if save:
            plt.savefig(f"./G23 Speech Data/{form_factor}.png")

        # Display figure
        if show:
            plt.show()
