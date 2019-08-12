#Detailed instructions on code and sounding data can be found 
#in Jupyter Notebook Sounding_analysis on this link:
#https://github.com/dsesar4/storm_track/blob/master/Sounding_analysis.ipynb

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math

from bs4 import BeautifulSoup
import urllib.request
import re

from siphon.simplewebservice.wyoming import WyomingUpperAir
from pylab import rcParams
from datetime import datetime


date = datetime(2019,7,7,12)
station = 'LDDD'

df1 = WyomingUpperAir.request_data(date,station)

Year = date.year
Month = date.month
Day = date.day
Hour = date.hour

if (date.hour == 0):
    url = 'http://weather.uwyo.edu/cgi-bin/sounding?region=europe&TYPE=TEXT%3ALIST'\
    '&YEAR={Year}&MONTH=0{Month}&FROM=0{Day}0{Hour}&TO=0{Day}0{Hour}&STNM={Station}'\
    .format(Year = Year, Month = Month, Day = Day, Hour = Hour, Station = station)
else:
    url = 'http://weather.uwyo.edu/cgi-bin/sounding?region=europe&TYPE=TEXT%3ALIST'\
    '&YEAR={Year}&MONTH=0{Month}&FROM=0{Day}{Hour}&TO=0{Day}{Hour}&STNM={Station}'\
    .format(Year = Year, Month = Month, Day = Day, Hour = Hour, Station = station)

response = urllib.request.urlopen(url)
html = response.read()

soup = BeautifulSoup(html,features="lxml")
data = soup.find_all('pre')

Sound_data = str(data[1])
x = re.findall(r'[-+]?[.]?[\d].+', Sound_data)

x1 = []

i = 0
for i in range(0, len(x)):
    if (i != 1 and 'thickness' not in x[i]):
        x[i] = float(x[i])
        x1.append(x[i])
    i = i + 1
    
y = ['Station number', 'Station latitude', 'Station longitude', 'Station elevation', \
     'Showalter index', 'Lifted index', 'LIFT computed using virtual temperature', 'SWEAT index', 'K index', \
     'Cross totals index', 'Vertical totals index', 'Totals totals index', 'Convective Available Potential Energy', \
     'CAPE using virtual temperature', 'Convective Inhibition', 'CINS using virtual temperature', 'Equilibrum Level', \
     'Equilibrum Level using virtual temperature', 'Level of Free Convection', 'LFCT using virtual temperature', \
     'Bulk Richardson Number', 'Bulk Richardson Number using CAPV', 'Temp [K] of the Lifted Condensation Level', \
     'Pres [hPa] of the Lifted Condensation Level', 'Mean mixed layer potential temperature', \
     'Mean mixed layer mixing ratio', 'Precipitable water [mm] for entire sounding']

y1 = []

j = 0
for j in range(0, len(y)):
    if (y[j] in Sound_data):
        y1.append(y[j])
    j = j + 1
    
all_data = {'Parameter': y1, 'Value': x1}
df2 = pd.DataFrame(data = all_data)


no_storms = 0
moderate_storms = 0
strong_storms = 0
supercells = 0

#Lifted Index

LI_ind = int(df2[df2['Parameter']=='LIFT computed using virtual temperature'].index.values.astype(int)[0])
LI = df2.iloc[LI_ind]['Value']

if (LI < -6):
    strong_storms = strong_storms + 2
    moderate_storms = moderate_storms + 2
        
elif (LI < -3 and LI >= -6):
    strong_storms = strong_storms + 1
    moderate_storms = moderate_storms + 1
    
elif (LI < 0 and LI >= -3):
    moderate_storms = moderate_storms + 1

else:
    strong_storms = strong_storms - 1
    moderate_storms = moderate_storms - 1
    no_storms = no_storms + 1

#SWEAT Index
    
sweat_ind = int(df2[df2['Parameter']=='SWEAT index'].index.values.astype(int)[0])
sweat = df2.iloc[sweat_ind]['Value']

if (sweat >= 400):
    supercells = supercells + 2
    strong_storms = strong_storms + 3
elif (sweat >= 300 and sweat < 400):
    supercells = supercells + 1
    strong_storms = strong_storms + 2
