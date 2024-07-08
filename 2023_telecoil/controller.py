""" Plots for Justin's telecoil tick perception study. 

    Note: Preliminary analyses in python showed the need 
    for linear mixed effects modeling, so further 
    analyses will be carried out in Minitab. 

    Written by: Travis M. Moore
    Last edited: October 16, 2023
"""

###########
# Imports #
###########
# Import data science packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})
import seaborn as sns
from scipy import stats

# Import system packages
from pathlib import Path


#############
# Arguments #
#############
show_plot = 'n'
save_plot = 'y'
sns.set(font_scale=1.2)
DPI = 300
legend_label_size = 10
legend_title_size = 12
box_colors = {'hi': '#1E9BE9', 'nh': '#888B8D'}
marker_colors = {'hi': 'black', 'nh': 'black'}


#################
# Organize Data #
#################
# Get list of .csv file paths
path = r'./telecoil_data_all/'
files = Path(path).glob('*.csv')
files = list(files)

normals = [4012, 4466, 3517, 4502, 4217]
hi = [2243, 3977, 2790, 3290, 1063, 2417, 1914, 269, 3123, 3132, 3309, 328]

dfs = []
# Create list of dataframes
for file in files:
    # Read in single file as df
    temp = pd.read_csv(file)

    # Append group level
    if temp['subject'].unique() in normals:
        temp['group'] = 'nh'
    elif temp['subject'].unique() in hi:
        temp['group'] = 'hi'

    # Append organized data to list
    dfs.append(temp)

# Concatenate list of dfs
data = pd.concat(dfs)

# Split condition column
data[['type', 'background', 'expansion', 'isi']] = data['condition'].str.split('_', expand=True)
data.drop('condition', axis=1, inplace=True)


#------------------------------------------------------------------------------
# Detection
#------------------------------------------------------------------------------
# Get average of 3 judgments
# Detection task had 3 presentations
det = data[data['type']=='Detection'].copy()
det['isi'] = det['isi'].astype(int)
det.sort_values(by=['isi'], inplace=True)
avg_det_vals = det.groupby(['subject', 'isi', 'group'])['db_level'].mean()
det = pd.DataFrame(avg_det_vals)
det.reset_index(inplace=True)


###################
# Detection Stats #
###################
#print("\nMann Whitney U: NH vs HI (collapsed across ISI)")
#print(stats.mannwhitneyu(x=det[det['group']=='hi']['db_level'], y=det[det['group']=='nh']['db_level']))

# Normal Hearing #
# Grab NH data only
det_nh = det[det['group']=='nh']

# print("\nFriedman with factor of ISI: NH")
# print(stats.friedmanchisquare(
#     det_nh[det_nh['isi']==20]['db_level'],
#     det_nh[det_nh['isi']==45]['db_level'],
#     det_nh[det_nh['isi']==200]['db_level']
#     )
# )

# print("\nTukey for NH Detection")
# print(stats.tukey_hsd(
#     det_nh[det_nh['isi']==20]['db_level'],
#     det_nh[det_nh['isi']==45]['db_level'],
#     det_nh[det_nh['isi']==200]['db_level'],
#     )
# )


# Hearing Impaired #
# Grab HI data only
det_hi = det[det['group']=='hi']

# print("\nFriedman with factor of ISI: HI")
# print(stats.friedmanchisquare(
#     det_hi[det_hi['isi']==20]['db_level'],
#     det_hi[det_hi['isi']==45]['db_level'],
#     det_hi[det_hi['isi']==200]['db_level']
#     )
# )

# print("\nTukey for HI Detection")
# print(stats.tukey_hsd(
#     det_hi[det_hi['isi']==20]['db_level'],
#     det_hi[det_hi['isi']==45]['db_level'],
#     det_hi[det_hi['isi']==200]['db_level'],
#     )
# )


###################
# Detection Plots #
###################
# Detection NH vs. HI, collapsed
sns.boxplot(data=det, x='group', y='db_level', hue='group', 
            palette=box_colors)
sns.swarmplot(data=det, x='group', y='db_level', hue='group', 
              palette=marker_colors)
