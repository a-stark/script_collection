#!/bin/bash
#
# Script to adjust fan speed according to temperature

# needs root privileges, since fdisk and smartctl needs root access to read out disk information

REFRESH="5"	                # refresh rate in seconds
DISK_TEMP_THRESHOLD="35"    # disk temperature threshold in degree 
DISK_TEMP_INTERVAL="5"	  	# temperature interval where nothing is done
CPU_TEMP_THRESHOLD="40"     # cpu temperature threshold in degree
CPU_TEMP_INTERVAL="20"       # cpu interval where nothing is done
FAN_CHANGED="*"

get_disk_dev_info() {
    # Pull disk info from /dev/sd*
    #fdisk -l > disks.txt 2>/dev/null # send all errors which are comming on stderr into never never land :D 
    SATA=( $(fdisk -l | grep -o '/dev/sd[a-z]')) 
}

get_disk_temperature() {
    for i in "${!SATA[@]}"
    do
        # declare and assign variable seperately to avoid masking return value
        DISK_TEMP[$i]=" (IDLE)"
        local t
        t=$(smartctl -a "${SATA[$i]}" -d sat | grep "Temp")

        if (( $? == 0 ))
        then

            # split the line obtained from smartctl by blank-character
            # and replace blank by new line, each new line is converted to
            # an indexed array.
            local temp=( $(echo $t | tr " " "\n")) 
            DISK_TEMP[$i]="${temp[-1]}"     # the last entry is the temperature
        else
            DISK_TEMP[$i]=""
        fi
    done
}

get_cpu_temperature() {
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
            disk_curr_threshold="${DISK_TEMP_THRESHOLD}"+"${DISK_TEMP_INTERVAL}"
        else
            disk_curr_threshold="${DISK_TEMP_THRESHOLD}"
        fi


        if (( "${DISK_TEMP[$i]}" > "${disk_curr_threshold}" ))
        then
            if [ "${FAN_CHANGED}" != "1" ]
            then
                echo "Turning fan on because disk $i has hit the threshold $disk_curr_threshold"
                echo "Disk $i has current temperature of $DISK_TEMP[$i] degree."
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
