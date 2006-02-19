#!/bin/sh

blacklist=$(nvram get on_gwblackaddrs)
gw_addrs=

for on_gwaddr in $(nvram get on_gwaddrs); do
	if [ "$(echo $on_gwaddr | cut -d':' -f2)" = "y" ]; then
		gw_addr=$(echo $on_gwaddr | cut -d':' -f1)
		
		# check for blacklisted Gateways, if found then continue in loop
		if [ -n "$(echo $blacklist | awk "/$gw_addr/"'{print}')" ]; then
				continue;
		fi
		
		gw_addrs="$gw_addrs $gw_addr"
	fi;
done;
echo $gw_addrs
