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
from nlct_ import IPS_EXPECTED, IPS_ASSURED, IPS_CONFIRMED, IPS_SRC_NAT, IPS_DST_NAT, IPS_NAT_MASK,\
                  IPS_SEQ_ADJUST, IPS_SRC_NAT_DONE, IPS_DST_NAT_DONE, IPS_NAT_DONE_MASK, IPS_DYING,\
                  IPS_FIXED_TIMEOUT, NFCT_MSG_UNKNOWN, NFCT_MSG_NEW, NFCT_MSG_UPDATE,\
                  NFCT_MSG_DESTROY
from nlct_ import NfctHandle as NfctHandle_

IPPROTO_SCTP = 132

nfct_connection_classes = {}
nfct_l4_address_classes = {}

def ip_make(ip_data):
   if (isinstance(ip_data, tuple) and (len(ip_data) == 4)):
      ip_data = ip_data[3] + 2**32 * ip_data[2] + 2**64 * ip_data[1] + 2**96 * ip_data[0] 
   return address_structures.ip_make(ip_data)

  
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

class Nfct_Picklable(object):
   def __getstate__(self):
      return [getattr(self, slotname) for slotname in self.__slots__]
   
   def __setstate__(self, state):
      for (slotname, val) in zip(self.__slots__, state):
         setattr(self, slotname, val)

class Nfct_Comparable(Nfct_Picklable):
   def __eq__(self, other):
      if not (isinstance(self.__class__, other) or (isinstance(other.__class__, self))):
         return False
      
      for attrstr in self.slots_relevant:
         if (getattr(self, attrstr) != getattr(other, attrstr)):
            return False

      return True

   def __ne__(self, other):
      return (not self.__eq__(other))

   def __hash__(self):
      return hash(tuple([getattr(self, attrstr) for attrstr in self.slots_relevant]))


class Nfct_Connection(Nfct_Comparable):
   __metaclass__ = Nfct_Connection_Meta
   __slots__ = ('to_src','to_dst', 'back_src','back_dst','l3proto','to_l4src','to_l4dst','back_l4src','back_l4dst','protoinfo','to_packets','to_bytes','back_packets','back_bytes','l4proto')
   slots_relevant = ('l3proto','to_src','to_dst','l4proto', 'to_l4src','to_l4dst')
   def __new__(cls, **kwargs):
      l4proto = kwargs['l4proto']
      if (l4proto in nfct_connection_classes):
         target_class = nfct_connection_classes[l4proto]
      else:
         target_class = nfct_connection_classes[None]
      return object.__new__(target_class, **kwargs)
   
   def __init__(self, to_src, to_dst, back_src, back_dst, l3proto, to_l4src, to_l4dst, back_l4src, back_l4dst, protoinfo, to_packets, to_bytes, back_packets, back_bytes, l4proto=None):
      self.to_src = ip_make(to_src)
      self.to_dst = ip_make(to_dst)
      self.back_src = ip_make(back_src)
      self.back_dst = ip_make(back_dst)
      self.l3proto = l3proto
      self.to_l4src = to_l4src
      self.to_l4dst = to_l4dst
      self.back_l4src = back_l4src
      self.back_l4dst = back_l4dst
      self.protoinfo = protoinfo
      self.to_packets = to_packets
      self.to_bytes = to_bytes
      self.back_packets = back_packets
      self.back_bytes = back_bytes
      if ((self.l4proto is None) and (not (l4proto is None))):
         self.l4proto = l4proto

   def super(self):
      return super(self.__class__, self)

   def __getinitargs__(self):
      return (self.to_src, self.to_dst, self.back_src, self.back_dst,
              self.l3proto, self.to_l4src, self.to_l4dst, self.back_l4src,
              self.back_l4dst, self.protoinfo, self.to_packets, self.to_bytes, 
              self.back_packets, self.back_bytes, self.l4proto)

   def __repr__(self):
      return '%s%r' % (self.__class__.__name__, self.__getinitargs__())

   def __str__(self):
      return '%s:%s -> %s:%s[%s/%s] ; %s:%s -> %s:%s[%s/%s] ; %s[%s] %s' % (
         self.to_src, self.to_l4src, self.to_dst, self.to_l4dst,
         self.to_packets, self.to_bytes, self.back_src, self.back_l4src,
         self.back_dst, self.back_l4dst, self.back_packets, self.back_bytes,
         self.l3proto, self.protoinfo, self.l4proto)

   def __eq__(self, other):
      if not (isinstance(self.__class__, other), isinstance(other.__class__, self)):
         return False
      
      for attrstr in self.slots_relevant:
         if (getattr(self, attrstr) != getattr(other, attrstr)):
            return False
      
      return True
   def __ne__(self, other):
      return (not self.__eq__(other))

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

