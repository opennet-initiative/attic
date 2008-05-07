#!/usr/bin/env python
#Copyright 2008 Sebastian Hagen
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

from alfredi_color import LQColorMap

class OM1FileWriter(LQColorMap):
   fieldsep = '\t'
   linesep = '\n'
   nf_header = fieldsep.join(('lat','lon','title','desc','icon','iconsize'))
   ef_header = fieldsep.join(('lat1','lon1','lat2','lon2','ip1','ip2','lq','color'))
   iconsize = 1
   
   def __init__(self, node_icon_urlmask, color_mask='hsl(%(hue)d,100%%,50%%)', hsv_map_constant=240):
      self.color_mask = color_mask
      self.hsv_map_constant = hsv_map_constant
      # syntax test
      node_icon_urlmask % {'name':'','color':''}
      self.node_icon_urlmask = node_icon_urlmask
      self.od_nodes = [self.nf_header]
      self.od_edges = [self.ef_header]
   
   def color_calculate(self, *args, **kwargs):
      color = LQColorMap.color_calculate(self, *args, **kwargs)
      for element in color:
         if not (0 <= element <= 255):
            raise StandardError('Got invalid color %r from LQColorMap.color_calculate on calling it with %r %r.' % (color, args, kwargs))
      return '%02X%02X%02X' % color

   def node_icon_url_get(self, name, lq):
      return (self.node_icon_urlmask % {'name':name, 'color': self.color_calculate(lq)})

   def node_draw(self, coord, lq, text, node_ip):
      if (lq is None):
         o_lq = 'NULL'
      else:
         o_lq = lq

      self.od_nodes.append(self.fieldsep.join([str(e) for e in (coord.latitude, coord.longitude, node_ip, o_lq, self.node_icon_url_get(text,lq), self.iconsize)]))
   
   def edge_draw(self, coord1, coord2, lq, node1_ip, node2_ip):
      self.od_edges.append(self.fieldsep.join([str(e) for e in (coord1.latitude, coord1.longitude, coord2.latitude, coord2.longitude, node1_ip, node2_ip, lq, self.color_calculate(lq))]))

   def save(self, nff, eff):
      no = file(nff, 'w')
      no.write(self.linesep.join(self.od_nodes))
      no.close()
      eo = file(eff, 'w')
      eo.write(self.linesep.join(self.od_edges))
      eo.close()
