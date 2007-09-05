#!/usr/bin/env python
#Copyright 2007 Sebastian Hagen
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

import os.path

# PIL
import Image
from ImageColor import getrgb
from ImageDraw import Draw


def image_build(color):
   img = Image.new('RGBA',(32,32),(0,0,0,1))
   d = Draw(img)
   d.ellipse((0,0,31,32), fill=color)
   return img


def main(color_mask='hsl(%(hue)d,100%%,50%%)', hsv_map_constant=240, basepath='alfredi_icons'):
   for i in range(hsv_map_constant + 1):
      colorstring = color_mask % {'hue': i}
      image_build(colorstring).save(os.path.join(basepath, '%.3d.png' % (i,)))
   
   image_build('#000000').save(os.path.join(basepath, 'undef.png'))
   

if (__name__ == '__main__'):
   main()
