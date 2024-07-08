""" Script for Validation Study MDR requirement to show 
    deviation from e-STAT 2.0 targets.

    Written by: Travis M. Moore
    Created: July 28, 2023
    Last edited: August 10, 2023
"""

###########
# Imports #
###########
# Import custom modules
from models import verifitmodel
from models import estatmodel
from models import datamodel

"""
    NOTE: To write print statements to file rather than console,
        run using: 'python controller.py > output.txt'. This will
        provide a .txt file with the results of the analyses.
"""

#############
# Constants #
#############
_PATH = r'\\starfile\Public\Temp\CAR Group\YST Validation\REM'
#_PATH = r'C:\Users\MooTra\OneDrive - Starkey\Desktop\REM'
FREQS = [200, 500, 1000, 1500, 2000, 3000, 4000, 6000, 8000]
LOW = [500, 1000, 2000]
HIGH = [3000, 4000]

# Create dictionary of arguments 
PARS = {
    'low_freqs': LOW,
    'low_ceiling': 5,
    'high_freqs': HIGH,
    'high_ceiling': 8
}


###############
# Import Data #
###############
# VERIFIT
v = verifitmodel.VerifitModel(_PATH, freqs=FREQS)
v.get_data()

# eSTAT
e = estatmodel.EstatModel(_PATH, freqs=FREQS)
e.get_targets()


################
# Process Data #
################
# Organize data
d = datamodel.DataModel(
        verifit_data=v.measured.copy(), 
        estat_data=e.estat_targets.copy()
    )

# Analyze data (number of ears meeting criteria)
d.analyze(**PARS)


#############
# Plot Data #
#############
# Make deviation from target plots (BestFit and TargetMatch - eSTAT)
d.abs_diff_plots(freqs=LOW, criterion=PARS['low_ceiling'], 
                      show='n', save='y')

d.abs_diff_plots(freqs=HIGH, criterion=PARS['high_ceiling'], 
                      show='n', save='y')

# Make fine tuning plots (TargetMatch - EndStudy)
d.fine_tuning_plots(show='n', save='y')


######################
# Write Data to File #
######################
# Write all data to .csv
d.write_data()
