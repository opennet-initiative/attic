#!/usr/bin/env python

from distutils.core import setup, Extension

pynlct__main = Extension('nlct_', sources = ['nlct_.c'], libraries = ['netfilter_conntrack'])

setup (name = 'nlct_',
       version = '0.03',
       description = 'experimental netfilter netlink conntrack interface',
       author = 'Sebastian Hagen',
       author_email = 'sh_py@memespace.net',
       py_modules = ['nlct', 'address_structures'],
       ext_modules = [pynlct__main],
      )
