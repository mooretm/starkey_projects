import pandas as pd
import data
import seaborn as sns
from matplotlib import pyplot as plt
from scipy import stats
from scipy.stats import jarque_bera
from scipy.stats import kstest
from scipy.stats import anderson
from scipy.stats import shapiro
import numpy as np

data = pd.read_csv(r'C:\Users\MooTra\Downloads\mba.csv')

d = data.Data()


