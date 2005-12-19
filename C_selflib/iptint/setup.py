#!/usr/bin/env python


from distutils.core import setup, Extension

iptint_main = Extension('iptint', sources = ['iptintmodule.c'], libraries = ['iptc'])

setup (name = 'iptint',
       version = '0.01',
       description = 'experimental ipt interface',
       ext_modules = [iptint_main],
      )
