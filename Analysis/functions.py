"""
This .py file contains all functions used for the AeroSpec project.
"""
from datetime import datetime
import pandas as pd
from scipy.spatial import Voronoi, voronoi_plot_2d
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import geoplot
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib import cm as cm
import matplotlib.dates as mdates
import matplotlib.axes as ax
import contextily as ctx
from datetime import timedelta
import plotly.graph_objects as go


def plot_wrapper(df, df_users, plot_style: str, particle_size: str, public_sensors, line_or_box=None, hour_or_10=None,
                 start="9/10/2020 0:00", end="9/19/2020 0:00"):
    """
    High level plot function wrappers that calls specific plot functions specified by users
    :param df: DataFrame (FullData)
    :param df_users: DataFrame (users and corresponding device names)
    :param plot_style: Plot style (Separate, I/O Ratio, or I/G Ratio)
    :param particle_size: Size of particles (column names of df)
    :param public_sensors: list of public sensors
    :param line_or_box: Line plot or box plot
    :param hour_or_10: hour average or ten-minute average
    :return: None
    """
    if plot_style == "Separate":
        line_plots(df, df_users, particle_size, public_sensors)
    elif plot_style == "I/O Ratio":
        io_ratio(df, df_users, line_or_box, hour_or_10, particle_size, start, end)
    elif plot_style == "I/G Ratio":
        ig_ratio(df, df_users, line_or_box, particle_size, public_sensors, start, end)
    elif plot_style == "O/G Ratio":
        og_ratio(df, df_users, line_or_box, particle_size, public_sensors, start, end)
    else:
        raise ValueError("Wrong input_style. Choose either Separate, I/O Ratio, or I/G Ratio")
    return


def line_plots(df, df_users, particle_size: str, public_sensors: list):
    """
    Plots specified separate line plots
    :param df: DataFrame (FullData)
    :param df_users: DataFrame (users and corresponding device names)
    :param particle_size: Size of particles (column names of df)
    :param public_sensors: list of public sensors
    :return: None
    """
    plot_in_or_out(df, df_users, 'Out', particle_size, public_sensors)  # plot outdoor
    plot_in_or_out(df, df_users, 'In', particle_size, public_sensors)  # plot indoor
    if particle_size == "PM2.5_Std":
        plot_both(df, df_users, public_sensors)  # plot both
    return


def io_ratio(df, df_users, line_or_box, hour_or_10: str, particle_size: str, start, end):
    """
    Plots Indoor/Outdoor Ratio line plots or box plots
    :param df: DataFrame (FullData)
    :param df_users: DataFrame (users and corresponding device names)
    :param line_or_box: Line plot or box plot
    :param hour_or_10: hour average or ten-minute average
    :param particle_size: Size of particles (column names of df)
    :return: None
    """
    dfs, df_users2 = input_output_ratio(df, df_users, particle_size, start, end)
    df_final = concat_df(dfs).reset_index(drop=True)
    if hour_or_10 == "hour":
        if particle_size == "PM2.5_Std":
            df_final.to_csv('Results/IORatioStd.csv', index=False)
        elif particle_size == "PM2.5_Env":
            df_final.to_csv('Results/IORatioEnv.csv', index=False)
    elif hour_or_10 == "10":
        if particle_size == "PM2.5_Std":
            df_final.to_csv('Results/IORatio10Std.csv', index=False)
        elif particle_size == "PM2.5_Env":
            df_final.to_csv('Results/IORatio10Env.csv', index=False)
    else:
        pass
    if line_or_box == "line":
        plot_ratio(df_final, df_users2)
    elif line_or_box == "box":
        if hour_or_10 == "hour":
            boxplots(df_final, df_users2, title="I/O Ratio for Hour Average", yaxis=particle_size)
        elif hour_or_10 == "10":
            boxplots(df_final, df_users2, title="I/O Ratio for 10min Average", yaxis=particle_size)
    else:
        raise ValueError("Choose line or box")
    return


def ig_ratio(df, df_users, line_or_box, particle_size: str, public_sensors: list, start, end):
    """
    Plots Indoor/Public Sensors Ratio line plots or box plots
    :param df: DataFrame (FullData)
    :param df_users: DataFrame (users and corresponding device names)
    :param line_or_box: Line plot or box plot
    :param particle_size: Size of particles (column names of df)
    :param public_sensors: list of public sensors
    :return: None
    """
    dfs_final = []
    # locations = ["Bellevue 12th SE", "Lake Forest Park", "Seattle 10th & Weller"]
    dfs2 = input_gov_ratio(df, df_users, particle_size, public_sensors, start, end)
    for _ in dfs2:
        dfs_final.append(concat_df(_).reset_index(drop=True))
    # if particle_size == "PM2.5_Std":
    #     dfs_final[0].to_csv('Results/I_Bellevue_RatioStd.csv', index=False)
    #     dfs_final[1].to_csv('Results/I_LFP_RatioStd.csv', index=False)
    #     dfs_final[2].to_csv('Results/I_Seattle_RatioStd.csv', index=False)
    # if particle_size == "PM2.5_Env":
    #     dfs_final[0].to_csv('Results/I_Bellevue_RatioEnv.csv', index=False)
    #     dfs_final[1].to_csv('Results/I_LFP_RatioEnv.csv', index=False)
    #     dfs_final[2].to_csv('Results/I_Seattle_RatioEnv.csv', index=False)
    if line_or_box == "line":
        for count, location in enumerate(public_sensors, 0):
            plot_ratio(dfs_final[count], df_users, location)
    elif line_or_box == "box":
        for count, location in enumerate(public_sensors, 0):
            boxplots(dfs_final[count], df_users, title="Indoor/" + location + " Ratio", yaxis=particle_size)
    else:
        raise ValueError("Choose line or box")
    return


def og_ratio(df, df_users, line_or_box, particle_size: str, public_sensors: list, start, end):
    """
    Plots Outdoor/Public Sensors Ratio line plots or box plots
    :param df: DataFrame (FullData)
    :param df_users: DataFrame (users and corresponding device names)
    :param line_or_box: Line plot or box plot
    :param particle_size: Size of particles (column names of df)
    :param public_sensors: list of public sensors
    :return: None
    """
    dfs_final = []
    dfs2 = outdoor_gov_ratio(df, df_users, particle_size, public_sensors, start, end)
    for _ in dfs2:
        dfs_final.append(concat_df(_).reset_index(drop=True))
    # if particle_size == "PM2.5_Std":
    #     dfs_final[0].to_csv('Results/O_Bellevue_RatioStd.csv', index=False)
    #     dfs_final[1].to_csv('Results/O_LFP_RatioStd.csv', index=False)
    #     dfs_final[2].to_csv('Results/O_Seattle_RatioStd.csv', index=False)
    # if particle_size == "PM2.5_Env":
    #     dfs_final[0].to_csv('Results/O_Bellevue_RatioEnv.csv', index=False)
    #     dfs_final[1].to_csv('Results/O_LFP_RatioEnv.csv', index=False)
    #     dfs_final[2].to_csv('Results/O_Seattle_RatioEnv.csv', index=False)
    if line_or_box == "line":
        for count, location in enumerate(public_sensors, 0):
            plot_ratio(dfs_final[count], df_users, location, "Out")
    elif line_or_box == "box":
        for count, location in enumerate(public_sensors, 0):
            boxplots(dfs_final[count], df_users, in_or_out="Out", title="Outdoor/" + location + " Ratio",
                     yaxis=particle_size)
    else:
        raise ValueError("Choose line or box")
    return