elif (sweat >= 150 and sweat < 300):
    strong_storms = strong_storms + 1
else:
    supercells = supercells - 1
    strong_storms = strong_storms - 1
    
#K Index
    
KI_ind = int(df2[df2['Parameter']=='K index'].index.values.astype(int)[0])
KI = df2.iloc[KI_ind]['Value']
    
if (KI >= 40):
    strong_storms = strong_storms + 2
    moderate_storms = moderate_storms + 2
elif (KI >= 20 and KI < 40):
    strong_storms = strong_storms + 1
    moderate_storms = moderate_storms + 1
else:
    strong_storms = strong_storms - 1
    moderate_storms = moderate_storms - 1
    no_storms = no_storms + 1
    
#TT Index
    
TT_ind = int(df2[df2['Parameter']=='Totals totals index'].index.values.astype(int)[0])
TT = df2.iloc[TT_ind]['Value']
    
if (TT >= 53):
    supercells = supercells + 2
    strong_storms = strong_storms + 2
elif (TT >= 51 and TT < 53):
    supercells = supercells + 1
    strong_storms = strong_storms + 1
    moderate_storms = moderate_storms + 1
elif (TT >= 44 and TT < 50):
    supercells = supercells - 1
    strong_storms = strong_storms - 1
    moderate_storms = moderate_storms + 1
else:
    supercells = supercells - 2
    strong_storms = strong_storms - 2
    moderate_storms = moderate_storms - 1
    no_storms = no_storms + 1  

#CAPE and Shear 0-6 km
    
CAPE_ind = int(df2[df2['Parameter']=='CAPE using virtual temperature'].index.values.astype(int)[0])
CAPE = df2.iloc[CAPE_ind]['Value']

six_km = int(df1[df1['height'] >= 6000].index[0])
dir_0km = df1['direction'].iloc[0]
dir_6km = df1['direction'].iloc[six_km]
speed_0km_x = df1['speed'].iloc[0] * math.cos(math.radians(-dir_0km+90))
speed_0km_y = df1['speed'].iloc[0] * math.sin(math.radians(-dir_0km+90))
speed_6km_x = df1['speed'].iloc[six_km] * math.cos(math.radians(-dir_6km+90))
speed_6km_y = df1['speed'].iloc[six_km] * math.sin(math.radians(-dir_6km+90))
shear = 0.514 * (math.sqrt((speed_6km_x - speed_0km_x)**2 + (speed_6km_y - speed_0km_y)**2))

if (CAPE >= 2000):
    if (shear >= 20):
        supercells = supercells + 7
        strong_storms = strong_storms + 7
    elif (shear >= 15 and shear < 20):
        supercells = supercells + 6
        strong_storms = strong_storms + 6
    elif (shear >= 10 and shear < 15):
        supercells = supercells + 3
        strong_storms = strong_storms + 5
    else:
        strong_storms = strong_storms + 3
        supercells = supercells - 3
    moderate_storms = moderate_storms + 1
    
elif (CAPE >= 1500 and CAPE < 2000):
    if (shear >= 20):
        supercells = supercells + 6
        strong_storms = strong_storms + 6
    elif (shear >= 14.9 and shear < 20):
        supercells = supercells + 5
        strong_storms = strong_storms + 5
    elif (shear >= 10 and shear < 14.9):
        supercells = supercells + 3
        strong_storms = strong_storms + 4
    else:
        strong_storms = strong_storms + 2
        supercells = supercells - 3
    moderate_storms = moderate_storms + 1
    
elif (CAPE >= 1000 and CAPE < 1500):
    if (shear >= 20):
        supercells = supercells + 5
        strong_storms = strong_storms + 5
    elif (shear >= 15 and shear <= 20):
        supercells = supercells + 4
        strong_storms = strong_storms + 4
    elif (shear >= 10 and shear <= 15):
        supercells = supercells + 2
        strong_storms = strong_storms + 3
    else:
        strong_storms = strong_storms + 1
        supercells = supercells - 3
    moderate_storms = moderate_storms + 1
    
