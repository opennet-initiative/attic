#!/usr/bin/env python


from distutils.core import setup, Extension

# might want to add iptc_pic to libraries, where existent
iptint_main = Extension('iptint', sources = ['iptintmodule.c'], libraries = ['iptc'])

setup (name = 'iptint',
       version = '0.01',
       description = 'experimental ipt interface',
       ext_modules = [iptint_main],
      )
