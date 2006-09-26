#!/usr/bin/env python
#Copyright 2006 Sebastian Hagen
# This file is part of brookii.

# brookii is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2
# as published by the Free Software Foundation

# brookii is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with py_selflib; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import datetime
import time
import logging
from socket import AF_INET

from socket_management import asynchronous_transfer_base, fd_wrap, Timer
from nlct import NfctHandle, NFCT_MSG_UNKNOWN, NFCT_MSG_NEW, NFCT_MSG_UPDATE, NFCT_MSG_DESTROY

_logger = logging.getLogger('brookii_main')

try:
   import MySQLdb as mysql_module
   db_module = mysql_module
except ImportError:
   _logger.log(35, 'Unable to import MySQLdb')
   db_module = None
else:
   mysql_DatabaseError = db_DatabaseError = mysql_module.DatabaseError


class Nfct_Connection_Wrapper:
   def __init__(self, connection_data):
      self.connection_data = connection_data
      self.start = None
      self.start_reliable = False
      self.finish_reliable = False
      self.finish = None
      self.id = None

   def __eq__(self, other):
      return ((isinstance(self.__class__, other) or isinstance(other.__class__, self)) and 
              (self.connection_data == other.connection_data))

   def __ne__(self, other):
      return not (self == other)

   def __hash__(self):
      return hash(self.connection_data)
   
   def __repr__(self):
      return '%s%s' % (self.__class__.__name__, (self.connection_data,))

class Data_Collocator(asynchronous_transfer_base):
   logger = logging.getLogger('DataCollocator')
   def __init__(self, family=AF_INET, connection_verify_interval=3600):
      asynchronous_transfer_base.__init__(self)
      self.nfct_handle = None
      self.fd = None
      self.family = family
      self.connections = {}
      self.interval_connection_verify = connection_verify_interval
      self.timer_connection_verify = None
      
   def __getinitargs__(self):
      return ()
   
   def timer_connection_verify_unregister(self):
      if (self.timer_connection_verify):
         self.timer_connection_verify.unregister()
         self.timer_connection_verify = None
   
   def nfct_init(self):
      self.nfct_handle = nfct_handle = NfctHandle()
      self.fd = fd_wrap(nfct_handle.fileno(), self, nfct_handle)
      self.fd.fd_register_read()
      self.fd_read(self.fd)
      self.connections_verify()
      self.timer_connection_verify_unregister()
      self.timer_connection_verify = Timer(self.interval_connection_verify, self.connections_verify, parent=self, persistence=True)

   def connections_verify(self):
      connections_active = len(self.connections)
      self.logger.log(20, 'Starting connection verify cycle (cached connections: %d).' % (connections_active,))
      now = datetime.datetime.now()
      data = self.nfct_handle.dump_conntrack_table(self.family)
      self.input_process(data)
      nfct_dict = dict.fromkeys([Nfct_Connection_Wrapper(nfct_msg.connection_data) for nfct_msg in data])
      connections_lost = 0
      for key in self.connections:
         if not (key in nfct_dict):
            connwrap = self.connections[key]
            if not (connwrap.finish_reliable):
               connwrap.finish = now
            self.data_store(connwrap)
            del(self.connections[key])
            connections_lost += 1
      self.logger.log(20, 'Connection verify cycle done. Expired %d lost connections.' % (connections_lost,))


   def fd_forget(self, fd):
      if (fd == self.fd):
         self.fd = self.nfct_handle = None
         self.timer_connection_verify_unregister()

   def fd_read(self, fd):
      if not (self.fd == fd):
         raise ValueError("I'm not responsible for fd %r." % (fd,))
   
      data = self.nfct_handle.event_conntrack()
      self.input_process(data)

   def input_process(self, data):
      now = datetime.datetime.now()
      for nfct_msg in data:
         nfct_msg_type = nfct_msg.type
         if (nfct_msg_type == NFCT_MSG_UNKNOWN):
            #I have no idea what this is supposed to be.
            self.logger.log(35, 'Got NFCT_MSG_UNKNOWN. Ignoring it. nfct_msg: %r' % nfct_msg)
            continue
         connwrap = Nfct_Connection_Wrapper(nfct_msg.connection_data)
         if (connwrap in self.connections):
            if (nfct_msg_type == NFCT_MSG_NEW):
               self.logger.log(38, 'Ignoring new connection %r since self.connections already contains %r.' % (connwrap.connection_data, self.connections[connwrap].connection_data))
               continue
            else:
               connwrap = self.connections[connwrap]
               #they may be equal, but that doesn't mean they're identical. use new connection data.
               connwrap.connection_data = nfct_msg.connection_data
         else:
            self.connections[connwrap] = connwrap
         connwrap.finish = now
         
         if not (connwrap.start):
            connwrap.start = now
            if (nfct_msg_type == NFCT_MSG_NEW):
               connwrap.start_reliable = True

         if (nfct_msg_type == NFCT_MSG_DESTROY):
            connwrap.finish_reliable = True
            self.data_store(connwrap)
            try:
               del(self.connections[connwrap])
            except KeyError:
               self.logger.log(25, 'Got DESTROY event for untracked connection %r. Processing anyway.' % (nfct_msg.connection_data,))
               
         else:
            self.data_store(connwrap)

   def data_store(self, connwrap):
      raise NotImplementedError('data_store should be implemented by subclass.')


