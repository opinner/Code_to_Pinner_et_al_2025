import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors
import pandas as pd
import scipy.stats as ss
from matplotlib.markers import MarkerStyle
import cmocean
cmap = cmocean.cm.tempo

ONE_COLUMN_WIDTH = 8.3
TWO_COLUMN_WIDTH = 12
GOLDEN_RATIO = 1.61
cm = 1/2.54  # centimeters in inches

# read data
#-------------------------------------------------------------------
data = np.load("/home/ole/Desktop/Mooring_Analysis/energy_levels/data/Thorpe_result.npz", allow_pickle=True)
mab = data["mab"]

energy_levels = pd.read_csv("/home/ole/Desktop/Mooring_Analysis/energy_levels/wave_energy_result.csv")

eps_df = pd.read_pickle("/home/ole/Desktop/Mooring_Analysis/energy_levels/data/Thorpe_eps_df.pkl")
T_df = pd.read_pickle("/home/ole/Desktop/Mooring_Analysis/energy_levels/data/Thorpe_T_df.pkl")

#TODO!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!TODO#
eps_df = eps_df*2.694 #Correction from Rw =3 to Rw = 7 of the strain-only parametrization
#TODO!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!TODO#

# add background dissipation, but only where there is temperature data
BACKGROUND_DISSIPATION = 1e-10 #value taken from Hirano et al 2015
eps_df.fillna(value = BACKGROUND_DISSIPATION, inplace = True)
eps_df.where(cond = ~T_df.isna(), other = np.nan, inplace = True)

lons = eps_df.columns.to_numpy()
max_lon = max(lons)
min_lon = min(lons)
NUMBER_OF_BINS = 20
BIN_EDGES = np.linspace(min_lon-1e-3*min_lon, max_lon+1e-3*max_lon, NUMBER_OF_BINS + 1)

# depth-level-wise (row-wise) arithmetic averaging
rows = []
for index, row in eps_df.iterrows():
    values = row.to_numpy()
    bin_means= ss.binned_statistic(x = lons, values = values, statistic=np.nanmean, bins = BIN_EDGES)[0]
    new_eps = bin_means
    new_row = pd.DataFrame([new_eps], columns = BIN_EDGES[:-1])
    rows.append(new_row)
binned_eps_df = pd.concat(rows, sort = False).reset_index(drop = True)

rows = []
for index, row in T_df.iterrows():
    values = row.to_numpy()
    bin_means= ss.binned_statistic(x = lons, values = values, statistic=np.nanmean, bins = BIN_EDGES)[0]
    new_row = pd.DataFrame([bin_means], columns = BIN_EDGES[:-1])
    rows.append(new_row)

binned_T_df = pd.concat(rows, sort = False).reset_index(drop = True)
#-------------------------------------------------------------------


fig,ax = plt.subplots(1, figsize=(TWO_COLUMN_WIDTH*cm, 0.8*TWO_COLUMN_WIDTH*cm))


######################################################################## 
######################################################################## 
##################### Axis 0 ###########################################
######################################################################## 
"""
def fexp(f):
    return int(np.floor(np.log10(abs(f)))) if f != 0 else 0
def fman(f):
    return f/10**fexp(f)
def generate_pattern(start, end):
    num_steps = (end - start) * 2  # Each step/order of magnitude has a multiplier of 1 and 5 e.g. 5 \times 10^{-8}
    return [multiplier * 10**(start + i // 2) for i, multiplier in enumerate([1, 5] * (num_steps + 1)) if start + i // 2 <= end]

# Start and stop order of magnitude:
start_point = -10
end_point = -7
bounds = generate_pattern(start_point, end_point)[:-1]
ncolors = len(bounds) - 1
#cmap = plt.cm.get_cmap('viridis', ncolors)
norm = mcolors.BoundaryNorm(boundaries=bounds, ncolors= 256)
"""
mpp = ax.pcolormesh(
    binned_eps_df.columns, 
    mab, 
    binned_eps_df,
    norm = mcolors.LogNorm(vmin=1e-10, vmax=1e-6), #TODO
    cmap = cmap,
    rasterized = True
)
"""
cb = plt.colorbar(mpp, ax = ax, location = "right")#, aspect = 40, shrink = 0.8)
cb.set_label(r"Dissipation rate $\varepsilon\,$(W kg$^{-1}$)")
print(cb.ax.get_xticklabels(), len(cb.ax.get_xticklabels()))
assert cb.ax.get_xticklabels()
cb.ax.set_xticklabels([f'{fman(b):.0f}$\\times10^{{{fexp(b):.0f}}}$' for b in bounds])
"""

