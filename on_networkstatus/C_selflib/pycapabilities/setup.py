#!/usr/bin/env python


from distutils.core import setup, Extension

capabilities_main = Extension('pycapabilities', sources = ['pycapabilities.c'], libraries = ['cap'])

setup (name = 'pycapabilities',
       version = '0.01',
       description = 'Linux capabilities(7) python interface',
       ext_modules = [capabilities_main],
      )
