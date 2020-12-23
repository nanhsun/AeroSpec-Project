import pandas as pd
import numpy as np
import glob
from datetime import timedelta
def get_device_location(df):
    '''
    Organize the dataframe and set coordinates according to device names
    Input: df -- Dataframe
    Output: device_name -- str
            df --Dataframe
    '''
    device_name = df['Date'][0]
    df.drop([0],inplace=True)
    df.insert(0,column = 'Device Name',value = device_name)
    df.reset_index(drop = True,inplace=True)
    if device_name == 'Beta-01' or device_name == 'Beta-19':
        if device_name == 'Beta-01':
            df.insert(5,column = 'In or Out', value = 'Out')
        elif device_name == 'Beta-19':
            df.insert(5,column = 'In or Out', value = 'In')
        df = df.assign(Latitude = '47.661273')
        df = df.assign(Longitude = '-122.323842')        
    if device_name == 'Beta-07' or device_name == 'Beta-17':
        if device_name == 'Beta-17':
            df.insert(5,column = 'In or Out', value = 'Out')
        elif device_name == 'Beta-07':
            df.insert(5,column = 'In or Out', value = 'In')
        df = df.assign(Latitude = '47.657965')
        df = df.assign(Longitude = '-122.333808')
    if device_name == 'Beta-03' or device_name == 'Beta-12':
        if device_name == 'Beta-03':
            df.insert(5,column = 'In or Out', value = 'Out')
        elif device_name == 'Beta-12':
            df.insert(5,column = 'In or Out', value = 'In')
        df = df.assign(Latitude = '47.695662')
        df = df.assign(Longitude = '-122.293314')
    if device_name == 'Beta-06' or device_name == 'Breakout-08':
        if device_name == 'Breakout-08':
            df.insert(5,column = 'In or Out', value = 'Out')
        elif device_name == 'Beta-06':
            df.insert(5,column = 'In or Out', value = 'In')
        df = df.assign(Latitude = '47.659161')
        df = df.assign(Longitude = '-122.317555')
    if device_name == 'Beta-11' or device_name == 'Beta-16' or device_name == 'Beta-14':
        if device_name == 'Beta-11' or device_name == 'Beta-14':
            df.insert(5,column = 'In or Out', value = 'In')
        elif device_name == 'Beta-16':
            df.insert(5,column = 'In or Out', value = 'Out')
        df = df.assign(Latitude = '47.661519')
        df = df.assign(Longitude = '-122.332354')
    if device_name == 'Beta-18' or device_name == 'Breakout-06':
        if device_name == 'Breakout-06':
            df.insert(5,column = 'In or Out', value = 'Out')
        elif device_name == 'Beta-18':
            df.insert(5,column = 'In or Out', value = 'In')
        df = df.assign(Latitude = '47.664879')
        df = df.assign(Longitude = '-122.27600')
    if device_name == 'Breakout-01' or device_name == 'Breakout-09' or device_name == 'Breakout-10' or device_name == 'Breakout-11':
        df.insert(5,column = 'In or Out', value = 'Unknown')
    if device_name == 'Breakout-02':
        df.insert(5,column = 'In or Out', value = 'Out')
    return device_name,df

def get_hour_averages(df):
    '''
    Calculate averages of all columns other than 'Date','Time','Battery','Fix','Latitude','Longitude' for each hour everyday
    Input: df -- Dataframe
    Ouput: df -- Dataframe
    '''
    cols_average = df.columns.drop(['Device Name','Date','Time','PT DateTime','PT_AMPM','Battery','Fix','Latitude','Longitude','In or Out'])
    df[cols_average] = df[cols_average].apply(pd.to_numeric,errors='coerce')
    df['PT DateTime'] = pd.to_datetime(df['PT DateTime']).dt.strftime('%Y/%m/%d %H:00')
    df_final = df.groupby(['Device Name','PT DateTime','PT_AMPM','Latitude','Longitude','In or Out'],as_index=False)[cols_average].mean().sort_values(['PT DateTime'])
    return df_final

def get_minute_averages(df):
    cols_average = df.columns.drop(['Device Name','Date','Time','PT DateTime','PT_AMPM','Battery','Fix','Latitude','Longitude','In or Out'])
    df[cols_average] = df[cols_average].apply(pd.to_numeric,errors='coerce')
    df['PT DateTime'] = pd.to_datetime(df['PT DateTime'])
    df_final = df.groupby(['Device Name','PT DateTime','PT_AMPM','Latitude','Longitude','In or Out'],as_index=False)[cols_average].mean().sort_values(['PT DateTime'])

    return df_final

def UTC_to_PST(df):
    df['PT DateTime'] = pd.to_datetime(df['PT DateTime'])
    df['PT DateTime'] = pd.to_datetime(df['PT DateTime'] - timedelta(hours=7))
    df['PT DateTime'] = pd.to_datetime(df['PT DateTime'],yearfirst = True).dt.strftime('%Y/%m/%d %I:%M %p')
    return df

