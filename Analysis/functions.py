"""
This .py file contains all functions used for the AeroSpec project.
"""

import pandas as pd
from scipy.spatial import Voronoi, voronoi_plot_2d
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import geoplot
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib import cm as cm
import contextily as ctx
from datetime import timedelta
import plotly.graph_objects as go


def plot_wrapper(df, df_users, plot_style: str, particle_size: str, line_or_box=None, hour_or_10=None):
    """
    High level plot function wrappers that calls specific plot functions specified by users
    :param df: DataFrame (FullData)
    :param df_users: DataFrame (users and corresponding device names)
    :param plot_style: Plot style (Separate, I/O Ratio, or I/G Ratio)
    :param particle_size: Size of particles (column names of df)
    :param line_or_box: Line plot or box plot
    :param hour_or_10: hour average or ten-minute average
    :return: None
    """
    if plot_style == "Separate":
        line_plots(df, df_users, particle_size)
    elif plot_style == "I/O Ratio":
        io_ratio(df, df_users, line_or_box, hour_or_10, particle_size)
    elif plot_style == "I/G Ratio":
        ig_ratio(df, df_users, line_or_box, particle_size)
    elif plot_style == "O/G Ratio":
        og_ratio(df, df_users, line_or_box, particle_size)
    else:
        raise ValueError("Wrong input_style. Choose either Separate, I/O Ratio, or I/G Ratio")
    return


def line_plots(df, df_users, particle_size: str):
    """
    Plots specified separate line plots
    :param df: DataFrame (FullData)
    :param df_users: DataFrame (users and corresponding device names)
    :param particle_size: Size of particles (column names of df)
    :return: None
    """
    plot_in_or_out(df, df_users, 'Out', particle_size)  # plot outdoor
    plot_in_or_out(df, df_users, 'In', particle_size)  # plot indoor
    if particle_size == "PM2.5_Std":
        plot_both(df, df_users)  # plot both
    return


def io_ratio(df, df_users, line_or_box, hour_or_10: str, particle_size: str):
    """
    Plots Indoor/Outdoor Ratio line plots or box plots
    :param df: DataFrame (FullData)
    :param df_users: DataFrame (users and corresponding device names)
    :param line_or_box: Line plot or box plot
    :param hour_or_10: hour average or ten-minute average
    :param particle_size: Size of particles (column names of df)
    :return: None
    """
    dfs, df_users2 = input_output_ratio(df, df_users, particle_size)
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


def ig_ratio(df, df_users, line_or_box, particle_size: str):
    """
    Plots Indoor/Public Sensors Ratio line plots or box plots
    :param df: DataFrame (FullData)
    :param df_users: DataFrame (users and corresponding device names)
    :param line_or_box: Line plot or box plot
    :param particle_size: Size of particles (column names of df)
    :return: None
    """
    dfs_final = []
    locations = ["Bellevue 12th SE", "Lake Forest Park", "Seattle 10th & Weller"]
    dfs2 = input_gov_ratio(df, df_users, particle_size)
    for _ in dfs2:
        dfs_final.append(concat_df(_).reset_index(drop=True))
    if particle_size == "PM2.5_Std":
        dfs_final[0].to_csv('Results/I_Bellevue_RatioStd.csv', index=False)
        dfs_final[1].to_csv('Results/I_LFP_RatioStd.csv', index=False)
        dfs_final[2].to_csv('Results/I_Seattle_RatioStd.csv', index=False)
    if particle_size == "PM2.5_Env":
        dfs_final[0].to_csv('Results/I_Bellevue_RatioEnv.csv', index=False)
        dfs_final[1].to_csv('Results/I_LFP_RatioEnv.csv', index=False)
        dfs_final[2].to_csv('Results/I_Seattle_RatioEnv.csv', index=False)
    if line_or_box == "line":
        for count, location in enumerate(locations, 0):
            plot_ratio(dfs_final[count], df_users, location)
    elif line_or_box == "box":
        for count, location in enumerate(locations, 0):
            boxplots(dfs_final[count], df_users, title="Indoor/" + location + " Ratio", yaxis=particle_size)
    else:
        raise ValueError("Choose line or box")
    return


