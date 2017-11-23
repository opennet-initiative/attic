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

import alfredi_color

color_mask = 'hsl(%(hue)d,100%%,50%%)'
hsv_map_constant = 240

step = 1.0/hsv_map_constant

#execfile('alfredi_conf.py')


class LQColorMapLocal(alfredi_color.LQColorMap):
   def __init__(self):
      self.color_mask = color_mask
      self.hsv_map_constant = hsv_map_constant


lq_color_map = LQColorMapLocal().color_calculate

if (__name__ == '__main__'):
   print '%3d %3d %3d %s %s' % (0,0,0,'NULL','NULL')
   for i in range(0, 241):
      lq_min = (i - 0.5)*step
      lq_max = lq_min + step
      if (lq_min < 0):
         lq_min = 0
      if (lq_max > 1):
         lq_max = 1
      print '%3d %3d %3d %.15f %.15f' % (lq_color_map(lq_min) + (lq_min, lq_max))
      


