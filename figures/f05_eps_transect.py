import warnings

import cmocean
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.markers import MarkerStyle

# Suppress specific RuntimeWarning related to mean of empty slice
warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*Mean of empty slice.*")

#plt.style.use('./paper.mplstyle')

ONE_COLUMN_WIDTH = 8.3
TWO_COLUMN_WIDTH = 12
GOLDEN_RATIO = 1.61
cm = 1 / 2.54  # centimeters in inches

plt.rcParams.update({
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
    "font.size": 9
})

#but then use the already binned version
binned_thorpe_gamma_n_df = pd.read_csv(
    "../scripts/preprocessing/method_results/binned_gamma_n.csv", index_col=0)
#binned_thorpe_gamma_n_df.set_index(keys='Unnamed: 0', inplace=True)
binned_thorpe_gamma_n_df = binned_thorpe_gamma_n_df.drop(
    binned_thorpe_gamma_n_df[binned_thorpe_gamma_n_df.index > 600].index)
binned_thorpe_gamma_n_df.columns = binned_thorpe_gamma_n_df.columns.astype("float")

binned_thorpe_eps_df = pd.read_csv(
    "../scripts/thorpe_scales/method_results/binned_thorpe_dissipation.csv", index_col=0)
binned_thorpe_eps_df.columns = binned_thorpe_eps_df.columns.astype("float")

#-------------------------------------------------------------------
# read eps_IGW results from IDEMIX method
eps_IGW_IDEMIX_df = pd.read_csv("../scripts/IDEMIX_parameterization/method_results/eps_IGW_IDEMIX_results.csv")

fig, ax = plt.subplots(1, figsize=(TWO_COLUMN_WIDTH * cm, 0.8 * TWO_COLUMN_WIDTH * cm), layout="constrained")

######################################################################## 
######################################################################## 
##################### Axis 0 ###########################################
######################################################################## 

cmap = cmocean.cm.tempo
mpp = ax.pcolormesh(
    -binned_thorpe_eps_df.columns,
    binned_thorpe_eps_df.index,
    binned_thorpe_eps_df.values,
    norm=mcolors.LogNorm(vmin=1e-10, vmax=1e-7),
    cmap=cmap,
    shading='nearest',
    rasterized=True
)

cb = plt.colorbar(mpp, ax=ax, location="top", extend="max", aspect=26)  # , aspect=40, shrink=0.8)
#cb = plt.colorbar(mpp, ax=ax, location="right", extend="max", aspect=26)  # , aspect=40, shrink=0.8)
cb.set_label(r"Dissipation rate $\varepsilon\,$(W$\,$kg$^{-1}$)")

water_mass_boundaries = [28.26, 28.40]  # + 28.00 boundary

CS = ax.contour(
    -binned_thorpe_gamma_n_df.columns,
    binned_thorpe_gamma_n_df.index,
    binned_thorpe_gamma_n_df,
    levels=water_mass_boundaries,
    linestyles=["dashed", "solid"],
    colors=["white","black"],
    linewidths=3,
    zorder=10
)
# fmt = {}
# strs = ['WSDW', 'WSBW']
# for l, s in zip(CS.levels, strs):
#     fmt[l] = s

# to be shifted in postprocessing
strs = ['WSDW', 'WSBW', "IL", "BL"]
colors = ["white", "black", "black", "xkcd:charcoal"]
for ix, (s, color) in enumerate(zip(strs, colors)):
    ax.text(0.9, 0.9-0.05*ix,s, color=color, fontsize=8, transform=ax.transAxes)


# Label every other level using strings
# clabels = ax.clabel(
#     CS,
#     CS.levels,
#     inline=False,
#     fmt=fmt,
#     colors="black",
#     fontsize=10,
#     zorder=11
# )
# # adjust bboxes for better readability
# [txt.set_bbox(dict(facecolor='lightgrey', alpha=0.8, edgecolor='darkgrey', boxstyle="round", pad=0)) for txt in clabels]

binned_regions = pd.read_csv("../scripts/preprocessing/method_results/binned_regions.csv", index_col=0)
binned_regions.columns = binned_regions.columns.astype("float") #convert column names from strings to floats
binned_regions = binned_regions.iloc[0:600]
levels = [2.5,3.5]  # Border between IL and BL
ax.contour(
    -binned_regions.columns,
    binned_regions.index,
    binned_regions.values,
    levels=levels,
    colors='xkcd:charcoal',
    linewidths=3,
    zorder=10
)

ax.scatter(
    -eps_IGW_IDEMIX_df["lon"],
    eps_IGW_IDEMIX_df["rounded mab"],
    c=eps_IGW_IDEMIX_df["eps_IGW"],
    cmap=cmap,
    norm=mcolors.LogNorm(vmin=1e-10, vmax=1e-7),
    edgecolor="black",
    marker=MarkerStyle("o"),
    s=300,
    zorder=10
)

# for the legend
# eps_IGW icon
ax.scatter(
    -eps_IGW_IDEMIX_df["lon"],
    eps_IGW_IDEMIX_df["rounded mab"],
    #c=energy_levels["eps"],
    color="tab:gray",
    edgecolor="black",
    marker=MarkerStyle("o"),
    s=200,
    zorder=-10,
    label='$\\varepsilon_{\\mathrm{IGW, IDEMIX}}$',
)

# artificial eps_total icon
ax.scatter(
    -eps_IGW_IDEMIX_df["lon"],
    eps_IGW_IDEMIX_df["rounded mab"],
    color="tab:gray",
    edgecolor="black",
    marker=MarkerStyle("s"),
    s=80,
    zorder=-10,
    label="$\\varepsilon_{\\mathrm{total, Thorpe}}$"
)

with np.load("./flowfield.npz") as data:
    xi = data['xi']
    yi = data['yi']
    avrg_v = data['avrg_v']

levels = [0.1, 0.2]
CS = ax.contour(
    -xi, yi, avrg_v,
    levels=levels,
    colors='yellow',
    linestyles=["dashed", "solid"],
    linewidths=3,
    alpha=0.8
)

# to be shifted in postprocessing
for ix, s in enumerate(levels):
    label = f"{s:.1f}" +r"$\,$m$\,$s$^{-1}$"
    ax.text(0+0.05*ix,0+0.05*ix,label, color="yellow", fontsize=7, transform=ax.transAxes)


# fmt = {}
# for l, s in zip(CS.levels, levels):
#     fmt[l] = f"{s:.1f}"
#
# clabels = ax.clabel(
#     CS,
#     CS.levels,
#     inline=True,
#     fmt=fmt,
#     fontsize=10,
#     colors='yellow',
#     zorder=11
# )

ax.legend(loc="upper left", ncol=3, columnspacing=1).set_zorder(50)
ax.set_ylim(-10, 500)
ax.invert_xaxis()
ax.set_facecolor('lightgrey')
ax.set_ylabel("Meters above bottom")
ax.set_xlabel(r"Longitude (°$\,$W)")

fig.savefig("./eps_transect.pdf")
fig.savefig("./eps_transect.svg")
plt.show()
