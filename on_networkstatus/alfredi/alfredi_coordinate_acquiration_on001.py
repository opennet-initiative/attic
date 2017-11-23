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

import HTMLParser
import logging
import string
import urllib2

from coordinate_structures import PointByCoordinates
from gonium.ip_address import ip_address_build

_log = logging.getLogger('acaon')
# build a string containing all ascii-chars except base-ten digits
digits = [ord(c) for c in string.digits]
stripmask = ''.join([chr(i) for i in range(256) if not (i in digits)])
del(digits)

ip_base = int(ip_address_build('192.168.1.0'))

class OnWikiNodeListParser(HTMLParser.HTMLParser):
   row_start = False
   cell_caching = False
   cell_cache = ''
   row_key = ''
   results = {}
   
   def handle_starttag(self, tag, attributes):
      if (tag == 'tr'):
         self.row_start = True
         self.cell_caching = True
      
   def handle_endtag(self, tag):
      if ((tag == 'td') and (self.row_start)):
         self.row_start = False
         self.row_key = self.cell_cache
         self.sell_cache = ''
      if ((tag == 'tr') and (self.cell_caching)):
         _log.log(15, 'Processing data pair %r, %r.' % (self.row_key, self.cell_cache))
         try:
            station_number = int(self.row_key.strip(stripmask))
         except ValueError:
            _log.log(18, 'Unable to convert %r to a number. Discarding row.' % (self.row_key,))
         else:
            #really ugly hardcoding to mangle the coordinate-strings into something useful
            try:
               (latitude_string, longitude_string) = [substring.upper().replace(',','.') for substring in self.cell_cache.split()]
            except ValueError:
               _log.log(18, 'Unable to split %r in excatly two substrings by whitespace. Discarding row.' % (self.cell_cache,))
            else:
               longitude_factor = latitude_factor = 1

               if (latitude_string[0] == 'S'):
                  latitude_factor = -1
               if (longitude_string[0] == 'W'):
                  longitude_factor = -1
               try:
                  latitude_base = float(latitude_string[1:])
               except ValueError:
                  _log.log(19, 'Unable to convert latitude string %r to a coordinate. Discarding row.' % (latitude_string,))
               else:
                  try:
                     longitude_base = float(longitude_string[1:])
                  except ValueError:
                     _log.log(19, 'Unable to convert longitude string %r to a coordinate. Discarding row.' % (longitude_string,))
                  else:
                     latitude = latitude_base * latitude_factor
                     longitude = longitude_base * longitude_factor
                     try:
                        point = PointByCoordinates(latitude, longitude)
                     except:
                        _log.log(35, 'Failed to instantiate PointByCoordinates; called it as PointByCoordinates(%r, %r). Discarding row. Error was:' % (latitude, longitude), exc_info=True)
                     else:
                        #Nothing went horribly wrong, so we save this result.
                        node_ip = ip_address_build(station_number + ip_base)
                        _log.log(20, 'Adding new station: (%s, %s)' % (node_ip, point))
                        self.results[node_ip] = point
         self.cell_caching = False
         self.cell_cache = ''

   def handle_data(self, data):
      data = data.strip()
      if (self.cell_caching and data):
         self.cell_cache = data