def voronoi_geoplot(df_sub):
    """
    Draw voronoi plot on map using geoplot (unfinished).
    :param df_sub: Dataframe
    :return: None (shows plots)
    """
    geometry = [Point(xy) for xy in zip(df_sub['Longitude'], df_sub['Latitude'])]
    seattle = gpd.read_file(geoplot.datasets.get_path('contiguous_usa'))
    gdf = gpd.GeoDataFrame(df_sub, crs="EPSG:4326", geometry=geometry)
    ax = geoplot.voronoi(gdf,  # Define the GeoPandas DataFrame
                         hue='PM2.5_Std',  # df column used to color regions
                         clip=seattle,  # Define the voronoi clipping (map edge)
                         # projection=proj,  # Define the Projection
                         cmap='Reds',  # color set
                         # k=None,  # No. of discretized buckets to create
                         legend=True,  # Create a legend
                         edgecolor='white',  # Color of the voronoi boundaries
                         linewidth=0.01  # width of the voronoi boundary lines
                         )
    ctx.add_basemap(ax, crs=gdf.crs)
    geoplot.polyplot(seattle,  # Base Map
                     ax=ax,  # Axis attribute we created above
                     extent=seattle.total_bounds,  # Set plotting boundaries to base map boundaries
                     edgecolor='black',  # Color of base map's edges
                     linewidth=1,  # Width of base map's edge lines
                     zorder=1  # Plot base map edges above the voronoi regions
                     )

    plt.show()
    return


def voronoi_scipy(df):
    """
    Draw voronoi plot on map using geoplot (unfinished).
    :param df: Dataframe
    :return: None (shows plots)
    """
    fig = plt.figure()
    ax = fig.add_subplot(111)
    # m = Basemap(projection='lcc', resolution='h',
    #             lat_0=47.6, lon_0=-122.35,
    #             width=1E6, height=1.2E6,
    #             ax=ax)
    # m.shadedrelief()
    vor = Voronoi(np.column_stack((df['Longitude'], df['Latitude'])))
    norm = colors.Normalize(vmin=df['PM2.5_Std'].min(), vmax=df['PM2.5_Std'].max())
    mapper = cm.ScalarMappable(norm=norm, cmap=cm.Blues_r)
    voronoi_plot_2d(vor, show_points=True, show_vertices=False, s=1, ax=ax)
    for r in range(len(vor.point_region)):
        region = vor.regions[vor.point_region[r]]
        if not -1 in region:
            polygon = [vor.vertices[i] for i in region]
            plt.fill(*zip(*polygon), color=mapper.to_rgba(df['PM2.5_Std'].to_numpy()[r]), alpha=.7)
    plt.show()
    return


def get_device_location(df):
    """
    Organize datasets, then set coordinates, classify indoor/outdoor according to device names
    :param df: Dataframe (Raw Data)
    :return device_name: str
    :return df: cleaned DataFrame
    """
    device_name = df['Date'][0]
    df.drop([0], inplace=True)
    df.insert(0, column='Device Name', value=device_name)
    df.reset_index(drop=True, inplace=True)
    if device_name == 'Beta-01' or device_name == 'Beta-19':
        if device_name == 'Beta-01':
            df.insert(5, column='In or Out', value='Out')
        elif device_name == 'Beta-19':
            df.insert(5, column='In or Out', value='In')
        df = df.assign(Latitude='47.661273')
        df = df.assign(Longitude='-122.323842')
    if device_name == 'Beta-07' or device_name == 'Beta-17':
        if device_name == 'Beta-17':
            df.insert(5, column='In or Out', value='Out')
        elif device_name == 'Beta-07':
            df.insert(5, column='In or Out', value='In')
        df = df.assign(Latitude='47.657965')
        df = df.assign(Longitude='-122.333808')
    if device_name == 'Beta-03' or device_name == 'Beta-12':
        if device_name == 'Beta-03':
            df.insert(5, column='In or Out', value='Out')
        elif device_name == 'Beta-12':
            df.insert(5, column='In or Out', value='In')
        df = df.assign(Latitude='47.695662')
        df = df.assign(Longitude='-122.293314')
    if device_name == 'Beta-06' or device_name == 'Breakout-08':
        if device_name == 'Breakout-08':
            df.insert(5, column='In or Out', value='Out')
        elif device_name == 'Beta-06':
            df.insert(5, column='In or Out', value='In')
        df = df.assign(Latitude='47.659161')
        df = df.assign(Longitude='-122.317555')
    if device_name == 'Beta-11' or device_name == 'Beta-16' or device_name == 'Beta-14':
        if device_name == 'Beta-11' or device_name == 'Beta-14':
            df.insert(5, column='In or Out', value='In')
        elif device_name == 'Beta-16':
            df.insert(5, column='In or Out', value='Out')
        df = df.assign(Latitude='47.661519')
        df = df.assign(Longitude='-122.332354')
    if device_name == 'Beta-18' or device_name == 'Breakout-06':
        if device_name == 'Breakout-06':
            df.insert(5, column='In or Out', value='Out')
        elif device_name == 'Beta-18':
            df.insert(5, column='In or Out', value='In')
        df = df.assign(Latitude='47.664879')
        df = df.assign(Longitude='-122.27600')
    if device_name == 'Breakout-01' or device_name == 'Breakout-09' or device_name == 'Breakout-10' \
            or device_name == 'Breakout-11':
        df.insert(5, column='In or Out', value='Unknown')
    if device_name == 'Breakout-02':
        df.insert(5, column='In or Out', value='Out')
    if device_name == 'Beta-08':
        df.insert(5, column='In or Out', value='Out')
        df = df.assign(Latitude='47.653598')
        df = df.assign(Longitude='-122.304305')
    if device_name == 'Beta-13':
        df.insert(5, column='In or Out', value='In')
        df = df.assign(Latitude='47.653598')
        df = df.assign(Longitude='-122.304305')
    return device_name, df


