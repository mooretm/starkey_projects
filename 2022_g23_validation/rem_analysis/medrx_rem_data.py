""" Controller script for analyzing REM data from MedRX

    Written by: Travis M. Moore
    Last edited: Jan 16, 2023
"""

###########
# Imports #
###########
# Import custom modules
from models import verifitmodel
from models import medrxmodel

# Import data science packages
import pandas as pd
import numpy as np
import scipy.stats as stats
import statsmodels.api as sm
import seaborn as sn


##########################
# Fetch Data from Models #
##########################
""" Instantiate class objects and load data
"""
# Verfit data
_verifit_path = '//starfile/Public/Temp/CAR Group/G23 Validation/Verifit'
#_verifit_path = 'C:/Users/MooTra/OneDrive - Starkey/Desktop/Verifit'
v = verifitmodel.VerifitModel(
    path=_verifit_path, 
    test_type='on-ear', 
    num_curves=1, 
    freqs=[200, 500, 800, 1400, 2000, 3000, 3900, 6300, 8100])

# MedRX Data
_medrx_path = '//starfile/Dept/Research and Development/HRT/Users/CR Studies/G23 Validation/REM Target Match'
#_medrx_path = 'C:/Users/MooTra/OneDrive - Starkey/Desktop/REM Target Match'
mx = medrxmodel.MedRXModel(_medrx_path)


#################
# Organize Data #
#################
""" Shape data to work with verifitmodel plotting
    functions
"""
print('\n'+'-'*60)
print(f'medrx_rem_data: Preparing MedRx data...')
# BESTFIT
spls = mx.bestfit.iloc[:, [0,1,2,7,8]].copy()
spls.rename(columns={'L2':'L1', 'R2':'R1'}, inplace=True)
targets = mx.bestfit.iloc[:, [0,1,2,3,4]].copy()
#targets.rename(columns={'target_L2':'L1', 'target_R2':'R1'}, inplace=True)

spls = mx._to_long_format(spls)
targets = mx._to_long_format(targets)
spls.rename(columns={'variable':'level', 'value':'measured'}, inplace=True)
spls['targets'] = targets['value']
spls['measured-target'] = spls['measured'] - spls['targets']
spls['session'] = 'bestfit'
bestfit = spls.copy()

# ENDSTUDY
spls = mx.endstudy.iloc[:, [0,1,2,7,8]].copy()
spls.rename(columns={'L2':'L1', 'R2':'R1'}, inplace=True)
targets = mx.endstudy.iloc[:, [0,1,2,3,4]].copy()
spls = mx._to_long_format(spls)
targets = mx._to_long_format(targets)
spls.rename(columns={'variable':'level', 'value':'measured'}, inplace=True)
spls['targets'] = targets['value']
spls['measured-target'] = spls['measured'] - spls['targets']
spls['session'] = 'endstudy'
endstudy = spls.copy()
print("Done!")


###############
# Export to R #
###############
medrx_data = mx.export_to_R(bestfit, endstudy)


# Uncomment to plot collapsed data
bestfit = mx.collapse_forms(bestfit)
endstudy = mx.collapse_forms(endstudy)


#############
# Plot Data #
#############
def plot_medrx():
    """ Plot using verifitmodel funcs
    """
    print('\n'+'-'*60)
    print("medrx_rem_data: Creating MedRX plots...")
    # Create labels to pass to plot
    plot_labels = {
        'titles': ['Average (65 dB SPL):'],
        'ylabs': ['Measured - Target'],
    }

    # Plot all form factors on separate plots
    dfs = [bestfit, endstudy]
    labels = ['Best Fit', 'Final']

    for ii, df in enumerate(dfs):
        form_factors = df['style'].unique()
        for form in form_factors:
            plot_labels['save_title'] = f"./G23 REM Data/MedRx_{labels[ii]}_{form}.png"
            vals = df[df['style']==form]
            v.plot_diffs(
                data=vals, 
                title=f"MedRx: Measured minus Target ({form}: {labels[ii]})",
                calc='both', # None, 'rms', 'mean', 'both'
                show=None,
                save=1,
                **plot_labels
            )
    print("Done!\n")

# Call plot function
plot_medrx()