class Data_Collocator_DB(Data_Collocator):
   logger = logging.getLogger('Data_Collocator_DB')
   db_exception = db_DatabaseError
   def __init__(self, db_connector=db_module.connect, connect_interval=100, db_args=(), db_kwargs={}, *args, **kwargs):
      Data_Collocator.__init__(self, *args, **kwargs)
      self.output_cache = []
      self.db_connector = db_connector
      self.db_args = db_args
      self.db_kwargs = db_kwargs
      self.db_connection = self.db_cursor = None
      self.db_connect_attempt_last = None
      self.db_connect_interval = connect_interval
      
   def db_connect(self):
      self.db_connect_attempt_last = time.time()
      self.db_connection = self.db_connector(*self.db_args, **self.db_kwargs)
      self.db_cursor = self.db_connection.cursor()
      
   def db_close(self):
      if (self.db_connection):
         self.db_connection.close()
      self.db_connection = self.db_cursor = None

   def data_store(self, connwrap):
      self.logger.log(10, '%r preparing to store data.' % (self,))
      self.output_cache.append(connwrap)
      try:
         self.data_output()
      except self.db_exception:
         self.logger.log(40, "Database access failed; I'll retry later. Error was:", exc_info=True)

   def __getinitargs__(self):
      return (self.db_connector, self.db_connect_interval, self.db_args, self.db_kwargs) + Data_Collocator.__getinitargs__(self)

   def __getstate__(self):
      return (self.connections, self.output_cache)
   
   def __repr__(self):
      return '%s%s' % (self.__class__.__name__, self.__getinitargs__())
   
   def __setstate__(self, state):
      (self.connections, self.output_cache) = state

   def data_output(self):
      raise NotImplementedError('data_output should be implemented by subclass.')


if (mysql_module):
   class Data_Collocator_Mysql(Data_Collocator_DB):
      logger = logging.getLogger('Data_Collocator_Mysql')
      exception = mysql_DatabaseError
      def __init__(self, db_table, *args, **kwargs):
         Data_Collocator_DB.__init__(self, *args, **kwargs)
         self.db_table = db_table

      def data_output(self):
         if (not self.db_connection):
            self.logger.log(10, "Not pushing data; waiting for db reconnect delay expiration.") 
            if ((not (self.db_connect_attempt_last is None)) and ((self.db_connect_attempt_last + self.db_connect_interval) > time.time())):
               return
            self.db_connect()

         self.logger.log(15, "%r beginning mysql push cycle." % (self,))
         while (self.output_cache):
            e = self.output_cache[0]
            c = e.connection_data.connection
            self.db_cursor.execute(('REPLACE INTO %s (id, start, finish, start_reliable, finish_reliable, l3proto, to_l3src, to_l3dst, back_l3src, back_l3dst, l4proto, to_l4src, to_l4dst, back_l4src, back_l4dst, protoinfo, status, to_packets, back_packets, to_bytes, back_bytes) VALUES' % (self.db_table,)) + ' (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            (e.id, e.start, e.finish, e.start_reliable, e.finish_reliable, c.l3proto, int(c.to_src), int(c.to_dst), int(c.back_src), int(c.back_dst), c.l4proto, int(c.to_l4src), int(c.to_l4dst), int(c.back_l4src), int(c.back_l4dst), c.protoinfo, e.connection_data.status, c.to_packets, c.back_packets, c.to_bytes, c.back_bytes))
            if not (e.id):
               self.db_cursor.execute('SELECT MAX(id) from %s' % (self.db_table,), ())
               e.id = self.db_cursor.fetchone()[0]
            self.logger.log(10, "Inserted %r into database." % (e,))
            del(self.output_cache[0])
         self.logger.log(15, "%r finished mysql push cycle." % (self,))

      def __getinitargs__(self):
         return (self.db_table,) + Data_Collocator_DB.__getinitargs__(self)



