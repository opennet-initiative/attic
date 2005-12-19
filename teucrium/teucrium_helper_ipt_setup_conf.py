#!/usr/bin/env python

#service configuration
rules['ppp+'] = (
   service_remote('tcp_http', 'tcp', ('80',)),
   service_remote('tcp_https', 'tcp', ('443',)),
   service_remote('tcp_bt', 'tcp', ('6881:6889',)),
   service_local('tcp_bt', 'tcp', ('6881:6889',)),
   protocol('tcp_other', 'tcp'),
   service_remote('udp_dns', 'udp', ('53',)),
   service_remote('udp_vpn', 'udp', ('600:602',)),
   protocol('udp_other', 'udp'),
   protocol('icmp_other', 'icmp'),
   wildcard('ip_other',),
   )

rules['eth0'] = rules['eth1'] = rules['eth2'] = rules['tun+'] = (
   service_local('tcp_http', 'tcp', ('80',)),
   service_local('tcp_https', 'tcp', ('443',)),
   service_remote('tcp_bt', 'tcp', ('6881:6889',)),
   service_local('tcp_bt', 'tcp', ('6881:6889',)),
   protocol('tcp_other', 'tcp'),
   service_local('udp_dns', 'udp', ('53',)),
   service_local('udp_vpn', 'udp', ('600:602',)),
   protocol('udp_other', 'udp'),
   protocol('icmp_other', 'icmp'),
   wildcard('ip_other',),
   )
   