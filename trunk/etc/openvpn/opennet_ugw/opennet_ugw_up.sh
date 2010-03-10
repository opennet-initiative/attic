#!/bin/sh
eval $(/usr/bin/netparam)
DEBUG="false"
if [ -n "$(nvram get on_fw_debug)" ]; then DEBUG=$(nvram get on_fw_debug); fi

[ -z "$(grep $(nvram get lan_ifname) /var/etc/olsrd.conf)" ] &&
	iptables -t nat -A POSTROUTING -o $dev -s $LANNET/$LANPRE -j SNAT --to-source $ifconfig_local
	
[ -n "$DHCPWIFIPRE" ] && iptables -t nat -A POSTROUTING -o $dev -s $DHCPWIFINET/$DHCPWIFIPRE -j SNAT --to-source $ifconfig_local

# exclude tunnel packets from policy rules
TAPNET_PRE="$(ipcalc $ifconfig_local $ifconfig_netmask | awk 'BEGIN{FS="="} { if ($1=="NETWORK") net=$2; if ($1="PREFIX") pre=$2;} END{print net"/"pre}')"
ip route add throw $TAPNET_PRE table 3 2>/dev/null
ip route add throw $TAPNET_PRE table 4 2>/dev/null

filename=${config#/etc/openvpn/}
filename=/tmp/${filename%.conf}_$dev.txt
echo $remote_1 > $filename	# a short message for the web frontend
