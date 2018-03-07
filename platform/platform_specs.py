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


# taken from adde88 (MIT license):
# https://github.com/adde88/sslstrip-hsts-openwrt/blob/master/python2.7/site-packages/cpyrit/util.py

def detect_ncpus():
    """Detect the number of effective CPUs in the system. 

    Returns
    -------
    int
        the number of available cpu units

    This function should work for the main OS, Linux, Unix, MacOS and Windows.
    """

    # Snippet taken from ParallelPython
    # For Linux, Unix and MacOS
    if hasattr(os, "sysconf"):
        if "SC_NPROCESSORS_ONLN" in os.sysconf_names:
            #Linux and Unix
            ncpus = os.sysconf("SC_NPROCESSORS_ONLN")
            if isinstance(ncpus, int) and ncpus > 0:
                return ncpus
        else:
            #MacOS X
            return int(os.popen2("sysctl -n hw.ncpu")[1].read())
            
    #for Windows
    if "NUMBER_OF_PROCESSORS" in os.environ:
        ncpus = int(os.environ["NUMBER_OF_PROCESSORS"])
        if ncpus > 0:
            return ncpus

    #return the default value
    return 1