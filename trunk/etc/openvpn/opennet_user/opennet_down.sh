#!/bin/sh
eval $(/usr/bin/netparam)
iptables -t nat -D POSTROUTING -o $dev -s $LANNET/$LANPRE -j SNAT --to-source $ifconfig_local
iptables -t nat -D POSTROUTING -o $dev -s $DHCPWIFINET/$DHCPWIFIPRE -j SNAT --to-source $ifconfig_local
rm -f /tmp/openvpn_msg.txt	# remove running message