elif (CAPE >= 500 and CAPE < 1000):
    if (shear >= 20):
        supercells = supercells + 4
        strong_storms = strong_storms + 4
    elif (shear >= 15 and shear <= 20):
        supercells = supercells + 3
        strong_storms = strong_storms + 3
    elif (shear >= 10 and shear <= 15):
        strong_storms = strong_storms + 2
        supercells = supercells - 1
    else:
        strong_storms = strong_storms - 1
        supercells = supercells - 3
    moderate_storms = moderate_storms + 1
    
elif (CAPE >= 100 and CAPE < 500):
    if (shear >= 20):
        supercells = supercells + 3
        strong_storms = strong_storms + 3
        moderate_storms = moderate_storms + 2
    elif (shear >= 15 and shear <= 20):
        strong_storms = strong_storms + 2
        supercells = supercells - 1
        moderate_storms = moderate_storms + 2
    elif (shear >= 10 and shear <= 15):
        moderate_storms = moderate_storms + 1
        supercells = supercells - 3
    else:
        strong_storms = strong_storms - 1
        supercells = supercells - 4
        no_storms = no_storms + 1
        
else:
    if (shear >= 20):
        strong_storms = strong_storms + 2
        moderate_storms = moderate_storms + 2
    elif (shear >= 15 and shear <= 20):
        supercells = supercells - 1
        moderate_storms = moderate_storms + 1
    else:
        supercells = supercells - 3
        strong_storms = strong_storms - 2
        no_storms = no_storms + 1

#CIN
    
CIN_ind = int(df2[df2['Parameter']=='CINS using virtual temperature'].index.values.astype(int)[0])
CIN = df2.iloc[CIN_ind]['Value']
    
if (CIN <= -130 and CAPE < 500):
    supercells = supercells - 3
    strong_storms = strong_storms - 3
    moderate_storms = moderate_storms - 3
    no_storms = no_storms + 3
elif (CIN <= -130 and CAPE >= 500):
    supercells = supercells - 2
    strong_storms = strong_storms - 2
    moderate_storms = moderate_storms - 2
    no_storms = no_storms + 2
elif (CIN <= -50 and CIN > -130 and CAPE < 250):
    supercells = supercells - 3
    strong_storms = strong_storms - 3
    moderate_storms = moderate_storms - 3
    no_storms = no_storms + 3
elif (CIN <= -50 and CIN > -130 and CAPE >= 250):
    supercells = supercells - 2
    strong_storms = strong_storms - 2
    moderate_storms = moderate_storms - 2
    no_storms = no_storms + 2
elif (CIN > -50 and CAPE < 90):
    supercells = supercells - 3
    strong_storms = strong_storms - 3
    moderate_storms = moderate_storms - 3
    no_storms = no_storms + 3
elif (CIN > -50 and CAPE > 90 and CAPE < 500):
    supercells = supercells - 1
    moderate_storms = moderate_storms + 1
else:
    supercells = supercells + 1
    strong_storms = strong_storms + 1
    moderate_storms = moderate_storms + 1
    
#Level of Free Convection
        
LFCT = int(df2[df2['Parameter']=='LFCT using virtual temperature'].index.values.astype(int)[0])
pom = int(df1[df1['pressure'] <= df2.iloc[LFCT]['Value']].index[0])
LFCT_level = df1['height'].iloc[pom]

if (LFCT_level < 3150 and (moderate_storms >= 4 or strong_storms >= 6 or supercells >= 3)):
    moderate_storms = moderate_storms + 1
    strong_storms = strong_storms + 1
    supercells = supercells + 1  
        
#No storms sign       
        
if (moderate_storms <= 3 and strong_storms <= 0 and supercells <= 0):
    no_storms = no_storms + 2
    
storm_array = ['No storms', 'Thunderstorms', 'Severe storms', 'Supercells']
index = np.arange(len(storm_array))     
storm_score = [no_storms/9*100, moderate_storms/9*100, strong_storms/18*100, supercells/13*100]
for j in range(0, len(storm_score)):
    if (storm_score[j] < 0):
        storm_score[j] = 0
        

rcParams['figure.figsize'] = 16, 10

