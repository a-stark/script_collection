


import subprocess

def get_cpu_temperature():

    cpu_temp =[]
    cpu_name = []
    for cpu_unit in range(5):
        with open("/sys/class/thermal/thermal_zone{0}/temp".format(cpu_unit)) as temp_file:
            cpu_temp.append(float(temp_file.read())/1000)

        with open("/sys/class/thermal/thermal_zone{0}/type".format(cpu_unit)) as type_file:
            cpu_name.append(type_file.read().strip())

    return [(cpu_name[i], cpu_temp[i]) for i in range(len(cpu_temp))]


def get_disk_temperature():

    hdd_temp = []
    hdd_list = ['sda', 'sdb']
    for hdd in hdd_list:

        output = float(subprocess.Popen(['smartctl -a /dev/{0} -d sat'.format(hdd)], 
                                        shell=True, stdout=subprocess.PIPE)

        output = output.stdout.read().decode('utf-8').split('/n')

        for line in output:
            if 'Temperature' in  line:
                temp = float(line.split()[-1])
                hdd_temp.append(temp)
                break   # assume just one temperature info

        hdd_temp.append(a)

    return [(hdd_list[i], hdd_temp[i]) for i in range(len(hdd_list))]



