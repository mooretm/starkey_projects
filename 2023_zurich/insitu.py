###########
# Imports #
###########
# Import system packages
from pathlib import Path
import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})
import numpy as np
import seaborn as sns


#############
# Functions #
#############
def _import_data(path):
    """ 
        Import insitu data and organize it.

        Returns: organized data frame
    """
    # Get list of file names/paths
    files = Path(path).glob('*.csv')
    files=list(files)

    # Read each file, organize and append to list
    df_list = []
    for file in files:
        # Removes '.csv' from file name
        filename=os.path.basename(file)[:-4]
        temp = pd.read_csv(file, header=None)
    
        # Cut off rows and then keeps only certain columns
        temp=temp.iloc[19:,0:3]
        # Name columns
        temp.columns=['frequency','left','right']
        # Move file name to front of print
        temp.insert(loc=0,column='file',value=filename) 
        df_list.append(temp)

    # Concatenate list of dfs into single df
    data = pd.concat(df_list)

    # Split file column
    data[['pid', 'style', 'venting', 'environment']] = data['file'].str.split('_', expand=True)
    data.drop(['file'], axis=1, inplace=True)
    data = pd.melt(
        data, 
        id_vars=['pid', 'style', 'frequency', 'venting', 'environment'], 
        value_vars=['left', 'right'], 
        var_name='side', 
        value_name='threshold'
    )

    # Convert numbers from str to int
    data['threshold'] = data['threshold'].astype(int)
    data['frequency'] = data['frequency'].astype(int)

    return data


def _ind_diffs_by_all(data):
    """
        Subtract insitu from booth thresholds

        Returns: dataframe of differences
    """
    # Create two dataframes for subtraction
    booth = data[data['environment']=='Booth']
    insitu = data[data['environment']=='InSitu']

    # Subtract
    diffs = np.array(booth['threshold']) - np.array(insitu['threshold'])

    # Create new dataframe to return
    df = booth[['pid', 'style', 'side', 'frequency', 'venting']].copy()
    df['diffs'] = diffs

    return df


def _ind_diffs_collapsed_by_side(data):
    """
        Args: 
            data: a dataframe from _ind_diffs_by_all

        Returns: dataframe of individual differences by 
            all factors, except collapsed across side.
    """
    ind_diffs_collapsed_by_side = data.groupby(['pid', 'style', 'frequency', 'venting'])['diffs'].mean()
    ind_diffs_collapsed_by_side = ind_diffs_collapsed_by_side.reset_index()
    return ind_diffs_collapsed_by_side



def _get_diffs_by_style_side_freq(data):
    """
        Args: 
            data: a dataframe from _ind_diffs_by_all
    """
    group_diffs_by_style_side_freq = data.groupby(['style', 'side', 'frequency'])['diffs'].mean()
    group_diffs_by_style_side_freq = group_diffs_by_style_side_freq.reset_index()
    return group_diffs_by_style_side_freq


def _get_diffs_by_style_freq(data):
    """
        Args: 
            data: a dataframe from _ind_diffs_by_all
    """
    group_diffs_by_style_freq = data.groupby(['style', 'frequency'])['diffs'].mean()
    group_diffs_by_style_freq = group_diffs_by_style_freq.reset_index()
    return group_diffs_by_style_freq


def _boxplot_by_style(data, name):
    '''
        Args: 
            data: a dataframe from _ind_diffs_collapsed_by_side
    '''  
    # pull all unique names from style column 
    styles = data['style'].unique()
    subs = len(data['pid'].unique())
    for style in styles:
        temp = data[data['style']==style]
        sns.boxplot(x='frequency', y='diffs', data=temp)
        plt.title(f"{style}: In-Situ Threshold - Booth Threshold ({name})" + 
                  f"\nn={subs}")
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Difference in Thresholds (dB HL)")
        #after seeing real data add line 134 back in
        #plt.ylim([-20, 20])
        plt.savefig(f"./zurich_insitu_plots/{name}_{style}_diffs.png")
        plt.show()
        plt.close()


