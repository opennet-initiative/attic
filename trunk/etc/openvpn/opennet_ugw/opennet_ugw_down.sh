#!/bin/sh
eval $(/usr/bin/netparam)

# simply remove all SNAT-rules for the opennet_usergateway tunnel
get_rulenum() {
	iptables -L POSTROUTING -t nat --line-numbers -n -v | awk '$4 == "SNAT" && $8 ~ "^tap" {print $1; exit}'
}
while $(iptables -D POSTROUTING $(get_rulenum) -t nat 2>/dev/null); do : ; done

rm -f /tmp/openvpn_ugw_msg.txt	# removing running message