def get_averages(df, freq: str):
    cols_average = df.columns.drop(['Device Name', 'Date', 'Time', 'PT DateTime', 'PT_AMPM', 'Battery', 'Fix',
                                    'Latitude', 'Longitude', 'In or Out'])
    df[cols_average] = df[cols_average].apply(pd.to_numeric, errors='coerce')
    if freq == "hour":
        df['PT DateTime'] = pd.to_datetime(df['PT DateTime']).dt.strftime('%Y/%m/%d %H:00')
        df_final = df.groupby(['Device Name', 'PT DateTime', 'PT_AMPM', 'Latitude', 'Longitude', 'In or Out'],
                              as_index=False)[cols_average].mean().sort_values(['PT DateTime'])
        return df_final
    else:
        df['PT DateTime'] = pd.to_datetime(df['PT DateTime'])
        df_final = df.groupby(['Device Name', pd.Grouper(key='PT DateTime', freq=freq), 'PT_AMPM', 'Latitude',
                               'Longitude', 'In or Out'])[cols_average].mean()
        df_final.reset_index(level=["Device Name", "PT DateTime", "PT_AMPM", "Latitude", "Longitude", "In or Out"],
                             inplace=True)
        return df_final


def get_hour_averages(df):
    """
    Calculate hourly averages of all columns other than 'Date','Time','Battery','Fix','Latitude','Longitude'
    :param df: DataFrame (cleaned data)
    :return df: DataFrame (with hourly averages)
    """
    cols_average = df.columns.drop(['Device Name', 'Date', 'Time', 'PT DateTime', 'PT_AMPM', 'Battery', 'Fix',
                                    'Latitude', 'Longitude', 'In or Out'])
    df[cols_average] = df[cols_average].apply(pd.to_numeric, errors='coerce')
    df['PT DateTime'] = pd.to_datetime(df['PT DateTime']).dt.strftime('%Y/%m/%d %H:00')
    df_final = df.groupby(['Device Name', 'PT DateTime', 'PT_AMPM', 'Latitude', 'Longitude', 'In or Out'],
                          as_index=False)[cols_average].mean().sort_values(['PT DateTime'])
    return df_final


def get_minute_averages(df):
    """
    (This function was not used but I kept it in case we need it in the future)
    Calculate minute averages of all columns other than 'Date','Time','Battery','Fix','Latitude','Longitude'
    :param df: DataFrame (cleaned data)
    :return df: DataFrame (with hourly averages)
    """
    cols_average = df.columns.drop(
        ['Device Name', 'Date', 'Time', 'PT DateTime', 'PT_AMPM', 'Battery', 'Fix', 'Latitude',
         'Longitude', 'In or Out'])
    df[cols_average] = df[cols_average].apply(pd.to_numeric, errors='coerce')
    df['PT DateTime'] = pd.to_datetime(df['PT DateTime'])
    df_final = df.groupby(['Device Name', 'PT DateTime', 'PT_AMPM', 'Latitude', 'Longitude', 'In or Out'],
                          as_index=False)[cols_average].mean().sort_values(['PT DateTime'])
    return df_final


def get_10min_averages(df):
    """
    Calculate ten-minute averages of all columns other than 'Date','Time','Battery','Fix','Latitude','Longitude'
    :param df: DataFrame (cleaned data)
    :return df: DataFrame (with ten-minute averages)
    """
    cols_average = df.columns.drop(
        ['Device Name', 'Date', 'Time', 'PT DateTime', 'PT_AMPM', 'Battery', 'Fix', 'Latitude',
         'Longitude', 'In or Out'])
    df[cols_average] = df[cols_average].apply(pd.to_numeric, errors='coerce')
    df['PT DateTime'] = pd.to_datetime(df['PT DateTime'])
    df_final = df.groupby(['Device Name', pd.Grouper(key='PT DateTime', freq='10Min'), 'PT_AMPM', 'Latitude',
                           'Longitude', 'In or Out'])[cols_average].mean()
    df_final.reset_index(level=["Device Name", "PT DateTime", "PT_AMPM", "Latitude", "Longitude", "In or Out"],
                         inplace=True)
    return df_final


def UTC_to_PST(df):
    """
    Convert UTC to PST
    :param df: DataFrame (cleaned data)
    :return df: DataFrame (with datetime converted to PT)
    """
    df['PT DateTime'] = pd.to_datetime(df['PT DateTime'])
    df['PT DateTime'] = pd.to_datetime(df['PT DateTime'] - timedelta(hours=7))
    df['PT DateTime'] = pd.to_datetime(df['PT DateTime'], yearfirst=True).dt.strftime('%Y/%m/%d %I:%M %p')
    return df


def reformat(df, device_name):
    """
    Remove rows with incorrect dates; add the column PT DateTime (formatted in YYYY/mm/dd HH:MM AM/PM) and add the
    column
    :param df: DataFrame (cleaned data)
    :param device_name: str
    :return df: DataFrame (reformatted data)
    """
    df.drop(df[df['Date'] == '0/0/0'].index, axis=0, inplace=True)
    df.drop(df[df['Date'].str.contains("80")].index, axis=0, inplace=True)
    df.reset_index(drop=True, inplace=True)

    df.insert(3, column='PT DateTime', value=df['Date'] + ' ' + df['Time'])
    if df[~df["PT DateTime"].str.contains("2020/")].empty is False:
        df.loc[df["PT DateTime"].str.contains("2020/") == False, "PT DateTime"] = pd.to_datetime(
            pd.to_datetime(df[~df["PT DateTime"].str.contains("2020/")]["PT DateTime"], yearfirst=True) - timedelta(
                hours=7))
    df['PT DateTime'] = pd.to_datetime(df['PT DateTime'], yearfirst=True).dt.strftime('%Y/%m/%d %I:%M %p')
    df['PT DateTime'] = df['PT DateTime'].str.replace('2005', '2020')
    # if device_name == 'Breakout-08':
    #     print("in")
    #     df = UTC_to_PST(df)
    df.insert(4, column='PT_AMPM', value=df['PT DateTime'].str.split(' ', n=2, expand=True)[2])
    return df


def concat_df(dfs: list):
    """
    Concatenate a list of Dataframe
    :param dfs: list
    :return df: DataFrame (concatenated DataFrame)
    """
    columns = dfs[0].columns
    df_final = pd.DataFrame(columns=columns)
    for i in range(len(dfs)):
        df_final = pd.concat([df_final, dfs[i]])
    return df_final


def puget_air_reformat(df, fileloc, columns):
    """
    Reformat Puget Air data to match our data's format
    :param df: DataFrame (Raw Data)
    :param fileloc: str (file location)
    :param columns:  list
    :return df: DataFrame (cleaned data)
    """
    if 'Bellevue' in fileloc:
        df.insert(0, column='Device Name', value='Bellevue SE 12th')
        df.insert(2, column='Latitude', value='47.601002')
        df.insert(3, column='Longitude', value='-122.149234')
    elif 'LakeForestPark' in fileloc:
        df.insert(0, column='Device Name', value='Lake Forest Park')
        df.insert(2, column='Latitude', value='47.753631')
        df.insert(3, column='Longitude', value='-122.277257')
    elif "Weller" in fileloc:
        df.insert(0, column='Device Name', value='Seattle 10th & Weller')
        df.insert(2, column='Latitude', value='47.597314')
        df.insert(3, column='Longitude', value='-122.3197095')
        print(df)
    df['PT DateTime'] = pd.to_datetime(df['PT DateTime']).dt.strftime("%Y/%m/%d %I:%M %p")
    df.insert(2, column='PT_AMPM', value=df['PT DateTime'].str.split(' ', n=2, expand=True)[2])
    i = 6
    for column in columns:
        if column in df.columns:
            continue
        if column == 'In or Out':
            df.insert(5, column=column, value='Out')
            continue
        df.insert(i, column=column, value=0)
        if i == 12:
            i += 1
        i += 1
    return df


