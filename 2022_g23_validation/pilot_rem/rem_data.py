""" REM data organization.

    Create .csv of Verifit measured SPLs and eSTAT 2.0 targets.

    Written by: Travis M. Moore
    Created: August 1, 2023
    Last edited: August 2, 2023
"""

###########
# Imports #
###########
# Import custom modules
from models import verifitmodel
from models import estatmodel


####################
# Get Verifit Data #
####################
# Constants
VFREQS = [500, 1120, 2000, 3000, 4240]
VPATH = r'\\starfile\Public\Temp\CAR Group\G23 Audio Integration Pilot\Verifit'

# Create verifit model
v = verifitmodel.VerifitModel(path=VPATH, freqs=VFREQS)
v.get_data()


####################
# Get Verifit Data #
####################
# Constants
EFREQS = [500, 1100, 2000, 3000, 4200]
EPATH = r'\\starfile\Public\Temp\CAR Group\G23 Audio Integration Pilot\Estat'

# Create estat model
e = estatmodel.EstatModel(path=EPATH, freqs=EFREQS)
e.get_targets()
e.long_format()
print(e.estat_targets_long)
