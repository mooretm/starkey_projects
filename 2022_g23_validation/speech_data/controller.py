""" Controller script for plotting G23 validation speech data
    obtained using the Speech Task Controller.

    Written by: Travis M. Moore
    Last edited: 01/10/2023
"""

###########
# Imports #
###########
# Import data science packages
import pandas as pd
import scipy.stats as stats

# Import system packages
import os

# Import custom modules
from models import speechmodel


#############
# Arguments #
#############
# Want to show/save plots?
SHOW = 1
SAVE = 1

# Define condition plotting order on x axis
wireless_order = {
    'quiet_xlabs': ['unaided', 'aided', 'embs', 'emes'],
    'noise_xlabs': ['unaided', 'omnioff', 'omnion', 'aided', 'embs']
}

wired_order = {
    'quiet_xlabs': ['unaided', 'aided'],
    'noise_xlabs': ['unaided', 'omnioff', 'omnion']
}

# List of form factors to plot
form_factors = ['RIC', 'MRIC', 'ITE', 'ITC', 'CIC', 'IIC']
form_factors_wireless = ['RIC', 'MRIC', 'ITE', 'ITC']
form_factors_wired = ['CIC', 'IIC']

collapsed_wireless = ['RIC', 'Custom']
collapsed_wired = ['Wired']

# List of data columns to analyze
#data_cols = ['word_pc', 'sentence_pc']
data_cols = ['sentence_pc']

# List of environments
envs = ['q', 'n']


###########################
# Instantiate speechmodel #
###########################
#_path = r'\\starfile\Public\Temp\CAR Group\G23 Validation\Speech Data'
#_path = 'C:/Users/MooTra/OneDrive - Starkey/Desktop/Speech Data'
_path = './data/Speech Data'
s = speechmodel.SpeechModel(_path)


##########################
# Descriptive data funcs #
##########################
def mismatch_scan():
    # Inspect data for file name and content match
    print('')
    print('-' * 60)
    print("controller: Looking for mismatches...")
    booted = []
    for idx, file in enumerate(s.files):
        df = pd.read_csv(file)
        specs = os.path.basename(file).split('_')[4:7]
        specs = '_'.join(specs)

        if not (df['Condition'] == specs).all():
            print(f"controller: Mismatch in file {os.path.basename(file)}")
            booted.append(idx)

    print(f"controller: Total files before scan: {len(s.files)}")
    print(f"controller: Total mismatches: {len(booted)}")
    s.files = [i for j, i in enumerate(s.files) if j not in booted]
    print(f"controller: Total files after scan: {len(s.files)}")

    print("controller: Complete!")
    print('-' * 60)
    print('')

def subject_count(data):
    print('')
    print('-' * 60)
    print("Calculating subject count per condition...")
    # Find n for each index level
    header = ['form_factor', 'environment', 'n']
    lines = {}
    counter = 0
    for env in envs:
        for form in form_factors:
            #n = len(data[(data['form_factor']==form) & (data['environment']==env)]['sub'].unique())
            temp = data.loc[(slice(None), [env], slice(None), [form])]
            n = len(temp.index.get_level_values('sub').unique())
            print(f"{form} in {env}: {n} subjects")
            lines[counter] = [form, env, n]
            counter += 1
    sub_count = pd.DataFrame.from_dict(lines, orient='index')
    sub_count.columns = header
    sub_count.to_csv('./G23 Speech Data/subject_count.csv', index=False)
    print("Complete!")
    print('-' * 60)

def write_sub_means(data):
    print('')
    print('-' * 60)
    print("Calculating individual means per condition...")
    data.to_csv("./G23 Speech Data/sub_means.csv")
    print("Complete!")
    print('-' * 60)

def write_group_means():
    print('')
    print('-' * 60)
    print("Calculating group means per condition...")
    # Write group means to file
    s.get_group_means()
    s.group_means.to_csv('./G23 Speech Data/speech_data_group_means.csv')
    print("Complete!")
    print('-' * 60)


##################
# Plotting Funcs #
##################
def wireless_boxplots(data, show=None, save=None):
    # Wireless plots
    print('')
    print('-' * 60)
    print("controller: Creating wireless products plots...")
    # Make boxplots
    for col in data_cols:
        for form in form_factors_wireless:
            s.single_device_boxplot(data=data, form_factor=form, data_col=col, 
                show=show, save=save, **wireless_order)
    print("controller: Complete!")
    print('-' * 60)
    print('')

def wireless_boxplots_env(data, show=None, save=None):
    # Wireless plots
    print('')
    print('-' * 60)
    print("controller: Creating wireless products plots...")
    # Make boxplots
    for col in data_cols:
        for form in collapsed_wireless:
            for env in envs:
                s.single_env_boxplot(
                    data=data, 
                    form_factor=form,
                    env=env,
                    data_col=col, 
                    show=show, 
                    save=save, 
                    **wireless_order)
    print("controller: Complete!")
    print('-' * 60)
    print('')

def wired_boxplots_env(data, show=None, save=None):
    # Wireless plots
    print('')
    print('-' * 60)
    print("controller: Creating wireless products plots...")
    # Make boxplots
    for col in data_cols:
        for form in collapsed_wired:
            for env in envs:
                s.single_env_boxplot(
                    data=data, 
                    form_factor=form,
                    env=env,
                    data_col=col, 
                    show=show, 
                    save=save, 
                    **wired_order)
    print("controller: Complete!")
    print('-' * 60)
    print('')

