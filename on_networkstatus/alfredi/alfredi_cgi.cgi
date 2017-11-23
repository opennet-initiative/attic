#!/usr/bin/env python
#Copyright 2005,2006 Sebastian Hagen
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

import os
import sys
import cgi
import cgitb; cgitb.enable()
import cPickle

import Image

alfredi_dir = '/home/olsr_services/alfredi'
default_padding = 100

sys.path.append(alfredi_dir)
os.chdir(alfredi_dir)

from alfredi_conf import *
from address_structures import ip_make
from coordinate_structures import PointByCoordinates
from alfredi_graphing import MapManipulator

os.chdir(alfredi_dir)

def crash(errortext):
   sys.stdout.write('Content-Type: text/plain\n\n%s' % errortext)
   sys.exit()
   
try:
   node_coords = cPickle.load(file(dump_filename))
except:
   crash('Unable to unpickle node_coords from %r.' % dump_filename)
   

form = cgi.FieldStorage()

node_ip_string = form.getfirst('node_ip')
if (node_ip_string):
   try:
      node_ip = ip_make(node_ip_string)
   except:
      crash('%r is not a valid ip string.' % node_ip_string)
else:
   ap_no = form.getfirst('ap_no')
   if not (ap_no):
      crash('No node_ip or ap_no has been specified.')
   try:
      node_ip = ip_make(int(ip_make('192.168.1.0')) + int(ap_no))
   except:
      crash('%r is not a valid ap number.' % ap_no)

try:
   padding = int(form.getfirst('padding'))
except:
   padding = default_padding

background_data = graph_calls[0]
mm = MapManipulator(Image.open(background_data[0]).convert(), PointByCoordinates(*background_data[1]), PointByCoordinates(*background_data[2]))
mm.node_draw(node_coords[node_ip], text=str(node_ip), lq=None)

try:
   output_image = mm.map_crop(padding, padding)
except ValueError:
   print 'Content-Type: image/png\n'
   mm.image.crop((0,0,1,1)).save(sys.stdout, 'PNG')
else:
   print 'Content-Type: image/png\n'
   output_image.save(sys.stdout, 'PNG')

