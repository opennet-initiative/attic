#!/usr/bin/env python2.3
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

import os
import sys

def daemon_init(stdout_filename='log/stdout', stderr_filename='log/stderr'):
   fork_result = os.fork()
   if (fork_result != 0):
      print 'Started as %s.' % (fork_result,)
      sys.exit(0)
   
   os.setsid()

   #Close stdin, stdout and stderr, and optionally replace the latter ones with file-streams.
   os.close(sys.stdin.fileno())
   sys.stdin.close()
   os.close(sys.stdout.fileno())
   sys.stdout.close()
   os.close(sys.stderr.fileno())
   sys.stderr.close()
   if (stdout_filename):
      sys.stdout = file(stdout_filename, 'a+', 1)
   if (stderr_filename):
      sys.stderr = file(stderr_filename, 'a+', 0)
   
   sys.__stderr__ = sys.__stdout__ = sys.__stdin__ = sys.stdin = None





