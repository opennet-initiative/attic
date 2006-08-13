#!/usr/bin/python2.4
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

import socket
from socket import IPPROTO_TCP, IPPROTO_UDP, IPPROTO_ICMP

import address_structures
import nlct_

IPPROTO_SCTP = 132

nfct_connection_classes = {}
nfct_l4_address_classes = {}

def ip_make(ip_data):
   if (isinstance(ip_data, tuple) and (len(ip_data) == 4)):
      ip_data = ip_data[3] + 2**32 * ip_data[2] + 2**64 * ip_data[1] + 2**96 * ip_data[0] 
   return address_structures.ip_make(ip_data)

def nfct_make(nfct_data):
   nfct_tuple = nfct_data[0]
   assert nfct_tuple[0] == nfct_data[1][1]
   assert nfct_tuple[1] == nfct_data[1][0]
   assert nfct_tuple[2] == nfct_data[1][2]
   assert nfct_tuple[3] == nfct_data[1][3]
   assert nfct_tuple[4] == nfct_data[1][5]
   assert nfct_tuple[5] == nfct_data[1][4]
   nfct_nat = nfct_data[10]
   l4proto = nfct_tuple[3]
   return Nfct(
      Nfct_Connection(
         src=nfct_tuple[0],dst=nfct_tuple[1],l3proto=nfct_tuple[2],l4proto=l4proto,
         l4src=L4_Address(l4proto,nfct_tuple[4]), l4dst=L4_Address(l4proto, nfct_tuple[5]), protoinfo=nfct_data[7], 
         packetsto=nfct_data[8][0], bytesto=nfct_data[8][1], packetsfrom=nfct_data[9][0], bytesfrom=nfct_data[9][1]),
      Nfct_Nat(nfct_nat[0], nfct_nat[1], L4_Address(l4proto, nfct_nat[2]), L4_Address(l4proto, nfct_nat[3])),
      *nfct_data[2:7]
   )
   
class Nfct_Indexed_Meta(type):
   def __init__(self, *args, **kwargs):
      type.__init__(self, *args, **kwargs)
      try:
         self.__class__.Index[self.l4proto] = self
      except AttributeError:
         pass

class Nfct_Connection_Meta(Nfct_Indexed_Meta):
   Index = nfct_connection_classes

class Nfct_L4_Address_Meta(Nfct_Indexed_Meta):
   Index = nfct_l4_address_classes

class Nfct_Connection(object):
   __metaclass__ = Nfct_Connection_Meta
   def __new__(cls, **kwargs):
      l4proto = kwargs['l4proto']
      if (l4proto in nfct_connection_classes):
         target_class = nfct_connection_classes[l4proto]
      else:
         target_class = nfct_connection_classes[None]
      return object.__new__(target_class, **kwargs)
   
   def __init__(self, src, dst, l3proto, l4src, l4dst, protoinfo, packetsto, bytesto, packetsfrom, bytesfrom, l4proto=None):
      self.src = ip_make(src)
      self.dst = ip_make(dst)
      self.l3proto = l3proto
      self.l4src = l4src
      self.l4dst = l4dst
      self.protoinfo = protoinfo
      self.to_packets = packetsto
      self.to_bytes = bytesto
      self.from_packets = packetsfrom
      self.from_bytes = bytesfrom
      if ((self.l4proto is None) and (not (l4proto is None))):
         self.l4proto = l4proto

   def super(self):
      return super(self.__class__, self)

   def __getinitargs__(self):
      return (self.src, self.dst, self.l3proto, self.l4src, self.l4dst, self.protoinfo, self.to_packets, self.to_bytes, 
         self.from_packets, self.from_bytes, self.l4proto)

   def __repr__(self):
      return '%s%r' % (self.__class__.__name__, self.__getinitargs__())

   def __str__(self):
      return '%s:%s(%s,%s) <-> %s:%s(%s,%s); %s[%s] %s' % (self.src, self.l4src, self.to_packets, self.to_bytes, self.dst, self.l4dst,
         self.from_packets, self.from_bytes, self.l3proto, self.protoinfo, self.l4proto)

class Nfct_Connection_Unknown(Nfct_Connection):
   l4proto = None	#default entry set by metaclass

class Nfct_Connection_TCP(Nfct_Connection):
   l4proto = IPPROTO_TCP

class Nfct_Connection_UDP(Nfct_Connection):
   l4proto = IPPROTO_UDP

class Nfct_Connection_SCTP(Nfct_Connection):
   l4proto = IPPROTO_SCTP

class Nfct_Connection_ICMP(Nfct_Connection):
   l4proto = IPPROTO_ICMP

class L4_Address(object):
   __metaclass__ = Nfct_L4_Address_Meta
   def __new__(cls, l4proto, *args, **kwargs):
      if (l4proto in nfct_l4_address_classes):
         target_class = nfct_l4_address_classes[l4proto]
      else:
         target_class = nfct_l4_address_classes[None]
      return object.__new__(target_class, l4proto, *args, **kwargs)
   
   def super(self):
      return super(self.__class__, self)

class L4_Address_ShortPort(L4_Address):
   def __init__(self, l4proto, port):
      self.port = port
   
   def __repr__(self):
      return '%s(%r)' % (self.__class__.__name__, self.port)
   
   def __int__(self):
      return int(self.port)
   
   def __str__(self):
      return str(int(self))

class L4_Address_Unknown(L4_Address_ShortPort):
   l4proto = None

class L4_Address_TCP(L4_Address_ShortPort):
   l4proto = IPPROTO_TCP

class L4_Address_UDP(L4_Address_ShortPort):
   l4proto = IPPROTO_UDP

class L4_Address_SCTP(L4_Address_ShortPort):
   l4proto = IPPROTO_SCTP

class L4_Address_ICMP(L4_Address):
   l4proto = IPPROTO_ICMP
   def __init__(self, l4proto, ctype, code, id):
      self.type = ctype
      self.code = code
      self.id = id

   def __repr__(self):
      return '%s%r' % (self.__class__.__name__, (self.type, self.code, self.id))

class Nfct_Nat:
   def __init__(self, min_ip, max_ip, min_l4, max_l4):
      self.min_ip = ip_make(min_ip)
      self.max_ip = ip_make(max_ip)
      self.min_l4 = min_l4
      self.max_l4 = max_l4

   def __getinitargs__(self):
      return (self.min_ip, self.max_ip, self.min_l4, self.max_l4)

   def __repr__(self):
      return '%s%r' % (self.__class__.__name__, self.__getinitargs__())

   def __str__(self):
      return 'NAT(%s:%s %s:%s)' % (self.min_ip, self.min_l4, self.max_ip, self.max_l4)

class Nfct:
   def __init__(self, connection, nat, timeout, mark, status, use, id):
      self.connection = connection
      self.nat = nat
      self.timeout = timeout
      self.mark = mark
      self.status = status
      self.use = use
      self.id = id
   
   def __getinitargs__(self):
      return (self.connection, self.nat, self.timeout, self.mark, self.status, self.use, self.id)
   
   def __repr__(self):
      return '%s%r' % (self.__class__.__name__, self.__getinitargs__())
   
   def __str__(self):
      return 'NFCT([%s] %s %s, [%s %s %s %s])' % (self.id, self.connection, self.nat, self.timeout, self.mark, self.status, self.use)
