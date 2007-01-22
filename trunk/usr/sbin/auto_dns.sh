#!/bin/sh

DEBUG="false"
if [ -n "$(nvram get on_fw_debug)" ]; then DEBUG=$(nvram get on_fw_debug); fi

if [ "$(nvram get on_autodns)" = "on" ]; then
	# check if recent dns-server's are overwritten with ppp-values
	if [ -e /tmp/resolv.conf_ppp ]; then
		RESOLV_CONF="/tmp/resolv.conf_ppp"
		DNS_VAR="lan_dns_store"
	else
		RESOLV_CONF="/tmp/resolv.conf"
		DNS_VAR="lan_dns"
	fi

	lan_dns=$(nvram get $DNS_VAR)
	new_dns=$(route -n | sort \
	| awk '
	BEGIN { max = -1; }
	$1 ~ "^192\\.168\\.0\\.[0-9]+$" && $1 != "192.168.0.0" {
		a[$5] = a[$5] "\n " $1;
		if ($5 > max)
			max = $5;
	}
	END {
		for (i = 0; i <= max; i++)
			ret = ret " " a[i];
		print ret;
	}')
	
	new_dns="$(echo $new_dns)"
	
	if [ "$lan_dns" != "$new_dns" ];then
		$DEBUG && logger -t "auto_dns.sh" "updating $RESOLV_CONF"
		nvram set $DNS_VAR="$new_dns"
		resolv=
		awk '!/nameserver/' $RESOLV_CONF > $RESOLV_CONF"_new"
		for dns in $new_dns; do echo "nameserver $dns" >>$RESOLV_CONF"_new"; done
		mv $RESOLV_CONF"_new" $RESOLV_CONF
	fi
fi
