#!/usr/bin/env python
# coding: utf-8
# Thorpe scale approach in the Weddell Sea

import warnings

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import mixsea as mx
import numpy as np
import pandas as pd
import scipy.stats as ss
from scipy.interpolate import interp1d  # is considered legacy code, will be in the future removed from scipy

import src.helper as helper
from src.read_CTDs import load_Joinville_transect_CTDs

warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)
# Suppress specific RuntimeWarning related to mean of empty slice
warnings.filterwarnings(action="ignore", category=RuntimeWarning, message=".*Mean of empty slice.*")

plt.rcParams.update({
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
    "figure.figsize": [8, 6]
})

DENSITY_NOISE = 5e-4  # Noise parameter, Default value = 5e-4
ALPHA = 0.8  # Coefficient relating the Thorpe and Ozmidov scales.
BACKGROUND_EPS = 1e-10  # Background value of epsilon applied where no overturns are detected.
OUTLIERS = ['PS71/216-1', 'PS40/099-1', 'PS49/015-2', 'PS71/212-3', 'PS71/210-2']

CTDs = load_Joinville_transect_CTDs()
CTDs_grouped = CTDs.groupby("Event")
events = CTDs_grouped.groups.keys()

# define a common axis with grid spacing of 1
new_mab = np.arange(0, 5000, 1)

# objects for saving the data later
LT_df = pd.DataFrame()
eps_df = pd.DataFrame()
N_df = pd.DataFrame()
T_df = pd.DataFrame()
gamma_n_df = pd.DataFrame()

for event in events:

    if event in OUTLIERS:
        continue

    current_profile = CTDs_grouped.get_group(event).reset_index(drop=True)

    eps, N2, diagnostics = mx.overturn.eps_overturn(
        current_profile['Depth water [m]'],
        current_profile['Temp [°C]'],
        current_profile['Sal'],
        current_profile["Longitude"].mean(),
        current_profile["Latitude"].mean(),
        dnoise=DENSITY_NOISE,
        alpha=ALPHA,
        background_eps=np.nan, #background will be added later
        return_diagnostics=True,
    )

    N = np.sqrt(N2)  # s* 86400 / (2 * np.pi) # Calculate buoyancy frequency in units of cycles per day (cpd).

    # Plot only in the depth range:
    max_depth = current_profile['Depth water [m]'].max()
    depth = current_profile['Depth water [m]']

    if np.all(np.isnan(N)):
        print(f"{event} only produces NaNs")
        continue

    if max_depth < 200:
        print(f"{event} is only {max_depth}m and is too shallow")
        continue
    if current_profile['Temp [°C]'].iloc[-1] > 0.2:
        print(f"{event} shows {current_profile['Temp [°C]'].iloc[-1]:.2f} °C at the bottom, which is too high ")
        continue

    # nearest interpolation to the defined axis
    LT_func = interp1d(max_depth - depth, diagnostics["Lt"], kind='nearest', bounds_error=False, fill_value=(np.nan, np.nan))
    N_func = interp1d(max_depth - depth, N, kind='nearest', bounds_error=False, fill_value=(np.nan, np.nan))
    eps_func = interp1d(max_depth - depth, eps, kind='nearest', bounds_error=False, fill_value=(np.nan, np.nan))
    T_func = interp1d(max_depth - depth, current_profile['Temp [°C]'], kind='nearest', bounds_error=False,
                      fill_value=(np.nan, np.nan))
    gamma_n_func = interp1d(max_depth - depth, current_profile['Neutral density [kg m^-3]'], kind='nearest',
                            bounds_error=False,
                            fill_value=(np.nan, np.nan))

    LT_df[current_profile["Longitude"].mean()] = LT_func(new_mab)
    N_df[current_profile["Longitude"].mean()] = N_func(new_mab)
    eps_df[current_profile["Longitude"].mean()] = eps_func(new_mab)
    T_df[current_profile["Longitude"].mean()] = T_func(new_mab)
    gamma_n_df[current_profile["Longitude"].mean()] = gamma_n_func(new_mab)

# sort columns after their longitude value
eps_df.sort_index(axis=1, inplace=True)
N_df.sort_index(axis=1, inplace=True)
T_df.sort_index(axis=1, inplace=True)
gamma_n_df.sort_index(axis=1, inplace=True)

## small data cleaning
# removes the super high Thorpe scales, for which no dissipation rate is computed
LT_df.where(cond=~eps_df.isna(), other=np.nan, inplace=True)
# remove all Thorpe scale values larger than 200m, in particular removes one very large overturn in the deep ocean around 47° W
LT_df.where(cond=LT_df<200, other=np.nan, inplace=True)
# communicate changes back to eps_df
eps_df.where(cond=~LT_df.isna(), other=np.nan, inplace=True)

