# CERES Visualisation Tool

This code uses Bokeh to display trends from the EBAF data from the CERES instrument <https://ceres.larc.nasa.gov>.
The main plot shows the linear trends (W/m2/decade). Clicking on a point in the plot will display the underlying anomaly data
in the lower plot.

## Requirements

* Python 2.7
* Bokeh 
* Pandas 
* xarray 
* numpy
* statsmodel
* seaborn

## Usage
Download the project.
You need to download the CERES data from <https://ceres.larc.nasa.gov/products.php?product=EBAF-TOA>.  Put this into `ceres_viz/data/`
At this point the dataset is hard-coded into main.py so must be called `CERES_EBAF-TOA_Ed2.8_Subset_200003-201605.nc` (this will change in the future).

To run the tool enter:
```
bokeh serve --show ceres_viz
```
into the command line from the parent directory.

This will launch a web browser and display the CERES SW trends on a lat/lon grid.  Clicking on a point in the map will display the underlying
anomaly data in the lower panel.

Note: the script computes trends for each 1°x1° region.  This can take some time (~2 mins) the first time you run the code.  
However, these values are stored for subsequent runs.
 
##Disclaimer
I work for SSAI, a NASA contractor on the CERES project.  This project was developed in my own time and on my own equipment.