def user_case(df_users, in_or_out: str, device_name: str):
    """
    Find user/owner of DataFrame/device names.
    :param df_users: DataFrame (users and corresponding device names)
    :param in_or_out: str
    :param device_name: str
    :return user: str
    """
    if device_name == 'Bellevue SE 12th' or device_name == 'Lake Forest Park' or device_name == "Seattle 10th & Weller":
        user = 'Public Sensor'
    elif device_name == 'Breakout-02':
        user = 'Moving Personal'
    else:
        if df_users[df_users[in_or_out] == device_name]['Location Number'].shape[0] == 0:
            if df_users[df_users[in_or_out] == device_name]['User'].shape[0] == 0:
                user = "Unknown"
            else:
                user = df_users[df_users[in_or_out] == device_name]['User'].values[0]
        else:
            user = df_users[df_users[in_or_out] == device_name]['Location Number'].values[0]
    return user


def plot_in_or_out(df, df_users, in_or_out: str, particle_size: str, public_sensors: list):
    """
    Plot indoor plot or outdoor plot.
    :param df: DataFrame (data to be plotted)
    :param df_users: DataFrame (users with their corresponding device names)
    :param in_or_out: Indoor or Outdoor
    :param particle_size: Size of particles (column names of df)
    :param public_sensors: list of public sensors
    :return: None (show plots)
    """
    devices = list(pd.unique(df[df['In or Out'] == in_or_out]['Device Name']))
    if in_or_out == 'In':
        for sensor in public_sensors:
            devices.append(sensor)
    else:
        devices_temp = devices
        for device in devices_temp:
            if "Beta" in device or "Breakout" in device:
                continue
            if device not in public_sensors:
                devices.remove(device)
    ymin = float('inf')
    ymax = 0

    for device in devices:
        if df[df['Device Name'] == device][particle_size].max() > ymax:
            ymax = df[df['Device Name'] == device][particle_size].max()
        if df[df['Device Name'] == device][particle_size].min() < ymin:
            ymin = df[df['Device Name'] == device][particle_size].min()

    if ymax > 500:
        ymax = 500
    fig = plt.figure()
    gs = fig.add_gridspec(len(devices), 1)
    for count, device in enumerate(devices, 0):
        ax1 = fig.add_subplot(gs[count, :])
        if device not in public_sensors:
            color = 'blue'
        else:
            color = 'red'
        plt.plot(df[df['Device Name'] == device]
                 [(df["PT DateTime"] >= "9/10/2020 0:00") & (df["PT DateTime"] <= "9/19/2020 0:00")]['PT DateTime'],
                 df[df['Device Name'] == device]
                 [(df["PT DateTime"] >= "9/10/2020 0:00") & (df["PT DateTime"] <= "9/19/2020 0:00")]
                 [particle_size], color)
        user = user_case(df_users, in_or_out, device)
        ax1.set_title(device + '\n' + user, x=1.07, y=-0.01)
        plt.ylim([ymin, ymax])
    for ax in plt.gcf().axes:
        try:
            ax.label_outer()
        except:
            pass
    fig.text(0.04, 0.5, particle_size, va='center', rotation='vertical', fontsize=20)
    plt.suptitle(in_or_out, fontsize=30)

    plt.show()
    return


def plot_both(df, df_users, public_sensors: list):
    """
    Plot both indoor plot and outdoor plot.
    :param df: DataFrame (data to be plotted)
    :param df_users: DataFrame (users with their corresponding device names)
    :param public_sensors: list of public sensors
    :return: None (show plots)
    """
    users = pd.unique(df_users['User'])
    users = np.delete(users, np.where(users == 'Charlie'))
    devices = pd.unique(df['Device Name'])
    ymin = float('inf')
    ymax = 0
    for device in devices:
        if df[df['Device Name'] == device]['PM2.5_Std'].max() > ymax:
            ymax = df[df['Device Name'] == device]['PM2.5_Std'].max()
        if df[df['Device Name'] == device]['PM2.5_Std'].min() < ymin:
            ymin = df[df['Device Name'] == device]['PM2.5_Std'].min()
    if ymax > 500:
        ymax = 500
    fig = plt.figure()
    gs = fig.add_gridspec(len(users) + 2, 1)
    for count, user in enumerate(users, 0):
        ax1 = fig.add_subplot(gs[count, :])
        if user != "Igor":
            for device in df_users[df_users['User'] == user][['In', 'Out']].values.tolist()[0]:
                if device in pd.unique(df['Device Name']):
                    plt.plot(df[df['Device Name'] == device]
                             [(df["PT DateTime"] >= "9/10/2020 0:00") & (df["PT DateTime"] <= "9/19/2020 0:00")]
                             ['PT DateTime'],
                             df[df['Device Name'] == device]
                             [(df["PT DateTime"] >= "9/10/2020 0:00") & (df["PT DateTime"] <= "9/19/2020 0:00")]
                             ['PM2.5_Std'],
                             label=df[df['Device Name'] == device]['In or Out'].values[0])
        else:
            for i in range(2):
                for device in df_users[df_users['User'] == user][['In', 'Out']].values.tolist()[i]:
                    if device in pd.unique(df['Device Name']):
                        if device == "Beta-11" or device == "Beta-14":
                            label = df[df['Device Name'] == device]['In or Out'].values[0] + " " + device
                        else:
                            label = df[df['Device Name'] == device]['In or Out'].values[0]
                        plt.plot(df[df['Device Name'] == device]
                                 [(df["PT DateTime"] >= "9/10/2020 0:00") & (df["PT DateTime"] <= "9/19/2020 0:00")]
                                 ['PT DateTime'],
                                 df[df['Device Name'] == device]
                                 [(df["PT DateTime"] >= "9/10/2020 0:00") & (df["PT DateTime"] <= "9/19/2020 0:00")]
                                 ['PM2.5_Std'],
                                 label=label)
        ax1.set_title(user, x=1.07, y=-0.01)
        plt.ylim([ymin, ymax])
        plt.legend()
    for count, device in enumerate(public_sensors, len(users)):
        ax1 = fig.add_subplot(gs[count, :])
        plt.plot(df[df['Device Name'] == device]
                 [(df["PT DateTime"] >= "9/10/2020 0:00") & (df["PT DateTime"] <= "9/19/2020 0:00")]
                 ['PT DateTime'], df[df['Device Name'] == device]
                 [(df["PT DateTime"] >= "9/10/2020 0:00") & (df["PT DateTime"] <= "9/19/2020 0:00")]
                 ['PM2.5_Std'], 'red',
                 label='Out')
        ax1.set_title(device, x=1.07, y=-0.01)
        plt.ylim([ymin, ymax])
        plt.legend()
    for ax in plt.gcf().axes:
        try:
            ax.label_outer()
        except:
            pass
    fig.text(0.04, 0.5, 'PM2.5(μg/m^3)', va='center', rotation='vertical', fontsize=20)
    plt.suptitle('Indoor v Outdoor', fontsize=30)
    plt.show()
    return


