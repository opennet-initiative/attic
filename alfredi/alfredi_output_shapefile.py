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

import shapelib
from shapelib import SHPObject, SHPT_POINT, SHPT_ARC
import dbflib

from alfredi_color import LQColorMap

class ShapefileWriter(LQColorMap):
   def __init__(self, basefilename_nodes, basefilename_links, color_mask='hsl(%(hue)d,100%%,50%%)', hsv_map_constant=240):
      self.outfile_nodes_shp = shapelib.create(basefilename_nodes, SHPT_POINT)
      self.outfile_nodes_dbf = dbflib.create(basefilename_nodes)
      self.outid_nodes_lq = self.outfile_nodes_dbf.add_field('LQ', dbflib.FTDouble, 10, 8)
      self.color_mask = color_mask
      self.hsv_map_constant = hsv_map_constant
      assert self.outid_nodes_lq >= 0
      self.outid_nodes_text = self.outfile_nodes_dbf.add_field('Text', dbflib.FTString, 15, 0)
      assert self.outid_nodes_text >= 0
      self.outid_nodes_color = self.outfile_nodes_dbf.add_field('color', dbflib.FTString, 7, 0)
      assert self.outid_nodes_color >= 0
      self.outfile_links_shp = shapelib.create(basefilename_links, SHPT_ARC)
      self.outfile_links_dbf = dbflib.create(basefilename_links)
      self.outid_links_lq = self.outfile_links_dbf.add_field('LQ', dbflib.FTDouble, 10, 8)
      assert self.outid_links_lq >= 0
      self.outid_links_color = self.outfile_links_dbf.add_field('color', dbflib.FTString, 7, 0)
      assert self.outid_links_color >= 0

   def color_calculate(self, *args, **kwargs):
      color = LQColorMap.color_calculate(self, *args, **kwargs)
      for element in color:
         if not (0 <= element <= 255):
            raise StandardError('Got invalid color %r from LQColorMap.color_calculate on calling it with %r %r.' % (color, args, kwargs))
      return '#%.2X%.2X%.2x' % color

   def node_draw(self, coord_node, lq, text):
      object_id = self.outfile_nodes_shp.write_object(-1, SHPObject(SHPT_POINT, -1, (((coord_node.longitude, coord_node.latitude),),)))
      self.outfile_nodes_dbf.write_record(object_id, {'LQ':lq, 'color': self.color_calculate(lq), 'Text':text})

   def edge_draw(self, coord_node1, coord_node2, lq):
      object_id = self.outfile_links_shp.write_object(-1, SHPObject(SHPT_ARC, -1, (((coord_node1.longitude, coord_node1.latitude), (coord_node2.longitude, coord_node2.latitude)),)))
      self.outfile_links_dbf.write_record(object_id, {'LQ':lq, 'color':self.color_calculate(lq)})

   def save(self):
      self.outfile_nodes_shp.close()
      self.outfile_nodes_dbf.close()
      self.outfile_links_shp.close()
      self.outfile_links_dbf.close()

