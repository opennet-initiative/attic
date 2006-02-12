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

import sys
import logging
import cPickle
from sets import Set

import pydot

import pid_filing; pid_filing.file_pid()
from socket_management import select_loop
from ketupo_input import olsrd_client_query
from address_structures import ip_make
from node_structures import olsr_node
import ketupo_dotdraw

target_address = ('127.0.0.1', 2006)

node_titan = olsr_node(ip_make('192.168.0.254'))

for ap_no in (6,8,14,15,16,18,53,54):
   ketupo_dotdraw.__dict__['node_ap%d' % ap_no] = olsr_node(ip_make('192.168.1.%d' % ap_no))

dump_filename = 'olsr_topology.csv'

wire_data = tuple(
   [Set(data_tuple) for data_tuple in 
      (
         (node_titan, node_ap6),
         (node_titan, node_ap14),
         (node_titan, node_ap15),
         (node_titan, node_ap16),
         (node_ap6, node_ap14),
         (node_ap6, node_ap15),
         (node_ap6, node_ap16),
         (node_ap14, node_ap15),
         (node_ap14, node_ap16),
         (node_ap15, node_ap16),
         (node_ap53, node_ap54),
         (node_ap8, node_ap18),
      )
   ]
)

def is_anything(uplink, connection):
   return True

def is_wired(uplink, connection):
   if (Set((uplink, connection.peer())) in wire_data):
      return True
   return False

def is_not_wired(uplink, connection):
   return (not is_wired(uplink, connection))

output_data = (
   ('on_olsr_topology_all.dot', 'on_olsr_topology_all.png', is_anything),
   ('on_olsr_topology_wire.dot', 'on_olsr_topology_wire.png', is_wired),
   ('on_olsr_topology_wireless.dot', 'on_olsr_topology_wireless.png', is_not_wired),
)


def color_connection(olsr_connection):
   return "%f,%f,%f" % (olsr_connection.local_lq*0.66666666667, 1, 0.8)

def input_handler(olsr_data):
   if (olsr_data != None):
      for (outfile_dot, outfile_png, filter_function) in output_data:
         dot = pydot.Dot()
         for olsr_node in olsr_data:
            dot.add_node(pydot.Node(name=olsr_node.address))
            for olsr_connection in olsr_node.connections:
               if (filter_function(olsr_node, olsr_connection)):
                  edge_color = color_connection(olsr_connection)
                  dot.add_edge(pydot.Edge(src=olsr_connection.peer().address, dst=olsr_node.address, label='LQ: %.2f' % (olsr_connection.local_lq,), color=edge_color, fontcolor=edge_color, weight=olsr_connection.local_lq*100))
         
         dot.write_raw(outfile_dot)
         dot.write_png(outfile_png)
         
      if (dump_filename):
         dump_file = file(dump_filename, 'w')
         
      for olsr_node in olsr_data:
         for olsr_connection in olsr_node.connections:
            dump_file.write('%s,%s,%f\n' % (olsr_connection.peer().address, olsr_node.address, olsr_connection.local_lq))
            
      dump_file.close()
      sys.exit(0)
   else:
      sys.exit(1)
   
   
rootlogger = logging.getLogger()
rootlogger.setLevel(30)
rootlogger.addHandler(logging.StreamHandler())

olsrd_client_query(target_address, input_handler, '')

select_loop()


