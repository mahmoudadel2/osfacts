#!/usr/bin/env python
__author__ = 'Mahmoud Adel <mahmoud.adel2@gmail.com>'
__license__ = "The MIT License (MIT)"

import platform
import fcntl
import struct
import socket
import os


def architecture():
    # Getting arch
    return platform.machine()


def disks():
    # Getting disks size
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
                if disk[-1:].isdigit():
                    disk = disk[:-1]
                if disk not in str(diskinfo.keys()):
                    diskname = tmplist[3]
                    size = int(tmplist[2]) * 1024
                    diskinfo[diskname] = dict()
                    diskinfo[diskname]['size'] = size
    # Getting disks model & serial number
    for disk in diskinfo.keys():
        try:
            with open('/dev/{0}'.format(disk), 'rb') as hd:
                # Getting disks model and serial
                formatstr = "@ 10H 20s 3H 8s 40s 2B H 2B H 4B 6H 2B I 36H I Q 152H"
                hdioid = 0x030d
                sizeofhddriveid = struct.calcsize(formatstr)
                buf = fcntl.ioctl(hd, hdioid, ' ' * sizeofhddriveid)
                fields = struct.unpack(formatstr, buf)
                serial = fields[10].strip()
                model = fields[15].strip()
                diskinfo[disk]['model'] = model
                diskinfo[disk]['serial'] = serial
        except IOError:
            diskinfo[disk]['model'] = str()
            diskinfo[disk]['serial'] = str()
    return diskinfo


def hostname():
    # Getting hostname
    hostname = socket.gethostname()
    return hostname


def fqdn():
    # Getting FQDN
    fqdn = socket.getfqdn()
    return fqdn


def distribution():
    # Getting distribution
    dist = platform.linux_distribution()
    distname = dist[0]
    version = dist[1]
    distid = dist[2]
    distinfo = {'distname': distname, 'version': version, 'id': distid}
    return distinfo


def interfaces():
    interfacesinfo = dict()
    interfaces = os.listdir('/sys/class/net/')
    for interface in interfaces:
        # Getting IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            ip = socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', interface[:15]))[20:24])
        except IOError:
            ip = str()
        # Getting MAC
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        macdata = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', interface[:15]))
        mac = str().join(['%02x:' % ord(char) for char in macdata[18:24]])[:-1]
        interfacesinfo[interface] = {'ipaddress': ip, 'macaddress': mac}
    return interfacesinfo


def kernel():
    # Getting Kernel info
    kernelname = platform.system()
    kernelrelease = platform.release()
    kernelinfo = {'kernelname': kernelname, 'kernelrelease': kernelrelease}
    return kernelinfo


def memory():
    # Getting memory info
    meminfo = dict()
    with open('/proc/meminfo') as f:
        for line in f:
            if 'MemTotal' in line:
                memorytotal = int(line.split(':')[1].strip().split()[0]) * 1024
                meminfo['memorytotal'] = memorytotal
            if 'SwapTotal' in line:
                swaptotal = int(line.split(':')[1].strip().split()[0]) * 1024
                meminfo['swaptotal'] = swaptotal
    return meminfo


def cpu():
    # Getting CPU info
    cpucount=0
    cpuinfo = dict()
    with open('/proc/cpuinfo') as f:
        for line in f:
            if 'model name' in line:
                model = line.split(':')[1].strip()
                cpuinfo['model'] = model
                cpucount = cpucount + 1
            if 'flags' in line:
                if 'vmx' in line or 'svm' in line:
                    virtualization = True
                else:
                    virtualization = False
                if 'ht' in line:
                    hyperthreading = True
                else:
                    hyperthreading = False
            if 'cpu cores' in line:
                cpucores = line.split(':')[1].strip()
    cpuinfo['virtualization'] = virtualization
    cpuinfo['hyperthreading'] = hyperthreading
    cpuinfo['cpucores'] = cpucores
    cpuinfo['processorcount'] = cpucount
    return cpuinfo


def system():
    # Getting system info
    with open('/sys/devices/virtual/dmi/id/product_name') as f:
        productname = f.read().strip()
    with open('/sys/devices/virtual/dmi/id/board_vendor') as f:
        boardvendor = f.read().strip()
    with open('/sys/devices/virtual/dmi/id/chassis_vendor') as f:
        chassisvendor = f.read().strip()
    sysinfo = {'productname': productname, 'boardvendor': boardvendor, 'chassisvendor': chassisvendor}
    return sysinfo


def partitions():
    # Getting partitions size
    partitionsinfo = dict()
    major = (3, 8)
    with open('/proc/partitions') as f:
        for line in f:
            tmplist = line.split()
            if len(tmplist) == 0 or not tmplist[0].isdigit():
                continue
            majorstr = tmplist[0]
            if majorstr in str(major):
                partition = tmplist[3]
                if partition[-1:].isdigit():
                    if partition not in str(partitionsinfo.keys()):
                        partitionname = tmplist[3]
                        size = int(tmplist[2]) * 1024
                        partitionsinfo[partitionname] = dict()
                        partitionsinfo[partitionname]['size'] = size
                        partitionsinfo[partitionname]['ismounted'] = False
    # Getting mount point
    with open('/proc/mounts') as f:
        for line in f:
            tmplist = line.split()
            partition = tmplist[0].split('/')[-1]
            if partition in partitionsinfo.keys():
                mountpoint = tmplist[1]
                partitionsinfo[partition]['ismounted'] = True
                partitionsinfo[partition]['mountpoint'] = mountpoint
    return partitionsinfo