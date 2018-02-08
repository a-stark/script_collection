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

Copyright (c) 2018 Alexander Stark alexander.stark@uni-ulm.de
"""



import os
import psutil
import stat
from sys import platform


def get_fd_max():
    """ Retrieve the maximal available file descriptors depending on the OS.

    Returns
    -------
    int
        the maximal number of file descriptors
    """

    if platform == 'win32':
        import win32file
        fd_max = win32file._getmaxstdio() # kind of the soft limit
        # hard limit is not specified but very often 4*softlimit

    # all other possibilites ('linux', 'cygwin', 'darwin') should support this:
    else: 
        import resource
        # the soft limit imposed by the current configuration
        # the hard limit imposed by the operating system.
        soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        fd_max = hard

    return fd_max


def get_raw_fd():
    """ Try to get all opened file descriptors via psutil.
    
    Returns
    -------
    list
        a list of popenfile objects, which is an instance of tuple. Each entry
        of this list should at least have the attributes
        path: str
            the path of the opened file
        fd: int 
            the file descriptor index associated with it.

    Depending on the OS, the information about file descriptors can be rich 
    (=> on Unix systems) or very sparse or even not complete (=> Windows).

    In general the popenfile is a tuple, and at least the attributes 'path' and
    'fd' are present. Ideally, the 'fd' will identify the opened files and 
    'path' is describing their path-location in the system.
    However, in Windows an 'fd=-1' might be very common, therefore the correct
    file descriptor 'fd' belonging to the opened file in 'path' cannot be 
    obtained by this method.
    """
    
    proc = psutil.Process(os.getpid())
    return proc.open_files()


def get_available_fd(fd_max=512):
    """ Retrieve the available file descriptors obtained from the fstat module.

    Parameters
    ----------
    fd_max: int, optional
        the maximal (non-negative) number of file descriptors to check. Specify
        here, depending on the OS, the correct maximal number. 

    Returns
    -------   
    list
        the entries of the list are tuples(fd, res) containing 
        fd: int
            the file descriptor and
        res: os.stat_result
            the result object of os.fstat request.

    All the file descriptors from 0 to fd_max are checked and the available 
    ones are appended to the returned list. 
    """

    fd_list = []
    for i in range(fd_max):
        try:
            a = os.fstat(i)
            fd_list.append((i,a))
        except OSError:
            pass
        
    return fd_list

def get_mapped_fd():
    """ Reconstruct the opened file descriptors associated to their file paths.

    Returns
    -------  
    list:
        containing tuples(fd, path) with the meaning
        fd: int
            the integer number of the file descriptor 
        path: str
            the path to the opened file associated to the file descriptor

    This procedure should work for all operating systems and does not rely on
    Unix specific or Windows specific implementations for file descriptors.
    """

    raw_fd = get_raw_fd()
    fd_max = get_fd_max()
    fd_list = get_available_fd(fd_max)
        
    # Try now to match the opened raw files found in raw_fd with those obtained
    # from fd_list and save the found ones in the list mapped_fd

    mapped_fd = []
    for entry in raw_fd:
        path = entry.path

        wrong_fd = entry.fd # this is not used, since it is not always correct
        
        # procedure: the trick is in trying to open the available path of a 
        # file (which will associate an file descriptor with it) and check, 
        # which file descriptor is the same as the current one.
        try:
            f = open(path, 'r')
            for fd, fstat in fd_list:
                try:
                    curr_fd = f.fileno()
                    if os.path.sameopenfile(curr_fd,fd):
                        mapped_fd.append((fd, path))
                except OSError:
                    break
    
            f.close()

        # by running a method in the (i)python interpreter a history of the 
        # used calls will be created. Eventually, this will be written to a 
        # history file, which also uses a file descriptor to open and save it. 
        # This file descriptor can be available at the beginning of the 
        # execution of this method (obtained in 'get_raw_fd') but it might be 
        # already closed during the actual checking procedure. Therefore this
        # exception has to be caught.
        except FileNotFoundError:   
            continue
            
    return mapped_fd


def clean_up_fd():
    """ Close all file descriptors, which are pointing to opened file paths."""

    fd_list = get_mapped_fd()
    for fd, path in fd_list:
        try:
            print('Closing file file descriptor "fd={0}" from the path:\n{0}'
                  ''.format(fd, path))
            os.close(fd)
        except OSError:
            print('fd={0} pointing at the path="{1} cannot be closed. '
                  'Skipping it.'.format(fd, path))


# originally taken from the blog of Vangelis M. (20.05.2014):
# http://mihalop.blogspot.dk/2014/05/python-subprocess-and-file-descriptors.html

# mapping the methods to a helper variable to check for the correct mode status
# on the opened file descriptor.

_fd_types = (
    ('BLK', stat.S_ISBLK),      # block special device file
    ('CHR', stat.S_ISCHR),      # character special device file
    ('DIR', stat.S_ISDIR),      # directory    
    ('DOOR', stat.S_ISDOOR),    # mode is from a door
    ('FIFO', stat.S_ISFIFO),    # FIFO (named pipe)
    ('LNK', stat.S_ISLNK),      # symbolic link
    ('PORT', stat.S_ISPORT),    # event port
    ('REG', stat.S_ISREG),      # regular file
    ('SOCK', stat.S_ISSOCK),    # socket
    ('WHT', stat.S_ISWHT)       # whiteout
)

def fd_mode_status():
    result = []
    
    fd_max = get_fd_max()
    
    for fd in range(fd_max):
        try:
            s = os.fstat(fd)
        except:
            continue
        for fd_type, func in _fd_types:
            if func(s.st_mode):
                break
        else:
            fd_type = str(s.st_mode)
        result.append((fd, fd_type))
    return result