cb = plt.colorbar(mpp, ax=ax, location="top")  # , aspect=40, shrink=0.8)
cb.set_label(r"Dissipation rate $\varepsilon\,$(W kg$^{-1}$)")

# Draw gravity courrent boundary defined as the -0.7 °C isotherm (Fahrbach 2001 et al.) 
ax.contour(
    binned_T_df.columns, 
    mab, 
    binned_T_df,
    levels = [-0.7],
    colors = "k",
    linewidths = 3,
)

ax.scatter(
    energy_levels["lon"],
    energy_levels["mab"]+5,
    c=energy_levels["eps_IW"],
    cmap = cmap,
    norm = mcolors.LogNorm(vmin=1e-10, vmax=1e-6), #TODO
    edgecolor="black",
    marker=MarkerStyle("o", fillstyle="left"),
    s = 300,
    zorder = 10
)


ax.scatter(
    energy_levels["lon"],
    energy_levels["mab"]+5,
    c=energy_levels["eps"],
    cmap = cmap,
    norm = mcolors.LogNorm(vmin=1e-10, vmax=1e-6), #TODO
    edgecolor="black",
    marker=MarkerStyle("o", fillstyle="right"),
    s = 300,
    zorder = 10
)

ax.set_facecolor('lightgrey')
ax.set_ylabel("Meters above bottom")
ax.set_xlabel("Longitude (°)")
#ax[0].set_title(r"Dissipation rate $\varepsilon$ across the slope")


ax.scatter(
    energy_levels["lon"],
    energy_levels["mab"]+5,
    #c=energy_levels["eps_IW"],
    color = "tab:gray",
    edgecolor="black",
    marker=MarkerStyle("o", fillstyle="left"),
    s = 200,
    zorder = -10,
    label = "$\\varepsilon_{\\mathrm{IGW}}$",
)

ax.scatter(
    energy_levels["lon"],
    energy_levels["mab"]+5,
    #c=energy_levels["eps"],
    color = "tab:gray",
    edgecolor="black",
    marker=MarkerStyle("o", fillstyle="right"),
    s = 200,
    zorder = -10,    
    label = "$\\varepsilon_{\\mathrm{IGW + tides}}$",
)

ax.scatter(
    energy_levels["lon"],
    energy_levels["mab"]+5,
    color = "tab:gray",
    edgecolor="black",
    marker=MarkerStyle("s"),
    s = 80,
    zorder = -10,
    label = "$\\varepsilon_{\\mathrm{total}}$"
)


ax.legend(loc = "upper left", ncol=3, columnspacing=1)
ax.annotate('gravity current\nboundary', xy=(-48.8, 130), xytext=(-48.5, 270), #fontsize=9,
            arrowprops = dict(facecolor='black', width = 2, shrink=0.05), ha = "center", va = "center", color = "white", bbox=dict(facecolor='black', alpha = 0.8, edgecolor='black', boxstyle='round, pad = 0.5'))

            
fig.tight_layout()
fig.savefig("./eps_transect.svg", bbox_inches = "tight")
fig.savefig("./eps_transect.png", dpi = 400, bbox_inches = "tight")
plt.show()







   