def og_ratio(df, df_users, line_or_box, particle_size: str):
    """
    Plots Outdoor/Public Sensors Ratio line plots or box plots
    :param df: DataFrame (FullData)
    :param df_users: DataFrame (users and corresponding device names)
    :param line_or_box: Line plot or box plot
    :param particle_size: Size of particles (column names of df)
    :return: None
    """
    dfs_final = []
    locations = ["Bellevue 12th SE", "Lake Forest Park", "Seattle 10th & Weller"]
    dfs2 = outdoor_gov_ratio(df, df_users, particle_size)
    for _ in dfs2:
        dfs_final.append(concat_df(_).reset_index(drop=True))
    if particle_size == "PM2.5_Std":
        dfs_final[0].to_csv('Results/O_Bellevue_RatioStd.csv', index=False)
        dfs_final[1].to_csv('Results/O_LFP_RatioStd.csv', index=False)
        dfs_final[2].to_csv('Results/O_Seattle_RatioStd.csv', index=False)
    if particle_size == "PM2.5_Env":
        dfs_final[0].to_csv('Results/O_Bellevue_RatioEnv.csv', index=False)
        dfs_final[1].to_csv('Results/O_LFP_RatioEnv.csv', index=False)
        dfs_final[2].to_csv('Results/O_Seattle_RatioEnv.csv', index=False)
    if line_or_box == "line":
        for count, location in enumerate(locations, 0):
            plot_ratio(dfs_final[count], df_users, location, "Out")
    elif line_or_box == "box":
        for count, location in enumerate(locations, 0):
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
    # df_final2 = df.resample("10Min", on="PT DateTime").groupby(['Device Name', 'PT_AMPM', 'Latitude',
    #                        'Longitude', 'In or Out'], as_index=False)[cols_average].mean()
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
    df['PT DateTime'] = pd.to_datetime(df['PT DateTime'], yearfirst=True).dt.strftime('%Y/%m/%d %I:%M %p')
    df['PT DateTime'] = df['PT DateTime'].str.replace('2005', '2020')
    if device_name == 'Breakout-08':
        df = UTC_to_PST(df)
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
        user = 'Igor'
    else:
        if df_users[df_users[in_or_out] == device_name]['User'].shape[0] == 0:
            user = 'Unknown'
        else:
            user = df_users[df_users[in_or_out] == device_name]['User'].values[0]
    return user


def plot_in_or_out(df, df_users, in_or_out: str, particle_size: str):
    """
    Plot indoor plot or outdoor plot.
    :param df: DataFrame (data to be plotted)
    :param df_users: DataFrame (users with their corresponding device names)
    :param in_or_out: Indoor or Outdoor
    :param particle_size: Size of particles (column names of df)
    :return: None (show plots)
    """
    devices = pd.unique(df[df['In or Out'] == in_or_out]['Device Name'])
    if in_or_out == 'In':
        devices = np.append(devices, ['Bellevue SE 12th', 'Lake Forest Park'])
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
        if device not in ['Bellevue SE 12th', 'Lake Forest Park']:
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


