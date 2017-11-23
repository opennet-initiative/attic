#!/usr/bin/env python
#Copyright 2006 Sebastian Hagen
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
import socket
import logging
import cPickle
import copy_reg

logger = logging.getLogger('process_reload')

copy_reg.constructor(os.fdopen)
copy_reg.constructor(socket.fromfd)

class picklablesocket(socket.socket):
   def __init__(self, family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0):
      self.family = family
      self.type = type
      self.proto = proto
      socket.socket.__init__(self, family, type, proto)

def file_pickle(fo):
   return (os.fdopen, (fo.fileno(), fo.mode))

def socket_pickle(so):
   return (socket.fromfd, (so.fileno(),))

def reload(persistent_data):
   #logger.log(50, 'Initiating process restart.')
   copy_reg.pickle(file, file_pickle)
   copy_reg.pickle(socket.socket, socket_pickle)
   store = os.tmpfile()
   cPickle.dump(persistent_data, store)
   store.seek(0)
   argv = sys.argv[:]
   try:
      i = argv.index('--restart')
   except:
      pass
   else:
      del(argv[i:i+2])

   os.execvp(sys.argv[0], argv + ['--restart', str(store.fileno())])
   
def restore(fd):
   store = os.fdopen(fd)
   retval = cPickle.load(store)
   store.close()
   return retval

