""" Signal Detection Theory functions.

    Written by: Travis M. Moore
    Created: June 28, 2023
    Last edited: August 22, 2023
"""

###########
# Imports #
###########
# Import data science packages
import numpy as np
import scipy.stats as stats


#########
# BEGIN #
#########
class SDT:
    def __init__(self, nH, nM, nFA, nCR):
        self.nH = nH
        self.nM = nM
        self.nFA = nFA
        self.nCR = nCR


    def get_vals(self):    
        # Proportions
        self.pH, self.pFA, self.PC = self.rates(
            self.nH, self.nM, self.nFA, self.nCR)

        # z-scores
        self.zH = self._p_to_z(self.pH)
        self.zFA = self._p_to_z(self.pFA)

        # Results
        self.dprime = self.dprime_p(self.pH, self.pFA)
        self.beta = self.beta_shortcut(self.pH, self.pFA)

        return self.dprime, self.beta, self.PC


    def _z_to_p(self, zscore):
        """ Return the p-value of a given, signed z-score.
        """
        pval = stats.norm.sf(zscore)
        return pval


    def _p_to_z(self, pval):
        """ Return the z-score associated with a given 
            right-tail p-value.
        """
        zscore = stats.norm.ppf(1-pval)
        return zscore


    def dprime_p(self, pH, pFA):
        zH = self._p_to_z(pH)
        zFA = self._p_to_z(pFA)
        dprime = zFA - zH
        return dprime


    def dprime_z(self, zH, zFA):
        dprime = zFA - zH
        return dprime


    def _dist_height(self, zscore):
        numerator = 2.718 ** (-0.5 * (zscore)**2)
        denominator = np.sqrt(2 * np.pi)
        y = numerator / denominator
        return y


    def calc_beta(self, pH, pFA):
        """ From McNicol (2005): A Primer of Signal Detection Theory
            beta gives a convenient measure of the response bias of any
            criterion point.
            beta = 1: unbiased
            beta > 1: strict/cautious criterion (bias toward noise trials)
            beta < 1: lax/risky criterion (bias toward signal trials)
        """
        # Convert proportions to z-scores
        zH = self._p_to_z(pH)
        zFA = self._p_to_z(pFA)

        # Calculate distribution heights
        ys = self._dist_height(zH)
        yn = self._dist_height(zFA)

        # Divide
        beta = ys / yn

        return beta


    def beta_shortcut(self, pH, pFA):
        """ 
        """
        # Get z-scores
        zH = self._p_to_z(pH)
        zFA = self._p_to_z(pFA)

        # Get dprime
        dprime = self.dprime_z(zH, zFA)
        
        # Log e beta
        ln_beta = 0.5 * dprime * (2 * zFA - dprime)

        # Convert to log10
        log_beta = ln_beta * 0.4343

        # Antilog to get back to regular beta
        beta = 10**log_beta

        return beta


    def rates(self, nH, nM, nFA, nCR):
        pH = nH/(nH+nM)
        pFA = nFA/(nFA+nCR)
        pCR = 1-pFA
        PC = 100*((pH+pCR)/2)
        return pH, pFA, PC
