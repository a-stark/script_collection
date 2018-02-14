#!/bin/bash
#
# Script to switch fan on or off according to CPU and disk temperature.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (c) 2018 Alexander Stark
#
# This script was originally taken from:
# https://github.com/crazyquark/xu4-cloudshell2-fancontrol/blob/master/xu4-fancontrol.sh
# and modified for custom purpose.


# Functionality of the Script:
# ============================
#
# Reads out the current temperature of CPU and DISKS and if a 
# THRESHOLD+INTERVAL value is exceeded the cloudshell fan is switched on. If 
# the temperature falls below THRESHOLD the fan is switched of. By using the
# variable INTERVAL it is prevented that the fan is not switched constantly on
# and off at the THRESHOLD. Therefore, 
#   - fan is switched ON at THRESHOLD + INTERVAL
#   - fan is switched OFF at THRESHOLD
# INTERVAL acts therefore as a buffer. 
#
# Note: script needs root privileges, since 'fdisk' and 'smartctl' require root 
#       access to read out disk information.



REFRESH="5"	                # refresh rate in seconds, how often it is checked.
DISK_TEMP_THRESHOLD="35"    # disk temperature threshold in degree 
DISK_TEMP_INTERVAL="5"	  	# temperature interval where nothing is done
CPU_TEMP_THRESHOLD="40"     # cpu temperature threshold in degree
CPU_TEMP_INTERVAL="20"      # cpu interval where nothing is done
FAN_CHANGED="*"

get_disk_dev_info() {
    # Pull disk info from /dev/sd* and save it into the array SATA

    # send all errors which are comming on stderr into never never land :D 
    # fdisk -l > disks.txt 2>/dev/null 
    SATA=( $(fdisk -l | grep -o '/dev/sd[a-z]')) 
}

get_disk_temperature() {
    # Pull disk temperature and save it into the array DISK_TEMP

    for i in "${!SATA[@]}"
    do
        # declare and assign variable separately to avoid masking return value
        DISK_TEMP[$i]=" (IDLE)"
        local t
        t=$(smartctl -a "${SATA[$i]}" -d sat | grep "Temp")

        if (( $? == 0 ))
        then

            # split the line obtained from smartctl by blank-character
            # and replace blank by new line, each new line is converted to
            # an indexed array.
            local temp=( $(echo $t | tr " " "\n")) 

            # alternatively the awk version for that (then temp is just a 
            # variable and not an array):
            # local temp=$(echo $t | awk '{print $10}')

            DISK_TEMP[$i]="${temp[-1]}"     # the last entry is the temperature
        else
            DISK_TEMP[$i]=""
        fi
    done
}

get_cpu_temperature() {
    # Pull the CPU temperature from each core (there are 4 cores) and save
    # the value to the array CPU_TEMP

    for i in {0..4}
    do
        _t=$(($(</sys/class/thermal/thermal_zone${i}/temp) / 1000))
        CPU_TEMP[$i]="$_t"
    done
}

fan_on() {
    i2cset -y 1 0x60 0x05 0x00
}

fan_off() {
    i2cset -y 1 0x60 0x05 0x05
}

handle_fan() {
    for i in "${!DISK_TEMP[@]}"
    do

        if [ "${FAN_CHANGED}" != "1" ]
        then
            disk_curr_threshold=$((DISK_TEMP_THRESHOLD+DISK_TEMP_INTERVAL))
        else
            disk_curr_threshold=$((DISK_TEMP_THRESHOLD))
        fi


        if (( "${DISK_TEMP[$i]}" > "${disk_curr_threshold}" ))
        then
            if [ "${FAN_CHANGED}" != "1" ]
            then
                echo "Turning fan on because disk $i has hit the threshold ${disk_curr_threshold}."
                echo "Disk $i has current temperature of ${DISK_TEMP[$i]} degree."
            fi

            FAN_CHANGED="1"
            fan_on
            return
        fi
    done

    for i in "${!CPU_TEMP[@]}"
    do

        if [ "${FAN_CHANGED}" != "1" ]
        then
            cpu_curr_threshold=$((CPU_TEMP_THRESHOLD+CPU_TEMP_INTERVAL))
        else
            cpu_curr_threshold=$((CPU_TEMP_THRESHOLD))
        fi


        if (( "${CPU_TEMP[$i]}" > "${cpu_curr_threshold}" ))
        then
            if [ "${FAN_CHANGED}" != "1" ]
            then
                echo "Turning fan on because CPU $i has hit the threshold $cpu_curr_threshold degree."
                echo "CPU $i has current temperature of ${CPU_TEMP[$i]} degree."
            fi

            FAN_CHANGED="1"
            fan_on
            return
        fi
    done

    # No fuss, fan is off
    if [ "${FAN_CHANGED}" != "0" ]
    then
        echo "All temps nominal, turning fan off."
        print_temp 
        FAN_CHANGED="0"
    fi
    fan_off
}

print_temp(){
    # print all temperature variables from CPU and disk
    for i in "${!CPU_TEMP[@]}"
    do
        echo "CPU $i has current temperature of ${CPU_TEMP[$i]} degree."
    done

    for i in "${!DISK_TEMP[@]}"
    do
        echo "Disk $i has current temperature of ${DISK_TEMP[$i]} degree."
    done
}

while true; do
	get_disk_dev_info
	get_disk_temperature
	get_cpu_temperature
	handle_fan

	sleep ${REFRESH}
done
