#!/bin/bash
#
# Script to perform periodic updates and save the output to log. Run this script as root.

echo "=========================================="
echo ""
echo "Starting update and upgrade of the system:"

echo $(date +"%Y-%m-%d on %A at %Hh%Mm%Ss.")
echo ""

/usr/bin/apt-get update -q
/usr/bin/apt-get upgrade -q -y
/usr/bin/apt-get dist-upgrade -q -y


echo ""
echo "Update and upgrade finalized."
echo ""
echo "=========================================="
