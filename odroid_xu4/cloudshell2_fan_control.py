# -*- coding: utf-8 -*-
"""
Obtain the available file descriptors and identify them.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

Copyright (c) 2018 Alexander Stark
"""


import subprocess

def get_cpu_temperature():
    """ Get the current CPU and GPU temperature

    Returns
    -------   
    list
        the entries of the list are tuples(cpu_type, temp) containing 
        cpu_type: str
            the type of the current unit
        temp: float
            the temperature of the current unit
    """

    cpu_temp =[]
    cpu_name = []
    for cpu_unit in range(5):
        with open("/sys/class/thermal/thermal_zone{0}/temp".format(cpu_unit)) as temp_file:
            cpu_temp.append(float(temp_file.read())/1000)

        with open("/sys/class/thermal/thermal_zone{0}/type".format(cpu_unit)) as type_file:
            cpu_name.append(type_file.read().strip())

    return [(cpu_name[i], cpu_temp[i]) for i in range(len(cpu_temp))]


def get_disk_temperature():
    """ Get the current disk temperature.

    Returns
    -------   
    list
        the entries of the list are tuples(disk_loc, temp) containing 
        disk_loc: str
            the location of the current disk
        temp: float
            the temperature of the current disk
    """

    hdd_temp = []
    hdd_list = ['sda', 'sdb']
    for hdd in hdd_list:

        output = float(subprocess.Popen(['smartctl -a /dev/{0} -d sat'.format(hdd)], 
                                        shell=True, stdout=subprocess.PIPE))

        output = output.stdout.read().decode('utf-8').split('/n')

        for line in output:
            if 'Temperature' in  line:
                temp = float(line.split()[-1])
                hdd_temp.append(temp)
                break   # assume just one temperature info

        hdd_temp.append(a)

    return [(hdd_list[i], hdd_temp[i]) for i in range(len(hdd_list))]


def print_temperature():
    """ Print out all the temperature sensors. """
    temp_list = get_disk_temperature()
    temp_list.extend(get_cpu_temperature())


    for sensortype, temp in temp_list:
        print("The temperature of <{0}> is currently {1} degrees."
              "".format(sensortype, temp))