class L4_Address(Nfct_Comparable):
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
   __slots__ = slots_relevant = ('port',)
   def __init__(self, l4proto, port):
      if not (0 <= port <= 65535):
         raise ValueError('Port %r is invalid.' % (port,))
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
   __slots__ = slots_relevant = ('type', 'code', 'id')
   def __init__(self, l4proto, ctype, code, id):
      if not (0 <= ctype <= 255):
         raise ValueError('Type %r is invalid.' % (type,))
      if not (0 <= code <= 255):
         raise ValueError('Code %r is invalid.' % (code,))
      if not (0 <= id <= 65535):
         raise ValueError('Id %r is invalid.' % (id,))
      self.type = ctype
      self.code = code
      self.id = id

   def __repr__(self):
      return '%s%r' % (self.__class__.__name__, (self.type, self.code, self.id))

   def __int__(self):
      return (int(self.type) + int(self.code)*256 + int(self.id)*65536)

class Nfct_Nat(Nfct_Comparable):
   __slots__ = slots_relevant = ('min_ip', 'max_ip', 'min_l4', 'max_l4')
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
      return '<NAT %s:%s %s:%s>' % (self.min_ip, self.min_l4, self.max_ip, self.max_l4)


class Nfct_Connection_Data(Nfct_Comparable):
   __slots__ = ('connection', 'nat', 'timeout', 'mark', 'status', 'use', 'id')
   slots_relevant = ('id','connection')
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
      return '<NFCT %s [%s %s %s %s %s]>' % (self.connection, self.id, self.timeout, self.mark, self.status, self.use)


class Nfct_Data(Nfct_Picklable):
   __slots__ = ('type', 'connection_data')
   def __init__(self, nfct_type, connection_data):
      self.type = nfct_type
      self.connection_data = connection_data

   def from_raw(cls, indata):
      nfct_tuple = indata[1]
      nfct_tuple2 = indata[2]
   
      assert nfct_tuple[2] == nfct_tuple2[2]
      assert nfct_tuple[3] == nfct_tuple2[3]
      nfct_nat = indata[11]
      l4proto = nfct_tuple[3]
      return cls(indata[0], Nfct_Connection_Data(
         Nfct_Connection(
            to_src=nfct_tuple[0],to_dst=nfct_tuple[1], back_src=nfct_tuple2[0],
            back_dst=nfct_tuple2[1], l3proto=nfct_tuple[2],l4proto=l4proto,
            to_l4src=L4_Address(l4proto, *nfct_tuple[4]),
            to_l4dst=L4_Address(l4proto, *nfct_tuple[5]),
            back_l4src=L4_Address(l4proto, *nfct_tuple2[4]),
            back_l4dst=L4_Address(l4proto, *nfct_tuple2[5]),protoinfo=indata[8],
            to_packets=indata[9][0], to_bytes=indata[9][1], back_packets=indata[10][0], back_bytes=indata[10][1]),
         Nfct_Nat(nfct_nat[0], nfct_nat[1], L4_Address(l4proto, *nfct_nat[2]), L4_Address(l4proto, *nfct_nat[3])),
         *indata[3:8]
      ))
   from_raw = classmethod(from_raw)

   def __repr__(self):
      return '%s(%s, %r)' % (self.__class__.__name__, self.type, self.connection_data)
   
   def __str__(self):
      return '%s(%s, %s)' % (self.__class__.__name__, self.type, self.connection_data)


class NfctHandle(NfctHandle_):
   def __init__(self, *args, **kwargs):
      """(re)open nfct handle and initialize instance; requires elevates privileges."""
      NfctHandle_.__init__(self, *args, **kwargs)
   
   def dump_conntrack_table(self, *args, **kwargs):
      return [Nfct_Data.from_raw(e) for e in NfctHandle_.dump_conntrack_table(self, *args, **kwargs)]
   
   def event_conntrack(self, *args, **kwargs):
      return [Nfct_Data.from_raw(e) for e in NfctHandle_.event_conntrack(self, *args, **kwargs)]


if (__name__ == '__main__'):
   # demonstration mode; works somewhat like conntrack -E
   import os, select
   nch = NfctHandle()
   # the following works starting with libnetfilter_conntrack svn revision 6664 or so,
   # the lib had a misfeature that prevented this before; comment out the setuid() part
   # in that case
   try:
      os.setuid(65534)
   except:
      # Hum, we didn't have that cap to begin with. No matter then.
      pass

   while (select.select([nch],[],[])):
      for nfct_data in nch.event_conntrack(): 
         print nfct_data.type, nfct_data.connection_data

