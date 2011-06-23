#!/bin/sh
eval $(/usr/bin/netparam)
. /usr/sbin/helper_functions.sh

TAPNET_PRE=$(get_NETPRE_dev tap0)
# if TAP not available set rule to the predefined value to enable routing from Usergateways.
[ -z "$TAPNET_PRE" ] && TAPNET_PRE="10.2.0.0/16"

ip route flush table 3
ip route add throw $TAPNET_PRE table 3
ip route add throw $LANNET/$LANPRE table 3
[ -n "$WIFIPRE" ] && ip route add throw $WIFINET/$WIFIPRE table 3
[ -n "$WANPRE" ] && ip route add throw $WANNET/$WANPRE table 3
ip route add default via $route_vpn_gateway dev $dev table 3

iptables -t nat -A POSTROUTING -o $dev -s $LANNET/$LANPRE -j SNAT --to-source $ifconfig_local
[ -n "$DHCPWIFIPRE" ] && iptables -t nat -A POSTROUTING -o $dev -s $DHCPWIFINET/$DHCPWIFIPRE -j SNAT --to-source $ifconfig_local

echo "vpn-tunnel active" >/tmp/openvpn_msg.txt	# a short message for the web frontend
if [ -f "/etc/init.d/dhcp-fwd" ]; then
	/etc/init.d/dhcp-fwd start
	iptables -A PREROUTING -t nat -p udp --dport 67 --sport 67 -j DNAT --to-destination $WIFIADR
fi