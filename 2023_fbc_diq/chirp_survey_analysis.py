""" Analyze FBC DiQ cleaned survey data.

    Written by: Travis M. Moore
    Last edited: Feb 21, 2024
"""

###########
# Imports #
###########
# Data science
import pandas as pd
import numpy as np
from scipy.stats import ttest_rel, ttest_ind
from matplotlib import pyplot as plt
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})
import seaborn as sns

# System
import os
import glob

# Custom Modules
import normality_testing


###############
# Import Data #
###############
_path = r'C:\Users\MooTra\Code\Python\Projects\2023_fbc_diq\clean_chirp_survey_data'
ALL_FILES = glob.glob(os.path.join(_path, "*.csv"))

df_list = []
for file in ALL_FILES:
    filename = os.path.basename(file)
    print(filename)
    temp = pd.read_csv(file)
    df_list.append(temp)

data = pd.concat(df_list)
data.reset_index(drop=True, inplace=True)

order=['Not at all', 'Slightly', 'Somewhat', 'Moderately', 'Extremely']


################
# Subs to Drop #
################
# # Remove P4073
# mask = data['subject'] == 'P4073'
# data = data[-mask]


######################
# Conditions to Drop #
######################
# Drop Noisy environments
mask = data['environment'] == 'Noisy'
data = data[-mask]


###########################
# NO Objects Near Devices #
###########################
# Functions
def to_percent(sub, count, dic):
    return np.round((count / dic[sub]['rating']) * 100, 2)


def organize_plot_data(objs_near, feature_state):
    # Subset data by "objects" and "memory"
    temp = data[(data['objects']==objs_near) & (data['memory']==feature_state)].copy()

    # Dict of total ratings per subject
    by_sub_df = temp.iloc[:,[0,4]].groupby(by='subject').count()
    rating_dict = by_sub_df.to_dict('index')

    # DF of counts by rating, per subject
    ratings = temp.groupby(['subject', 'rating']).size().reset_index(name='count')

    # Calculate and add rating proportions column
    ratings['percent'] = ratings.apply(
        lambda x: to_percent(
            sub=x['subject'],
            count=x['count'],
            dic=rating_dict
            ), axis=1
    )

    # Add identifying info columns
    ratings['objs_near'] = objs_near
    ratings['feature_state'] = feature_state

    return ratings


def plot_ind_data(df1, df2):
    # PLOTS
    # Create Figure and Axes
    fig, (ax0, ax1) = plt.subplots(nrows=2, ncols=1, sharey=True)

    # Plot ON
    sns.barplot(
        ax=ax0,
        data=df1, 
        x='subject', 
        y='percent', 
        hue='rating', 
        hue_order=[
            'Not at all', 
            'Slightly', 
            'Somewhat', 
            'Moderately', 
            'Extremely'
            ]
    )
    # Create title
    objs = str(df1['objs_near'].unique()[0]).capitalize()
    state=str(df1['feature_state'].unique()[0]).capitalize()
    ax0.set(
        title=(f"Objects Near Devices: {objs}" +
               f"\nDiQ: {state}")
    )

    # Plot OFF
    sns.barplot(
        ax=ax1,
        data=df2, 
        x='subject', 
        y='percent', 
        hue='rating', 
        hue_order=[
            'Not at all', 
            'Slightly', 
            'Somewhat', 
            'Moderately', 
            'Extremely'
        ]
    )
    # Create title
    objs = str(df2['objs_near'].unique()[0]).capitalize()
    state=str(df2['feature_state'].unique()[0]).capitalize()
    ax1.set(
        title=(f"Objects Near Devices: {objs}" +
               f"\nDiQ: {state}")
    )


def stacked_barplot_ind(df):
    objs = str(df['objs_near'].unique()[0]).capitalize()
    state=str(df['feature_state'].unique()[0]).capitalize()
    df = df.pivot(index=['subject'], columns='rating', values='percent')

    # Look for missing rating columns (due to no response)
    vals = (set(order).difference(df.columns))
    # Add 0s for missing ratings values
    if vals:
        for val in list(vals):
            df[val] = np.nan

    # Reorder columns
    df = df.loc[:,['Not at all', 'Slightly', 'Somewhat', 'Moderately', 'Extremely']]

    print(df)

    df.plot(kind='bar', stacked=True)

    plt.title(f"Objects Near Devices: {objs}" +
               f"\nDiQ: {state}")
    plt.ylabel("Percentage of Responses")
    plt.xlabel("Subject")


    # Display percents on the stacked bars
    df_rel = df[df.columns]
    for n in df_rel:
        for i, (cs, ab, pc, tot) in enumerate(zip(df.iloc[:,:].cumsum(1)[n], df[n], df_rel[n], df[n])):
            #plt.text(tot, i, str(tot), va='center')
            #plt.text(i, tot, str(round(tot,1)), va='center', ha='center')
            #plt.text(cs - ab/2, i, str(np.round(pc, 1)) + '%', va='center', ha='center')
            #plt.text(i, cs - ab/2, str(np.round(pc, 1)) + '%', ha='center')
            plt.text(i, cs - ab/2, str(np.round(pc, 1)) + '%', ha='center')


