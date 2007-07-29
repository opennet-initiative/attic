#!/usr/bin/env python
#Copyright 2006, 2007 Sebastian Hagen
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

import xml.sax.saxutils

from alfredi_color import LQColorMap

class KMLPlacemark:
   def __init__(self, name, description, lq, colorstring, tags=[]):
      self.name = name
      self.description = description
      self.lq = lq
      self.colorstring = colorstring
      self.tags = tags

   def tag_make(self, name, content, linebreaks=True, arguments=''):
      if (linebreaks):
         sep = '\n'
      else:
         sep = ''
      return sep.join(('<%s%s>' % (name, arguments), xml.sax.saxutils.escape(content),'</%s>' % name, ''))
      
   def tags_get(self, color_set):
      color_set.add(self.colorstring)
      return [self.tag_make(x, self.__dict__[x]) for x in ('name', 'description')] + self.tags
      
   def markup_generate(self, color_set):
      return '<Placemark>\n' + ''.join(self.tags_get(color_set)) + '</Placemark>\n'


class KMLPlacemarkNode(KMLPlacemark):
   def __init__(self, coord, *args, **kwargs):
      KMLPlacemark.__init__(self, *args, **kwargs)
      self.coord = coord
   
   def tags_get(self, color_set):
      return KMLPlacemark.tags_get(self, color_set) + \
         [self.tag_make('styleUrl', '#col%s' % (self.colorstring,), False) + '\n'] + \
         ['<Point>%s</Point>\n' % self.tag_make('coordinates', '%f,%f,0' % (
            self.coord.longitude, self.coord.latitude))]


class KMLPlacemarkEdge(KMLPlacemark):
   def __init__(self, coord1, coord2, *args, **kwargs):
      KMLPlacemark.__init__(self, *args, **kwargs)
      self.coord1 = coord1
      self.coord2 = coord2
      
   def tags_get(self, color_set):
      return KMLPlacemark.tags_get(self, color_set) + \
         [self.tag_make('styleUrl', '#col%s' % (self.colorstring,), False) + '\n'] + \
         ['<LineString>\n%s</LineString>\n' % 
         self.tag_make('coordinates', '%f,%f,0\n%f,%f,0' % (
            self.coord1.longitude, self.coord1.latitude, self.coord2.longitude,
            self.coord2.latitude))]
         


class KMLFileWriter(LQColorMap):
   def __init__(self, color_mask='hsl(%(hue)d,100%%,50%%)', hsv_map_constant=240, elementlimit=None):
      self.color_mask = color_mask
      self.hsv_map_constant = 240
      self.nodetags = []
      self.edgetags = []
      self.elementlimit = elementlimit
      self.elementcount = 0

   def color_calculate(self, *args, **kwargs):
      color = LQColorMap.color_calculate(self, *args, **kwargs)
      for element in color:
         if not (0 <= element <= 255):
            raise StandardError('Got invalid color %r from LQColorMap.color_calculate on calling it with %r %r.' % (color, args, kwargs))
      return 'ff%02x%02x%02x' % (color[2], color[1], color[0])

   def element_new(self):
      if ((not self.elementlimit) or (self.elementcount < self.elementlimit)):  
         self.elementcount += 1
         return True
      else:
         return False

   def node_draw(self, coord, lq, text, node_ip):
      if (self.element_new()):
         self.nodetags.append(KMLPlacemarkNode(coord=coord, lq=lq, colorstring=self.color_calculate(lq), name=text, description=str(node_ip)))

   def edge_draw(self, coord1, coord2, lq, node1_ip, node2_ip):
      if (self.element_new()):
         self.edgetags.append(KMLPlacemarkEdge(coord1=coord1, coord2=coord2, lq=lq, colorstring=self.color_calculate(lq), name="%s %s" % (node1_ip, node2_ip), description=str(lq))) 

   def markup_generate(self):
      color_set = set()
      ne_tags = [x.markup_generate(color_set) for x in (self.nodetags + self.edgetags)]
      color_style_tags = ['<Style id="col%s"><LabelStyle><color>%s</color></LabelStyle></Style>\n' % (cs, cs) for cs in color_set]
      return '<?xml version="1.0" encoding="UTF-8"?>\n<kml xmlns="http://earth.google.com/kml/2.1">\n<Document>\n' + \
             ''.join(color_style_tags) + ''.join(ne_tags) + '</Document>\n</kml>\n'

   def save(self, filename):
      file(filename, 'w').write(self.markup_generate())

