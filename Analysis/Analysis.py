import pandas as pd
import glob
from functions import get_device_location, get_hour_averages, puget_air_reformat, reformat, concat_df, \
    get_10min_averages

if __name__ == "__main__":
    files = glob.glob("D:/UW/AeroSpec - Sensor Network/2020 Wildfire Data/Wildfire 2020/*")
    betas = []
    breakouts = []
    pugets = []
    dfs = []
    ### Reformat all data files ###
    for fileloc in files:
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
            df_columns = betas[0].columns
            df = pd.read_csv(fileloc, skiprows=9, names=['PT DateTime', 'PM2.5_Std'])
            df_final = puget_air_reformat(df, fileloc, df_columns)
            pugets.append(df_final)
            continue
        df.drop([1], inplace=True)
        for column in df.columns:
            df[column] = df[column].str.strip()
        device_name, df = get_device_location(df)
        df = reformat(df, device_name)
        # df_final = get_hour_averages(df)
        df_final = get_10min_averages(df)
        if 'Beta' in fileloc:
            betas.append(df_final)
        elif 'Breakout' in fileloc:
            breakouts.append(df_final)
    ################################

    ### Concatenate all dataframes to a single df, then save to one csv file ##
    df_betas = concat_df(betas)
    df_breakouts = concat_df(breakouts)

    df_final = pd.concat([df_betas, df_breakouts])

    for i in range(len(pugets)):
        df_final = pd.concat([df_final, pugets[i]])

    df_betas.to_csv('Results/Betas10.csv', index=False)
    df_breakouts.to_csv('Results/Breakouts10.csv', index=False)
    df_final.to_csv('Results/FullData10.csv', index=False)
    ############################################################################
