import pandas as pd
import numpy as np
import seaborn as sns
import scipy.stats as stats
import statsmodels.api as sm


import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

data = pd.read_csv('TCoil_G23.csv')
data.drop('Rep', axis=1, inplace=True)

barriers = []
inputs = []
for ii in range(0, data.shape[0]):
    x = data.iloc[ii, 2].split('_')
    barriers.append(x[0])
    inputs.append(x[1])

data['Barrier'] = barriers
data['Input'] = inputs

data = data.groupby(
    ['ID', 'Style', 'Condition', 'Barrier', 'Input', 'List']
    ).sum(numeric_only=True)

data.reset_index(inplace=True)

cond_order = ['Unobstructed_Mic', 'Unobstructed_Loop', 'Mask_Mic', 
'Mask_Loop', 'Barrier_Mic', 'Barrier_Loop']

barrier_order = ['Unobstructed', 'Mask', 'Barrier']
input_order = ['Mic', 'Loop']


#data = data.iloc[pd.Categorical(data['Condition'], cond_order).argsort()]     


print("justin: Creating plots...")

sns.set(rc={'figure.figsize':(9,6)})
#sns.set(font_scale=3)
# Macro_RIC
fig, ax1 = plt.subplots(1)
ric_data = data[data['Style']=='Macro_RIC']
ax1 = sns.boxplot(data=ric_data, x='Barrier', y='Score', 
    order=barrier_order, hue='Input', hue_order=input_order)
ax1 = sns.swarmplot(data=ric_data, x='Barrier', y='Score', 
    order=barrier_order, hue='Input', hue_order=input_order, 
    dodge=True, palette=['black', 'black'], legend=False)
plt.ylabel('Score', fontsize=16)
plt.title('Macro RIC', fontsize=18)
plt.xlabel('')
plt.tick_params(labelsize=16)
plt.savefig(f"RIC_boxplot.png")

# ITE
fig2, ax2 = plt.subplots(1)
ite_data = data[data['Style']=='ITE']
ax2 = sns.boxplot(data=ite_data, x='Barrier', y='Score', 
    order=barrier_order, hue='Input', hue_order=input_order)
ax2 = sns.swarmplot(data=ite_data, x='Barrier', y='Score', 
    order=barrier_order, hue='Input', hue_order=input_order, 
    dodge=True, palette=['black', 'black'], legend=False)
plt.ylabel('Score', fontsize=16)
plt.title('ITE', fontsize=18)
plt.xlabel('')
plt.tick_params(labelsize=16)
plt.savefig(f"ITE_boxplot.png")

#plt.show()
print("justin: Done!")


