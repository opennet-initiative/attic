#!/bin/sh
eval $(/usr/bin/netparam)

iptables -t nat -A POSTROUTING -o $dev -s $LANNET/$LANPRE -j SNAT --to-source $ifconfig_local
iptables -t nat -A POSTROUTING -o $dev -s $DHCPWIFINET/$DHCPWIFIPRE -j SNAT --to-source $ifconfig_local

nagare_ip=$(nslookup nagare.on-i.de 2>/dev/null | tail -n 1 | awk '{ print $2 }')
#nagare_ip=$(ping -c 1 nagare.on-i.de 2>/dev/null | grep PING);
#nagare_ip=${nagare_ip#*\(};
#nagare_ip=${nagare_ip%%\)*};

# dont use ugw-tunnel for user-tunneld packages
iptables -t nat -A POSTROUTING -o $WANDEV -s $WIFINET/$WIFIPRE -d $nagare_ip -p udp --dport 1600 -j SNAT --to-source $WANADR
iptables -t nat -A PREROUTING -d 192.168.0.251  -p udp --dport 1600 -j DNAT --to-destination $nagare_ip

echo "ugw-tunnel active" >/tmp/openvpn_ugw_msg.txt	# a short message for the web frontend
