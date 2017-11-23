#!/usr/bin/env python

import logging.handlers

target_uid = FIXME
target_gid = target_uid

settings = {
   'basic_io': {
      'handlers':(
         ([None], logging.handlers.RotatingFileHandler, (), {'filename':'log/all', 'maxBytes':1048576, 'backupCount':1}, (('setLevel', (20,)),)),
         #([None], logging.StreamHandler, (), {}, (('setLevel', (20,)),))
         )
      },
  }

db_kwargs = {
   'db':'brookii',
   'user':'brookii',
   'passwd':FIXME
}