def input_output_ratio(df, df_users, particle_size: str, start, end, a=1):
    """
    Calculate Indoor/Outdoor Ratio
    :param df: DataFrame (FullData)
    :param df_users: DataFrame (Users and corresponding device names)
    :param particle_size: Size of particles (column names of df)
    :return: dfs --- list of DataFrames
             df_users: cleaned df_users
    """
    df_users = df_users[df_users['Out'].notna()].reset_index(drop=True)
    dfs = []
    for user in pd.unique(df_users['User']):
        df_temp = pd.merge(df[df['Device Name'] == df_users[df_users['User'] == user]['In'].values[0]],
                           df[df['Device Name'] == df_users[df_users['User'] == user]['Out'].values[0]],
                           on="PT DateTime")
        df_result = df_temp[['Device Name_x', 'Device Name_y', 'PT DateTime', 'PT_AMPM_x', particle_size + "_x",
                             particle_size + "_y"]]
        df_result = df_result[df_result[particle_size + "_y"] != 0]
        df_result = df_result[df_result["PT DateTime"] >= start]
        df_result = df_result[df_result["PT DateTime"] <= end]
        df_result['I/O Ratio'] = df_result[particle_size + "_x"] / (a*df_result[particle_size + "_y"])
        if df_result.empty:
            continue
        else:
            dfs.append(df_result)
    return dfs, df_users


def input_gov_ratio(df, df_users, particle_size: str, public_sensors: list, start, end):
    """
    Calculate Indoor/Public Sensors Ratio
    :param df: DataFrame (FullData)
    :param df_users: DataFrame (Users and corresponding device names)
    :param particle_size: Size of particles (column names of df)
    :param public_sensors: list of public sensors
    :return: dfs --- list of list of DataFrames
    """
    df_users = df_users[df_users['In'].notna()].reset_index(drop=True)
    dfs_temp = {}
    for device in public_sensors:
        dfs_temp[device] = []
    # dfs_temp = {"Bellevue SE 12th": [], "Lake Forest Park": [], "Seattle 10th & Weller": []}
    for device in public_sensors:
        for user in pd.unique(df_users['User']):
            df_temp = pd.merge(df[df['Device Name'] == df_users[df_users['User'] == user]['In'].values[0]],
                               df[df['Device Name'] == device],
                               on="PT DateTime")
            df_result = df_temp[['Device Name_x', 'Device Name_y', 'PT DateTime', 'PT_AMPM_x', particle_size + "_x",
                                 'PM2.5_Std_y']]
            df_result = df_result[df_result['PM2.5_Std_y'] != 0]
            df_result = df_result[df_result["PT DateTime"] >= start]
            df_result = df_result[df_result["PT DateTime"] <= end]
            df_result['I/O Ratio'] = df_result[particle_size + "_x"] / df_result['PM2.5_Std_y']
            if df_result.empty:
                continue
            else:
                dfs_temp[device].append(df_result)
    dfs = []
    for device in public_sensors:
        dfs.append(dfs_temp[device])
    # dfs = [dfs_temp["Bellevue SE 12th"], dfs_temp["Lake Forest Park"], dfs_temp["Seattle 10th & Weller"]]
    return dfs


def outdoor_gov_ratio(df, df_users, particle_size: str, public_sensors: list, start, end):
    """
    Calculate Outdoor/Public Sensors Ratio
    :param df: DataFrame (FullData)
    :param df_users: DataFrame (Users and corresponding device names)
    :param particle_size: Size of particles (column names of df)
    :param public_sensors: list of public sensors
    :return: dfs --- list of list of DataFrames
    """
    df_users = df_users[df_users['Out'].notna()].reset_index(drop=True)
    dfs_temp = {}
    for device in public_sensors:
        dfs_temp[device] = []
    for device in public_sensors:
        for user in pd.unique(df_users['User']):
            df_temp = pd.merge(df[df['Device Name'] == df_users[df_users['User'] == user]['Out'].values[0]],
                               df[df['Device Name'] == device],
                               on="PT DateTime")
            df_result = df_temp[['Device Name_x', 'Device Name_y', 'PT DateTime', 'PT_AMPM_x', particle_size + "_x",
                                 'PM2.5_Std_y']]
            df_result = df_result[df_result['PM2.5_Std_y'] != 0]
            df_result = df_result[df_result["PT DateTime"] >= start]
            df_result = df_result[df_result["PT DateTime"] <= end]
            df_result['I/O Ratio'] = df_result[particle_size + "_x"] / df_result['PM2.5_Std_y']
            if df_result.empty:
                continue
            else:
                dfs_temp[device].append(df_result)
    dfs = []
    for device in public_sensors:
        dfs.append(dfs_temp[device])
    # dfs = [dfs_temp["Bellevue SE 12th"], dfs_temp["Lake Forest Park"], dfs_temp["Seattle 10th & Weller"]]
    return dfs


def plot_ratio(df, df_users, location=None, in_or_out="In"):
    """
    Plot line plots for Indoor/Outdoor Ratio
    :param df: DataFrame (I/O Ratio)
    :param df_users: DataFrame (Users and corresponding device names)
    :param location: location name
    :param in_or_out: Indoor or Outdoor
    :return: None (shows plot)
    """
    devices = pd.unique(df['Device Name_x'])
    xmin = df['PT DateTime'].min()
    xmax = df['PT DateTime'].max()
    ymin = 0
    ymax = 3
    fig = plt.figure()
    gs = fig.add_gridspec(len(devices), 1)
    for count, device in enumerate(devices, 0):
        ax1 = fig.add_subplot(gs[count, :])
        plt.axhline(y=1, color='r', linestyle='--')
        plt.plot(df[df['Device Name_x'] == device]['PT DateTime'], df[df['Device Name_x'] == device]['I/O Ratio'],
                 'blue')
        user = user_case(df_users, in_or_out, device)
        ax1.set_title(user, x=1.07, y=-0.01)
        plt.xlim([xmin, xmax])
        plt.ylim([ymin, ymax])
    for ax in plt.gcf().axes:
        try:
            ax.label_outer()
        except:
            pass

    fig.text(0.04, 0.5, 'I/O Ratio', va='center', rotation='vertical', fontsize=20)
    if location is None:
        plt.suptitle('I/O Ratio', fontsize=20)
    else:
        plt.suptitle("Indoor/" + location + " Ratio", fontsize=20)
    plt.show()
    return