plt.yticks(range(30,55,2))
plt.title("Telecoil Tick Detection Threshold (Collapsed)")
plt.xlabel("Group")
plt.ylabel("Tick Level")
plt.axhline(33, c='red', linestyle='dashed')
if save_plot == 'y':
    plt.savefig(r'.\plots\det_collapsed.png', dpi=DPI)
if show_plot == 'y':
    plt.show()
plt.close()


# Detection NH vs. HI, by isi
sns.boxplot(data=det, x='isi', y='db_level', hue='group', 
            hue_order=['hi', 'nh'], order=[20, 45, 200],
            palette=box_colors
            )
sns.swarmplot(data=det, x='isi', y='db_level', hue='group', 
              hue_order=['hi', 'nh'], order=[20, 45, 200],
              dodge=True, palette=marker_colors, legend=False
              )
plt.yticks(range(30,55,2))
plt.title("Telecoil Tick Detection Thresholds by ISI")
plt.legend(title="Group", fontsize=legend_label_size, 
           title_fontsize=legend_title_size)
plt.xlabel("Interstimulus Interval (ms)")
plt.ylabel("Tick Level")
plt.axhline(33, c='red', linestyle='dashed')
if save_plot == 'y':
    plt.savefig(r'.\plots\det_by_isi.png', dpi=DPI)
if show_plot == 'y':
    plt.show()
plt.close()



#------------------------------------------------------------------------------
# Tolerance
#------------------------------------------------------------------------------
# Get average of 3 judgments
# Tolerance had a single presentation
tol = data[data['type']=='Tolerance'].copy()
tol['isi'] = tol['isi'].astype(int)
tol.sort_values(by=['isi'], inplace=True)
avg_tol_vals = tol.groupby(['subject', 'isi', 'group', 'background', 'expansion'])['db_level'].mean()
tol = pd.DataFrame(avg_tol_vals)
tol.reset_index(inplace=True)

#print("\nMann Whitney U: NH vs HI (collapsed across ISI, background, expansion)")
#print(stats.mannwhitneyu(x=tol[tol['group']=='hi']['db_level'], y=tol[tol['group']=='nh']['db_level']))


# Normal Hearing #
# Grab NH data only
tol_nh = tol[tol['group']=='nh']

# print("\nFriedman with factor of ISI, background, expansion: NH")
# print(stats.friedmanchisquare(
#     det_nh[det_nh['isi']==20]['db_level'],
#     det_nh[det_nh['isi']==45]['db_level'],
#     det_nh[det_nh['isi']==200]['db_level']
#     )
# )

# print("\nTukey for NH Detection")
# print(stats.tukey_hsd(
#     det_nh[det_nh['isi']==20]['db_level'],
#     det_nh[det_nh['isi']==45]['db_level'],
#     det_nh[det_nh['isi']==200]['db_level'],
#     )
# )


# Hearing Impaired #
# Grab HI data only
tol_hi = tol[tol['group']=='hi']

# print("\nFriedman with factor of ISI: HI")
# print(stats.friedmanchisquare(
#     det_hi[det_hi['isi']==20]['db_level'],
#     det_hi[det_hi['isi']==45]['db_level'],
#     det_hi[det_hi['isi']==200]['db_level']
#     )
# )

# print("\nTukey for HI Detection")
# print(stats.tukey_hsd(
#     det_hi[det_hi['isi']==20]['db_level'],
#     det_hi[det_hi['isi']==45]['db_level'],
#     det_hi[det_hi['isi']==200]['db_level'],
#     )
# )


###################
# Tolerance Plots #
###################
# Tolerance NH vs. HI, collapsed
fig1, ax1 = plt.subplots(1)
sns.boxplot(data=tol, x='group', y='db_level', hue='group',
            palette=box_colors)
sns.swarmplot(data=tol, x='group', y='db_level', hue='group',
              palette=marker_colors, legend=False)
plt.axhline(33, c='red', linestyle='dashed')
plt.yticks(range(30,86,5))
plt.title("Tolerance Level (Collapsed)")
plt.xlabel("Group")
plt.ylabel("Tick Level")
if save_plot == 'y':
    plt.savefig(r'.\plots\tol_collapsed.png', dpi=DPI)
if show_plot == 'y':
    plt.show()
plt.close()


