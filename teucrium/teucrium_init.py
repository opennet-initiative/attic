#!/usr/bin/env python
#Copyright 2005 Sebastian Hagen
# This file is part of teucrium.

# teucrium is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 
# as published by the Free Software Foundation

# teucrium is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with teucrium; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
import sys

import pycapabilities
import iptint

import socket_management
import teucrium_main
import basic_io
import daemon_init
import pid_filing

chroot_target = os.path.expanduser('~')
execfile('teucrium_conf.py')

if (os.getuid() == 0):
   os.chroot(chroot_target)
   os.chdir('/')
   basic_io.log_init()
   pycapabilities.prctl(pycapabilities.PR_SET_KEEPCAPS,1,0,0,0)
   os.setgid(target_gid)
   os.setuid(target_uid)
   pycapabilities.cap_set('all= CAP_NET_ADMIN,CAP_NET_RAW+ep')

if (os.getuid() == 0):
   print 'Switching uid from root failed. Terminating.'
   os.exit(1)
   
pid_filing.file_pid()

pid_filing.release_pid_file()
daemon_init.daemon_init()
pid_filing.file_pid()

iptg01 = teucrium_main.ipt_grapher(rrd_filename=filename_rrd, rrd_step=rrd_step, timer_register=True)

for target_specification in counters_to_track:
   iptg01.target_add(*target_specification[0], **target_specification[1])

if ('-c' in sys.argv):
   iptg01.rrd_create(start_time=rrd_start, minimum=ds_min, maximum=ds_max, heartbeat=rrd_heartbeat, ds_type='DERIVE', RRAs=rrd_rras)
   
socket_management.select_loop()
