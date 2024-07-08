""" FBC DiQ analysis script for normal-hearing categorization of 
    recordings with/without chirps.
"""

###########
# Imports #
###########
# Import data science packages
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

# Import system packages
import glob
import os


#########
# BEGIN #
#########
# Import data
#datapath = './Data_Categories/sample_data'
#datapath = './Data_Categories/n3'
#datapath = './Data_Categories/s2'
datapath= r'\\starfile\Public\Temp\MooreT\2023 FBC DiQ\Data\Categorized_Proofing'
all_files = glob.glob(os.path.join(datapath, "*.csv"))

li = []

for filename in all_files:
    df = pd.read_csv(filename, index_col=None, header=0)
    li.append(df)

data = pd.concat(li)
counts = data.groupby("stimulus")["actual_resp"].sum()

print("\nResponse counts for each stimulus:")
print(counts)
counts.to_csv(r"Results\all_resposnes.csv")

# counts2 = data.groupby(['stimulus', 'actual_resp'])['actual_resp'].sum()
# print("\nResponse counts for each stimulus by response type:")
# print(counts2)

# Create dataframe of response counts
df = pd.DataFrame(counts)

# CHIRPS DETECTED
print("\nChirp Detected:")
print(df[df['actual_resp']==max(data.stimulus.value_counts())])
df[df['actual_resp']==max(data.stimulus.value_counts())].to_csv(
    r'Results\chirp_detected.csv'
)

# CHIRPS NOT DETECTED
print("\nChirp NOT Detected:")
print(df[df['actual_resp']==0])
df[df['actual_resp']==0].to_csv(r"Results\chirp_not_detected.csv")

# Plot response counts by stimulus
plt.bar(counts.index, counts.values)
plt.title("Number of 'Yes' Responses per Stimulus\n" +
          f"Yes Criterion={max(data.stimulus.value_counts())}, No Criterion=0"
)
plt.tick_params(axis='x', labelbottom=False)
plt.ylabel("Yes Responses")
plt.xlabel("Stimulus")
plt.show()
