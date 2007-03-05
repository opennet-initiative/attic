#!/bin/sh
# script to check, if usergateway is reachable via WANDEV
# if it is reachable via WANDEV, a special routing rule is added in table 5
# finally decrement the internet_sharing-blocking-counter every minute.
. /usr/sbin/helper_functions.sh

DEBUG="false"
if [ -n "$(nvram get on_fw_debug)" ]; then DEBUG=$(nvram get on_fw_debug); fi

test -d /tmp/lock || mkdir -p /tmp/lock
if [ -e /tmp/lock/check_usergateway.sh ];then exit; fi
echo "running" >/tmp/lock/check_usergateway.sh

ugw_wan_route () {
	if [ "$1" = "add" ]; then
		# check if route is still there
		if [ -n "$(ip route show table 5 | awk '$1 == "'on_ugw_ip'" && $3 == "'$table_4_default_route'"')" ]; then
				return;
		fi

		#~ ip route flush table 5
		ip route add $on_ugw_ip via $table_4_default_route table 5
		$DEBUG && logger -t check_usergateway "route to ugw ($on_ugw/$on_ugw_ip) registered in table 5"
		
	else
		ip route flush table 5
		$DEBUG && logger -t check_usergateway "routes to ugw removed from table 5"
	fi
}

table_4_default_route=$(ip route show table 4 | awk '$1 == "default" {print $3}')
if [ -n "$table_4_default_route" ]; then
	for on_ugw in $(nvram get on_ugws); do
		on_ugw_ip=$(nslookup $on_ugw 2>/dev/null | tail -n 1 | awk '{ print $2 }')
		if $(ping -c 1 $on_ugw_ip >/dev/null 2>/dev/null); then
			$DEBUG && logger -t check_usergateway "ok, $on_ugw can be reached via WAN-device"
			if [ ! -e /tmp/ugw_reachable_$on_ugw ]; then
				echo "ugw reachable" >/tmp/ugw_reachable_$on_ugw
				ugw_wan_route add $on_ugw
			fi
		else
			$DEBUG && logger -t check_usergateway "no, $on_ugw can't be reached via WAN-device"
			rm -f /tmp/ugw_reachable_$on_ugw
		fi
	done
else
	$DEBUG && logger -t check_usergateway "no, missing default routing policy for WAN-device"
	rm -f /tmp/ugw_reachable_*
	if [ -n "$(ip route show table 5)" ]; then ugw_wan_route del; fi
fi

on_share_internet_blocked=$(nvram get on_share_internet_blocked)
if [ "$1" != "checkonly" ] && [ -n "$on_share_internet_blocked" ]; then
	nvram set on_share_internet_blocked=$(($on_share_internet_blocked-1))
	# if counter reaches zero, ugw is (re)activated
	if [ "$on_share_internet_blocked" = "0" ]; then
		nvram unset on_share_internet_blocked
		nvram set on_share_internet="on"
		nvram commit
	fi
fi

if [ "$(nvram get on_share_internet)" = "on" ] && [ -z "$(ls /var/run/openvpn.opennet_ugw*pid 2>/dev/null)" ]; then
	/etc/init.d/S80openvpn start opennet_ugw
fi

rm /tmp/lock/check_usergateway.sh
