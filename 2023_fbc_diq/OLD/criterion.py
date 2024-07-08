
import numpy as np
import scipy.stats as stats


def z_to_p(val, tails='one-tailed'): # or "two-tailed"
    if tails=='one-tailed':
        p = stats.norm.sf(np.abs(val))
    elif tails == 'two-tailed':
        p = stats.norm.sf(np.abs(val))*2
    return p


def p_to_z(val):
    return stats.norm.ppf(1-val)



def dist_height(zscore):
    numerator = 2.718 ** (-0.5 * (zscore)**2)
    denominator = np.sqrt(2 * np.pi)
    y = numerator / denominator
    return y


def calc_beta(zH, zFA):
    """ From McNicol (2005): A Primer of Signal Detection Theory
        beta gives a convenient measure of the response bias of any
        criterion point.
        beta = 1: unbiased
        beta > 1: strict/cautious criterion
        beta < 1: lax/risky criterion
    """
    ys = dist_height(zH)
    yn = dist_height(zFA)
    beta = ys/ yn
    return beta


def calc_dprime(zFA, zH):
    dprime = zFA - zH
    return dprime


def beta_shortcut(zH, zFA):
    """ This DOES NOT work.
        And I don't know why...
    """
    dprime = calc_dprime(zFA, zH)
    ln_beta = 0.5 * dprime * (2 * zFA - dprime)
    beta = ln_beta * 0.4343
    return (beta, ln_beta)
