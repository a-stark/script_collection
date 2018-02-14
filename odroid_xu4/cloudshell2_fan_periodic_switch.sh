#!/bin/bash

REFRESH=2

fan_on() {
    i2cset -y 1 0x60 0x05 0x00
}

fan_off() {
    i2cset -y 1 0x60 0x05 0x05
}


while true; do
    fan_on
    sleep ${REFRESH}
    fan_off
    sleep ${REFRESH}
done




