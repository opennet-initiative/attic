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

from ImageColor import getrgb

class LQColorMap:
   def color_calculate(self, lq):
      if (lq is None):
         return (0,0,0)
      else:
         hue = round(self.hsv_map_constant*lq)
         return getrgb(self.color_mask % vars())