def boxplots(df, df_users, title: str, yaxis: str, in_or_out="In"):
    """
    Plot boxplots
    :param df: DataFrame (I/O Ratio)
    :param df_users: DataFrame (Users and corresponding device names)
    :param title: Plot title
    :param yaxis: Y-axis title
    :return: None (Show plots)
    """
    fig = go.Figure()
    for device in pd.unique(df["Device Name_x"]):
        user = user_case(df_users, in_or_out, device)
        fig.add_trace(
            go.Box(y=df[df["Device Name_x"] == device][df["I/O Ratio"] < 3]["I/O Ratio"].values, name=user))
        # fig.add_trace(
        #     go.Box(y=df[df["Device Name_x"] == device]["I/O Ratio"].values, name=user))
    fig.update_layout(
        title=title,
        yaxis_title=yaxis,
        yaxis=dict(
            range=[0, 3]
        ),
        paper_bgcolor='rgba(255,255,255,1)',
        plot_bgcolor='rgba(255,255,255,1)'
    )
    fig.update_xaxes(showline=True, linewidth=2, linecolor='black')
    fig.update_yaxes(showline=True, linewidth=2, linecolor='black', gridcolor='black')

    fig.show()
    return


def average(df, df_users, in_or_out: str, particle_size: str, breakout=False, start="9/10/2020 0:00",
            end= "9/19/2020 0:00"):
    """
    Outputs a new DataFrame that has the Average column
    :param df: DataFrame (FullData)
    :param df_users: DataFrame (Users and corresponding device names)
    :param in_or_out: Indoor or Outdoor
    :param particle_size: Size of particles (column names of df)
    :return: DataFrame that includes a column "Average"
    """
    df_out_users = list(set(df_users[in_or_out].dropna()))
    print(df_users[df_users["User"] == "MEB"][in_or_out])
    df_temp = df[df["Device Name"] == df_users[df_users["User"] == "MEB"][in_or_out].values[0]] \
        [(df["PT DateTime"] >= start) & (df["PT DateTime"] <= end)] \
        [["PT DateTime", particle_size]].reset_index(drop=True)
    df_temp.rename(columns={particle_size: df_users[df_users["User"] == "MEB"][in_or_out].values[0]}, inplace=True)
    for i in range(0, len(df_out_users)):
        if df_out_users[i] == "Beta-08" or df_out_users[i] == "Beta-13":
            continue
        if df_out_users[i] not in pd.unique(df["Device Name"]):
            continue
        df_temp = pd.merge(df_temp, df[df["Device Name"] == df_out_users[i]] \
            [(df["PT DateTime"] >= start) & (df["PT DateTime"] <= end)] \
            [["PT DateTime", particle_size]].reset_index(drop=True), on="PT DateTime", how="left")
        df_temp.rename(columns={particle_size: df_out_users[i]}, inplace=True)
    if breakout is True:
        df_test = df[df["Device Name"] == "Breakout-02"]
        cols_average = df_test.columns.drop(['Device Name', 'PT DateTime', 'PT_AMPM',
                                             'Latitude', 'Longitude', 'In or Out'])
        df_test = df_test.groupby(['Device Name', 'PT DateTime', 'PT_AMPM'],
                                  as_index=False)[cols_average].mean().sort_values(['PT DateTime'])
        df_temp = pd.merge(df_temp, df_test[(df_test["PT DateTime"] >= start) &
                                            (df_test["PT DateTime"] <= end)]
                           [["PT DateTime", particle_size]].reset_index(drop=True), on="PT DateTime", how="left")

    col = list(df_temp.columns)
    col.pop(0)
    df_temp["Average"] = df_temp[col].mean(axis=1)
    df_temp["Q1"] = df_temp[col].quantile(q=0.05, axis=1)
    df_temp["Q3"] = df_temp[col].quantile(q=0.95, axis=1)
    return df_temp

def individual_vs_all(df, df_users, particle_size: str, public_sensors=None
                      , end_date="9/19/2020 0:00"):
    """
    Draws subplots that plot individual sensor's air particle data against its average and public sensors' data
    :param df: DataFrame (FullData)
    :param df_users: DataFrame (Users and corresponding device names)
    :param df_ave: DataFrame (Includes Average column)
    :param particle_size: Size of particles (column names of df)
    :param in_or_out: Indoor or Outdoor
    :param public_sensors: list of public sensors
    :return: None
    """
    first = True
    plt.rc('xtick', labelsize=15)
    plt.rc('ytick', labelsize=15)
    devices = []
    devices_out = []
    igor_ = False
    igors = []
    df_devices = pd.unique(df["Device Name"])
    for device in list(df_users["In"].dropna()):
        if device in df_devices:
            if device == "Beta-11" or device == "Beta-14":
                if igor_ is False:
                    devices.append("Igor")
                    igor_ = True
                igors.append(device)
            else:
                devices.append(device)
    # for device in list(df_users["Out"].dropna()):
    #     if device in df_devices:
    #         if device not in devices_out:
    #             devices_out.append(device)


    fig = plt.figure()
    for count, device in enumerate(devices, 1):
        # fig = plt.figure()
        user_out = df_users[df_users["In"] == device]["Out"].reset_index(drop=True)[0]
        df_2 = df[(df["PT DateTime"] >= "9/10/2020 0:00") & (df["PT DateTime"] <= end_date)]
        # if device != "Igor":
        df_3 = df_2[df_2["Device Name"] == device].set_index("PT DateTime").asfreq("1H")
        df_3_out = df_2[df_2["Device Name"] == user_out].set_index("PT DateTime").asfreq("1H")
        if device == "Beta-12":
            start_date = "9/13/2020 0:00"
        else:
            start_date = "9/10/2020 0:00"
        plt.subplot(np.ceil(len(devices)/2), 2, count)
        # if device != "Breakout-02" and device != "Breakout-02 test":
        if device != "Igor":
            plt.plot(df_3.index, df_3\
                     [particle_size], label=user_case(df_users, "In", device))
        else:
            linestyle = "-"
            for igor in igors:
                df_4 = df_2[df_2["Device Name"] == igor].set_index("PT DateTime").asfreq("1H")
                plt.plot(df_4.index, df_4\
                     [particle_size], color="#1f77b4", linestyle=linestyle, label=user_case(df_users,
                                                                                                    "In", igor))
                linestyle = "-."
        plt.legend(prop={'size': 20})


        plt.plot(df_3_out.index, df_3_out[particle_size],
                 label=user_case(df_users, "Out", user_out),
                 color="purple")
        if public_sensors is not None:
            color = "#ff7f0e"
            for place in public_sensors:
                if place == "Lake Forest Park":
                    abbrev = "LFP"
                if place == "Seattle 10th & Weller":
                    abbrev = "S&W"
                plt.plot(df[df["Device Name"] == place] \
                             [(df["PT DateTime"] >= "9/10/2020 0:00") & (df["PT DateTime"] <= end_date)] \
                             ["PT DateTime"], df[df["Device Name"] == place] \
                             [(df["PT DateTime"] >= "9/10/2020 0:00") & (df["PT DateTime"] <= end_date)] \
                             ["PM2.5_Std"], color=color,label="Reference Monitor " + abbrev)
                color = "#2ca02c"
        dtfmt = mdates.DateFormatter("%m-%d")
        plt.gca().xaxis.set_major_formatter(dtfmt)

        plt.ylim([0, 450])

    fig.text(0.04, 0.5, "PM2.5 Concentration (µg/$m^{3}$)", va='center', rotation='vertical', fontsize=30)
    fig.text(0.5, 0.04, 'Date', ha='center', fontsize=30)
    plt.show()
    return


