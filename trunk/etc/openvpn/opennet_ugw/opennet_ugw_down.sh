#!/bin/sh
eval $(/usr/bin/netparam)

# simply remove all SNAT-rules for the opennet_usergateway tunnel
get_rulenum() {
	iptables -L POSTROUTING -t nat --line-numbers -n -v | awk '$4 == "SNAT" && $8 ~ "^tap" {print $1; exit}'
}
while [ -n "$(get_rulenum)" ]; do
	iptables -D POSTROUTING $(get_rulenum) -t nat
done


# cause usergateway might be unreachable and WAN might be down its better to search for the rules to remove

# dont use ugw-tunnel for user-tunneld packages
RULENUM=$(iptables -L POSTROUTING -t nat --line-numbers -n | awk "/$WIFINET\/$WIFIPRE/"'&& /dpt:1600/ {print $1; exit}')
iptables -D POSTROUTING $RULENUM -t nat

RULENUM=$(iptables -L PREROUTING -t nat --line-numbers -n | awk '/192.168.0.251/ && /dpt:1600/ {print $1; exit}')
iptables -D PREROUTING $RULENUM -t nat

rm -f /tmp/openvpn_ugw_msg.txt	# removing running message
