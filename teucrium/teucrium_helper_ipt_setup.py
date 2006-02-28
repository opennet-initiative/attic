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

import os
import sys

#constants
CHAIN_INPUT = 1
CHAIN_OUTPUT = 2

#basic stuff
table='mangle'
iptables='iptables'

chains_base={
   'tc_in':CHAIN_INPUT,
   'tc_out':CHAIN_OUTPUT
   }

base_separator='_'
rules = {}

class service_local:
   def __init__(self, name, protocol, portranges):
      self.service_name = name
      self.protocol = protocol
      self.portranges = portranges
      
   def name(self):
      return self.service_name()
      
   def rule_in(self):
      return_value = []
      for portrange in self.portranges:
         return_value.append('-p %s --dport %s' % (self.protocol, portrange))
      return return_value
      
   def rule_out(self):
      return_value = []
      for portrange in self.portranges:
         return_value.append('-p %s --sport %s' % (self.protocol, portrange))
      return return_value
   
   def rule_bd(self):
      return_value = []
      for portrange in self.portranges:
         return_value.append('-p %s --dport %s' % (self.protocol, portrange))
         return_value.append('-p %s --sport %s' % (self.protocol, portrange))
      return return_value

class service_remote(service_local):
   rule_in = service_local.rule_out
   rule_out = service_local.rule_in

class protocol:
   def __init__(self, name, protocol):
      self.protocol_name = name
      self.protocol = protocol
   def name(self):
      return self.procotol_name
      
   def rule_in(self):
      return (('-p %s' % self.protocol),)

   rule_bd = rule_out = rule_in

class wildcard:
   def __init__(self, name):
      self.wildcard_name = name
      
   def name(self):
      return self.wildcard_name
   
   def rule_in(self):
      return ('',)
   
   rule_bd = rule_out = rule_in

def ipt(commandstring, table=table, stderr_out=True):
   commandstring = '%s -t %s %s' % (iptables, table, commandstring)
   if not (stderr_out):
      commandstring += ' 2>/dev/null'
   print 'Executing: %s' % commandstring
   os.system(commandstring)

def main():
   for chainname in chains_base:
      ipt('-N %s' % chainname, stderr_out=False)
      ipt('-F %s' % chainname)

   for interface in rules.keys():
      for chainname in chains_base.keys():
         chainname_if = base_separator.join((chainname, interface))
         ipt('-N %s' % chainname_if, stderr_out=False)
         ipt('-F %s' % chainname_if)
         
         conditions = []
         if ((chains_base[chainname] & CHAIN_INPUT) == CHAIN_INPUT):
            conditions.append('-i %s' % interface)
         if ((chains_base[chainname] & CHAIN_OUTPUT) == CHAIN_OUTPUT):
            conditions.append('-o %s' % interface)
         for condition in conditions:
            ipt('-A %s %s -j %s' % (chainname, condition, chainname_if))
         
         for rule in rules[interface]:
            if ((chains_base[chainname] & CHAIN_INPUT) == CHAIN_INPUT):
               for ipt_command in rule.rule_in():
                  ipt('-A %s %s -j RETURN' % (chainname_if, ipt_command))
            if ((chains_base[chainname] & CHAIN_OUTPUT) == CHAIN_OUTPUT):
               for ipt_command in rule.rule_out():
                  ipt('-A %s %s -j RETURN' % (chainname_if, ipt_command))



   if ('-f' in sys.argv):
      for chainname in chains_base:
         if ((chains_base[chainname] & CHAIN_INPUT) == CHAIN_INPUT):
            source_chainname = 'PREROUTING'
         if ((chains_base[chainname] & CHAIN_OUTPUT) == CHAIN_OUTPUT):
            source_chainname = 'POSTROUTING'
         
         ipt('-D %s -j %s' % (source_chainname, chainname), stderr_out=False)
         ipt('-I %s 1 -j %s' % (source_chainname, chainname))


if (__name__ == '__main__'):
   execfile('teucrium_helper_ipt_setup_conf.py')
   main()