# cut to only cover the core of the gravity current
vertical_eps_df = eps_df.drop(eps_df.columns[eps_df.columns < -51.5], axis="columns")
vertical_eps_df.drop(vertical_eps_df.columns[vertical_eps_df.columns > -48.5], axis="columns", inplace=True)

# Fill NaN with 'assumed_background_dissipation' only where there is temperature data
vertical_eps_df.fillna(value=BACKGROUND_EPS, inplace=True)
vertical_eps_df.where(cond=~T_df.isna(), other=np.nan, inplace=True)
mean_profile = vertical_eps_df.mean(axis=1)
std_of_mean_profile = vertical_eps_df.std(axis=1)

# save data
eps_df.to_pickle("./method_results/Thorpe_eps_df_with_mab.pkl")
T_df.to_pickle("./method_results/Thorpe_T_df_with_mab.pkl")
gamma_n_df.to_pickle("./method_results/Thorpe_neutral_density_df_with_mab.pkl")
np.savez("./method_results/horizontally_averaged_Thorpe_eps", z=vertical_eps_df.index, eps=mean_profile)

eps_df.to_csv("./method_results/Thorpe_eps_df_with_mab.csv")
gamma_n_df.to_csv("./method_results/Thorpe_neutral_density_df_with_mab.csv")

# read thorpe results data
#thorpe_eps_df = pd.read_pickle("../scripts/thorpe_scales/method_results/Thorpe_eps_df_with_mab.pkl")
#thorpe_mab = thorpe_eps_df.index
#thorpe_gamma_n_df = pd.read_pickle("../scripts/thorpe_scales/method_results/Thorpe_neutral_density_df_with_mab.pkl")

# add background dissipation, but only where there is temperature data
BACKGROUND_DISSIPATION = 1e-10  #value taken from Hirano et al 2015
eps_df.fillna(value=BACKGROUND_DISSIPATION, inplace=True)
# use gamma_n as a mask
eps_df.where(cond=~gamma_n_df.isna(), other=np.nan, inplace=True)

# bin dissipation rates
thorpe_lons = eps_df.columns.to_numpy()
max_lon = max(thorpe_lons)
min_lon = min(thorpe_lons)

# half a degree bins
#BIN_EDGES = np.arange(min_lon - 1e-3 * min_lon, 0.5 + max_lon + 1e-3 * max_lon, 0.5)
BIN_EDGES = np.arange(-53.75, -46.25, 0.5)
BIN_CENTER = BIN_EDGES[:-1]+0.25
eps_df.drop(eps_df.columns[eps_df.columns < BIN_EDGES[0]], axis="columns")
index_col = 0
# depth-level-wise (row-wise) arithmetic averaging
rows = []
for index, row in eps_df.iterrows():
    values = row.to_numpy()
    bin_means = ss.binned_statistic(x=thorpe_lons, values=values, statistic=np.nanmean, bins=BIN_EDGES)[0]
    new_eps = bin_means
    new_row = pd.DataFrame([new_eps], columns=BIN_CENTER)
    rows.append(new_row)
binned_thorpe_eps_df = pd.concat(rows, sort=False).reset_index(drop=True)
binned_thorpe_eps_df.to_csv("./method_results/binned_thorpe_dissipation.csv")
binned_thorpe_eps_df.to_csv("../../derived_data/binned_thorpe_dissipation.csv")


print("done")


def plotting():
    f, ax = plt.subplots(nrows=1, figsize=(10, 5))
    # mab_bin_edges = bin_edges(eps_strain_df.index,dz)
    # lon_edges = eps_strain_df.columns - np.diff(eps_strain_df.columns)
    mpp = ax.pcolormesh(eps_df.columns, eps_df.index, eps_df,
                        norm=mcolors.LogNorm(vmax=1e-7, vmin=1e-10),
                        shading="nearest"
                        )
    cb = plt.colorbar(mpp, ax=ax)
    cb.set_label(r"$\varepsilon$ / (W kg$^{-1}$)")
    # ax.set_facecolor('lightgrey')
    ax.set_ylim(0, 500)
    ax.set_title(r"Dissipation diagnosed from Thorpe scales")
    helper.Plot.path_as_footnote(fig=f,
                                 path="Code_to_Pinner_et_al_2025/scripts/thorpe_scales/thorpe_scales.py",
                                 rot="vertical")

    levels = [28.00, 28.26, 28.40]
    ax.contour(
        gamma_n_df.columns,
        gamma_n_df.index,
        gamma_n_df,
        levels=levels,
        colors="k",
        linewidths=1,
    )
    f.tight_layout()

#plotting()
plt.show()