def plot_both(df, df_users):
    """
    Plot both indoor plot and outdoor plot.
    :param df: DataFrame (data to be plotted)
    :param df_users: DataFrame (users with their corresponding device names)
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
    for count, device in enumerate(['Bellevue SE 12th', 'Lake Forest Park'], len(users)):
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


def input_output_ratio(df, df_users, particle_size: str):
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
        df_result = df_result[df_result["PT DateTime"] >= "9/10/2020 0:00"]
        df_result = df_result[df_result["PT DateTime"] <= "9/19/2020 0:00"]
        df_result['I/O Ratio'] = df_result[particle_size + "_x"] / df_result[particle_size + "_y"]
        if df_result.empty:
            continue
        else:
            dfs.append(df_result)
    return dfs, df_users


def input_gov_ratio(df, df_users, particle_size: str):
    """
    Calculate Indoor/Public Sensors Ratio
    :param df: DataFrame (FullData)
    :param df_users: DataFrame (Users and corresponding device names)
    :param particle_size: Size of particles (column names of df)
    :return: dfs --- list of list of DataFrames
    """
    df_users = df_users[df_users['In'].notna()].reset_index(drop=True)
    dfs_temp = {"Bellevue SE 12th": [], "Lake Forest Park": [], "Seattle 10th & Weller": []}
    for device in ["Bellevue SE 12th", "Lake Forest Park", "Seattle 10th & Weller"]:
        for user in pd.unique(df_users['User']):
            df_temp = pd.merge(df[df['Device Name'] == df_users[df_users['User'] == user]['In'].values[0]],
                               df[df['Device Name'] == device],
                               on="PT DateTime")
            df_result = df_temp[['Device Name_x', 'Device Name_y', 'PT DateTime', 'PT_AMPM_x', particle_size + "_x",
                                 'PM2.5_Std_y']]
            df_result = df_result[df_result['PM2.5_Std_y'] != 0]
            df_result = df_result[df_result["PT DateTime"] >= "9/10/2020 0:00"]
            df_result = df_result[df_result["PT DateTime"] <= "9/19/2020 0:00"]
            df_result['I/O Ratio'] = df_result[particle_size + "_x"] / df_result['PM2.5_Std_y']
            if df_result.empty:
                continue
            else:
                dfs_temp[device].append(df_result)

    dfs = [dfs_temp["Bellevue SE 12th"], dfs_temp["Lake Forest Park"], dfs_temp["Seattle 10th & Weller"]]
    return dfs


def outdoor_gov_ratio(df, df_users, particle_size: str):
    """
    Calculate Outdoor/Public Sensors Ratio
    :param df: DataFrame (FullData)
    :param df_users: DataFrame (Users and corresponding device names)
    :param particle_size: Size of particles (column names of df)
    :return: dfs --- list of list of DataFrames
    """
    df_users = df_users[df_users['Out'].notna()].reset_index(drop=True)
    dfs_temp = {"Bellevue SE 12th": [], "Lake Forest Park": [], "Seattle 10th & Weller": []}
    for device in ["Bellevue SE 12th", "Lake Forest Park", "Seattle 10th & Weller"]:
        for user in pd.unique(df_users['User']):
            df_temp = pd.merge(df[df['Device Name'] == df_users[df_users['User'] == user]['Out'].values[0]],
                               df[df['Device Name'] == device],
                               on="PT DateTime")
            df_result = df_temp[['Device Name_x', 'Device Name_y', 'PT DateTime', 'PT_AMPM_x', particle_size + "_x",
                                 'PM2.5_Std_y']]
            df_result = df_result[df_result['PM2.5_Std_y'] != 0]
            df_result = df_result[df_result["PT DateTime"] >= "9/10/2020 0:00"]
            df_result = df_result[df_result["PT DateTime"] <= "9/19/2020 0:00"]
            df_result['I/O Ratio'] = df_result[particle_size + "_x"] / df_result['PM2.5_Std_y']
            if df_result.empty:
                continue
            else:
                dfs_temp[device].append(df_result)
    dfs = [dfs_temp["Bellevue SE 12th"], dfs_temp["Lake Forest Park"], dfs_temp["Seattle 10th & Weller"]]
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
        yaxis_title=yaxis
    )

    fig.show()
    return


def average(df, df_users, in_or_out: str, particle_size: str):
    """
    Outputs a new DataFrame that has the Average column
    :param df: DataFrame (FullData)
    :param df_users: DataFrame (Users and corresponding device names)
    :param in_or_out: Indoor or Outdoor
    :param particle_size: Size of particles (column names of df)
    :return: DataFrame that includes a column "Average"
    """
    df_out_users = list(df_users[in_or_out].dropna())
    df_temp = df[df["Device Name"] == df_out_users[0]] \
        [(df["PT DateTime"] >= "9/10/2020 0:00") & (df["PT DateTime"] <= "9/19/2020 0:00")] \
        [["PT DateTime", particle_size]].reset_index(drop=True)
    df_temp.rename(columns={particle_size: df_out_users[0]}, inplace=True)

    for i in range(1, len(df_out_users)):
        if df_out_users[i] not in pd.unique(df["Device Name"]) or \
                df_out_users[i] == "Beta-01" or df_out_users[i] == "Beta-12":
            continue
        df_temp = pd.merge(df_temp, df[df["Device Name"] == df_out_users[i]] \
            [(df["PT DateTime"] >= "9/10/2020 0:00") & (df["PT DateTime"] <= "9/19/2020 0:00")] \
            [["PT DateTime", particle_size]].reset_index(drop=True), on="PT DateTime")
        df_temp.rename(columns={particle_size: df_out_users[i]}, inplace=True)

    col = list(df_temp.columns)
    col.pop(0)
    df_temp["Average"] = df_temp[col].mean(axis=1)
    return df_temp


def individual_vs_all(df, df_users, df_ave, particle_size: str, in_or_out: str, hour_or_10: str, public_sensor=True):
    """
    Draws subplots that plot individual sensor's air particle data against its average and public sensors' data
    :param df: DataFrame (FullData)
    :param df_users: DataFrame (Users and corresponding device names)
    :param df_ave: DataFrame (Includes Average column)
    :param particle_size: Size of particles (column names of df)
    :param in_or_out: Indoor or Outdoor
    :param hour_or_10: Hour average or 10-min average
    :param public_sensor: Includes public sensors data or no
    :return: None
    """
    devices = []
    for device in list(df_users[in_or_out].dropna()):
        if device in pd.unique(df["Device Name"]):
            devices.append(device)
    for count, device in enumerate(devices, 1):
        plt.subplot(np.ceil(len(devices)/2), 2, count)
        plt.plot(df[df["Device Name"] == device] \
                     [(df["PT DateTime"] >= "9/10/2020 0:00") & (df["PT DateTime"] <= "9/19/2020 0:00")] \
                     ["PT DateTime"], df[df["Device Name"] == device] \
                     [(df["PT DateTime"] >= "9/10/2020 0:00") & (df["PT DateTime"] <= "9/19/2020 0:00")] \
                     [particle_size], label=user_case(df_users, in_or_out, device))
        plt.plot(df_ave["PT DateTime"], df_ave["Average"], "--", label="Average", color="purple")
        if public_sensor is True:
            for place in ["Bellevue SE 12th", "Lake Forest Park", "Seattle 10th & Weller"]:
                plt.plot(df[df["Device Name"] == place] \
                             [(df["PT DateTime"] >= "9/10/2020 0:00") & (df["PT DateTime"] <= "9/19/2020 0:00")] \
                             ["PT DateTime"], df[df["Device Name"] == place] \
                             [(df["PT DateTime"] >= "9/10/2020 0:00") & (df["PT DateTime"] <= "9/19/2020 0:00")] \
                             ["PM2.5_Std"], label=place)
        plt.setp(plt.gca().xaxis.get_majorticklabels(),
                 'rotation', 90)
        plt.legend()
    if public_sensor:
        plt.ylim([0, 400])
        plt.suptitle(particle_size + " " +
                     in_or_out + " " + hour_or_10 + " vs Average (10min) vs Public Sensors (Hour)")
    else:
        plt.suptitle(particle_size + " " + in_or_out + " " + hour_or_10 + " vs Average (10min)")
    plt.text(0.04, 0.5, particle_size, va='center', rotation='vertical', fontsize=20)
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
