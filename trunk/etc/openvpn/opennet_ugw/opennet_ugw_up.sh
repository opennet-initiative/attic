#!/bin/sh
eval $(/usr/bin/netparam)

DEBUG="false"
if [ -n "$(nvram get on_fw_debug)" ]; then DEBUG=$(nvram get on_fw_debug); fi

iptables -t nat -A POSTROUTING -o $dev -s $LANNET/$LANPRE -j SNAT --to-source $ifconfig_local
[ -n "$DHCPWIFIPRE" ] && iptables -t nat -A POSTROUTING -o $dev -s $DHCPWIFINET/$DHCPWIFIPRE -j SNAT --to-source $ifconfig_local

on_ugw=$(nvram get on_ugw)
ugw_ip=$(nslookup $on_ugw 2>/dev/null | tail -n 1 | awk '{ print $2 }')

# dont use ugw-tunnel for user-tunneld packages
iptables -t nat -A POSTROUTING -o $WANDEV -s $WIFINET/$WIFIPRE -d $ugw_ip -p udp --dport 1600 -j SNAT --to-source $WANADR
iptables -t nat -A PREROUTING -d 192.168.0.251  -p udp --dport 1600 -j DNAT --to-destination $ugw_ip

# exclude tunnel packets from policy rules
TAPNET_PRE="$(ipcalc $ifconfig_local $ifconfig_netmask | awk 'BEGIN{FS="="} { if ($1=="NETWORK") net=$2; if ($1="PREFIX") pre=$2;} END{print net"/"pre}')"
ip route add throw $TAPNET_PRE table 3
ip route add throw $TAPNET_PRE table 4


echo "ugw-tunnel active" >/tmp/openvpn_ugw_msg.txt	# a short message for the web frontend
