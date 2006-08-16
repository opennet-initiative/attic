#!/usr/bin/env python

from distutils.core import setup, Extension

pynlct__main = Extension('nlct_', sources = ['nlct_.c'], libraries = ['netfilter_conntrack'])

setup (name = 'nlct_',
       version = '0.02',
       description = 'experimental netfilter netlink conntrack interface',
       ext_modules = [pynlct__main],
      )
