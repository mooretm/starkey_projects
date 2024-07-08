import pandas as pd
import numpy as np
from pathlib import Path





def create_matrix(path, name):
    """ Make a single CSV out of several matrix 
        files created by Parth.
    """
    files = Path(path).glob('*.csv')
    files = list(files)

    df_list = []
    for file in files:
        temp = pd.read_csv(file)
        df_list.append(temp)

    data = pd.concat(df_list)
    print(f"{name}: {data.shape[0]}")
    data.to_csv(f"matrix_{name}.csv", index=False)

    return data.shape[0]

# Impulses
impulse_path = r'\\Starfile\Dept\Research and Development\FBC\DiQ\Round2_TRL6\Yes_No_Data\Recordings_for_TRL6\HS_Impulses'
speech_path = r'\\Starfile\Dept\Research and Development\FBC\DiQ\Round2_TRL6\Yes_No_Data\Recordings_for_TRL6\Shortened_Filtered_Recordings_Static_fbp_case1'
paths = [impulse_path, speech_path]

print("Creating matrix files...")
lengths = []
for path in paths:
    l = create_matrix(path=path, name=path.split('_')[-1])
    lengths.append(l)
print("Done")



trial_dur = 5
total = sum(lengths)
print(f"\nTotal trials: {total}")
print(f"Seconds per trial: {trial_dur}")

seconds = total * trial_dur
print(f"Seconds: {np.round(seconds, 2)}")

minutes = seconds / 60
print(f"Minutes: {np.round(minutes, 2)}")

hours = minutes / 60
print(f"Hours: {np.round(hours, 2)}")
