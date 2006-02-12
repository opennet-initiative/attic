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

import Image
import ImageDraw
import ImageColor

import coordinate_structures
import alfredi_color

class MapManipulator(alfredi_color.LQColorMap):
   def __init__(self, image, coord_zero, coord_one, color_mask='hsl(%(hue)d,100%%,50%%)', hsv_map_constant=240, off_maps_checks=False, crop=True):
      self.ctoc = coordinate_structures.CoordsToOffsetConverter(coord_zero, coord_one, image.size[0], image.size[1])
      self.image = image
      self.draw = ImageDraw.Draw(image)
      self.off_map_checks = False
      self.x_min = None
      self.x_max = None
      self.y_min = None
      self.y_max = None
      self.color_mask = color_mask
      self.hsv_map_constant = hsv_map_constant
      self.crop = crop

   def position_calculate(self, coords):
      return tuple([int(round(number)) for number in self.ctoc(coords, sanity=self.off_map_checks)])

   def node_draw(self, coords, lq, width=4, height=4, text=''):
      position = self.position_calculate(coords)
      point_zero = (position[0]-width, position[1]-height)
      point_one = (position[0]+width, position[1]+height)
      self.position_register(point_zero)
      self.position_register(point_one)
      #self.draw.line(point_zero + point_one, fill=fill)
      #self.draw.line((point_zero[0], point_one[1], point_one[0], point_zero[1]), fill=fill)
      self.draw.chord(point_zero + point_one, 0, 360, fill=self.color_calculate(lq))
      self.draw.text((point_zero[0]+2*width, point_zero[1]+height), text, fill=(0,0,0))

   def position_register(self, pos, check_borders=False):
      x,y = pos
      if ((self.x_min == None) or (x < self.x_min)):
         self.x_min = x
      if ((self.x_max == None) or (x > self.x_max)):
         self.x_max = x
      if ((self.y_min == None) or (y < self.y_min)):
         self.y_min = y
      if ((self.y_max == None) or (y > self.y_max)):
         self.y_max = y

   def map_crop(self, x_margin=5, y_margin=5):
      x1 = min(max(self.x_min-x_margin, 0), self.image.size[0])
      y1 = min(max(self.y_min-y_margin, 0), self.image.size[1])
      x2 = min(max(self.x_max+x_margin,0), self.image.size[0])
      y2 = min(max(self.y_max+y_margin,0), self.image.size[1])
      if ((x2 - x1 == 0) or (y2 - y1 == 0)):
         raise ValueError('Bounding sizes (%d,%d,%d,%d) would corrupt PIL image.' % (x1,y1,x2,y2))
      return self.image.copy().crop((max(self.x_min-x_margin, 0), max(self.y_min-y_margin, 0), min(self.x_max+x_margin, self.image.size[0]), min(self.y_max+y_margin, self.image.size[1])))

   def edge_draw(self, coords1, coords2, lq):
      pos1 = self.position_calculate(coords1)
      pos2 = self.position_calculate(coords2)
      self.position_register(pos1)
      self.position_register(pos2)
      self.draw.line((pos1, pos2), fill=self.color_calculate(lq))

   def save(self, *args, **kwargs):
      if (self.crop):
         self.map_crop()
      self.image.save(*args, **kwargs)

