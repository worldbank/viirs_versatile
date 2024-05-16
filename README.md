# viirs_versatile (VIIRS versatile downloader and analyzer)
VIIRS downloader and analyzer using Google Earth Engine (GEE) with a complete Pythonic approach. This pipeline is for downloading the [VIIRS Stray Light Corrected Nighttime Day/Night Band Composites Version 1](https://developers.google.com/earth-engine/datasets/catalog/NOAA_VIIRS_DNB_MONTHLY_V1_VCMSLCFG) dataset from GEE. It also provides basic time-series statistics of the VIIRS NTL intensity within specified zonal AOIs. As a default, the World Bank official admin 0 and admin 1 boundaries are available for a quick analysis. Due to the large file size, the World Bank admin 2 Shapefile is not included in this package. Please prepare your own admin 2 ESRI shapefile.

All Jupyter notebooks are optimized for the [Google Colab](https://colab.google/) environment. The pre-processing of monthly VIIRS data in an X-array dataset is memory-heavy. Hence, if you want to work with countries with large area sizes, you likely need to upgrade your Google Colab account from a free to a paid one.

## Structure of the pipeline
- `VIIRS_downloader.ipynb` : Download VIIRS rater images from GEE
- `VIIRS_analyzer.ipynb` : Pre-process the VIIRS images and compute zonal stats
- `data` : This directory will contain all relevant materials and products

NOTE: For reference, the package includes the raw NTL raster images and process results of Switzerland (CHE). You can just delete them if you want to save your strage space.

## Quick start:
(1) Copy and paste all materials to your own Google Colab environment. If you are good at Python coding, a new Conda environment could also work but you likely need to modify some code blocks (especially around libraries and paths).

(2) Start with `VIIRS_downloader.ipynb` to first download the VIIRS raster images for your AOI from GEE.

(3) Once all raster images are downloaded, go to `VIIRS_analyzer.ipynb` to reduce anomaly pixels and compute zonal statistics within your AOI zones.


## Technical notes:
- `VIIRS_analyzer.ipynb` has an anomaly-NTL pixel reduction process (`Anomaly NTL pixels reduction (background noise and max anomalies)`) based on the NTL background noise mask (average_masked in [VIIRS Nighttime Day/Night Annual Band Composites V2.1](https://developers.google.com/earth-engine/datasets/catalog/NOAA_VIIRS_DNB_ANNUAL_V21#bands)) and the avg_rad < 300 max-cap threshold. This process should be run before the other filtering processes.

Fig. Anomaly pixel reduction result of Switzerland (CHE), example

![Anomaly pixel reduction result of Switzerland, CHE](/data/fig/spatial_visualization_of_anomalyReduction.png)

## Contributors
Eigo Tateishi (main coder)

The World Bank (2024)