def wired_boxplots(data, show=None, save=None):
    # Wired plots
    print('')
    print('-' * 60)
    print("controller: Creating wired products plots...")
    # Run through plots to find outliers
    for col in data_cols:
        for form in form_factors_wired:
            s.single_device_boxplot(data=data, form_factor=form, data_col=col, 
                show=show, save=save, **wired_order)
    print("controller: Complete!")
    print('-' * 60)
    print('')

def wireless_plots(data, show=None, save=None):
    # Wireless plots
    print('')
    print('-' * 60)
    print("controller: Creating wireless products plots...")
    for col in data_cols:
        for form in form_factors_wireless:
            s.single_device_barplot(data, form, data_col=col, show=show, save=save, **wireless_order)
    print("controller: Complete!")
    print('-' * 60)

def wired_plots(data, show=None, save=None):
    # Wired plots
    print('')
    print('-' * 60)
    print("controller: Creating wired products plots...")
    for col in data_cols:
        for form in form_factors_wired:
            s.single_device_barplot(data, form, data_col=col, show=show, save=save, **wired_order)
    print("controller: Complete!")
    print('-' * 60)

def multi_barplot():
    # Multi-barplot
    print('')
    print('-' * 60)
    print("controller: Creating multi-barplot...")
    s.multi_barplot(form_factors, show=SHOW, save=SAVE)
    print("controller: Complete!")
    print('-' * 60)


##############
# Statistics #
##############
def compare_form_factor_pairs(data):
    print('')
    print('-'*60)
    print('controller: Comparing conditions across form factor pairs...')
    data_dict = {}
    for form in form_factors:
        data_dict[form] = data.loc[(slice(None), slice(None), slice(None), [form])]

    pairs = [('RIC', 'MRIC'), ('ITC', 'ITE'), ('CIC', 'IIC')]
    for pair in pairs: 
        for env in ['q', 'n']:
            temp = data_dict[pair[0]].loc[(slice(None), [env], slice(None), [pair[0]])]
            conds = temp.index.get_level_values('condition').unique()
            for cond in conds:
                try:
                    p1 = data_dict[pair[0]].loc[(slice(None), [env], [cond], [pair[0]])]
                    p2 = data_dict[pair[1]].loc[(slice(None), [env], [cond], [pair[1]])]
                except:
                    print(f"No condition '{cond}' for {pair} in {env}")
                    break

                U1, p = stats.mannwhitneyu(p1, p2, alternative='two-sided')
                print('-'*50)
                print(f"{pair[0]} v. {pair[1]}: {cond} in {env}")
                print('-'*50)
                for ii, col in enumerate(p1.columns):
                    print(f"'{col}' statistic: {U1[ii]}")
                    print(f"p-value: {p[ii]}")
                    print('')
    print("controller: Complete!")
    print('-'*60)
    print('')


###########
# Routine #
###########
# Check for mismatches
mismatch_scan()

# Get df with clean files
s.organize_data()

# Get individual means
s.get_ind_means()
print(f"Length of ind_means: {len(s.ind_means)}")

# Write means to file
s._to_wide_format(s.ind_means, title='wide_sub_means_all_data.csv')

# Remove outliers
wireless_boxplots(s.ind_means, show=None, save=None)
wired_boxplots(s.ind_means, show=None, save=None)
s.remove_outliers(s.ind_means, show=None, save=1)
print(f"Length of ind_means: {len(s.ind_means)}")
print(f"Length of clean: {len(s.clean)}")

# Write cleaned means to file
s._to_wide_format(s.ind_means, title='wide_sub_means_clean.csv')


# Collapse across form factors
# Use either: "s.clean" (outliers removed) or 
# "s.ind_means" (outliers retained)
s.collapse_form_factors(s.ind_means)
print(f"Length of collapsed: {len(s.collapsed)}")


# # Create csv files for R
# wired_bools = s.collapsed.index.get_level_values('form_factor') == 'Wired'
# wired = s.collapsed[wired_bools].copy()
# wireless = s.collapsed[~wired_bools].copy()

# wired.to_csv('./G23 Speech Data/wired_R.csv')
# wireless.to_csv('./G23 Speech Data/wireless_R.csv')


#################
# One-Off Plots #
#################
d = s.final_plot_format(s.collapsed)

# Define condition plotting order on x axis
wireless_order = {
    'quiet_xlabs': ['Unaided', 'Aided', 'EM - Best Sound', 'EM - Enhanced Speech'],
    'noise_xlabs': ['Unaided', 'NR Off + Omni', 'NR On + Omni', 'NR On + Dir', 'Edge Mode']
}

wired_order = {
    'quiet_xlabs': ['Unaided', 'Aided'],
    'noise_xlabs': ['Unaided', 'NR Off + Omni', 'NR On + Omni']
}

# List of form factors to plot
form_factors = ['RIC', 'MRIC', 'ITE', 'ITC', 'CIC', 'IIC']
form_factors_wireless = ['RIC', 'Wireless Custom']
form_factors_wired = ['Wired Custom']

collapsed_wireless = ['RIC', 'Wireless Custom']
collapsed_wired = ['Wired Custom']



# Plot
wireless_boxplots_env(d, show=1, save=1)
wired_boxplots_env(d, show=1, save=1)

# # Descriptive outputs
# write_sub_means(s.ind_means)
#subject_count(s.collapsed)



#wireless_boxplots(s.collapsed)
#wired_boxplots(clean)
#wireless_plots()
#wired_plots()
#multi_barplot()

