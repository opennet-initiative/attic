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
import pprint

import Image

import address_structures
from coordinate_structures import PointByCoordinates
from alfredi_graphing import MapManipulator
from alfredi_coordinate_acquiration_on001 import OnWikiNodeListParser
from alfredi_link_acquiration_on001 import links_from_csv

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
handler_stderr = logging.StreamHandler()
handler_stderr.setLevel(logging.DEBUG)
handler_stderr.setFormatter(formatter)
logger.addHandler(handler_stderr)

execfile('alfredi_conf.py')

mm = MapManipulator(Image.open(background_data[0]), PointByCoordinates(*background_data[1]), PointByCoordinates(*background_data[2]))

#data = {
#   'AP14':(54.08667, 12.11065),
#   'CSR':(54.08899, 12.11065),
#   'INR':(54.09100, 12.11501),
#   'IFNM':(54.0883, 12.12353),
#   '__RED':(54.0869, 12.1099),
#   '__BLUE':(54.0914, 12.1139),
#   '__GREEN':(54.0905, 12.1051),
#   '__YELLOW':(54.0874, 12.1153),
#}

ownlp = OnWikiNodeListParser()
ownlp.feed(urllib2.urlopen('http://wiki.opennet-initiative.de/index.php/Opennet_Nodes').read())
ownlp.close()
node_coords = ownlp.results
link_data = links_from_csv(file('olsr_topology.csv'))

#don't use for here since the internal index-counter would be confused by deletions in the dict during iteration
while (len(link_data) > 0):
   ((src_node, dst_node), lq) = link_data.popitem()
   key = (dst_node, src_node)
   #c = True
   #for ip_string in ('192.168.1.16', '192.168.1.14', '192.168.2.16', '192.168.2.14'):
   #   if (address_structures.ip_make(ip_string) in (dst_node, src_node)):
   #      break
   #else:
   #   c = False
   #if (c): continue
   if (key in link_data):
      lq_inverse = link_data[key]
      del(link_data[key])
      if ((src_node in node_coords) and (dst_node in node_coords)):
         hue = round(240*lq*lq_inverse)
         try:
            mm.edge_draw(node_coords[src_node], node_coords[dst_node], kwargs={'fill':'hsl(%d,100%%,50%%)' % hue})
         except ValueError:
            logger.log(30, 'Failed to add edge from node %r(%r) to node %r(%r). Error:' % (src_node, node_coords[src_node], dst_node, node_coords[dst_node]), exc_info=True)
   
for node_id in node_coords.keys():
   try:
      mm.node_draw(node_coords[node_id], text=str(node_id.__tuple__()[-1]))
   except ValueError:
      logger.log(30, 'Failed to add node %r at %r. Error:' % (node_id, node_coords[node_id]), exc_info=True)

      
mm.save('test01out.png')

