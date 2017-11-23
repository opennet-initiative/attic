#!/usr/bin/env python
#Copyright 2005 Sebastian Hagen
# This file is part of alfredi.

# alfredi is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 
# as published by the Free Software Foundation

# alfredi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with alfredi; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from sets import ImmutableSet as frozenset
import logging

from gonium.ip_address import ip_address_build

_log = logging.getLogger('link_acquiration')

def links_from_csv(infile):
   results = {}
   for line in infile:
      try:
         (src_node_string, dst_node_string, lq_string) = line.split(',')
         (src_node, dst_node) = [ip_address_build(string) for string in (src_node_string, dst_node_string)]
         lq_float = float(lq_string)
      except ValueError:
         _log.log(35, 'Unable to process line %r. Discarding it. Error:' % (line,), exc_info=True)
         continue
      
      results[(src_node, dst_node)] = lq_float

   return results

def links_symmetrize(input_dict):
   results = {}
   while (len(input_dict) > 0):
      ((src_node, dst_node), lq) = input_dict.popitem()
      key = (dst_node, src_node)
      
      if (key in input_dict):
         lq_inverse = input_dict[key]
         del(input_dict[key])
         results[frozenset((src_node, dst_node))] = lq*lq_inverse
   
   return results