def _boxplot_by_style_vent(data):
    '''
        Args: 
            data: a dataframe from _ind_diffs_collapsed_by_side
    '''  
    # pull all unique names from style column 
    styles = data['style'].unique()
    
    subs = len(data['pid'].unique())
    for style in styles:
        temp = data[data['style']==style]
        vents = temp['venting'].unique()
        for vent in vents: 
            #temp = data[(data['style']==style) & (data['venting']==vent)]
            temp = data[data['venting']==vent]
            sns.boxplot(x='frequency', y='diffs', data=temp)
            plt.title(f"{vent} Vent {style}: In-Situ Threshold - Booth Threshold" + 
                    f"\nn={subs}")
            plt.xlabel("Frequency (Hz)")
            plt.ylabel("Difference in Thresholds (dB HL)")
            #after seeing real data add line 134 back in
            #plt.ylim([-20, 20])
            plt.savefig(f"./zurich_insitu_plots/{style}_{vent}_diffs.png")
            plt.show()
            plt.close()


def _ind_pass_criterion_results(data):
    styles = data['style'].unique()
    for style in styles:
        temp = data[data['style']==style]
        bools = temp['diffs'].between(-10,10)
        failures = temp[~bools]
        #counts = failures.groupby(['pid', 'style', 'side'])['frequency'].count()
        counts = failures.groupby(['frequency'])['diffs'].count()
        #print(failures)
        print(f"\nnumber of {style} failures by ear")
        print(counts)


def _clean_by_booth_thresholds(data):
    """ Grab booth and insitu data only where booth thresholds are 
        within the upper and lower limits.
    """
    # Create separate dataframes of equal length based on environment
    # Reset index to indexes align across dataframes
    booth = data[data['environment']=='Booth'].reset_index(drop=True)
    insitu = data[data['environment']=='InSitu'].reset_index(drop=True)

    # Only grab booth thresholds that are within the limits
    bools = booth['threshold'].between(15,35)

    # Filter booth and insitu dataframes using bools
    booth2 = booth[bools]
    insitu2 = insitu[bools]

    # Concatenate booth and insitu data into a single, long-format dataframe
    cleaned = pd.concat([booth2, insitu2])

    return cleaned


#########
# Begin #
#########
# path=r'\\starfile\Public\Temp\CAR Group\Zurich Validation\In-Situ'

# # Import and organize data
# data = _import_data(path)
# print(f"\nData after import: \n{data}")

# cleaned = _clean_by_booth_thresholds(data)
# print(f"\nCleaned by booth thresholds: \n{cleaned}")

# # Subtract insitu from booth thresholds
# #ind_diffs_by_all = _ind_diffs_by_all(data)
# ind_diffs_by_all = _ind_diffs_by_all(cleaned)
# print(f"\nIndividual differences by all factors: \n{ind_diffs_by_all}")

# ind_diffs_collapsed_by_side = _ind_diffs_collapsed_by_side(ind_diffs_by_all)
# print("\n Individual differences by all factors, collapsed across side: " +
#       f"\n{ind_diffs_collapsed_by_side}")

# group_diffs_by_style_side_freq = _get_diffs_by_style_side_freq(ind_diffs_by_all)
# print("\nGroup differences by style, side and frequency: " +
#       f"\n{group_diffs_by_style_side_freq}")

# group_diffs_by_style_freq = _get_diffs_by_style_freq(ind_diffs_by_all)
# print("\nGroup differences by style and frequency: " +
#       f"\n{group_diffs_by_style_freq}")

# _boxplot_by_style(ind_diffs_collapsed_by_side)
# _boxplot_by_style_vent(ind_diffs_collapsed_by_side)

# _ind_pass_criterion_results(ind_diffs_by_all)


##########################
# Plot all data protocol #
##########################
path=r'\\starfile\Public\Temp\CAR Group\Zurich Validation\In-Situ'

# Import and organize data
data = _import_data(path)

# Subtract insitu from booth thresholds
ind_diffs_by_all = _ind_diffs_by_all(data)

# Collapse across side
ind_diffs_collapsed_by_side = _ind_diffs_collapsed_by_side(ind_diffs_by_all)

_boxplot_by_style(ind_diffs_collapsed_by_side, name='all')


##############################
# Plot cleaned data protocol #
##############################
# Clean the data
cleaned = _clean_by_booth_thresholds(data)

# Subtract insitu from booth thresholds
ind_diffs_by_all = _ind_diffs_by_all(cleaned)

# Collapse across side
ind_diffs_collapsed_by_side = _ind_diffs_collapsed_by_side(ind_diffs_by_all)

_boxplot_by_style(ind_diffs_collapsed_by_side, name='cleaned')
