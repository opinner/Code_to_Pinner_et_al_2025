[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.13134608.svg)](https://doi.org/10.5281/zenodo.13134608)
[![DOI](https://img.shields.io/badge/Paper--DOI%20-%2010.5194%2Fos--21--701--2025%20-%20%23f3d50d)](https://doi.org/10.5194/os-21-701-2025)  
[![output data regression test](https://github.com/opinner/Pinner_et_al_2025/actions/workflows/output_regression_tests.yml/badge.svg)](https://github.com/opinner/Pinner_et_al_2025/actions/workflows/output_regression_tests.yml)

## Analysis code to the publication: 
# [Pinner et al., 2025](https://doi.org/10.5194/os-21-701-2025)
# [*Internal-wave-induced dissipation rates <br> in the Weddell Sea Bottom Water gravity current*](https://doi.org/10.5194/os-21-701-2025)
<img src="https://os.copernicus.org/articles/21/701/2025/os-21-701-2025-avatar-web.png" align="right" height="300"/>

The Weddell Sea Bottom Water gravity current transports dense water from the continental shelf to the deep sea and is crucial for the formation of new deep-sea water. Building on vertical profiles and time series measured in the northwestern Weddell Sea, we apply three methods to distinguish turbulence caused by internal waves from that by other sources. We find that in the upper part of the gravity current, internal waves are important for the mixing of less dense water down into the current.

## Derived Quantities
The most important derived quantities are 3 transects across the continental slope of near-bottom dissipation rates:

- **Total dissipation rate** $\pmb{\varepsilon}_\textbf{total, Thorpe}$  
Derived from CTD profiles and the Thorpe scale approach

- **Wave-induced dissipation rate** $\pmb{\varepsilon}_\textbf{IGW, fine}$  
Derived from CTD profiles and the strain-based finestructure method

- **Wave-induced dissipation rate** $\pmb{\varepsilon}_\textbf{IGW, IDEMIX}$  
Derived from velocity timeseries and parameterization from squared wave energy.

All data sets are saved as `.csv` files in the `derived_data` folder, with the vertical coordinate `meters above the seafloor` and horizontal coordinate `longitude`. Examples of use are shown in `derived_data/examples.ipynb`. 


```mermaid
flowchart TD
    subgraph **In situ Measurements**
        %% CTD@{shape: cyl, label: "IBSCO
        %% bathymetry" }
        %% CTD[bathy]
        CTD@{shape: cyl, label: "CTD
        profiles" }
        %% A2[CTD]
        %% CTD2@{shape: cyl, label: "CTD
        %% profiles" }
        A3@{shape: cyl, label: "velocity
        time series" }
        %% A3[series]
    end

    subgraph **Pre-processing**
        CTD --> matlab[[""eos80_legacy_gamma_n matlab toolbox""]]
        CTD --> Nsquared[["GSW toolbox"]]
        matlab --> gamma["Neutral Density γⁿ"]
        Nsquared --> strat[Stratification N²]
    end

    subgraph **Spectral Analysis**
        A3 --> multitaper[[Multitaper]]
        multitaper --> spectrum[Energy spectra]
    end

    strat --> Thorpe
    strat --> fine
    strat --> idemix
    gamma --> region

subgraph **Turbulence Quantification**
    %% CTD --> idemix[[wave energy/IDEMIX parameterization]]
    spectrum --> idemix[[wave energy/IDEMIX parameterization]]

    fine[[Fine-structure]]
    gamma --> Thorpe[[Thorpe Scales]]
    %% TS --> fine[[finestructure]]
    %% TS --> Thorpe[[Thorpe scales]]
end

    subgraph **Derived Datasets**
        region[Region mask]
        fine --> epsfine["ε_{IGW, fine}"]
        Thorpe --> epstotal["ε_{total}"]
        idemix --> epsidemix["ε_{IGW, IDEMIX}"]
        A3-->M[Flowfield]
    end
```

## Reproducibility

Reproducing these works is unfortunately not straight forward, depending on your expertise. Multiple intermediate steps are needed to go from raw data to results. For example, I used a Matlab script to calculate neutral densities for all CTD profiles. Additionally, some of data files are not read in as `.csv` but as `.mat` files, due to early collaboration in the analysis. PS129 data is of right now unpublished and not yet converted into a neatly organized data set. 

The high-level requirements are given in `requirements.txt`, with my complete python enviroment detailed in `enviroment.yaml`, and can be reinstalled by the installer/enviroment manager of your choice (pip, conda, etc.), for example by `conda create --file requirements.txt`.

## Disclaimer
> [!IMPORTANT]  
> - Although this code produces the results and figures to the accompanying paper, this repository occasionally contains unused code snippets and partial documentation. 
> - Comments or corrections to the code can be given on GitHub as issues.  
> - Note that figures created here can differ slightly from the published versions, as some post-processing (adjustements and labeling) were made with *Inkscape*. 
