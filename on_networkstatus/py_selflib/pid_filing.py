#!/usr/bin/env python
#Copyright 2004 Sebastian Hagen
# This file is part of py_selflib.

# py_selflib is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 
# as published by the Free Software Foundation

# py_selflib is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with py_selflib; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import sys
import os
import fcntl

pid_file = None

def file_pid(pid_filename=os.path.basename(sys.argv[0]) + '.pid'):
   global pid_file
   if (os.path.exists(pid_filename)):
      pid_file = file(pid_filename, 'r+')
   else:
      pid_file = file(pid_filename, 'w')

   try:
      fcntl.lockf(pid_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
   except IOError:
      pid_file.close()
      print 'Our pid-file %s is already locked, aborting.' % (pid_filename,)
      sys.exit(0)
   else:
      pid_file.write('%s' % (os.getpid(),))
      pid_file.truncate()
      pid_file.flush()
      return pid_file

def release_pid_file(pidfile=None):
   global pid_file
   if not (pidfile):
      pidfile = pid_file
   
   fcntl.lockf(pidfile.fileno(), fcntl.LOCK_UN)
   pidfile.close()
   pidfile = None
   
