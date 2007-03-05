#!/bin/sh
eval $(/usr/bin/netparam)

# simply remove all SNAT-rules for the opennet_usergateway tunnel
get_rulenum() {
	iptables -L POSTROUTING -t nat --line-numbers -n -v | awk '$4 == "SNAT" && $8 ~  "'"$dev"'" {print $1; exit}'
}
while $(iptables -D POSTROUTING $(get_rulenum) -t nat 2>/dev/null); do : ; done

filename=${config#/etc/openvpn/}
filename=/tmp/${filename%.conf}_$dev.txt
rm -f $filename	# removing running message
