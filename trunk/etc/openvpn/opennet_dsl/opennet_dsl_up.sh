#!/bin/sh
eval $(/usr/bin/netparam)

# get ip of nagare from routing table 5
# table 5 and the following iptable-rules should have alsways the same nagare-ip
# if nagare-ip will change, this will be recognized by cron.hourly
nagare_ip=$(ip route show table 5 | cut -d' ' -f1)

# dont use dsl-tunnel for user-tunneld packages
iptables -t nat -A POSTROUTING -o ppp0 -s $WIFINET/$WIFIPRE -d $nagare_ip -p udp --dport 1600 -j SNAT --to-source $WANADR
iptables -t nat -A PREROUTING -d 192.168.0.251  -p udp --dport 1600 -j DNAT --to-destination $nagare_ip

echo "dsl-tunnel active" >/tmp/openvpn_dsl_msg.txt	# a short message for the web frontend
