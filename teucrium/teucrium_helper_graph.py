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

col_sequence = (('tot','TOTAL'), ('avg','AVERAGE'),('last','LAST'))

def html_pack_table(text):
   return '<table class="teucrium_table_table">\n%s</table>\n' % (text,)

def html_pack_tr(text):
   return '<tr class="teucrium_table_tr">\n%s</tr>\n' % (text,)

def html_pack_td(text):
   return '<td class="teucrium_table_td">\n%s\n</td>\n' % (text,)

def html_pack_th(cols, text):
   return '<th class="teucrium_table_th" colspan="%d">\n%s\n</th>\n' % (cols, text)

def html_colordiv(color):
   if (color):
      colorstr = 'background-color:%s; ' % (color,)
   else:
      colorstr = ''
   return '<div class="teucrium_table_colordiv" style="%s width:%dpx; height:%dpx" />' % (colorstr, html_legend_sample_edge_length, html_legend_sample_edge_length)


def ipt_graph(interface, start_time, rrd_filename=rrd_filename, graph_filename=None, base=1024, collocation_function='AVERAGE', width=600, height=200, vertical_label='bytes/s', return_html=True, options=[]):
   if not (graph_filename):
      if (start_time in rrd_graph_periods):
         timeperiod_desc = rrd_graph_periods[start_time]
      else:
         timeperiod_desc = str(start_time)
         
      graph_filename = base_separator.join((filename_graphics_base, timeperiod_desc, interface)) + '.png'
   
   first_graph_out = first_graph_in = True
   arguments = []
   arguments_negative = []
   if (return_html):
      html_data = []

   for servicename in services_graph:
      if not (servicename in conf_service_dict):
         print "Unknown service %s: can't graph it." % (servicename,)
         continue
      if (conf_service_dict[servicename]):
         for direction in (DIRECTION_INPUT, DIRECTION_OUTPUT):
            ds_name = ds_name_filter(devicename=interface, servicename=servicename, direction=direction)
            arguments.append('DEF:%s=%s:%s:%s' % (ds_name, rrd_filename, ds_name, collocation_function))
            (color, legend_name, service_args) = conf_service_dict[servicename][:3]

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

               if (legend_name):
                  arguments.append('%s:%s%s:%s%s' % (graph_call, ds_name, rrd_color, legend_name, service_args))
               else:
                  arguments.append('%s:%s%s%s' % (graph_call, ds_name, rrd_color, service_args))

            else:
               if (first_graph_out):
                  graph_call = 'AREA'
                  first_graph_out = False
               else:
                  graph_call = 'STACK'
               
               arguments.append('CDEF:%s_=%s,-1,*' % (ds_name, ds_name))
               arguments_negative.append('%s:%s_%s%s' % (graph_call, ds_name, rrd_color, service_args))

         if (return_html):
            html_data.append((ds_name, color, legend_name))
            ifservice_id_string = 'bd_%s_%s' % (interface.replace('+','_'), servicename)
            arguments.append('CDEF:%s=%s,%s,+' % (ifservice_id_string,
               ds_name_filter(devicename=interface, servicename=servicename, direction=DIRECTION_INPUT),
               ds_name_filter(devicename=interface, servicename=servicename, direction=DIRECTION_OUTPUT)
            ))
            for (col_id_string, col_string) in col_sequence:
               arguments.append('VDEF:%s_%s=%s,%s' % (ifservice_id_string, col_id_string, ds_name, col_string))
               arguments.append('PRINT:%s_%s:%%lf' % (ifservice_id_string, col_id_string))

   arguments += arguments_negative
   arguments += list(options)

   rrd_retval = rrdtool.graph(graph_filename, 
      '-z', 
      '-a', 'PNG', 
      '--base', str(base),
      '--start', str(start_time),
      '--width', str(width),
      '--height', str(height),
      '--vertical-label', str(vertical_label),
       *arguments)

   if (return_html):
      rrd_stats_raw = rrd_retval[2]
      if (rrd_stats_raw):
         rrd_stats = [float(x) for x in rrd_stats_raw]
         index_post = len(col_sequence)
         assert len(rrd_stats) == index_post*len(html_data)
      color_dict = {}
      summary_dict = {}
      for (ds_name, color, legend_name) in html_data:
         color_dict[legend_name] = color
         if (rrd_stats_raw):
            summary_dict[legend_name] = tuple(rrd_stats[:index_post])
            del(rrd_stats[:index_post])
      return (color_dict, summary_dict)



if (__name__ == '__main__'):
   return_html = bool(html_out_file)
   summaries = {}
   for interface in conf_interfaces:
      for start_time in rrd_graph_periods:
         if (return_html):
            (color_dict, summary_dict) = ipt_graph(interface=interface, start_time=start_time, return_html=return_html, *graph_args, **graph_kwargs)
            summaries[(interface,start_time)] = summary_dict
         else:
            ipt_graph(interface=interface, start_time=start_time, return_html=return_html, *graph_args, **graph_kwargs)

   if (return_html):
      legend_names = color_dict.keys()
      legend_names.sort()
      summary_columns = summaries.keys()
      summary_columns.sort()
      
      colspan = len(col_sequence)
      html_output = '<th /><th />'
      for header_one in summary_columns:
         html_output += html_pack_th(colspan, header_one)
      html_output = html_pack_tr(html_output)
      html_output += html_pack_tr('<th /><th />' + ''.join([html_pack_th(1,element[1]) for element in col_sequence]*len(summary_columns)))
      for legend_name in legend_names:
         row_stats = []
         for key in summary_columns:
            try:
               row_stats.extend(summaries[key][legend_name])
            except KeyError:
               row_stats.extend(('',)*colspan)
         html_output += html_pack_tr(''.join([html_pack_td(text) for text in [html_colordiv(color_dict[legend_name]),legend_name] + row_stats]))

      html_output = html_header + html_pack_table(html_output) + html_footer
      html_out_file.write(html_output)
