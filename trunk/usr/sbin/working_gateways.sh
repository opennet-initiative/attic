#!/bin/sh

# this script returns a list of gateways, separated by space
# if there are any working gateways, it will return them (if they are not blacklisted)
# if there are no working gateways found, it will generate a list of possible gateways from routes
# all entries are checked against blacklist, so if only blacklisted gateways found, this script will return nothing


blacklist=$(nvram get on_gwblackaddrs)
gw_addrs=
accept_nonworking=

while [ "$gw_addrs" = "" ]; do
	if [ -z "$accept_nonworking" ]; then
		on_gwaddrs=$(nvram get on_gwaddrs)
	else
		ip_classB=$(nvram get wifi_ipaddr | awk 'BEGIN{FS="."} {print $1"\\\\."$2}')
		# usual gateways are 192.168.0.X, reachable over batman they have 192.168.43.X
		on_gwaddrs=$(ip route show table all type unicast \
			| awk '$1 ~ "^'"$ip_classB"'\\.(0|43)\\.[1-9][0-9]*$" { print $1 }')
		gw_addrs="$(nvram get on_gw)";
	fi;
	
	for on_gwaddr in $on_gwaddrs; do
		if [ -n "$accept_nonworking" ] || [ "$(echo $on_gwaddr | cut -d':' -f2)" = "y" ]; then
			gw_addr=$(echo $on_gwaddr | cut -d':' -f1)
			
			# check if still in list (may happen if accept_nonworking is set) or
			# 	blacklisted Gateways, if found then continue in loop
			if [ -n "$(echo "$gw_addrs $blacklist" | awk "/$gw_addr/"'{print}')" ]; then
					continue;
			fi
			
			gw_addrs="$gw_addrs $gw_addr"
		fi;
	done;
	if [ -n "$accept_nonworking" ]; then break; fi
	accept_nonworking="true"
done;

echo $gw_addrs
