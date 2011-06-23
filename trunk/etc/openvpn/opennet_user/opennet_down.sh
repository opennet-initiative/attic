#!/bin/sh
#~ ip rule del unicast from $ifconfig_local table 3

# simply remove all SNAT-rules for the opennet_user tunnel
get_rulenum() {
	iptables -L POSTROUTING -t nat --line-numbers -n -v | awk '$4 == "SNAT" && $8 ~ "^tun" {print $1; exit}'
}
while $(iptables -D POSTROUTING $(get_rulenum) -t nat 2>/dev/null); do : ; done

rm -f /tmp/openvpn_msg.txt	# remove running message
if [ -f "/etc/init.d/dhcp-fwd" ]; then
	/etc/init.d/dhcp-fwd stop
	iptables -D PREROUTING -t nat -p udp --dport 67 --sport 67 -j DNAT --to-destination $WIFIADR
fi