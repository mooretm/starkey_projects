""" Demonstration SDT code using the single subject and 
    multi-subject SDT classes.

    Written by: Travis M. Moore
    Last edited: August 23, 2023
"""

# Import data science packages
import pandas as pd

# Import system packages
import os
import glob

# Import custom modules
from models import sdt_multi_subs
from models import sdt_single_sub


# Categorization proofing with NH
#N_NOISE = 24
#N_SIGNAL = 27

# # Screening for HI 1st visit
# no = 9
# yes=10
# N_NOISE = no * 4
# N_SIGNAL = yes * 4




#################
# Organize Data #
#################
# data = {
#     'subject': [1, 2, 3, 4],
#     'nH': [5, 20, 30, 45],
#     'nM': [45, 30, 20, 5],
#     'nFA': [20, 20, 10, 5], 
#     'nCR': [30, 30, 40, 45]
# }
# df = pd.DataFrame(data)
# print("\nOriginal Dataframe")
# print(df)

#datapath = r'C:\Users\MooTra\Code\Python\Projects\2023_fbc_diq\Data_SDT'
#datapath = r'\\starfile\Public\Temp\MooreT\2023 FBC DiQ\Lab_Data\Categorized_Proofing'
#datapath = r'\\starfile\Public\Temp\MooreT\2023 FBC DiQ\Lab_Data\Screening\HI_Screening_Visit_1'
datapath = r'\\starfile\Public\Temp\MooreT\2023 FBC DiQ\Lab_Data\HI'
all_files = glob.glob(os.path.join(datapath, "*.csv"))

# Import and concatenate all data files
li = []
for filename in all_files:
    df = pd.read_csv(filename, index_col=None, header=0)
    li.append(df)
data = pd.concat(li)

# Organize df and calculate value counts
df = data[['subject', 'resp_type']]
df = df.value_counts()
df = df.reset_index()
df = df.pivot(index='subject', columns='resp_type', values='count')
df = df[['H', 'M', 'FA', 'CR']]

""" In case of 0s, there must be a correction factor applied to 
    achieve non-zero. The link below has a good discussion. 
    I like option 4 for ease of use. It will take some logic to 
    catch these instances, or, I could run the code, find subjects
    with NaNs and calculate and insert values 'by hand.' 
    https://stats.stackexchange.com/questions/134779/d-prime-with-100-hit-rate-probability-and-0-false-alarm-probability

"""
# Replace NaNs with correction factor
#df = df.fillna(0.5/(N_NOISE*3))
#print("\n\nsdt_sample: Correction factor hard-coded - CHANGE THIS")


################
# Analyze Data #
################
s = sdt_multi_subs.SDT(df)
x = s.get_vals()
print("\ncontroller: SDT results")
print(x)

# ss = sdt_single_sub.SDT(4,2,1,2)
# x = ss.get_vals()
# print("\nSDT results - single subject")
# print(x)

# for ii in range(0, len(df['subject'].unique())):
#     s = sdt_single_sub.SDT(df.iloc[ii, 1], df.iloc[ii, 2], df.iloc[ii, 3], df.iloc[ii, 4])
#     print(f"\nSubject {df.iloc[ii,0]}")
#     dprime, beta = s.get_vals()
#     print(f"d-prime: {np.round(dprime, 2)}")
#     print(f"beta: {np.round(beta, 2)}")
#     print(f"PC: {s.PC}")
