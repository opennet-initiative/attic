#!/usr/bin/env python

import logging.handlers

target_uid = 1000
target_gid = target_uid

settings = {
   'basic_io': {
      'handlers':(
         ([None], logging.handlers.RotatingFileHandler, (), {'filename':'log/all'}, (('setLevel', (20,)),)),
         ([None], logging.StreamHandler, (), {}, (('setLevel', (20,)),))
         )
      },
  }
