""" Class for organizing and analyzing Validation Study 
    REM data for European MDR.

    Written by: Travis M. Moore
    Created: August 03, 2023
    Last edited: January 26, 2024
"""

###########
# Imports #
###########
# Import data science packages
import numpy as np
import pandas as pd
from scipy import stats

import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

# Import system packages
import os


#########
# BEGIN #
#########
class DataModel:
    def __init__(self, verifit_data, estat_data):
        
        # Define variables
        self.vdf = verifit_data
        self.edf = estat_data

        # Prepare data
        self._organize_estat_data()
        self._organize_verifit_data()
        self._assign_form_factors()


    #################
    # Organize Data #
    #################
    def _organize_estat_data(self):
        # Organize df
        self.edf[['subject', 'junk']] = self.edf['filename'].str.split('_', expand=True)
        self.edf.drop(['filename', 'junk', 'data'], axis=1, inplace=True)
        self.edf.set_index(['subject', 'form_factor'], inplace=True)
        self.edf.reset_index(inplace=True)


    def _organize_verifit_data(self):
        # Organize df
        self.vdf[['subject', 'condition']] = self.vdf['filename'].str.split("_", expand=True)
        self.vdf.loc[:, 'form_factor'] = ""
        self.vdf = self.vdf[['subject', 'condition', 'form_factor', 'freq', 'left65', 'right65']]
        self.vdf.reset_index(drop=True, inplace=True)


    def _assign_form_factors(self):
        """ Add form_factor column to verifit dataframe,
            based on e-stat dataframe form_factor column.
        """
        # Create dictionary of subject/form_factor from eSTAT df
        temp = self.edf.groupby(['subject', 'form_factor']).size()
        temp = temp.reset_index()
        temp = dict(zip(temp['subject'], temp['form_factor']))

        # Update empty form_factor column in Verifit df using dict
        for ii in range(0, self.vdf.shape[0]):
            self.vdf.iloc[ii, 2] = temp[self.vdf.iloc[ii,0]]


    def _collapse_form_factors(self):
        """ Collapse all RICs and all Wireless Customs (ITC and ITE).
            Change form factor name.
        """
        # Grab form factors to collapse 
        estat_RICs = self.edf[self.edf["form_factor"].isin(["RIC_RT", "RIC312"])].copy()
        verifit_RICs = self.vdf[self.vdf["form_factor"].isin(["RIC_RT", "RIC312"])].copy()

        estat_wireless_customs = self.edf[self.edf["form_factor"].isin(["ITC", "ITE"])].copy()
        verifit_wireless_customs = self.vdf[self.vdf["form_factor"].isin(["ITC", "ITE"])].copy()

        # Change form factor name
        estat_RICs["form_factor"] = "allRIC"
        verifit_RICs["form_factor"] = "allRIC"
        estat_wireless_customs["form_factor"] = "WirelessCustoms"
        verifit_wireless_customs["form_factor"] = "WirelessCustoms"

        self.estat_collapsed = pd.concat([estat_RICs, estat_wireless_customs])
        self.verifit_collapsed = pd.concat([verifit_RICs, verifit_wireless_customs])


    ################
    # Analyze Data #
    ################
    def analyze(self, verifit_data, estat_data, **kwargs):
        # Calculate difference scores
        self._diff_from_estat(verifit_data, estat_data)

        # Create list of dfs for each condition and form factor
        for cond in verifit_data['condition'].unique():
            # Condition title
            msg_cond = cond.upper()
            print("")
            print('*' * len(msg_cond))
            print(msg_cond)
            print('*' * len(msg_cond))

            for form in verifit_data['form_factor'].unique():
                # Form title
                msg_form = '**' + form.upper() + '**'
                print(msg_form)

                # LOW FREQUENCIES
                print("datamodel: Low Frequencies")
                print(f"datamodel: Percent of {cond} {form} ears <={kwargs['low_ceiling']} dB from target")
                for cps in kwargs['low_freqs']:
                    temp = self.estat_diffs[cond + '_' + form]
                    temp = temp[temp['freq']==cps]
                    #print(temp)
                    bools = np.abs(temp[['left_diff', 'right_diff']]) <= kwargs['low_ceiling']
                    t = bools.values.sum()
                    f = (~bools).values.sum()
                    total = t + f
                    score = np.round(t/total*100, 1)
                    print(f"datamodel: {cond} {form} {cps}: {score} percent")
                    print(f"datamodel: {cond} {form} {cps}: Ears meeting criteria: {t}")
                    print(f"datamodel: {cond} {form} {cps}: Total ears: {total}")

                    # One-way test: different from criterion?
                    diffs = list(temp['right_diff']) + list(temp['left_diff']) 
                    result = stats.ttest_1samp(a=diffs, popmean=kwargs['low_ceiling'], nan_policy='omit', alternative='two-sided')
                    print(f"datamodel: {cond} {form} {cps} one-way U test:")
                    print(f"datamodel: {cond} {form} {cps} one-way t test statistic: {np.round(result.statistic,2)}")
                    print(f"datamodel: {cond} {form} {cps} one-way t test p-value: {np.round(result.pvalue,4)}")
                    print(f"datamodel: {cond} {form} {cps} one-way t test df: {np.round(result.df,2)}")
                    print(f"datamodel: {cond} {form} {cps} one-way t test CI: {np.round(result.confidence_interval(confidence_level=0.95),2)}\n")


                # HIGH FREQUENCIES
                print("datamodel: High Frequencies")
                print(f"datamodel: Percent of {cond} {form} ears <={kwargs['high_ceiling']} dB from target")
                for cps in kwargs['high_freqs']:
                    temp = self.estat_diffs[cond + '_' + form]
                    temp = temp[temp['freq']==cps]
                    bools = np.abs(temp[['left_diff', 'right_diff']]) <= kwargs['high_ceiling']
                    t = bools.values.sum()
                    f = (~bools).values.sum()
                    total = t + f
                    score = np.round(t/total*100, 1)
                    print(f"datamodel: {cond} {form} {cps}: {score} percent")
                    print(f"datamodel: {cond} {form} {cps}: Ears meeting criteria: {t}")
                    print(f"datamodel: {cond} {form} {cps}: Total ears: {total}\n")

                    # One-way test: different from criterion?
                    diffs = list(temp['right_diff']) + list(temp['left_diff']) 
                    result = stats.ttest_1samp(a=diffs, popmean=kwargs['high_ceiling'], nan_policy='omit', alternative='two-sided')
                    print(f"datamodel: {cond} {form} {cps} one-way U test:")
                    print(f"datamodel: {cond} {form} {cps} one-way t test statistic: {np.round(result.statistic,2)}")
                    print(f"datamodel: {cond} {form} {cps} one-way t test p-value: {np.round(result.pvalue,4)}")
                    print(f"datamodel: {cond} {form} {cps} one-way t test df: {np.round(result.df,2)}")
                    print(f"datamodel: {cond} {form} {cps} one-way t test CI: {np.round(result.confidence_interval(confidence_level=0.95),2)}\n")


    def _diff_from_estat(self, verifit_data, estat_data):
        # Dictionary to hold dfs with difference scores by 
        # condition and form factor
        self.estat_diffs = {}

        for cond in verifit_data['condition'].unique():
            for form in verifit_data['form_factor'].unique():
                v = verifit_data.loc[((verifit_data['condition']==cond) & \
                    (verifit_data['form_factor']==form))].copy()
                v.reset_index(drop=True, inplace=True)
                e = estat_data.loc[((estat_data['form_factor']==form) & \
                    (estat_data['subject'].isin(v['subject'].unique())))].copy()
                e.reset_index(drop=True, inplace=True)
                v['left_diff'] = v['left65'] - e['left']
                v['right_diff'] = v['right65'] - e['right']
                self.estat_diffs[cond + '_' + form] = v


    def _diff_from_endstudy(self, verifit_data):
        # Dictionary to hold difference scores by condition and form factor
        self.endstudy_diffs = {}

        """
            This block of code gets all conditions from the verifit_data df, 
            but only grabs subjects that have EndStudy data. (Will also grab
            BestFit and TargetMatch.)
        """
        # Get list of subjects that have EndStudy data
        subs = verifit_data[verifit_data['condition']=='EndStudy']['subject'].unique()
        # Create mask of subjects in entire data set that have EndStudy data
        mask = verifit_data['subject'].apply(lambda y: y in subs)
        # Create df of all conditions for subjects with EndStudy data
        # That means: just subs with EndStudy BUT ALSO HAVE ALL OTHER CONDITIONS
        # This is just a subset of the verifit data, grabbing only subjects who 
        # also have endstudy data
        all_conds = verifit_data[mask].copy()


        """
            This block of code does the subtraction to find differences between 
            EndStudy and whatever other conditions exist.
        """
        # Get EndStudy values by condition and form factor
        for cond in verifit_data['condition'].unique():
            if cond == "TargetMatch":
                for form in verifit_data['form_factor'].unique():
                    # Get EndStudy values
                    endstudy = all_conds.loc[((verifit_data['condition']=='EndStudy') & \
                        (all_conds['form_factor']==form))].copy()
                    endstudy.reset_index(drop=True, inplace=True)

                    # Get looped condition values
                    target_match = all_conds.loc[((verifit_data['condition']==cond) & \
                        (all_conds['form_factor']==form))].copy()
                    target_match.reset_index(drop=True, inplace=True)

                    target_match['left_diff'] = endstudy['left65'] - target_match['left65']
                    target_match['right_diff'] = endstudy['right65'] - target_match['right65']
                    #target_match['left_diff'] = target_match['left65'] - endstudy['left65']
                    #target_match['right_diff'] = target_match['right65'] - endstudy['right65']

                    self.endstudy_diffs[cond + '_' + form] = target_match


    ######################
    # Plotting Functions #
    ######################
    def _reshape_for_plots(self, data):
        # Left/right diff columns to long format
        data = pd.melt(data, id_vars=['subject', 'freq'], 
            value_vars=['left_diff', 'right_diff'],
            var_name='side', value_name='diff')

        data = pd.pivot(data, index=['subject', 'side'], columns='freq', values='diff') 
        return data


    def _ylim_max(self, base=5):
        dfx = pd.concat([df for df in self.estat_diffs.values()], ignore_index=True)
        upper = np.max(np.abs(dfx.iloc[:,6:]))
        upper += 5 # Add 5 in case value was rounded down
        return base * round(upper/base)


    ########################################
    # Absolute Difference From eSTAT Plots #
    ########################################
    def abs_diff_plots(self, freqs, criterion, **kwargs):
        """ Organize and make boxplots of data.
        """
        # Check for kwargs
        # Show plot kwarg
        if 'show' in kwargs:
            show = kwargs['show']
        else:
            show = 'y'

        # Save plot kwarg
        if 'save' in kwargs:
            save = kwargs['save']
        else:
            save = 'n'

        # Define style for plot
        plt.style.use('seaborn-v0_8')
        plt.rc('font', size=18)
        plt.rc('axes', titlesize=15)
        plt.rc('axes', labelsize=15)
        plt.rc('xtick', labelsize=15)
        plt.rc('ytick', labelsize=15)

        # Get low or high frequency group for naming the plots
        if 500 in freqs:
            group = 'low'
        else:
            group = 'high'

        # Get max value of entire dataset for common ylim max
        #upper = self._ylim_max()

        # Make a plot for each condition (frequency) and each 
        # form factor.
        #print(self.estat_diffs)
        for cond in self.estat_diffs.keys():
            data = self._reshape_for_plots(self.estat_diffs[cond])
            data = data[freqs]
            plt.boxplot(np.abs(data), labels=data.columns, patch_artist=True)
            plt.axhline(y=criterion, color='red')
            plt.title(f"Difference Between {cond.split('_')[1]} " +
                    f"({cond.split('_')[0]}) and " + 
                    "e-STAT 2.0 Target\nFor 65 dB SPL Inputs " +
                    f"(n={len(data)} ears)")
            plt.ylabel('Absolute Difference (dB SPL)')
            plt.xlabel('Frequency (Hz)')
            #plt.ylim([0, upper])

            # Check whether to save plot
            if save == 'y':
                # Assign directory
                data_dir = 'deviation_plots'

                # Check whether directory exists
                data_dir_exists = os.access(data_dir, os.F_OK)
                if not data_dir_exists:
                    print("datamodel: Deviation plot directory not found; " +
                        "creating one...")
                    os.mkdir(data_dir)
                    print("datamodel: Created new directory.")

                # Save plot
                plt.savefig(data_dir + os.sep + cond + '_' + group + '.png')

            # Check whether to display plot
            if show == 'y':
                plt.show()

            # Clear plot from memory to start fresh on next iteration
            plt.close()


    #####################
    # Fine Tuning Plots #
    #####################
    def fine_tuning_plots(self, endstudy_data, show='y', save='n'):
        """ Plot study conditions (TargetMatch, BestFit) minus 
            EndStudy values.
        """
        # Calculate differences between conditions and endstudy
        # Results in "self.endstudy_diffs" dictionary
        self._diff_from_endstudy(endstudy_data)

        # Define style for plot
        plt.style.use('seaborn-v0_8')
        plt.rc('font', size=18)
        plt.rc('axes', titlesize=15)
        plt.rc('axes', labelsize=15)
        plt.rc('xtick', labelsize=15)
        plt.rc('ytick', labelsize=15)

        # Make a boxplot with all frequencies and form factors.
        for cond in self.endstudy_diffs.keys():
            data = self._reshape_for_plots(self.endstudy_diffs[cond])
            plt.boxplot(data, labels=data.columns, patch_artist=True)
            plt.axhline(y=0, color='black', linestyle='dotted')
            plt.title(f"EndStudy Minus {cond.split('_')[0]} ({cond.split('_')[1]})" +
                    "\nFor 65 dB SPL Inputs " +
                    f"(n={len(data)} ears)")
            plt.ylabel(f"EndStudy - {cond.split('_')[0]} (dB SPL)")
            plt.xlabel('Frequency (Hz)')

            # Check whether to save plot
            if save == 'y':
                # Assign directory
                data_dir = 'fine_tuning_plots'

                # Check whether directory exists
                data_dir_exists = os.access(data_dir, os.F_OK)
                if not data_dir_exists:
                    print("datamodel: Directory not found; " +
                        "creating one...")
                    os.mkdir(data_dir)
                    print("datamodel: Created new directory.")

                # Save plot
                plt.savefig(data_dir + os.sep + cond + '_FT.png')

            # Check whether to display plot
            if show == 'y':
                plt.show()

            # Clear plot from memory to start fresh on next iteration
            plt.close()


    #################
    # Write to .csv #
    #################
    def write_estat_diffs(self, estat_diffs, title=None):
        # Check for custom title argument
        if not title:
            title = 'estat_diffs'
        # Concatenate dict into single df and write to .csv
        estat = pd.concat(estat_diffs.values(), ignore_index=True)
        estat.to_csv(title+'.csv', index=False)


    def write_endstudy_diffs(self, endstudy_diffs, title=None):
        # Check for custom title argument
        if not title:
            title = 'endstudy_diffs'
        # Concatenate dict into single df and write to .csv
        estat = pd.concat(endstudy_diffs.values(), ignore_index=True)
        estat.to_csv(title+'.csv', index=False)
