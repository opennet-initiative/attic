SHELL := /bin/bash
SHELL := /bin/posh
SHELL := /bin/dash
SHELL := /bin/sh

default:
	@echo 'iptables 1.3.8'
	@echo 'Linux 2.6.22'
	@echo 'patch-o-matic-ng 20070714'

prep howtos build clean install binary-indep binary-arch binary:
	$(MAKE) -f $(CURDIR)/debian/rules $@

.PHONY: prep howtos clean binary build
