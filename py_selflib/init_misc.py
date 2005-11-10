#!/usr/bin/env python2.3
#Copyright 2004 Sebastian Hagen
# This file is part of py_selflib.

# py_selflib is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 
# as published by the Free Software Foundation

# py_selflib is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with py_selflib; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

def set_defaults(defaults, global_scope):
   for variablenamestring in defaults:
      if not (variablenamestring in global_scope):
         if (type(defaults[variablenamestring]) == list):
            global_scope[variablenamestring] = defaults[variablenamestring][:]
         elif (type(defaults[variablenamestring]) == dict):
            global_scope[variablenamestring] = defaults[variablenamestring].copy()
         else:
            global_scope[variablenamestring] = defaults[variablenamestring]

