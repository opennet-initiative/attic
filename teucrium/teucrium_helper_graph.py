#!/usr/bin/env python
#Copyright 2005 Sebastian Hagen
# This file is part of teucrium.

# teucrium is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 
# as published by the Free Software Foundation

# teucrium is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with teucrium; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os.path

import rrdtool

from teucrium_conf import chroot_target, filename_rrd, filename_graphics_base, conf_service_dict, \
                          conf_interfaces, ds_name_filter, rrd_graph_periods, base_separator, graph_args, \
                          graph_kwargs, services_graph, DIRECTION_INPUT, DIRECTION_OUTPUT, html_out_file, \
                          html_header, html_footer, html_legend_sample_edge_length, html_header, html_footer

rrd_filename = os.path.join(chroot_target, filename_rrd)

def html_pack_table(text):
   return '<table class="teucrium_table_table">\n%s</table>\n' % (text,)

def html_pack_tr(text):
   return '<tr class="teucrium_table_tr">\n%s</tr>\n' % (text,)

def html_pack_td(text):
   return '<td class="teucrium_table_td">\n%s\n</td>\n' % (text,)

def html_colordiv(color):
   if (color):
      colorstr = 'background-color:%s; ' % (color,)
   else:
      colorstr = ''
   return '<div class="teucrium_table_colordiv" style="%s width:%dpx; height:%dpx" />' % (colorstr, html_legend_sample_edge_length, html_legend_sample_edge_length)


def ipt_graph(interface, start_time, rrd_filename=rrd_filename, graph_filename=None, base=1024, collocation_function='AVERAGE', width=600, height=200, vertical_label='bytes/s', options=[]):
   if not (graph_filename):
      if (start_time in rrd_graph_periods):
         timeperiod_desc = rrd_graph_periods[start_time]
      else:
         timeperiod_desc = str(start_time)
         
      graph_filename = base_separator.join((filename_graphics_base, timeperiod_desc, interface)) + '.png'
   
   first_graph_out = first_graph_in = True
   arguments = []
   arguments_negative = []
   retval = ''
   
   for servicename in services_graph:
      if not (servicename in conf_service_dict):
         print "Unknown service %s: can't graph it." % (servicename,)
         continue
      for direction in (DIRECTION_INPUT, DIRECTION_OUTPUT):
         ds_name = ds_name_filter(devicename=interface, servicename=servicename, direction=direction)
         arguments.append('DEF:%s=%s:%s:%s' % (ds_name, rrd_filename, ds_name, collocation_function))
         if (conf_service_dict[servicename]):
            (color, rrd_name, service_args) = conf_service_dict[servicename][:3]
            
            if (isinstance(color,basestring)):
               #color value sanity checks; avoid writing invalid html later
               assert (color[0] == '#')
               assert (len(color) == 7)
               int(color[1:],16)
               rrd_color = color
            else:
               color = None
               rrd_color = ''
            if (direction == DIRECTION_INPUT):
               if (first_graph_in):
                  graph_call = 'AREA'
                  first_graph_in = False
               else:
                  graph_call = 'STACK'

               if (rrd_name):
                  arguments.append('%s:%s%s:%s%s' % (graph_call, ds_name, rrd_color, rrd_name, service_args))
               else:
                  arguments.append('%s:%s%s%s' % (graph_call, ds_name, rrd_color, service_args))

               retval += html_pack_tr(''.join([html_pack_td(text) for text in (html_colordiv(color),ds_name,)]))

            else:
               if (first_graph_out):
                  graph_call = 'AREA'
                  first_graph_out = False
               else:
                  graph_call = 'STACK'
               
               arguments.append('CDEF:%s_=%s,-1,*' % (ds_name, ds_name))
               arguments_negative.append('%s:%s_%s%s' % (graph_call, ds_name, rrd_color, service_args))
            

   arguments += arguments_negative
   arguments += list(options)

   rrdtool.graph(graph_filename, 
      '-z', 
      '-a', 'PNG', 
      '--base', str(base), 
      '--start', str(start_time),
      '--width', str(width),
      '--height', str(height),
      '--vertical-label', str(vertical_label),
       *arguments)

   return retval



if (__name__ == '__main__'):
   html_output = ''
   for interface in conf_interfaces:
      for start_time in rrd_graph_periods:
         html_output = ipt_graph(interface=interface, start_time=start_time, *graph_args, **graph_kwargs)
   
   if (html_out_file):
      html_output = html_header + html_pack_table(html_output) + html_footer
      html_out_file.write(html_output)
      
   
   