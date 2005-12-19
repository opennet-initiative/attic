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

import logging
import time
from sets import Set

import rrdtool
import iptint

from socket_management import timers_add

COUNTER_PACKETS = 0
COUNTER_BYTES = 1

class ipt_grapher:
   def __init__(self, rrd_filename, rrd_step=1, timer_register=False):
      self.rrd_filename = rrd_filename
      self.rrd_step = rrd_step
      self.targets = {}
      self.loggername = '.'.join((self.__class__.__name__, rrd_filename))
      self.logger = logging.getLogger(self.loggername)
      if (timer_register):
         timers_add(rrd_step, self.rrd_update, parent=self, persistence=True)

   def target_add(self, ds_name, nf_table, nf_chain, nf_index, counter_type=COUNTER_BYTES):
      """Register <counter_type> counter of rule no. <nf_index> of chain <nf_chain> of table <nf_table> for data source <ds_name>"""
      if not (nf_table in self.targets):
         self.targets[nf_table] = {}
      if not (nf_chain in self.targets[nf_table]):
         self.targets[nf_table][nf_chain] = {}
      if not (nf_index in self.targets[nf_table][nf_chain]):
         self.targets[nf_table][nf_chain][nf_index] = Set()
      
      self.targets[nf_table][nf_chain][nf_index].add((ds_name, counter_type))
      
   def target_remove(self, ds_name, nf_table, nf_chain, nf_index, counter_type=COUNTER_BYTES):
      self.targets[nf_table][nf_chain][nf_index].remove((ds_name, counter_type))
      
      if (len(self.targets[nf_table][nf_chain][nf_index]) == 0):
         del(self.targets[nf_table][nf_chain][nf_index])
      if (len(self.targets[nf_table][nf_chain]) == 0):
         del(self.targets[nf_table][nf_chain])
      if (len(self.targets[nf_table]) == 0):
         del(self.targets[nf_table])

   def rrd_update(self):
      ds_names = []
      values = ['N']
      for tablename in self.targets:
         table = iptint.table_get(tablename)
         for chainname in self.targets[tablename]:
            if not (chainname in table):
               self.logger.log(45, 'Unable to find chain %r in table %r. Not updating any counters related to it.' % (chainname, tablename))
               continue
            
            chain_targets = self.targets[tablename][chainname]
            chain = table[chainname]
            
            for rule_index in chain_targets:
               if (rule_index == None):
                  #try to read chain counters
                  if (chain[0] == None):
                     self.logger.log(45, 'Unable to process chain-counters (nf_index == None) for chain %r of table %r since this is not a built-in chain.' % (chainname, tablename))
                     continue

                  for target_spec in chain_targets[rule_index]:
                     ds_name, counter_type = target_spec
                     ds_names.append(ds_name)
                     values.append(chain[1][counter_type])
                     
               elif not (rule_index < len(chain[2])):
                  self.logger.log(40, 'Unable to get data from rule no. %r of chain %r of table %r since the chain only has %r rules.' % (rule_index, chainname, tablename, len(chain)))
                     
               else:
                  #try to read rule counters
                  for target_spec in chain_targets[rule_index]:
                     ds_name, counter_type = target_spec
                     ds_names.append(ds_name)
                     values.append(chain[2][rule_index][2][counter_type])
      
      self.logger.log(12, 'Recording %d counter values.' % (len(ds_names),))
      
      try:
         rrdtool.update(self.rrd_filename, '--template', ':'.join(ds_names), ':'.join(map(str,values)))
      except rrdtool.error:
         self.logger.log(48, 'Failed to update rrd. Error:', exc_info=True)

      else:
         self.logger.log(11, 'Done recording.')
   
   def rrd_create(self, RRAs, start_time=time.time(), minimum=0, maximum=12500000000, heartbeat=10, ds_type='DERIVE'):
      arguments = ['--start', str(start_time), '--step', str(self.rrd_step)]
      for nf_table in self.targets:
         for nf_chain in self.targets[nf_table]:
            for nf_index in self.targets[nf_table][nf_chain]:
               for target_spec in self.targets[nf_table][nf_chain][nf_index]:
                  arguments.append('DS:%s:%s:%s:%s:%s' % (target_spec[0], ds_type, heartbeat, minimum, maximum))
      
      for rra in RRAs:
         if not (isinstance(rra, basestring)):
            rra = 'RRA:%s:%s:%s:%s' % rra
         arguments.append(rra)
         
      self.logger.log(25, 'Creating rrd.')
      
      rrdtool.create(self.rrd_filename, *arguments)
   