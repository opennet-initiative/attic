#!/bin/sh
# script to check, if usergateway is reachable via WANDEV

DEBUG="false"
if [ -n "$(nvram get on_fw_debug)" ]; then DEBUG=$(nvram get on_fw_debug); fi

table_4=$(ip route show table 4)
if [ -n "$table_4" ]; then
	on_ugw=$(nvram get on_ugw)
	on_ugw_ip=$(nslookup $on_ugw 2>/dev/null | tail -n 1 | awk '{ print $2 }')
	WANDEV=$(nvram get wan_ifname)
	ip_remote=$(route -n | awk '$8 == "'$WANDEV'"  && $1 == "0.0.0.0" { print $2; exit }')
	if [ -n "$ip_remote" ] && [ -n "on_ugw_ip" ]; then
		if [ -z "$(ip route show table 5 | awk '$1 == "'$on_ugw_ip'" && $3 == "'$ip_remote'"')" ]; then
			# policy-route noch nicht vorhanden
			$DEBUG && logger -t check_usergateway "activate policy-routing for $on_ugw via table 5"
			ip route flush table 5 2>/dev/null
			ip route add $on_ugw_ip via $ip_remote table 5
		fi
		if $(ping -c 1 $on_ugw_ip >/dev/null 2>/dev/null); then
			$DEBUG && logger -t check_usergateway "ok, $on_ugw can be reached via WAN-device"
			echo "ugw reachable" >/tmp/ugw_reachable
		else
			$DEBUG && logger -t check_usergateway "no, $on_ugw can't be reached via WAN-device"
			rm -f /tmp/ugw_reachable
		fi
	fi
else
	rm -f /tmp/ugw_reachable
fi

on_share_internet_blocked=$(nvram get on_share_internet_blocked)
if [ "$1" != "checkonly" ] && [ -n "$on_share_internet_blocked" ]; then
	nvram set on_share_internet_blocked=$(($on_share_internet_blocked-1))
	# if counter reaches zero, ugw is (re)activated
	if [ "$on_share_internet_blocked" = "0" ]; then
		nvram unset on_share_internet_blocked
		nvram set on_share_internet="on"
		nvram commit
		#~ if [ -n "$table_4" ]; then /etc/init.d/S80openvpn start opennet_ugw; fi
		/etc/init.d/S80openvpn start opennet_ugw
	fi
fi
