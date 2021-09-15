import pandas as pd
import glob
from functions import get_device_location, get_hour_averages, puget_air_reformat, reformat, concat_df, \
    get_10min_averages, get_averages

if __name__ == "__main__":
    # files = glob.glob("D:/UW/AeroSpec - Sensor Network/2020 Wildfire Data/Wildfire 2020/*")
    # print(files)
    devices = []
    df_users = pd.read_excel(
        "D:/UW/AeroSpec - Sensor Network/2020 Wildfire/Data/Device Locations and Users Split.xlsx", engine='openpyxl')
    for device in df_users["In"].dropna():
        if device == "Beta-04":
            continue
        if device == "Beta-13":
            devices.append(device + "(MEB IN)")
        else:
            devices.append(device)
    for device in df_users["Out"].dropna():
        if device in devices or device == "Beta-15":
            continue
        if device == "Beta-08":
            devices.append(device + "(MEB)")
        else:
            devices.append(device)
    devices.append("Breakout-02")
    print(devices)
    remains = ["Breakout-01", "Breakout-09", "Breakout-10", "Breakout-11"]
    for remain in remains:
        devices.append(remain)
    for puget in ["Puget-Bellevue", "Puget-LakeForestPark", "Puget-Seattle 10th and Weller"]:
        devices.append(puget)

    finals_hour = []
    finals_10min = []
    finals_10sec = []
    breakouts = []
    pugets = []
    dfs = []
    fileloc = "D://UW//AeroSpec - Sensor Network//2020 Wildfire//Wildfire 2020 Raw Data//" + devices[0] + ".txt"
    print(devices)
    ### Reformat all data files ###
    for device in devices:
        if "Puget" in device:
            fileloc = "D://UW//AeroSpec - Sensor Network//2020 Wildfire//Wildfire 2020 Raw Data//" + device + ".csv"
        else:
            fileloc = "D://UW//AeroSpec - Sensor Network//2020 Wildfire//Wildfire 2020 Raw Data//" + device + ".txt"
        print(fileloc)
        if 'Wildfire Dataset' in fileloc:
            continue
        if 'Beta' in fileloc:
            df = pd.read_csv(fileloc, dtype='a', sep=',', names=['Date', 'Time',
                                                                 'Battery', 'Fix', 'Latitude', 'Longitude', 'Dp>0.3',
                                                                 'Dp>0.5', 'Dp>1.0', 'Dp>2.5', 'Dp>5.0', 'Dp>10.0',
                                                                 'PM1_Std', 'PM2.5_Std', 'PM10_Std',
                                                                 'PM1_Env', 'PM2.5_Env', 'PM10_Env', 'Temp(C)', 'RH(%)',
                                                                 'P(hPa)', 'Alti(m)'])
            df.drop(['Temp(C)', 'RH(%)', 'P(hPa)', 'Alti(m)'], axis=1, inplace=True)
        elif 'Breakout' in fileloc:
            df = pd.read_csv(fileloc, dtype='a', sep=',', names=['Date', 'Time',
                                                                 'Battery', 'Fix', 'Latitude', 'Longitude', 'Dp>0.3',
                                                                 'Dp>0.5', 'Dp>1.0', 'Dp>2.5', 'Dp>5.0', 'Dp>10.0',
                                                                 'PM1_Std', 'PM2.5_Std', 'PM10_Std',
                                                                 'PM1_Env', 'PM2.5_Env', 'PM10_Env'])
        elif 'Puget' in fileloc:
            # df_columns = finals_hour[0].columns
            df_columns = finals_10min[0].columns
            # df_columns = finals_hour[0].columns
            df = pd.read_csv(fileloc, skiprows=9, names=['PT DateTime', 'PM2.5_Std'])
            df_final = puget_air_reformat(df, fileloc, df_columns)
            pugets.append(df_final)
            continue
        df.drop([1], inplace=True)
        for column in df.columns:
            df[column] = df[column].str.strip()
        device_name, df = get_device_location(df)
        df = reformat(df, device_name)
        # df_final_hour = get_averages(df, "hour")
        df_final_10min = get_averages(df, "10Min")
        # df_final_10sec = get_averages(df, "10S")
        # finals_hour.append(df_final_hour)
        finals_10min.append(df_final_10min)
        # finals_10sec.append(df_final_10sec)
        # if 'Beta' in fileloc:
        #     betas.append(df_final)
        # elif 'Breakout' in fileloc:
        #     breakouts.append(df_final)
    ################################

    ### Concatenate all dataframes to a single df, then save to one csv file ##
    # df_hour = concat_df(finals_hour)
    df_10min = concat_df(finals_10min)
    # df_10sec = concat_df(finals_10sec)
    # df_betas = concat_df(betas)
    # df_breakouts = concat_df(breakouts)

    # df_final = pd.concat([df_betas, df_breakouts])

    for i in range(len(pugets)):
        # df_hour = pd.concat([df_hour, pugets[i]])
        df_10min = pd.concat([df_10min, pugets[i]])
        # df_10sec = pd.concat([df_10sec, pugets[i]])
    #
    # df_hour.to_csv("Results/1_HourAverage2.csv", index=False)
    df_10min.to_csv("Results/2_10MinAverage.csv", index=False)
    # df_10sec.to_csv("Results/3_10SecAverage.csv", index=False)

    # df_betas.to_csv('Results/Betas10.csv', index=False)
    # df_breakouts.to_csv('Results/Breakouts10.csv', index=False)
    # df_final.to_csv('Results/FullData10.csv', index=False)
    ###########################################################################
