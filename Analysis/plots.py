import pandas as pd
from matplotlib import pyplot as plt
import numpy as np

def user_case(df_users,in_or_out:str,device_name:str):
    if device_name == 'Bellevue SE 12th' or device_name == 'Lake Forest Park':
        user = 'Public Sensor'
    elif device_name == 'Breakout-02':
        user = 'Igor'
    else:
        if df_users[df_users[in_or_out] == device_name]['User'].shape[0] == 0:
            user = 'Unknown'
        else:
            user = df_users[df_users[in_or_out] == device_name]['User'].values[0]
    return user

def plot_in_or_out(df,df_users,in_or_out:str):
    devices = pd.unique(df[df['In or Out'] == in_or_out]['Device Name'])
    if in_or_out == 'In':
        devices = np.append(devices,['Bellevue SE 12th','Lake Forest Park'])
    subplot_position = 11
    ymin = float('inf')
    ymax = 0
    xmax = df[df['Device Name'] == 'Lake Forest Park']['PT DateTime'].max()
    xmin = df[df['Device Name'] == 'Lake Forest Park']['PT DateTime'].min()

    for device in devices:
        if df[df['Device Name'] == device]['PM2.5_Std'].max()>ymax:
            ymax = df[df['Device Name'] == device]['PM2.5_Std'].max()
        if df[df['Device Name'] == device]['PM2.5_Std'].min()<ymin:
            ymin = df[df['Device Name'] == device]['PM2.5_Std'].min()
        if df[df['Device Name'] == device]['PT DateTime'].max() < xmax:
            xmax = df[df['Device Name'] == device]['PT DateTime'].max()
        if df[df['Device Name'] == device]['PT DateTime'].min() > xmin:
            xmin = df[df['Device Name'] == device]['PT DateTime'].min()
        subplot_position += 100

    if ymax >500:
        ymax = 500
    
    for device in devices:
        ax1 = plt.subplot(subplot_position)
        if device not in ['Bellevue SE 12th','Lake Forest Park']:
            color = 'blue'
        else:
            color = 'red'
        plt.plot(df[df['Device Name'] == device]['PT DateTime'],df[df['Device Name'] == device]['PM2.5_Std'],color)
        user = user_case(df_users,in_or_out,device)
        ax1.set_title(device+ '\n'+ user,x= 1.07,y = -0.01)  
        subplot_position += 1
        if subplot_position == 916:
            plt.ylabel('PM2.5(μg/m^3)',fontsize = 16)
        plt.xlim([xmin,xmax])
        plt.ylim([ymin, ymax])
    for ax in plt.gcf().axes:
        try:
            ax.label_outer()
        except:
            pass
    # plt.ylabel('PM2.5_Std')
    plt.text(0.04, 0.5, 'PM2.5(μg/m^3)', va='center', rotation='vertical')
    plt.suptitle(in_or_out)
    plt.show()
    return

def plot_both(df,df_users):
    users = pd.unique(df_users['User'])
    users = np.delete(users,np.where(users == 'MEB'))
    users = np.delete(users,np.where(users == 'Charlie'))
    devices = pd.unique(df['Device Name'])
    ymin = float('inf')
    ymax = 0
    xmax = df[df['Device Name'] == 'Lake Forest Park']['PT DateTime'].max()
    xmin = df[df['Device Name'] == 'Lake Forest Park']['PT DateTime'].min()
    for device in devices:
        if df[df['Device Name'] == device]['PM2.5_Std'].max()>ymax:
            ymax = df[df['Device Name'] == device]['PM2.5_Std'].max()
        if df[df['Device Name'] == device]['PM2.5_Std'].min()<ymin:
            ymin = df[df['Device Name'] == device]['PM2.5_Std'].min()
        if df[df['Device Name'] == device]['PT DateTime'].max() < xmax:
            xmax = df[df['Device Name'] == device]['PT DateTime'].max()
        if df[df['Device Name'] == device]['PT DateTime'].min() > xmin:
            xmin = df[df['Device Name'] == device]['PT DateTime'].min()
    if ymax >500:
        ymax = 500
    subplot_position = 811
    for user in users:
        ax1 = plt.subplot(subplot_position)
        if user != 'Igor':
            for device in df_users[df_users['User'] == user][['In','Out']].values.tolist()[0]:
                if device in pd.unique(df['Device Name']):
                    plt.plot(df[df['Device Name'] == device]['PT DateTime'],df[df['Device Name'] == device]['PM2.5_Std'],label = df[df['Device Name']== device]['In or Out'].values[0])
        else:
            for i in range(2):
                for device in df_users[df_users['User'] == user][['In','Out']].values.tolist()[i]:
                    if device in pd.unique(df['Device Name']):
                        plt.plot(df[df['Device Name'] == device]['PT DateTime'],df[df['Device Name'] == device]['PM2.5_Std'],label = df[df['Device Name']== device]['In or Out'].values[0])
        ax1.set_title(user,x= 1.07,y = -0.01)  
        subplot_position += 1
        plt.xlim([xmin,xmax])
        plt.ylim([ymin, ymax])
        if subplot_position == 816:
            plt.ylabel('PM2.5(μg/m^3)',fontsize = 16)
        plt.legend()
    for device in ['Bellevue SE 12th','Lake Forest Park']:
        ax1 = plt.subplot(subplot_position)
        plt.plot(df[df['Device Name'] == device]['PT DateTime'],df[df['Device Name'] == device]['PM2.5_Std'],'red',label = 'Out')
        ax1.set_title(device,x= 1.07,y = -0.01)  
        subplot_position += 1
        plt.xlim([xmin,xmax])
        plt.ylim([ymin, ymax])
        plt.legend()
    for ax in plt.gcf().axes:
        try:
            ax.label_outer()
        except:
            pass
    # plt.ylabel('PM2.5_Std')
    ax1.text(0.5,0.5, 'PM2.5(μg/m^3)')
    plt.suptitle('Indoor v Outdoor')
    plt.show()
    return

df = pd.read_csv('../Results/FullData.csv')
df['PT DateTime'] = pd.to_datetime(df['PT DateTime'])
df_users = pd.read_excel("../UW/AeroSpec - Sensor Network/Map Vis/Device Locations and Users.xlsx")
df_users = df_users[df_users['In'].notna()].reset_index(drop=True)
# plot_in_or_out(df,df_users,'Out')
plot_in_or_out(df,df_users,'In')
# plot_both(df,df_users) 