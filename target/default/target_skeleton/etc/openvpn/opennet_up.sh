#!/bin/sh
eval $(/usr/bin/netparam)
ip route flush table 3
ip route add throw $LANNET/$LANPRE table 3
ip route add throw $WIFINET/$WIFIPRE table 3
ip route add default via $route_vpn_gateway table 3
iptables -t nat -A POSTROUTING -o $dev -s $LANNET/$LANPRE -j SNAT --to-source $ifconfig_local
echo "vpn-tunnel active" >/tmp/openvpn_msg.txt	# a short message for the web frontend
/etc/init.d/portmapping start