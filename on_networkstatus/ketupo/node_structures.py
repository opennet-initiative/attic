#!/usr/bin/env python
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


from address_structures import ip_address_base
import weakref
from sets import Set


class olsr_node:
   def __init__(self, main_address):
      if not (isinstance(main_address, ip_address_base)):
         raise TypeError('Argument main_address %r is of type %r ; expected instance of ip_address_base.' % (main_address, type(main_address)))
      self.address = main_address
      self.connections = Set()
      
   def connection_add(self, connection):
      if not (isinstance(connection, olsr_node_connection)):
         raise TypeError('Argument connection %r is of type %r ; expected instance of olsr_node_connection.' % (connection, type(connection)))
      self.connections.add(connection)
      
   def connection_return(self, address):
      if not (isinstance(address, ip_address_base)):
         raise TypeError('Argument address %r is of type %r ; expected instance of ip_address_base.' % (address, type(address)))
      for connection in self.connections:
         if (connection.peer().address == address):
            return connection
      return None
      
      
   def __eq__(self, other):
      if (isinstance(other, self.__class__) and (other.address == self.address)):
         return True
      else:
         return False
      
   def __ne__(self, other):
      if (self.__eq__(other)):
         return False
      else:
         return True
      
   def __hash__(self):
      return hash(self.address)
   
   def __repr__(self):
      return '%s(%r)' % (self.__class__, self.address)

   __str__ = __repr__      


class olsr_node_connection:
   def __init__(self, peer, local_lq):
      if not (isinstance(peer, olsr_node)):
         raise TypeError('Argument peer %r is of type %r ; expected instance of olsr_node.' % (peer, type(peer)))
      self.peer = weakref.ref(peer)
      self.local_lq = float(local_lq)
      self.status = None
      self.willingness = None
      self.mpr = None
      self.linkcount = None

   def __eq__(self, other):
      if (isinstance(other, self.__class__) and (other.peer() == self.peer())):
         return True
      else:
         return False
      
   def __ne__(self, other):
      if (self.__eq__(other)):
         return False
      else:
         return True
      
   def __hash__(self):
      return hash(self.peer())
   
   def __repr__(self):
      return '%s(%r, %r)' % (self.__class__, self.peer(), self.local_lq)

   __str__ = __repr__
   