def outlier_percentage(dfs: list, df_users, fences: list, in_or_out: str):
    """
    Calculate number of each device's outliers and their percentages
    :param dfs: list of DataFrame
    :param df_users: DataFrame (Users and corresponding device names)
    :param fences: list of lists of length 2 that includes lower fence and upper fence
    :param in_or_out: Indoor or Outdoor
    :return: DataFrame that shows the number of outliers and their percentages
    """
    percentages = {"User": [], "Outliers": [], "Total": [], "Percentage": []}
    for count, df in enumerate(dfs, 0):
        outliers = df[(df["I/O Ratio"] <= fences[count][0]) | (df["I/O Ratio"] >= fences[count][1])].shape[0]
        total = df.shape[0]
        percentages["User"].append(user_case(df_users, in_or_out, pd.unique(df["Device Name_x"])[0]))
        percentages["Outliers"].append(outliers)
        percentages["Total"].append(total)
        percentages["Percentage"].append(outliers / total * 100)
    df_final = pd.DataFrame(percentages)
    return df_final


def moving_vs_static(df, df_users, particle_size, freq: str, df2=None, start="9/10/2020 0:00", end="9/19/2020 0:00"):
    df_test = df[df["Device Name"] == "Breakout-02"]
    cols_average = df_test.columns.drop(['Device Name', 'PT DateTime', 'PT_AMPM',
                                         'Latitude', 'Longitude', 'In or Out'])
    df_test = df_test.groupby(['Device Name', 'PT DateTime', 'PT_AMPM'],
                              as_index=False)[cols_average].mean().sort_values(['PT DateTime'])
    fig = plt.figure()
    plt.plot(
        df_test[(df_test["PT DateTime"] >= start) & (df_test["PT DateTime"] <= end)] \
            ["PT DateTime"], df_test \
            [(df_test["PT DateTime"] >= start) & (df_test["PT DateTime"] <= end)] \
            [particle_size], label=user_case(df_users, None, "Breakout-02")
    )

    if df2 is None:
        df2 = df

    for device in ["Beta-11", "Beta-14"]:
        plt.plot(df2[df2["Device Name"] == device] \
                     [(df2["PT DateTime"] >= start) & (df2["PT DateTime"] <= end)] \
                     ["PT DateTime"], df2[df2["Device Name"] == device] \
                     [(df2["PT DateTime"] >= start) & (df2["PT DateTime"] <= end)] \
                     [particle_size], label=user_case(df_users, "In", device) + " Indoor")
    plt.plot(df2[df2["Device Name"] == "Beta-16"] \
                 [(df2["PT DateTime"] >= start) & (df2["PT DateTime"] <= end)] \
                 ["PT DateTime"], df2[df2["Device Name"] == "Beta-16"] \
                 [(df2["PT DateTime"] >= start) & (df2["PT DateTime"] <= end)] \
                 [particle_size], label="Location 1 Outdoor")
    plt.plot(df2[df2["Device Name"] == "Seattle 10th & Weller"] \
                 [(df2["PT DateTime"] >= start) & (df2["PT DateTime"] <= end)] \
                 ["PT DateTime"], df2[df2["Device Name"] == "Seattle 10th & Weller"] \
                 [(df2["PT DateTime"] >= start) & (df2["PT DateTime"] <= end)] \
                 ["PM2.5_Std"], label="Seattle 10th & Weller")
    fmt = "%m/%d/%Y %H:%S"
    tdelta = datetime.strptime(end, fmt) - datetime.strptime(start, fmt)
    if tdelta.days > 2:
        dtfmt = mdates.DateFormatter("%m-%d")
        plt.gca().xaxis.set_major_formatter(dtfmt)
    plt.legend(prop={'size': 20})
    plt.ylim([0,250])
    plt.ylabel("PM2.5_Env Concentration", fontsize=25)
    plt.xlabel("Date", fontsize=25)
    fig.suptitle("Personal Exposure " + freq, fontsize=45)
    plt.show()
    return


def freq_comparison(df, df_10min, df_1min, particle_size: str, df2=None, additional=None,
                    start="9/10/2020 0:00", end="9/19/2020 0:00",
                    public_sensors=False):
    dfs = [df, df_10min, df_1min]
    df_tests = []
    for df in dfs:
        df_test = df[df["Device Name"] == "Breakout-02"]
        cols_average = df_test.columns.drop(['Device Name', 'PT DateTime', 'PT_AMPM',
                                             'Latitude', 'Longitude', 'In or Out'])
        df_test = df_test.groupby(['Device Name', 'PT DateTime', 'PT_AMPM'],
                                  as_index=False)[cols_average].mean().sort_values(['PT DateTime'])
        df_tests.append(df_test)
    freqs = ["Hour", "10 min", "1 min"]
    fig, ax = plt.subplots(nrows=3, ncols=1, sharex=True)
    for count, row in enumerate(ax, 0):
        row.plot(
            df_tests[count][(df_tests[count]["PT DateTime"] >= start) & (df_tests[count]["PT DateTime"] <= end)] \
                ["PT DateTime"], df_tests[count] \
                [(df_tests[count]["PT DateTime"] >= start) & (df_tests[count]["PT DateTime"] <= end)] \
                [particle_size], label="Personal Exposure"
            )
        if public_sensors:
            row.plot(
                dfs[count][dfs[count]["Device Name"] == "Seattle 10th & Weller"] \
                    [(dfs[count]["PT DateTime"] >= start) & (dfs[count]["PT DateTime"] <= end)] \
                    ["PT DateTime"], dfs[count][dfs[count]["Device Name"] == "Seattle 10th & Weller"] \
                    [(dfs[count]["PT DateTime"] >= start) & (dfs[count]["PT DateTime"] <= end)] \
                    ["PM2.5_Std"], "r", label="Seattle 10th & Weller"
                )
        if additional:
            if df2 is None:
                df2 = dfs[count]
            if additional == "Indoor 1":
                row.plot(
                    df2[df2["Device Name"] == "Beta-11"] \
                        [(df2["PT DateTime"] >= start) & (df2["PT DateTime"] <= end)] \
                        ["PT DateTime"], df2[df2["Device Name"] == "Beta-11"] \
                        [(df2["PT DateTime"] >= start) & (df2["PT DateTime"] <= end)] \
                        [particle_size], "g", label="Location 1-1 Indoor"
                    )
            elif additional == "Indoor 2":
                row.plot(
                    df2[df2["Device Name"] == "Beta-14"] \
                        [(df2["PT DateTime"] >= start) & (df2["PT DateTime"] <= end)] \
                        ["PT DateTime"], df2[df2["Device Name"] == "Beta-14"] \
                        [(df2["PT DateTime"] >= start) & (df2["PT DateTime"] <= end)] \
                        [particle_size], "orange", label="Location 1-2 Indoor"
                    )
            elif additional == "Outdoor":
                row.plot(
                    df2[df2["Device Name"] == "Beta-16"] \
                        [(df2["PT DateTime"] >= start) & (df2["PT DateTime"] <= end)] \
                        ["PT DateTime"], df2[df2["Device Name"] == "Beta-16"] \
                        [(df2["PT DateTime"] >= start) & (df2["PT DateTime"] <= end)] \
                        [particle_size], "purple", label="Location 1 Outdoor"
                    )
        row.set_title(freqs[count], size=20)
        row.set_ylim([0,250])
    fmt = "%m/%d/%Y %H:%S"
    tdelta = datetime.strptime(end, fmt) - datetime.strptime(start, fmt)
    if tdelta.days > 2:
        dtfmt = mdates.DateFormatter("%m-%d")
        plt.gca().xaxis.set_major_formatter(dtfmt)
    plt.legend()
    plt.suptitle("Personal Exposure Frequency Comparison", fontsize=45)
    fig.text(0.04, 0.5, "PM2.5 Concentration (ug/m^3)", va='center', rotation='vertical', fontsize=20)
    fig.text(0.5, 0.04, 'Date', ha='center', fontsize=20)
    plt.show()
    return


