#!/usr/bin/env python
#Copyright 2006 Sebastian Hagen
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

class CSVFileWriter(LQColorMap):
   def __init__(self, color_mask='hsl(%(hue)d,100%%,50%%)', hsv_map_constant=240):
      self.color_mask = color_mask
      self.hsv_map_constant = 240
      self.outdata = []
   
   def color_calculate(self, *args, **kwargs):
      color = LQColorMap.color_calculate(self, *args, **kwargs)
      for element in color:
         if not (0 <= element <= 255):
            raise StandardError('Got invalid color %r from LQColorMap.color_calculate on calling it with %r %r.' % (color, args, kwargs))
      return '#%.2X%.2X%.2x' % color

   def node_draw(self, coord, lq, text, node_ip):
      if (lq is None):
         o_lq = -1
      else:
         o_lq = lq

      self.outdata.append('V,%f,%f,%s, %f,%s,%s' % (coord.latitude, coord.longitude, node_ip, o_lq, self.color_calculate(lq), text))
   
   def edge_draw(self, coord1, coord2, lq, node1_ip, node2_ip):
      self.outdata.append('E,%f,%f,%f,%f,%s,%s,%f,%s' % (coord1.latitude, coord1.longitude, coord2.latitude, coord2.longitude, node1_ip, node2_ip, lq, self.color_calculate(lq)))

   def save(self, filename):
      outfile = file(filename, 'w')
      outfile.write('\n'.join(self.outdata))
      outfile.close()
