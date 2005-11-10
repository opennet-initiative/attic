#!/usr/bin/python
#Copyright 2005 Sebastian Hagen
# This file is part of ketupo.

# ketupo is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 
# as published by the Free Software Foundation

# ketupo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with ketupo; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import time
import logging

import socket_management
from address_structures import ip_make
from node_structures import olsr_node, olsr_node_connection


MODE_IDLE = 0
MODE_DATA = 1

class olsrd_client_connection(socket_management.sock_stream_connection_linebased):
   def __init__(self, address, input_handler, close_handler, parent_loggername=''):
      self.loggername = parent_loggername + '.olsrd_client_connection'
      self.logger = logging.getLogger(self.loggername)

      socket_management.sock_stream_connection_linebased.__init__(self, line_delimiters=['\n'])
      
      self.input_handler_parent = input_handler
      self.close_handler = close_handler
      self.mode = 0
      self.connection_init(address)
      self.olsr_data = []
      
   def input_handler(self):
      for line in self.buffer_lines:
         line_split = line.split()
         if (len(line_split) == 0):
            continue
         command = line_split.pop(0)
         
         if (command == 'START'):
            self.mode = MODE_DATA
            self.olsr_data = []
         elif (command == 'END'):
            self.mode = MODE_IDLE
            if (callable(self.input_handler_parent)):
               self.input_handler_parent(self, self.olsr_data)
               
         elif (command in ('LL', 'TC')):
            if (self.mode != MODE_DATA):
               self.logger.log(38, 'Got LL/TC line while in mode %r; ignoring. Line: %r' % (self.mode, line))
            if (len(line_split) <= 3):
               self.logger.log(35, 'Read invalid LL/TC line: too few fields (expected at least 4). Ignoring line. Line: %r' % (line,))
               continue
            try:
               ip_1 = ip_make(line_split[0])
               ip_2 = ip_make(line_split[1])
               link_quality = float(line_split[2])
               link_quality_neighbor = float(line_split[3])
            except ValueError:
               self.logger.log(35, 'Read invalid LL/TC line: unable to convert field. Ignoring line. Line: %r ; Error:' % (line,), exc_info=True)
               continue
            
            node_1 = olsr_node(ip_1)
            node_2 = olsr_node(ip_2)
            
            if (node_1 in self.olsr_data):
               node_1 = self.olsr_data[self.olsr_data.index(node_1)]
            else:
               self.olsr_data.append(node_1)
            
            if (node_2 in self.olsr_data):
               node_2 = self.olsr_data[self.olsr_data.index(node_2)]
            else:
               self.olsr_data.append(node_2)
            
            connection_1 = node_1.connection_return(ip_2)
            connection_2 = node_2.connection_return(ip_1)
            
            if not (connection_1):
               connection_1 = olsr_node_connection(node_2, link_quality)
               node_1.connection_add(connection_1)

            if not (connection_2):
               connection_2 = olsr_node_connection(node_1, link_quality_neighbor)
               node_2.connection_add(connection_2)
               
            
            if (len(line_split) >= 5):
               try:
                  link_status = int(line_split[4])
               except ValueError:
                  link_status = None
                  self.logger.log(30, 'Read invalid extended LL/TC line: unable to convert field 4. Ignoring field. Line: %r ; Error:' % (line,), exc_info=True)
               else:
                  connection_1.status = link_status
               
               if (len(line_split) >= 6):
                  try:
                     link_willingness = int(line_split[5])
                  except ValueError:
                     self.logger.log(30, 'Read invalid extended LL/TC line: unable to convert field 5. Ignoring field. Line: %r ; Error:' % (line,), exc_info=True)
                  else:
                     connection_1.willingness = link_willingness
                  
                  if (len(line_split) >= 7):
                     try:
                        link_mpr = bool(line_split[6])
                     except ValueError:
                        self.logger.log(30, 'Read invalid extended LL/TC line: unable to convert field 6. Ignoring field. Line: %r ; Error:' % (line,), exc_info=True)
                     else:
                        connection_1.mpr = link_mpr
               
                     if (len(line_split) >= 8):
                        try:
                           linkcount = int(line_split[7])
                        except ValueError:
                           self.logger.log(30, 'Read invalid extended LL/TC line: unable to convert field 7. Ignoring field. Line: %r ; Error:' % (line,), exc_info=True)
                        else:
                           connection_1.linkcount=linkcount

      del(self.buffer_lines[:])
      

class olsrd_client_query:
   def __init__(self, address, input_handler, parent_loggername=''):
      self.loggername = parent_loggername + '.olsrd_client_query'
      self.logger = logging.getLogger(self.loggername)
      if not (callable(input_handler)):
         raise TypeError('Value %r for input_handler parent is not callable.' % (input_handler,))
      
      self.input_handler_parent = input_handler
      self.olsrd_connection = olsrd_client_connection(address=address, input_handler=self.input_handler, close_handler=self.close_handler, parent_loggername=self.loggername)

   def input_handler(self, olsrd_connection, olsrd_data):
      if (self.olsrd_connection):
         olsrd_connection = self.olsrd_connection
         self.olsrd_connection = None
         olsrd_connection.clean_up()
         self.input_handler_parent(olsrd_data)
      
   def close_handler(self, olsrd_connection, fd):
      if (self.olsrd_connection):
         self.olsrd_connection.clean_up()
         self.input_handler_parent(None)
   
         