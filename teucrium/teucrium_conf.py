#!/usr/bin/env python

import sys
import time
import logging
import logging.handlers

from teucrium_main import COUNTER_BYTES, COUNTER_PACKETS

#logging stuff
settings = {
   'basic_io': {
      'handlers':(
         ([None], logging.handlers.RotatingFileHandler, (), {'filename':'log/all'}, (('setLevel', (20,)),)),
         ([None], logging.StreamHandler, (), {}, (('setLevel', (20,)),))
         )
      },
  }

DIRECTION_INPUT = 1
DIRECTION_OUTPUT = 2

base_separator='_'

target_uid = 2037
target_gid = target_uid

#filename of filename_rrd: rrd to use; teucrium will not create it, 
#a suitable rrd with this name must already exist for it to work
filename_rrd = 't_traffic_001.rrd'
filename_graphics_base = 't_traffic_001_'
chroot_target = '/home/FIXME/teucrium/chroot'

#counters_to_track specifies which netfilter rules/chains to read the
#counters of and where to put the results
#It should be a sequence of an arbitrary number of sequences of the 
#following scheme: (), {} 
#See teucrium_main.iptgrapher.target_add for the relevant function.
counters_to_track = []

conf_table = 'mangle'
conf_interfaces = ('tun+', 'eth0', 'eth1', 'eth2', 'ppp+')
conf_service_dict = {
   'tcp_http':('#ff00ff', 'tcp-http', ''),
   'tcp_https':('#ff0080', 'tcp-https', ''),
   'tcp_bt_up':('#0000a0', 'tcp-bt-up', ''),
   'tcp_bt_down':('#0000ff', 'tcp-bt-down', ''),
   'tcp_other':('#ff0000', 'tcp-other', ''),
   
   'udp_dns':('#00b0b0', 'udp-dns', ''),
   'udp_vpn':('#006060', 'udp-vpn', ''),
   'udp_other':('#00ffff', 'udp-other', ''),
   
   'icmp':('#04c000', 'icmp', ''),
   
   'ip_other':('#808080', 'ip-other', ''),
   }

services_graph = (
   'ip_other',
   'icmp',
   'udp_other', 'udp_dns', 'udp_vpn',
   'tcp_https', 'tcp_http', 'tcp_other', 'tcp_bt_up', 'tcp_bt_down'
   )
   
graph_args = ()
graph_kwargs = {
   'width':600,
   'height':200,
   'options':[]
   }
      
conf_service_list = (
   'tcp_http', 'tcp_https', 'tcp_bt_up', 'tcp_bt_down', 'tcp_other',
   'udp_dns', 'udp_vpn', 'udp_other',
   'icmp',
   'ip_other'
   )

ds_mask_in = '%s_i_%s'
ds_mask_out = '%s_o_%s'


def ds_name_filter(devicename, servicename, direction):
   if (direction == DIRECTION_INPUT):
      ds_mask = ds_mask_in
   elif (direction == DIRECTION_OUTPUT):
      ds_mask = ds_mask_out
   else:
      raise ValueError("Value %r is invalid for argument 'direction'." % (direction,))
   
   devicename = devicename.replace('+','_')

   return ds_mask % (devicename, servicename)

ds_min = 0
ds_max = 12500000
rrd_step = 10
rrd_start = int(time.time())
rrd_heartbeat = 10
rrd_rras = (
   ('AVERAGE', 0, 1, 380),
   ('AVERAGE', 0.4, 6, 1600),
   ('AVERAGE', 0.4, 60, 5500),
   ('AVERAGE', 0.1, 360, 10000),
)

rrd_graph_periods = {
   -3600:'1h',
   -86400:'1d',
   -2592000:'30d',
   -31557600:'365d',
}

html_out_file = file('tecurium_legend.html', 'w')
html_header = '''<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>Test graphics</title>
  </head>
  <body>'''
html_footer = '''
  </body>
</html>'''
html_legend_sample_edge_length = 10

for devicename in conf_interfaces:
   for i in range(len(conf_service_list)):
      counters_to_track.append(((ds_name_filter(devicename, conf_service_list[i], DIRECTION_INPUT), conf_table, 'tc_in_%s' % (devicename,),  i), {}))
      counters_to_track.append(((ds_name_filter(devicename, conf_service_list[i], DIRECTION_OUTPUT), conf_table, 'tc_out_%s' % (devicename,), i), {}))
   