def plot_group_data(df1, df2):
    # Create Figure and Axes
    fig, (ax0, ax1) = plt.subplots(nrows=2, ncols=1)

    # DF1
    sns.barplot(
        ax=ax0,
        data=df1,
        x='rating',
        y='percent',
        order=[
            'Not at all', 
            'Slightly', 
            'Somewhat', 
            'Moderately', 
            'Extremely'
            ]
    )
    # Create title
    objs = str(df1['objs_near'].unique()[0]).capitalize()
    state=str(df1['feature_state'].unique()[0]).capitalize()
    ax0.set(
        title=(f"Objects Near Devices: {objs}" +
               f"\nDiQ: {state}")
    )

    # DF2
    sns.barplot(
        ax=ax1,
        data=df2,
        x='rating',
        y='percent',
        order=[
            'Not at all', 
            'Slightly', 
            'Somewhat', 
            'Moderately', 
            'Extremely'
            ]
    )
    # Create title
    objs = str(df2['objs_near'].unique()[0]).capitalize()
    state=str(df2['feature_state'].unique()[0]).capitalize()
    ax1.set(
        title=(f"Objects Near Devices: {objs}" +
               f"\nDiQ: {state}")
    )


def fill_missing_conditions(df):
    # Look for missing rating columns (due to no response)
    vals = (set(order).difference(df['rating']))
    # Add 0s for missing ratings values
    if vals:
        for val in list(vals):
            df.loc[len(df.index)] = [val, np.nan, np.nan, np.nan]
    
    return df


#########
# BEGIN #
#########
conds = {
    # Objects near devices, feature_state
    "C1": [('No', 'on'), ('No', 'off')],
    "C2": [('Yes', 'on'), ('Yes', 'off')],
}
for key in conds.keys():
    # DF1
    objs_near_1 = conds[key][0][0]
    feature_state_1 = conds[key][0][1]
    df1 = organize_plot_data(objs_near=objs_near_1, feature_state=feature_state_1)
    print(f"\nchirp_survey_analysis: df1\n{df1}")
    avg1 = df1.groupby(by=['rating'])['percent'].sum()/len(df1['subject'].unique())
    avg1 = avg1.reset_index()
    avg1['objs_near'] = objs_near_1
    avg1['feature_state'] = feature_state_1
    avg1 = fill_missing_conditions(avg1)
    print(f"\nchirp_survey_analysis: Average Response Rate Per Rating")
    print(avg1)
    print(f"chirp_survey_analysis: Sum: {np.round(avg1['percent'].sum(),2)} (should equal 100)")

    # DF2
    objs_near_2 = conds[key][1][0]
    feature_state_2 = conds[key][1][1]
    df2 = organize_plot_data(objs_near=objs_near_2, feature_state=feature_state_2)
    print(f"\nchirp_survey_analysis: df2\n{df2}")
    avg2 = df2.groupby(by=['rating'])['percent'].sum()/len(df2['subject'].unique())
    avg2 = avg2.reset_index()
    avg2['objs_near'] = objs_near_2
    avg2['feature_state'] = feature_state_2
    avg2 = fill_missing_conditions(avg2)
    print(f"\nchirp_survey_analysis: Average Response Rate Per Rating")
    print(avg2)
    print(f"chirp_survey_analysis: Sum: {np.round(avg2['percent'].sum(), 2)} (should equal 100)")


    combo = pd.concat([df1, df2])
    file_name = f"objs_{objs_near_1}_data.csv"
    combo.to_csv(file_name, index=False)


    #####################
    # Statistical Tests #
    #####################
    print(f"\nchirp_survey_analysis: Welch's t test (unequal variances)")
    print(f"chirp_survey_analysis: Comparing percents from feature on/off")
    print(f"Objects Near Devices: {conds[key][0][0]}")
    result = ttest_ind(df1['percent'], df2['percent'], equal_var=False)
    print(f"t = {result[0]}")
    print(f"p = {result[1]}")

    print(f"\nchirp_survey_analysis: Welch's t test (unequal variances)")
    print(f"chirp_survey_analysis: Comparing percents from feature on/off")
    print(f"Objects Near Devices: {conds[key][0][0]}")
    result = ttest_ind(df1['percent'], df2['percent'], equal_var=False)
    print(f"t = {result[0]}")
    print(f"p = {result[1]}")


    # Plot individual data
    #plot_ind_data(df1=df1, df2=df2)
    stacked_barplot_ind(df1)
    stacked_barplot_ind(df2)

    # Plot group data
    plot_group_data(df1=avg1, df2=avg2)
    
    plt.show()







#####################
# Normality Testing #
#####################
#combo = pd.concat([df1, df2])
#nt = normality_testing.Data(combo)
#nt.calc_mad(dist="normal", data=combo, values_colname='percent')
#nt.normality_tests()
#nt.normality_plots()