def reformat(df,device_name):
    df.drop(df[df['Date'] == '0/0/0'].index,axis = 0,inplace = True)
    df.drop(df[df['Date'].str.contains("80")].index,axis = 0,inplace = True)
    df.reset_index(drop = True,inplace=True)

    df.insert(3,column = 'PT DateTime', value = df['Date']+' '+df['Time'])
    df['PT DateTime'] = pd.to_datetime(df['PT DateTime'],yearfirst = True).dt.strftime('%Y/%m/%d %I:%M %p')
    # uni = pd.unique(df['PT DateTime'])
    # uni = pd.unique(df['PT DateTime'])
    df['PT DateTime'] = df['PT DateTime'].str.replace('2005','2020')
    if device_name == 'Breakout-08':
        df = UTC_to_PST(df)
    df.insert(4,column = 'PT_AMPM',value = df['PT DateTime'].str.split(' ', n = 2,expand = True)[2])
    return df

def concat_df(dfs:list):
    columns = dfs[0].columns
    df_final = pd.DataFrame(columns = columns)
    for i in range(len(dfs)):
        df_final = pd.concat([df_final,dfs[i]])
    return df_final

def puget_air_reformat(df,fileloc,columns):
    if 'Bellevue' in fileloc:
        df.insert(0,column = 'Device Name',value = 'Bellevue SE 12th')
        df.insert(2,column = 'Latitude',value = '47.601002')
        df.insert(3,column = 'Longitude',value = '-122.149234')
    elif 'LakeForestPark' in fileloc:
        df.insert(0,column = 'Device Name',value = 'Lake Forest Park')
        df.insert(2,column = 'Latitude',value = '47.753631')
        df.insert(3,column = 'Longitude',value = '-122.277257')
    df.insert(2,column = 'PT_AMPM',value = df['PT DateTime'].str.split(' ', n = 2,expand = True)[2])
    i = 6
    print(columns)
    for column in columns:
        if column in df.columns:
            continue
        if column == 'In or Out':
            df.insert(5,column = column,value = 'Out')
            continue
        df.insert(i,column = column,value = 0)
        if i == 12:
            i+=1
        i+=1
    return df

if __name__ == "__main__":
    files = glob.glob("../UW/AeroSpec - Sensor Network/Data/Wildfire 2020/*")
    
    # files = glob.glob("../Test/*")
    fileloc = '../UW/AeroSpec - Sensor Network/Data/Wildfire 2020/Beta-01.txt'
    # fileloc = '../UW/AeroSpec - Sensor Network/Data/Wildfire 2020/Puget-Bellevue.csv'
    betas = []
    breakouts = []
    pugets = []
    dfs = []
    for fileloc in files:
        print(fileloc)
        if 'Beta' in fileloc:
            df = pd.read_csv(fileloc,dtype = 'a',sep = ',',names=['Date','Time',
            'Battery','Fix','Latitude','Longitude','Dp>0.3','Dp>0.5','Dp>1.0','Dp>2.5','Dp>5.0','Dp>10.0','PM1_Std','PM2.5_Std','PM10_Std',
            'PM1_Env','PM2.5_Env','PM10_Env','Temp(C)','RH(%)','P(hPa)','Alti(m)'])
            df.drop(['Temp(C)','RH(%)','P(hPa)','Alti(m)'],axis = 1,inplace = True)
        elif 'Breakout' in fileloc:
            df = pd.read_csv(fileloc,dtype = 'a',sep = ',',names=['Date','Time',
            'Battery','Fix','Latitude','Longitude','Dp>0.3','Dp>0.5','Dp>1.0','Dp>2.5','Dp>5.0','Dp>10.0','PM1_Std','PM2.5_Std','PM10_Std',
            'PM1_Env','PM2.5_Env','PM10_Env'])
        elif 'Puget' in fileloc:
            df_columns = betas[0].columns
            df = pd.read_csv(fileloc,skiprows = 9, names = ['PT DateTime','PM2.5_Std'])
            df_final = puget_air_reformat(df,fileloc,df_columns)
            pugets.append(df_final)
            continue
        df.drop([1],inplace=True)
        for column in df.columns:
            df[column] = df[column].str.strip()
        device_name,df = get_device_location(df)
        df = reformat(df,device_name)
        df_final = get_hour_averages(df)
        if 'Beta' in fileloc:
            betas.append(df_final)
        elif 'Breakout' in fileloc:
            breakouts.append(df_final)
    ####################################33
    df_betas = concat_df(betas)
    df_breakouts = concat_df(breakouts)

    df_final = pd.concat([df_betas,df_breakouts])

    for i in range(len(pugets)):
        df_final = pd.concat([df_final,pugets[i]])

    df_betas.to_csv('../Results/Betas.csv',index=False)
    df_breakouts.to_csv('../Results/Breakouts.csv',index =False)
    df_final.to_csv('../Results/FullData.csv',index = False)
    # df_final.to_csv('../Results/Beta-01.csv',index = False)