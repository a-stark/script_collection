from cloudshell2_fan_control import get_cpu_temperature, get_disk_temperature

import datetime
import time
import numpy as np

REFRESH = 5

while True:

    date = datetime.datetime.now()
    year = int(date.strftime('%Y'))
    month = int(date.strftime('%m'))
    day = int(date.strftime('%d'))
    hour = int(date.strftime('%H')) 
    minute = int(date.strftime('%M'))
    second = int(date.strftime('%S'))

    temperature = get_cpu_temperature()
    temperature.extend(get_disk_temperature())

    write_arr = np.zeros(13, dtype=np.int)

    write_arr[0] = year
    write_arr[1] = month 
    write_arr[2] = day
    write_arr[3] = hour
    write_arr[4] = minute
    write_arr[5] = second

    for index, (sensor_type, temp) in enumerate(temperature):
        write_arr[index+6] = temp

    with open('temp_log.txt', 'a') as f:
        for entry in write_arr:
            f.write('{0:d}\t'.format(entry)) 

        f.write('\n')

    time.sleep(REFRESH)