plt.bar(index, storm_score, align='center', color=['green', 'yellow', 'orange', 'red'],  edgecolor='blue')
plt.xticks(index, storm_array, fontsize = 20)
plt.yticks(np.arange(0, 105, 5), fontsize = 20)
plt.axhline(30, color="black", linestyle='dashed')
plt.text(3.65, 15, "  Low \nchance", va='center', ha="left",  fontsize = 15)
plt.axhline(70, color="black", linestyle='dashed')
plt.text(3.65, 50, "Medium \nchance", va='center', ha="left", fontsize = 15)
plt.text(3.65, 85, "  High \nchance", va='center', ha="left", fontsize = 15)
a = 'Storm track for {day}.{month}.{year}. at {hour} UTC'.format\
(day = date.day, month = date.month, year = date.year, hour = date.hour)
plt.title(a, fontsize = 30)
plt.grid()


#Storm motion

wind_direction = [['NE', 22.5, 67.5], ['E', 67.5, 112.5], ['SE', 112.5, 157.5], ['S', 157.5, 202.5],\
                  ['SW', 202.5, 247.5], ['W', 247.5, 292.5], ['NW', 292.5, 337.5]]
df4 = pd.DataFrame(wind_direction, columns = ['Direction','UL','LL'])
    
storm_dir = round(df1['direction'].iloc[3:six_km].mean(), 2)

for i in range (len(df4)):
    if (storm_dir > df4['UL'].iloc[i] and storm_dir < df4['LL'].iloc[i]):
        storm_dir_letter = df4['Direction'].iloc[i]
    elif (storm_dir > 337.5 and storm_dir < 22.5):
        storm_dir_letter = 'N'
        
if (supercells > 0):
    supercell_dir = storm_dir + 30
    for i in range (len(df4)):
        if (supercell_dir > df4['UL'].iloc[i] and supercell_dir < df4['LL'].iloc[i]):
            supercell_dir_letter = df4['Direction'].iloc[i]
        elif (supercell_dir > 337.5 and supercell_dir < 22.5):
            supercell_dir_letter = 'N'

if (moderate_storms >= 1 or strong_storms >= 1 or supercells >= 1):
    print('\033[1m' + 'Storms are coming from {storm_dir_letter} direction ({storm_dir}°).'\
                .format(storm_dir_letter = storm_dir_letter, storm_dir = storm_dir))

if (supercells >= 1):
    print('\033[1m' + 'Supercells are coming from {supercell_dir_letter} direction ({supercell_dir}°).'\
                .format(supercell_dir_letter = supercell_dir_letter, supercell_dir = supercell_dir))
    
#Hail, heavy rain and tornado warnings

if ('Equilibrum Level using virtual temperature' in y1):
    EQLV_ind = int(df2[df2['Parameter']=='Equilibrum Level using virtual temperature'].index.values.astype(int)[0])
    LCL_ind = int(df2[df2['Parameter']=='Pres [hPa] of the Lifted Condensation Level'].index.values.astype(int)[0])
    PW_ind = int(df2[df2['Parameter']=='Precipitable water [mm] for entire sounding'].index.values.astype(int)[0])
    PW = df2.iloc[PW_ind]['Value']
    ind1 = int(df1[df1['pressure'] < df2.iloc[EQLV_ind]['Value']].index[0])
    ind2 = int(df1[df1['pressure'] < df2.iloc[LCL_ind]['Value']].index[0])
    EQLV = df1['height'].iloc[ind1]
    LCL = df1['height'] .iloc[ind2]
    
    ind = int(df1[df1['temperature'] < 0].index[0])
    hail_level = df1['pressure'].iloc[ind]
    
    if (EQLV - LCL > 7000 and CAPE < 1000 and PW > 43):
        print('Heavy rain possible!')
    elif ((EQLV - LCL > 7000 and CAPE > 2000) or \
          (EQLV - LCL < 7000 and EQLV - LCL > 4000 and CAPE > 1500)):
        print('Big hail possible!')
    elif (EQLV - LCL > 2000 and EQLV - LCL < 4000 and moderate_storms > 4):
        print('Possible showers.') 
        
if (LFCT_level < 2000 and supercells >= 6 and shear >= 22):
    print('Tornado possible!')
