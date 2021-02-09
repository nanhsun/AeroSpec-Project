from functions import plot_wrapper, average
import pandas as pd
# Choose a fileloc: Results/FullData.csv or Results/FullData10.csv
# Choose an input style: Separate, I/O Ratio, I/G Ratio
# Choose line or box (for I/O  saving purposes): line, box
# Optional: Choose hour average or 10 min: hour, 10 (string)
df = pd.read_csv("Results/FullData.csv")
df['PT DateTime'] = pd.to_datetime(df['PT DateTime'])

df_users = pd.read_excel("D:/UW/AeroSpec - Sensor Network/2020 Wildfire Data/Device Locations and Users.xlsx",
                             engine='openpyxl')
df_users = df_users[df_users['In'].notna()].reset_index(drop=True)

df_users_split = pd.read_excel("D:/UW/AeroSpec - Sensor Network/2020 Wildfire Data/Device Locations and Users Split.xlsx",
                             engine='openpyxl')
# df_users_split = df_users_split[df_users_split['In'].notna()].reset_index(drop=True)

df_temp = average(df, df_users, "Out")
print(df_temp)

# hour average line plot
# plot_wrapper(df, df_users, "Separate")
# # hour average I/O ratio line plot
# plot_wrapper(df, df_users, "I/O Ratio", "line")
# hour average I/O ratio box plot
# plot_wrapper(df, df_users_split, "I/O Ratio", "box")
# # hour average I/Gov ratio line plot
# plot_wrapper(df, df_users, "I/G Ratio", "line")
# # hour average I/Gov ratio box plot
# plot_wrapper(df, df_users, "I/G Ratio", "box")
# df_10 = pd.read_csv("Results/FullData10.csv")
# df_10['PT DateTime'] = pd.to_datetime(df_10['PT DateTime'])
# # 10min average line plot
# plot_wrapper(df_10, df_users, "Separate")
# 10min average I/O ratio line plot
# plot_wrapper(df_10, df_users, "I/O Ratio", "line")
# 10min average I/O ratio box plot
# plot_wrapper(df_10, df_users_split, "I/O Ratio", "box")

# plot_wrapper(df, df_users, "O/G Ratio", "box")
