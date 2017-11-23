#!/usr/bin/python
#Copyright 2005 Sebastian Hagen
# This file is part of ketupo.

# ketupo is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 
# as published by the Free Software Foundation

# ketupo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with ketupo; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA


import logging
from socket_management import select_loop
from ketupo_input import olsrd_client_connection, olsrd_client_query


def input_handler(olsrd_data):
   print 'DO2: ', olsrd_data
   
rootlogger = logging.getLogger()
rootlogger.setLevel(5)
rootlogger.addHandler(logging.StreamHandler())

olsrd_client_query(('127.0.0.1', 2004), input_handler, '')

select_loop()