def moving_vs_static2(df, additionals: list, particle_size, freq,
                      df2=None, start="9/10/2020 0:00", end="9/19/2020 0:00"):
    plt.rc('xtick', labelsize=15)
    plt.rc('ytick', labelsize=15)
    df_test = df[df["Device Name"] == "Breakout-02"]
    cols_average = df_test.columns.drop(['Device Name', 'PT DateTime', 'PT_AMPM',
                                         'Latitude', 'Longitude', 'In or Out'])
    df_test = df_test.groupby(['Device Name', 'PT DateTime', 'PT_AMPM'],
                              as_index=False)[cols_average].mean().sort_values(['PT DateTime'])
    df_test["PT DateTime"] = pd.to_datetime(df_test["PT DateTime"])
    df_test2 = df_test[(df_test["PT DateTime"] >= start) & (df_test["PT DateTime"] <= end)]
    df_test3 = df_test2.set_index("PT DateTime").asfreq(freq)
    plt.plot(
            df_test3.index, df_test3 \
                [particle_size], linewidth=0.6, label="Personal Exposure"
            )
    start_date = datetime.strptime(start, "%m/%d/%Y %H:%M")
    end_date = datetime.strptime(end, "%m/%d/%Y %H:%M")
    plt.axvspan(start_date, start_date + timedelta(hours=6), color='grey', alpha=0.5, lw=0)
    start_date += timedelta(hours=21)
    while start_date < end_date:
        if end_date.day - start_date.day == 1:
            plt.axvspan(start_date, start_date + timedelta(hours=3), color='grey', alpha=0.5, lw=0)
        else:
            plt.axvspan(start_date, start_date + timedelta(hours=9), color='grey', alpha=0.5, lw=0)
        start_date += timedelta(days=1)

    for add in additionals:
        if add == "Indoor 1":
            color = "g"
            device = "Beta-11"
            label = "L2-a Indoor"
        if add == "Indoor 2":
            color = "orange"
            device = "Beta-14"
            label = "L2-b Indoor"
        if add == "Outdoor":
            color = "purple"
            device = "Beta-16"
            label = "L2 Outdoor"
        if add == "public":
            color = "red"
            device = "Seattle 10th & Weller"
            label = "Reference Monitor #2"
        if add == "MEB":
            color = "brown"
            device = "Beta-08"
            label = "Location 0 Indoor"
        plt.plot(
                    df2[df2["Device Name"] == device] \
                        [(df2["PT DateTime"] >= start) & (df2["PT DateTime"] <= end)] \
                        ["PT DateTime"], df2[df2["Device Name"] == device] \
                        [(df2["PT DateTime"] >= start) & (df2["PT DateTime"] <= end)] \
                        [particle_size], color, linewidth=0.6, label=label
                    )
    fmt = "%m/%d/%Y %H:%S"
    tdelta = datetime.strptime(end, fmt) - datetime.strptime(start, fmt)
    if tdelta.days > 2:
        dtfmt = mdates.DateFormatter("%m-%d")
        plt.gca().xaxis.set_major_formatter(dtfmt)
    plt.legend(prop={'size': 20})
    # plt.title("Personal Exposure (1 min) vs Placed Sensors (10 min)", fontsize=45)
    plt.ylabel("PM2.5 Concentration (µg/$m^{3}$)", fontsize=30)
    plt.xlabel('Date', fontsize=30)
    plt.ylim([0, 250])
    plt.show()
    return


def personal_1min_average(df_10sec):
    df_test = df_10sec[df_10sec["Device Name"] == "Breakout-02"]
    cols_average = df_test.columns.drop(['Device Name', 'PT DateTime', 'PT_AMPM',
                                         'Latitude', 'Longitude', 'In or Out'])
    df_test = df_test.groupby(['Device Name', 'PT DateTime', 'PT_AMPM'],
                              as_index=False)[cols_average].mean().sort_values(['PT DateTime'])
    df_test["PT DateTime"] = pd.to_datetime(df_test["PT DateTime"])
    return df_test


def correlation(df, start, end, indoor):
    if indoor == "Indoor 1":
        device = "Beta-11"
    elif indoor == "Indoor 2":
        device = "Beta-14"
    else:
        print("No indoor option selected")
        return None
    df_test = df[df["Device Name"] == "Breakout-02"]
    cols_average = df_test.columns.drop(['Device Name', 'PT DateTime', 'PT_AMPM',
                                         'Latitude', 'Longitude', 'In or Out'])
    df_test = df_test.groupby(['Device Name', 'PT DateTime', 'PT_AMPM'],
                              as_index=False)[cols_average].mean().sort_values(['PT DateTime'])
    df_test["PT DateTime"] = pd.to_datetime(df_test["PT DateTime"])

    df_corr = pd.merge(df_test[(df_test["PT DateTime"] >= start) & (df_test["PT DateTime"] <= end)] \
                       [["PT DateTime", "PM2.5_Env"]],
                       df[df["Device Name"] == device][(df["PT DateTime"] >= start) & (df["PT DateTime"] <= end)]
                       [["PT DateTime", "PM2.5_Env"]],
                       on="PT DateTime")
    # print(df_corr)
    return df_corr[["PM2.5_Env_x", "PM2.5_Env_y"]].corr()