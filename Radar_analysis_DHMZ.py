#Detailed instructions on code and radar data can be found 
#in Jupyter Notebook Radar_analysis_DHMZ on this link:
#https://github.com/dsesar4/storm_track/blob/master/Radar_analysis.ipynb

import pandas as pd
import urllib.request
import time
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from pylab import rcParams
rcParams['figure.figsize'] = 10, 10

DHMZ_possible_reflections = [[0,255,255],[0,199,199],[0,146,145],[0,56,184],\
                             [0,129,0],[0,202,0],[41,255,10],[255,255,0],\
                             [237,194,0],[255,0,0],[247,0,219]]
df3 = pd.DataFrame(DHMZ_possible_reflections, columns = ['r','g','b'])

hour_start = 12
minute_start = 55
day = 7
month = 7
year = 2019

iterations = 4


hour = hour_start
minute = minute_start
hour_querry = hour

if (month//10 == 0):
    month = '0' + str(month)

if (day//10 == 0):
    day = '0' + str(day)
    
x_rain = [[0 for i in range(145)] for j in range(160)]
x_shower = [[0 for i in range(145)] for j in range(160)]
x_thunderstorm = [[0 for i in range(145)] for j in range(160)]
x_severe_storm = [[0 for i in range(145)] for j in range(160)]

k = 0

while (k <= iterations):
    urllib.request.urlretrieve('http://139.59.144.6/arhiva/bilogora_stat/{year}/{month}/{day}/bilogora_stat_{year}{month}{day}{hour}{minute}Z.png'\
                               .format(year = year, month = month, day = day, hour = hour, minute = minute), "bilogora-stat.png")
    
    im = Image.open("bilogora-stat.png")
    rgb_im = im.convert('RGB') 
    
    i = 0
    j = 0

    for i in range (105,250):
        for j in range (165,325):
            r, g, b = rgb_im.getpixel((i, j))
            if ((r == df3['r'][0] or r == df3['r'][1] or r == df3['r'][2] or r == df3['r'][3]) and (g in df3['g'].values)):
                x_rain[j - 165][i - 105] = x_rain[j - 165][i - 105] + 1
            elif ((r == df3['r'][5] or r == df3['r'][6] or r == df3['r'][7]) and (g in df3['g'].values)):
                x_shower[j - 165][i - 105] = x_shower[j - 165][i - 105] + 1
            elif ((r == df3['r'][8] or r == df3['r'][9]) and (g in df3['g'].values) and (b in df3['b'].values)):
                x_thunderstorm[j - 165][i - 105] = x_thunderstorm[j - 165][i - 105] + 1
            elif ((r == df3['r'][10]) and (g in df3['g'].values) and (b in df3['b'].values)):
                x_severe_storm[j - 165][i - 105] = x_severe_storm[j - 165][i - 105] + 1
    
    if (minute == 55):
        minute = 10
        if (hour == 23):
            hour = 0
            if (day == 31):
                day = 1
                month = month + 1
        else:
            hour = hour + 1
    else:
        minute = minute + 15
    
    k = k + 1    
                
    time.sleep(1) 

i = 0
j = 0

for i in range(0,160):
    mask = max(x_rain[i])
    for j in range (0,145):
        if x_rain[i][j] == mask:
            x_rain[i][j] = 0

template = Image.open("template.png")
template = template.crop((105,165,250,325))

def transparent_cmap(cmap, N = 255):
    mycmap = cmap
    mycmap._init()
    mycmap._lut[:,-2] = np.linspace(0, 1, N + 4)
    return mycmap

mycmap = transparent_cmap(plt.cm.rainbow)

w, h = template.size
y, x = np.mgrid[0:h, 0:w]

rain = np.ravel(x_rain)
shower = np.ravel(x_shower)
thunderstorm = np.ravel(x_thunderstorm)
severe_storm = np.ravel(x_severe_storm)

if (minute == 10):
    if (hour == 0):
        hour_end = 23
    else:
        hour_end = hour - 1
    minute_end = 45
else:
    minute_end = minute - 25
    hour_end = hour 

fig1, ax1 = plt.subplots(1, 1)

ax1.imshow(template)
cb1 = ax1.contourf(x, y, rain.reshape(x.shape[0], y.shape[1]), 15, cmap=mycmap, alpha = 0.5)
plt.colorbar(cb1)
plt.title('{day}.{month}.{year}, {start_hour}:{start_minutes}-{end_hour}:{end_minutes} UTC\n 15-35 dBZ'\
          .format(day = day, month = month, year = year, start_hour = hour_start,\
          start_minutes = minute_start - 10, end_hour = hour_end, end_minutes = minute_end), fontsize = 22)
plt.show()

fig2, ax2 = plt.subplots(1, 1)

ax2.imshow(template)
cb2 = ax2.contourf(x, y, shower.reshape(x.shape[0], y.shape[1]), 15, cmap=mycmap, alpha = 0.5)
plt.colorbar(cb2)
plt.title('{day}.{month}.{year}, {start_hour}:{start_minutes}-{end_hour}:{end_minutes} UTC\n 35-50 dBZ'\
          .format(day = day, month = month, year = year, start_hour = hour_start,\
          start_minutes = minute_start - 10, end_hour = hour_end, end_minutes = minute_end), fontsize = 22)
plt.show()

fig3, ax3 = plt.subplots(1, 1)

ax3.imshow(template)
cb3 = ax3.contourf(x, y, thunderstorm.reshape(x.shape[0], y.shape[1]), 15, cmap=mycmap, alpha = 0.5)
plt.colorbar(cb3)
plt.title('{day}.{month}.{year}, {start_hour}:{start_minutes}-{end_hour}:{end_minutes} UTC\n 50-60 dBZ'\
          .format(day = day, month = month, year = year, start_hour = hour_start,\
          start_minutes = minute_start - 10, end_hour = hour_end, end_minutes = minute_end), fontsize = 22)
plt.show()

fig4, ax4 = plt.subplots(1, 1)

ax4.imshow(template)
cb4 = ax4.contourf(x, y, severe_storm.reshape(x.shape[0], y.shape[1]), 15, cmap=mycmap, alpha = 0.5)
plt.colorbar(cb4)
plt.title('{day}.{month}.{year}, {start_hour}:{start_minutes}-{end_hour}:{end_minutes} UTC\n 60+ dBZ'\
          .format(day = day, month = month, year = year, start_hour = hour_start,\
          start_minutes = minute_start - 10, end_hour = hour_end, end_minutes = minute_end), fontsize = 22)
plt.show()












            