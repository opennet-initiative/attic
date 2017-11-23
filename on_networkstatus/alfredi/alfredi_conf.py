#!/usr/bin/env python

import os
import os.path
import sys
import urllib2
import cPickle
import logging
import inspect

import Image

from gonium.ip_address import ip_address_build
from alfredi_coordinate_acquiration_on001 import OnWikiNodeListParser
from alfredi_link_acquiration_on001 import links_from_csv, links_symmetrize
from coordinate_structures import PointByCoordinates
from alfredi_graphing import MapManipulator
#from alfredi_output_shapefile import ShapefileWriter
from alfredi_output_kml import KMLFileWriter
from alfredi_output_csv import CSVFileWriter
from alfredi_output_om1 import OM1FileWriter

_log_config = logging.getLogger('config')

def localdummy(): pass
os.chdir(os.path.split(inspect.getfile(localdummy))[0])
del(localdummy)

border_gateways = tuple([ip_address_build(x) for x in ('192.168.0.254', '192.168.0.244', '10.2.0.251', '10.2.0.247')])
hsv_map_constant = 240

graph_calls = (
   #(  'image004.gif', 
   #   (54.09463, 12.09373),
   #   (54.06865, 12.1296),
   #   (
   #      (('alfredi_output.png',), {}), 
   #      (('alfredi_output.jpg',), {})
   #   )
   #),
   (   'image008.png',
      (54.09465, 12.09432),
      (54.06960, 12.14260),
      (
         (('output/alfredi_output.png',), {}),
         (('output/alfredi_output.jpg',), {}),
      )
   ),
   (   'image006.jpg',
      (54.093235630379752, 12.104001046365916),
      (54.070965179746835, 12.125914110275689),
      (
         (('output/alfredi_output_6.jpg',), {}),
      )
   ),
   (   'image007.png',
      (54.1025061796, 12.0876606931),
      (54.0625653304, 12.1562126764),
      (
         (('output/alfredi_output_7.jpg',), {}),
      )
   ),
   (  'image005.gif',
      (54.09308, 12.10549),
      (54.08078, 12.12221),
      (
         (('output/alfredi_output_big.png',), {}),
      )
   )
   #(  'image_1414x1024_transparent.png',
   #   (54.093235630379752, 12.104001046365916),
   #   (54.070965179746835, 12.125914110275689),
   #   (
   #      (('alfredi_output_1414x1024_transparent.png',),{}),
   #   )
   #)
)

#output_unit_shp = (
#   ShapefileWriter(basefilename_nodes='alfredi_nodes', basefilename_links='alfredi_links'),
#   (
#      ((),{}),
#   )
#)

output_unit_kml = (
   KMLFileWriter(elementlimit=None, icon_url_base='http://titan.www.opennet-initiative.de/topology/olsr/map_icons/'),
   (
      (('output/alfredi_output.kml',),{}),
   )
)

output_unit_csv = (
   CSVFileWriter(),
   (
      (('output/alfredi_output.csv',),{}),
   )
)

output_unit_om1 = (
   OM1FileWriter('http://www.opennet-initiative.de/marker/%(name)s/%(color)s.png', '20,35'),
   (
      (('output/alfredi_output_om1n.tsv','output/alfredi_output_om1e.tsv'),{}),
   )
)

def output_units_generate():
   retval = [output_unit_kml, output_unit_csv, output_unit_om1] + [(MapManipulator(Image.open(source_filename).convert('RGBA'), PointByCoordinates(*coordpair1), PointByCoordinates(*coordpair2)), output_calls) for (source_filename, coordpair1, coordpair2, output_calls) in graph_calls]
   #retval.append(output_unit_shp)
   return retval

url_node_list = 'http://wiki.opennet-initiative.de/index.php/Opennet_Nodes'
olsr_topology_filename = 'olsr_topology.csv'
dump_filename = 'alfredi_node_coords.pickle'

color_mask = 'hsl(%(hue)d,100%%,50%%)'

_formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
_handler_stderr = logging.StreamHandler()
_handler_stderr.setLevel(25)
_handler_stderr.setFormatter(_formatter)
logging.getLogger().addHandler(_handler_stderr)

def node_coords_get():
   _log_config.log(25, 'Attempting to retrieve node list from %r.' % url_node_list)
   url_data = urllib2.urlopen(url_node_list).read()
   _log_config.log(25, 'Read %d bytes. Parsing...' % (len(url_data),))
   ownlp = OnWikiNodeListParser()
   ownlp.feed(url_data)
   ownlp.close()
   node_coords = ownlp.results
   _log_config.log(25, 'Attempting to dump node_coords to file %r.' % (dump_filename,))
   cPickle.dump(node_coords, file(dump_filename,'w'), -1)
   return node_coords

def links_symmetrized_get():
   _log_config.log(25, 'Attempting to read link data from %r and symmetrize.' % (olsr_topology_filename,))
   return links_symmetrize(links_from_csv(file(olsr_topology_filename)))

