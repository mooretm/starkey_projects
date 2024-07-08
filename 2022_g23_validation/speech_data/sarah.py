import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import scipy.stats as stats
import statsmodels.api as sm


# Maddie Stuff
_path = 'C:/Users/MooTra/OneDrive - Starkey/Desktop/vent_data_sir.csv'
vent = pd.read_csv(_path)

# print(stats.shapiro(vent['rating']))

# sm.qqplot(vent['rating'], line='45')
# plt.show()

# sns.kdeplot(vent['rating'])
# plt.show()

U, mwp = stats.mannwhitneyu(vent[vent['cond']=='va']['rating'], vent[vent['cond']=='vr']['rating'], alternative='two-sided')
print(f"Mann Whitney p = {mwp}")



# SARAH STUFF
# _path = 'C:/Users/MooTra/OneDrive - Starkey/Desktop/ric_quicksin.csv'
# ric = pd.read_csv(_path)

# print(stats.shapiro(ric))

# sm.qqplot(ric, line='45')
# #plt.show()

# sns.kdeplot(ric)
#plt.show()

# U, mwp = stats.mannwhitneyu(ric['Aided'], ric['Unaided'], alternative='two-sided')
# print(f"Mann Whitney p = {mwp}")

# x, wp = stats.wilcoxon(ric['Aided'], ric['Unaided'], alternative='two-sided')
# print(f"Wilcoxon p = {wp}")

# t, tp = stats.ttest_rel(ric['Aided'], ric['Unaided'], alternative='two-sided')
# print(f"t test p = {tp}")
