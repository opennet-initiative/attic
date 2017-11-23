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

import logging
import logging.handlers
import urllib2
from sets import Set as set
from sets import ImmutableSet as frozenset
import pprint

import Image

import pid_filing

_log = logging.getLogger()
_log.setLevel(logging.DEBUG)

from alfredi_conf import *

pid_filing.file_pid()

node_coords = node_coords_get()
output_units = output_units_generate()
link_data = links_symmetrized_get()

node_border_lq = {}
#Draw link-lines, and prepare list of nodes participating in known links
_log.log(25, 'Graphing connections.')
for ((node_1, node_2), lq_total) in link_data.items():
   if ((node_1 in node_coords) and (node_2 in node_coords)):
      for (output_unit, output_calls) in output_units:
         try:
            output_unit.edge_draw(node_coords[node_1], node_coords[node_2], lq_total, node1_ip=node_1, node2_ip=node_2)
         except ValueError:
            _log.log(30, 'Failed to add edge between nodes %r(%r) and %r(%r). Error:' % (node_1, node_coords[node_1], node_2, node_coords[node_2]), exc_info=True)

   for node in (node_1, node_2):
      if not (node in node_border_lq):
         node_border_lq[node] = 0

_log.log(25, 'Calculating node-to-edge LQs.')
#Applied graph theory: Find the best route from each node to the nearest gateway, and record how good it is
for border_gateway in border_gateways:
   node_border_lq[border_gateway] = 1

pending_targets = list(border_gateways)
while (pending_targets):
   pending_target = pending_targets.pop()
   for (link, lq) in link_data.items():
      if not (pending_target in link):
         continue
      border_lq = node_border_lq[pending_target]*lq
      link = set(link)
      link.remove(pending_target)
      new_target = link.pop()
      assert (len(link) == 0)
      if (border_lq > node_border_lq[new_target]):
         node_border_lq[new_target] = border_lq
         pending_targets.append(new_target)

for (node_ip, lq) in node_border_lq.items():
   _log.log(20, 'Total node-to-edge LQs computed for node %s are: %s' % (node_ip, lq))

_log.log(25, 'Graphing nodes.')
#draw the nodes
for node_id in node_coords.keys():
   if (node_id in node_border_lq):
      lq = node_border_lq[node_id]
   else:
      lq = None
   for (output_unit, output_calls) in output_units:
      try:
         output_unit.node_draw(node_coords[node_id], text=str(int(node_id) % 256), lq=lq, node_ip=node_id)
      except ValueError:
         _log.log(30, 'Failed to add node %r at %r. Error:' % (node_id, node_coords[node_id]), exc_info=True)


for (output_unit, output_calls) in output_units:
   for args, kwargs in output_calls:
      _log.log(25, 'Calling save: %r %r' % (args, kwargs))
      output_unit.save(*args, **kwargs)

_log.log(25, 'All done.')

