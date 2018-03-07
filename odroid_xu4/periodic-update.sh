#!/bin/bash
#
# Script to perform periodic updates and save the output to log. 
# Note: Run this script as root.
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
