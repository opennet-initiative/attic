#!/usr/bin/env python

import os
import daemon_init
import logging
import cPickle
import socket

import socket_management
import pycapabilities
import pid_filing
import daemon_init
import basic_io
import signal_handling

_logger = logging.getLogger()

statefilename = 'brookii.pickle'
statefilename_new = statefilename + '.tmp'

db_args = ()
db_kwargs = {'db':'brookii'}
db_table = 'connection_log_ipv4'
dc_family = socket.AF_INET
restore = True
target_uid = 65534
target_gid = target_uid
save_interval = 600

execfile('brookii_config.py')

pycapabilities.cap_set('= CAP_NET_ADMIN,CAP_SETUID,CAP_SETGID=ep')
pycapabilities.prctl(pycapabilities.PR_SET_KEEPCAPS,1,0,0,0)
os.setgid(target_gid)
os.setuid(target_uid)

if (os.getuid() == 0):
   print 'Failed to change uid. Terminating.'
   sys.exit(255)
   os._exit(255)

pycapabilities.cap_set('= CAP_NET_ADMIN=ep')

pid_filing.file_pid()
pid_filing.release_pid_file()
#daemon_init.daemon_init()
pid_filing.file_pid()

basic_io.log_init()
daemon_init.warnings_redirect_logging()

from data_collocator import Data_Collocator_Mysql

dc = Data_Collocator_Mysql(db_table=db_table, db_args=db_args, db_kwargs=db_kwargs, family=dc_family)

if (restore):
   _logger.log(20, 'Trying to restore previous DB Data Collocator.')
   try:
      dc = cPickle.load(file(statefilename))
   except (IOError, OSError):
      _logger.log(35, 'Failed to unpickle previous DB Data Collocator. Using new object. Error: ', exc_info=True)
   

def state_save(target):
   _logger.log(20, 'Pickling main Data Collector %r to %r.' % (dc, statefilename_new))
   outfile = file(statefilename_new, 'w')
   cPickle.dump(target, outfile)
   outfile.close()
   _logger.log(20, 'Moving %r to %r.' % (statefilename_new, statefilename))
   os.rename(statefilename_new, statefilename) 



dc.nfct_init()

socket_management.Timer(save_interval, state_save, args=(dc,), persistence=True, align=True)
try:
   socket_management.select_loop()
finally:
   _logger.log(50, 'Something terminated the main loop...cleaning up.')
   try:
      dc.data_output()
   except dc.db_exception:
      _logger.log(30, 'data_output() call in cleanup code failed. Continuing as normal. Error:', exc_info=True)
   state_save(dc)
   _logger.log(50, 'Terminating.')

