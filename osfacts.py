#!/usr/bin/env python
__author__ = 'Mahmoud Adel <mahmoud.adel2@gmail.com>'

import platform
import fcntl
import struct

def architecture():
    return platform.machine()


def disks():
    # Getting disks
    disklist = list()
    diskinfo = dict()
    major = (3, 8)
    with open('/proc/partitions') as f:
        for line in f:
            tmplist = line.split()
            if len(tmplist) == 0 or not tmplist[0].isdigit():
                continue
            majorstr = tmplist[0]
            if majorstr in str(major):
                disk = tmplist[3]
                if disk[-1:].isdigit(): disk = disk[:-1]
                if disk not in str(disklist): disklist.append(tmplist[3])
    # Getting disks model & serial number
    for disk in disklist:
        try:
            with open('/dev/{0}'.format(disk), 'rb') as hd:
                formatstr = "@ 10H 20s 3H 8s 40s 2B H 2B H 4B 6H 2B I 36H I Q 152H"
                hdioid = 0x030d
                sizeofhddriveid = struct.calcsize(formatstr)
                buf = fcntl.ioctl(hd, hdioid, " " * sizeofhddriveid)
                fields = struct.unpack(formatstr, buf)
                serial = fields[10].strip()
                model = fields[15].strip()
                diskinfo[disk] = {'model': model, 'serial': serial}
        except IOError:
            diskinfo[disk] = {'model': '', 'serial': ''}
    return diskinfo




print disks()
