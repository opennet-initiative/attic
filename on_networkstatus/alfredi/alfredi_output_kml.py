#!/usr/bin/env python
#Copyright 2006, 2007, 2008 Sebastian Hagen
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

from ImageColor import getrgb


class KMLLQ:
   """Color computing LQ class"""
   def __init__(self, lq, hsv_map_constant=240, color_mask='hsl(%(hue)d,100%%,50%%)'):
      if not ((0 <= lq <= 1) or (lq is None)):
         raise ValueError('LQ value %r is invalid' % (lq,))
      
      self.lq = lq
      self.hsv_map_constant = hsv_map_constant
      self.color_mask = color_mask

   def hue_get(self):
      """Return color hue for this lq"""
      if (self.lq is None):
         return None
      else:
         return round(self.hsv_map_constant*self.lq)

   @classmethod
   def build_from_similar(cls, other):
      return cls(other.lq, other.hsv_map_constant, other.color_mask)

   def color_calculate(self):
      if (self.lq is None):
         return (0,0,0)
      else:
         return getrgb(self.color_mask % {'hue':self.hue_get()})

   def colorstring_get(self):
      """Return #XXXXXX RGB html-format colorstring for our color"""
      color_tuple = self.color_calculate()
      return 'ff%02x%02x%02x' % (color_tuple[2], color_tuple[1], color_tuple[0])

   def __int__(self):
      return int(self.lq)
   
   def __long__(self):
      return long(self.lq)
   
   def __float__(self):
      return float(self.lq)


class ColorEqKMLLQ(KMLLQ):
   def __eq__(self, other):
      if not (isinstance(other, KMLLQ)):
         return False
      
      return (self.hue_get() == other.hue_get())
   
   def __neq__(self, other):
      return not (self == other)
   
   def __hash__(self):
      return hash(self.hue_get())


class KMLPlacemark:
   def __init__(self, name, description, lq, tags=[]):
      self.name = name
      self.description = description
      self.lq = lq
      self.tags = tags

   def tag_make(self, name, content, linebreaks=True, arguments=''):
      if (linebreaks):
         sep = '\n'
      else:
         sep = ''
      return sep.join(('<%s%s>' % (name, arguments), xml.sax.saxutils.escape(content),'</%s>' % name, ''))
      
   def tags_get(self, color_set):
      color_set.add(ColorEqKMLLQ.build_from_similar(self.lq))
      return [self.tag_make(x, self.__dict__[x]) for x in ('name', 'description')] + self.tags
      
   def markup_generate(self, color_set):
      return '<Placemark>\n' + ''.join(self.tags_get(color_set)) + '</Placemark>\n'


class KMLPlacemarkNode(KMLPlacemark):
   def __init__(self, coord, *args, **kwargs):
      KMLPlacemark.__init__(self, *args, **kwargs)
      self.coord = coord
   
   def tags_get(self, color_set):
      return KMLPlacemark.tags_get(self, color_set) + \
         [self.tag_make('styleUrl', '#col%s' % (self.lq.colorstring_get(),), False) + '\n'] + \
         ['<Point>%s</Point>\n' % self.tag_make('coordinates', '%f,%f,0' % (
            self.coord.longitude, self.coord.latitude))]


class KMLPlacemarkEdge(KMLPlacemark):
   def __init__(self, coord1, coord2, *args, **kwargs):
      KMLPlacemark.__init__(self, *args, **kwargs)
      self.coord1 = coord1
      self.coord2 = coord2
      
   def tags_get(self, color_set):
      return KMLPlacemark.tags_get(self, color_set) + \
         [self.tag_make('styleUrl', '#col%s' % (self.lq.colorstring_get(),), False) + '\n'] + \
         ['<LineString>\n%s</LineString>\n' % 
         self.tag_make('coordinates', '%f,%f,0\n%f,%f,0' % (
            self.coord1.longitude, self.coord1.latitude, self.coord2.longitude,
            self.coord2.latitude))]
         


class KMLFileWriter:
   def __init__(self, color_mask='hsl(%(hue)d,100%%,50%%)', hsv_map_constant=240, elementlimit=None, icon_url_base=None):
      self.color_mask = color_mask
      self.hsv_map_constant = 240
      self.nodetags = []
      self.edgetags = []
      self.elementlimit = elementlimit
      self.elementcount = 0
      self.icon_url_base = icon_url_base

   def color_calculate(self, *args, **kwargs):
      """Return color tuple"""
      color = LQColorMap.color_calculate(self, *args, **kwargs)
      for element in color:
         if not (0 <= element <= 255):
            raise StandardError('Got invalid color %r from LQColorMap.color_calculate on calling it with %r %r.' % (color, args, kwargs))

   def element_new(self):
      if ((not self.elementlimit) or (self.elementcount < self.elementlimit)):  
         self.elementcount += 1
         return True
      else:
         return False

   def node_draw(self, coord, lq, text, node_ip):
      clq = KMLLQ(lq, self.hsv_map_constant, self.color_mask)
      
      if (self.element_new()):
         self.nodetags.append(KMLPlacemarkNode(coord=coord, lq=clq, name=text, description='IP: %s\nLQ: %s' % (node_ip, lq)))

   def edge_draw(self, coord1, coord2, lq, node1_ip, node2_ip):
      clq = KMLLQ(lq, self.hsv_map_constant, self.color_mask)
      
      if (self.element_new()):
         self.edgetags.append(KMLPlacemarkEdge(coord1=coord1, coord2=coord2, lq=clq, name="%s %s" % (node1_ip, node2_ip), description=str(lq))) 

   def markup_generate(self):
      color_set = set()
      ne_tags = ['<Folder id="nodes"><name>nodes</name>'] + [e.markup_generate(color_set) for e in self.nodetags] + ['</Folder>',
      '<Folder id="edges"><name>edges</name>'] + [e.markup_generate(color_set) for e in self.edgetags] + ['</Folder>']
      
      color_style_tags = []
      for clq in color_set:
         if (self.icon_url_base is None):
            icon_style = ''
         else:
            hue = clq.hue_get()
            if (hue is None):
               huestring = 'undef'
            else:
               huestring = '%.3d' % (hue,)
            icon_style = '<IconStyle><Icon><href>%s%s.png</href></Icon></IconStyle>' % (self.icon_url_base, huestring)
         
         cs = clq.colorstring_get()
         color_style_tags.append('<Style id="col%s">%s<LineStyle><color>%s</color><width>0.25</width></LineStyle></Style>\n' % (cs, icon_style, cs))
      
      return '<?xml version="1.0" encoding="UTF-8"?>\n<kml xmlns="http://earth.google.com/kml/2.1">\n<Document>\n' + \
             ''.join(color_style_tags) + ''.join(ne_tags) + '</Document>\n</kml>\n'

   def save(self, filename):
      file(filename, 'w').write(self.markup_generate())

