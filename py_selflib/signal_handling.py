#!/usr/bin/env python

import signal
import os
import sys
import logging
import thread

import data_pickling
import socket_management

logger = logging.getLogger('signal_handling')

def program_shutdown(signal, stack_frame):
   logger.log(50, 'Caught signal %s, shutting down.' % (signal,))
   thread.start_new_thread(socket_management.shutdown, ())
   data_pickling.save_variables()
   sys.exit(signal)


signal.signal(signal.SIGTERM, program_shutdown)
signal.signal(signal.SIGINT, program_shutdown)
