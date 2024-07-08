""" Control script for pulling Verifit and e-STAT data.

    Conditions to test:
        Official:
        1. e-STAT targets vs. BestFit spls
        2. e-STAT targets vs. EndStudy spls
        3. BestFit spls vs. EndStudy spls

        Interesting:
        4. NAL-NL2 targets vs. BestFit spls
        5. NAL-NL2 targets vs. EndStudy spls

    Written by: Travis M. Moore
    Created: Nov 17, 2022
    Last edited: Jan 16, 2023
"""

###########
# Imports #
###########
# Import plotting packages
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

# Import data science packages
import pandas as pd
import numpy as np
import scipy.stats as stats
import statsmodels.api as sm
import seaborn as sn

# Import custom modules
from models import verifitmodel
from models import estatmodel
from models import g23model


##########################
# Fetch Data from Models #
##########################
# Verfit data
_verifit_path = '//starfile/Public/Temp/CAR Group/G23 Validation/Verifit'
#_verifit_path = 'C:/Users/MooTra/OneDrive - Starkey/Desktop/Verifit'
v = verifitmodel.VerifitModel(path=_verifit_path, 
    test_type='on-ear', 
    num_curves=3,
    freqs=[200, 500, 800, 1000, 1500, 2000, 3000, 4000, 6000, 8000])
v.get_all()
v.get_diffs()

# Estat data
_estat_path = r'\\starfile\Public\Temp\CAR Group\G23 Validation\Estat'
#_estat_path = 'C:/Users/MooTra/OneDrive - Starkey/Desktop/Estat'
e = estatmodel.Estatmodel(_estat_path)
e._to_long_format()

# Form factor by subject key
x = pd.read_csv(_verifit_path + '/form_key.csv')
form_key = x.set_index('PID').transpose().to_dict()

# Provide some feedback to console 
print(f"rem_data: Length of Verifit dataframe: {len(v.diffs)}")
print(f"rem_data: Length of Verifit BestFit: {len(v.diffs[v.diffs['filename'].str.contains('BestFit')])}")
print(f"rem_data: Length of Verifit EndStudy: {len(v.diffs[v.diffs['filename'].str.contains('EndStudy')])}")
print(f"rem_data: Length of eSTAT dataframe: {len(e.estat_targets_long)}")


#################
# Organize Data #
#################
# BESTFIT
bestfit = g23model.G23Model(v.diffs, e.estat_targets_long, form_key, "BestFit")
bestfit.get_data()
bestfit.final_data.to_csv('./G23 REM Data/estat_bestfit.csv', index=False)

# ENDSTUDY
endstudy = g23model.G23Model(v.diffs, e.estat_targets_long, form_key, "EndStudy")
endstudy.get_data()
endstudy.final_data.to_csv('./G23 REM Data/estat_endstudy.csv', index=False)


#######################
# Call Plotting Funcs #
#######################
# Plot eSTAT target deviation
# BESTFIT
#bestfit.plot_estat_target_deviation(bestfit, endstudy, v, calc='both', show=None, save=1)
best_collapsed = bestfit.collapse_forms(bestfit.final_data)
bestfit.plot_estat_target_deviation(best_collapsed, 'Best Fit', v, calc='both', show=None, save=1)

# ENDSTUDY
end_collapsed = endstudy.collapse_forms(endstudy.final_data)
endstudy.plot_estat_target_deviation(end_collapsed, 'Final', v, calc='both', show=None, save=1)


# Plot eSTAT BestFit - EndStudy
combo = bestfit.compare_estat(bestfit.final_data, endstudy.final_data)
combo_collapsed = bestfit.collapse_forms(combo)
bestfit.plot_best_minus_end(data=combo_collapsed, verifit_model=v, calc='both', show=None, save=1)


# Plot NAL-NL2 target deviation
#bestfit.plot_nal_target_deviation(bestfit, endstudy, v, calc='both', show=None, save=1)


###############
# Export long #
###############
bestfit.export_to_R()
d = bestfit.BestEndLong.copy()

# Subset data by level and side
softL = d[d['level']=='L1']
softR = d[d['level']=='R1']
avgL = d[d['level']=='L2']
avgR = d[d['level']=='R2']
loudL = d[d['level']=='L3']
loudR = d[d['level']=='R3']

# print("\nSoft left vs right")
# print(stats.mannwhitneyu(softL['value'], softR['value'], alternative='two-sided'))

# print("\nAverage left vs right")
# print(stats.mannwhitneyu(avgL['value'], avgR['value'], alternative='two-sided'))

# print("\nLoud left vs right")
# print(stats.mannwhitneyu(loudL['value'], loudR['value'], alternative='two-sided'))


#########
# Stats #
#########
def do_stats():
    x = combo.copy()
    x.drop(['file', 'unit'], axis=1, inplace=True)
    x.set_index(['filename', 'form_factor', 'freq', 'level'], inplace=True)

    # QQ plot
    sm.qqplot(x['end-target'], line='45')
    plt.show()

    sn.distplot(x['end-target'], hist=False, rug=True, kde=True)
    plt.show()

    #Shapiro-Wilk test
    stat, p = stats.shapiro(x['end-target'])
    print(f"Shapiro-Wilk p-value: {p}")

    # Mann-Whitney test for each frequency
    for level in ['L1', 'L2', 'L3', 'R1', 'R2', 'R3']:
        print('\n', '-'*60)
        print(f"Level: {level}")
        print('-'*60)
        for f in [250, 500, 750, 1000, 1500, 2000, 3000, 4000, 6000, 8000]:
            temp = x.loc[(slice(None), ['RIC'], [f], [level])]['end-target']
            U, pu = stats.mannwhitneyu(np.abs(temp), np.repeat(0,len(temp)), alternative='two-sided')
            t, pt = stats.ttest_1samp(temp, 0)
            print(f"Mann-Whitney: {f} Hz: U={U}, p={pu}")
            print(f"t-test: {f} Hz: t={t}, p={pt}\n")

