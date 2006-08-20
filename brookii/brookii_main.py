#!/usr/bin/env python

import os
import daemon_init
import logging
import cPickle

import socket_management
import pycapabilities

_logger = logging.getLogger()

statefilename = 'brookii.pickle'
statefilename_new = statefilename + '.tmp'

from data_collocator import Data_Collocator_Mysql

db_args = ()
db_kwargs = {db:'brookii'}
db_table = 'connection_log_ipv4'
restore = True
target_uid = 65534
save_interval = 600

execfile('brookii_config.py')

pycapabilities.cap_set('= CAP_NET_ADMIN,CAP_SETUID+ep')
pycapabilities.prctl(pycapabilities.PR_SET_KEEPCAPS,1,0,0,0)
os.setuid(target_uid)
if (os.getuid() == 0):
   _logger.log(50, 'Failed to change uid. Dying.')
   sys.exit(255)
   os._exit(255)

pycapabilities.cap_set('= CAP_NET_ADMIN+ep')

dc = Data_Collocator_Mysql(table=db_table, db_args=db_args, db_kwargs=db_kwargs)

if (restore):
   _logger.log(20, 'Trying to restore previous DB Data Collocator.')
   try:
      dc = cPickle.load(file(statfilename))
   except (IOError, OSError):
      _logger.log(35, 'Failed to unpickle previous DB Data Collocator. Using new object. Error: ', exc_info=True)
   

def state_save(target):
   _logger.log(20, 'Pickling main Data Collector %r to %r.' % (dc, statefilename_new))
   outfile = file(statefilename_new, 'w')
   cPickle.dump(target, outfile)
   outfile.close()
   _logger.log(20, 'Moving %r to %r.' % (statefilename_new, statefilename))
   os.rename(statefilename_new, statefilename) 


socket_management.Timer(save_interval, state_save, args=(dc,), persistence=True, align=True)
socket_management.select_loop()
