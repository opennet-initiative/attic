#!/bin/sh
eval $(/usr/bin/netparam)

# cause nagare might be unreachable and WAN might be down its better to search for the rules to remove

# dont use dsl-tunnel for user-tunneld packages
RULENUM=$(iptables -L POSTROUTING -t nat --line-numbers -n | awk "/$WIFINET\/$WIFIPRE/"'&& /dpt:1600/ {print $1; exit}')
iptables -D POSTROUTING $RULENUM -t nat

RULENUM=$(iptables -L PREROUTING -t nat --line-numbers -n | awk '/192.168.0.251/ && /dpt:1600/ {print $1; exit}')
iptables -D POSTROUTING $RULENUM -t nat

rm -f /tmp/openvpn_dsl_msg.txt	# removing running message