# Tolerance NH vs. HI, by background
sns.boxplot(data=tol, x='background', y='db_level', hue='group', 
            hue_order=['hi', 'nh'], order=['Music', 'Silence', 'Speech'],
            palette=box_colors
            )
sns.swarmplot(data=tol, x='background', y='db_level', hue='group', 
              hue_order=['hi', 'nh'], order=['Music', 'Silence', 'Speech'],
              palette=marker_colors, dodge=True, legend=False
              )
plt.axhline(33, c='red', linestyle='dashed')
plt.yticks(range(30,86,5))
plt.title("Tolerance Level by Foreground")
plt.legend(title="Group", fontsize=legend_label_size, 
           title_fontsize=legend_title_size)
plt.xlabel("Foreground")
plt.ylabel("Tick Level")
if save_plot == 'y':
    plt.savefig(r'.\plots\tol_background.png', dpi=DPI)
if show_plot == 'y':
    plt.show()
plt.close()


# Tolerance NH vs. HI, by expansion
g = sns.boxplot(data=tol, x='expansion', y='db_level', hue='group', 
            hue_order=['hi', 'nh'], order=['Off', '2', '3'],
            palette=box_colors
            )
sns.swarmplot(data=tol, x='expansion', y='db_level', hue='group', 
              hue_order=['hi', 'nh'], order=['Off', '2', '3'],
              dodge=True, palette=marker_colors, legend=False
              )
plt.axhline(33, c='red', linestyle='dashed')
plt.yticks(range(30,86,5))
plt.title("Tolerance Level by Expansion Level")
plt.legend(title="Group", fontsize=legend_label_size, 
           title_fontsize=legend_title_size)
plt.xlabel("Expansion Setting")
plt.ylabel("Tick Level")
g.set_xticks([0, 1, 2])
g.set_xticklabels(["Off", "Level 2", "Level 3"])
if save_plot == 'y':
    plt.savefig(r'.\plots\tol_expansion.png', dpi=DPI)
if show_plot == 'y':
    plt.show()
plt.close()


# Tolerance NH, by background and expansion
g = sns.boxplot(data=tol_nh, x='expansion', y='db_level', hue='background',
              order=['Off', '3'], palette="Greys")
sns.swarmplot(data=tol_nh, x='expansion', y='db_level', hue='background',
              order=['Off', '3'], dodge=True, 
              palette=['black', 'black', 'black'], legend=False
              )
plt.axhline(33, c='red', linestyle='dashed')
plt.yticks(range(30,86,5))
plt.title("Tolerance Thresholds by Expansion Level and Foreground (NH)")
plt.legend(title="Foreground", fontsize=legend_label_size, 
           title_fontsize=legend_title_size)
plt.xlabel("Expansion Setting")
plt.ylabel("Tick Level")
plt.xlim([-0.2, 1.5])
g.set_xticks([0, 1])
g.set_xticklabels(["Expansion Off", "Level 3"])
if save_plot == 'y':
    plt.savefig(r'.\plots\nh_tol_background_expansion.png', dpi=DPI)
if show_plot == 'y':
    plt.show()
plt.close()


# Tolerance HI, by background and expansion
g = sns.boxplot(data=tol_hi, x='expansion', y='db_level', hue='background',
              order=['Off', '2', '3'], palette="Blues")
sns.swarmplot(data=tol_hi, x='expansion', y='db_level', hue='background', 
              order=['Off', '2', '3'], dodge=True, 
              palette=['black', 'black', 'black'], legend=False
              )
plt.axhline(33, c='red', linestyle='dashed')
plt.yticks(range(30,86,5))
plt.xlim([-0.4, 3.4])
plt.title("Tolerance Thresholds by Expansion Level and Foreground (HI)")
plt.legend(title="Foreground", fontsize=legend_label_size, 
           title_fontsize=legend_title_size)
plt.xlabel("Expansion Setting")
plt.ylabel("Tick Level")
g.set_xticks([0, 1, 2])
g.set_xticklabels(["Expansion Off", "Level 2", "Level 3"])
if save_plot == 'y':
    plt.savefig(r'.\plots\hi_tol_background_expansion.png', dpi=DPI)
if show_plot == 'y':
    plt.show()
plt.close()

print('\ncontroller: Done!\n')
