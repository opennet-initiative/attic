#!/bin/sh
eval $(/usr/bin/netparam)

iptables -t nat -A POSTROUTING -o $dev -s $LANNET/$LANPRE -j SNAT --to-source $ifconfig_local
iptables -t nat -A POSTROUTING -o $dev -s $DHCPWIFINET/$DHCPWIFIPRE -j SNAT --to-source $ifconfig_local

on_ugw=$(nvram get on_ugw)
ugw_ip=$(nslookup $on_ugw 2>/dev/null | tail -n 1 | awk '{ print $2 }')

# dont use ugw-tunnel for user-tunneld packages
iptables -t nat -A POSTROUTING -o $WANDEV -s $WIFINET/$WIFIPRE -d $ugw_ip -p udp --dport 1600 -j SNAT --to-source $WANADR
iptables -t nat -A PREROUTING -d 192.168.0.251  -p udp --dport 1600 -j DNAT --to-destination $ugw_ip

# clean contrack from registered connections to let them use the new settings
echo 0 > /proc/sys/net/ipv4/netfilter/ip_conntrack_udp_timeout
echo 0 > /proc/sys/net/ipv4/netfilter/ip_conntrack_udp_timeout_stream
while [ -n "$(cat /proc/net/ip_conntrack | grep 'port=1600 .*=192.168.0.251')" ]; do sleep 5; done
echo 30 > /proc/sys/net/ipv4/netfilter/ip_conntrack_udp_timeout
echo 180 > /proc/sys/net/ipv4/netfilter/ip_conntrack_udp_timeout_stream

echo "ugw-tunnel active" >/tmp/openvpn_ugw_msg.txt	# a short message for the web frontend
