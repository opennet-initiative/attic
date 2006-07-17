#!/bin/sh

# simply remove all SNAT-rules for the opennet_user tunnel
get_rulenum() {
	iptables -L POSTROUTING -t nat --line-numbers -n -v | awk '$4 == "SNAT" && $8 == "tun0" {print $1; exit}'
}
while [ -n "$(get_rulenum)" ]; do
	iptables -D POSTROUTING $(get_rulenum) -t nat
done

rm -f /tmp/openvpn_msg.txt	# remove running message
