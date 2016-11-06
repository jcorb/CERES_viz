
import xarray as xr
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
import numpy as np
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure, curdoc
from bokeh.layouts import column
import os

"""
This code uses Bokeh to display trends from the EBAF data from the CERES instrument (https://ceres.larc.nasa.gov).
The main plot shows the trends (W/m2/decade). Clicking on a point in the plot will display the underlying anomaly data
in the lower plot.

TODO:
add legend to anomaly plot
allow for multi-line plots
add colorbar
allow for choosing of the dataset that is displayed
"""

def calc_trends(df, ds_name):
    '''
    Using statsmodels calculate the trend for each lat/lon gridbox
    Input:
    '''
    X = np.arange(0, df['time'].count())
    X = sm.add_constant(X)
    y = df[ds_name]

    model = sm.OLS(y, X)
    results = model.fit()
    [a0, a1] = results.params

    return pd.Series({ds_name + '_slope': a1 * 120})

def update(attr, old, new):
    """Use the selected points from map plot add a time-series plot of the anomalies"""

    inds = np.array(new['1d']['indices'])
    lat = ceres_sw_trends['lat'][inds[0]]
    lon = ceres_sw_trends['lon'][inds[0]]
    anoms_source.data = ColumnDataSource(ceres_anomalies_df[(ceres_anomalies_df.lat==lat) & (ceres_anomalies_df.lon==lon)]).data

    return


##load data
file_path = os.path.join(os.path.dirname(__file__), './data/CERES_EBAF-TOA_Ed2.8_Subset_200003-201605.nc')
ceres_ds  = xr.open_dataset(file_path)

##create deasonalised anomalies
ceres_anomalies = ceres_ds.groupby('time.month') - ceres_ds.groupby('time.month').mean(dim='time')
ceres_anomalies_df = ceres_anomalies.to_dataframe().reset_index()

trend_path = os.path.join(os.path.dirname(__file__), './data/CERES_EBAF-TOA_Ed2.8_Subset_200003-201605.TRENDS.h5')
if os.path.exists(trend_path):
    ceres_sw_trends = pd.read_hdf(trend_path, 'trends', mode='r')
else:
    print 'calculating trends'
    ##calculate trends and save a copy locally to reduce re-computation time
    ceres_sw_trends = ceres_anomalies_df.groupby(['lat', 'lon']).apply(calc_trends, 'toa_sw_all_mon').reset_index()
    ceres_sw_trends.to_hdf(trend_path, 'trends', format='fixed', mode='w')
    print 'done'


##map trend values to colors -> using a diverging colormap
cmap = sns.color_palette('PuOr_r', 13).as_hex()
bins = [-1000, -11, -9, -7, -5, -3, -1, 1, 3, 5, 7, 9, 11, 1000]
ceres_sw_trends['color'] = pd.cut(ceres_sw_trends['toa_sw_all_mon_slope'], bins=bins, labels=cmap)
trends_cds = ColumnDataSource(ceres_sw_trends)
trends_cds.on_change('selected', update)
## main map figure
TOOLS = "pan,wheel_zoom,box_zoom,reset,hover,tap"
world = figure(plot_width=900, plot_height=450, tools=TOOLS,
               title='CERES SW TOA Flux Trends',
               x_range=[0, 360],
               y_range=[-90, 90])

world.xaxis.axis_label = 'Longitude'
world.yaxis.axis_label = 'Latitude'
world.grid.grid_line_color = None
rect_glyph = world.rect('lon', 'lat', 1, 1, source=trends_cds,
                        color='color', line_color=None,
                        nonselection_color='color',
                        nonselection_alpha=1.0)

hover = world.select_one(HoverTool)
hover.point_policy = "follow_mouse"
hover.tooltips = [
    ("Trend", "@toa_sw_all_mon_slope W/m2/decade"),
    ("(Lon, Lat)", "(@lon, @lat)"),
]

## anomaly plot
anoms_source = ColumnDataSource(data=dict(lat=[], lon=[], time=[], toa_sw_all_mon=[], toa_lw_all_mon=[], toa_net_all_mon=[]))
anom_plot = figure(plot_width=900, plot_height=250, x_axis_type='datetime', tools='reset')
anom_plot.line('time', 'toa_sw_all_mon', source=anoms_source, color='cadetblue')
anom_plot.yaxis.axis_label = 'Flux (W/m2)'

layout = column(world, anom_plot)
curdoc().add_root(layout)
curdoc().title = "CERES Visualisation"
