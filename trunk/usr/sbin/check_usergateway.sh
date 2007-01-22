#!/bin/sh
# script to check, if usergateway is reachable via WANDEV
# if it is reachable via WANDEV, a special routing rule is added in table 5
# if there are user-vpn-connections to the central gateway trough the usergateway-tunnel,
# they will be routed around to prevent tunnel-in-tunnel traffic.
# fianlly decrement the internet_sharing-blocking-counter every minute.

DEBUG="false"
if [ -n "$(nvram get on_fw_debug)" ]; then DEBUG=$(nvram get on_fw_debug); fi

test -d /tmp/lock || mkdir -p /tmp/lock
if [ -e /tmp/lock/check_usergateway.sh ];then exit; fi
echo "running" >/tmp/lock/check_usergateway.sh

ugw_wan_route () {
	if [ "$1" = "add" ]; then
		# check if route is still there
		if [ -n "$(ip route show table 5 | awk '$3 == "'$table_4_default_route'"')" ]; then
				return;
		fi

		ip route flush table 5
		ip route add $on_ugw_ip via $table_4_default_route table 5
		$DEBUG && logger -t check_usergateway "route to usergateway ($on_ugw_ip) registered in table 5"
		
	else
		ip route flush table 5
		$DEBUG && logger -t check_usergateway "route to usergateway ($on_ugw_ip) removed from table 5"
	fi
}

table_4_default_route=$(ip route show table 4 | awk '$1 == "default" {print $3}')
on_ugw_ip=
if [ -n "$table_4_default_route" ]; then
	on_ugw=$(nvram get on_ugw)
	on_ugw_ip=$(nslookup $on_ugw 2>/dev/null | tail -n 1 | awk '{ print $2 }')
	if $(ping -c 1 $on_ugw_ip >/dev/null 2>/dev/null); then
		$DEBUG && logger -t check_usergateway "ok, $on_ugw can be reached via WAN-device"
		if [ ! -e /tmp/ugw_reachable ]; then
			echo "ugw reachable" >/tmp/ugw_reachable
			ugw_wan_route add
		fi
	else
		$DEBUG && logger -t check_usergateway "no, $on_ugw can't be reached via WAN-device"
		rm -f /tmp/ugw_reachable
	fi
else
	$DEBUG && logger -t check_usergateway "no, missing default routing policy for WAN-device"
	rm -f /tmp/ugw_reachable
	if [ -n "$(ip route show table 5)" ]; then ugw_wan_route del; fi
fi


# check if there are any connections trough a usergateway-tunnel which are double-tunneld
if [ "$1" != "checkonly" ] && [ -n "$(ip route show table 5)" ]; then
	wanaddr="$(ip addr show primary $(nvram get wan_ifname) | awk '$1 == "inet" { print $2 }')"
	vpn_conns="$(cat /proc/net/ip_conntrack | \
			awk '
				BEGIN {FS=" +|="}
				$11 == "1600" && !/dst='"$wanaddr"'/ {
					if (erg !~ $7) erg=erg" "$7
				};
				END{print erg}'	)"

	for vpn_gw in $vpn_conns; do
		if [ -n "$(ip route show $vpn_gw | awk '$5 ~ "^tap" && /metric 1 /')" ]; then
			logger -t check_usergateway "cleaning /proc/net/ip_conntrack"
			# clean conntrack from registered connections to let them use the new settings
			echo 0 > /proc/sys/net/ipv4/netfilter/ip_conntrack_udp_timeout
			echo 0 > /proc/sys/net/ipv4/netfilter/ip_conntrack_udp_timeout_stream
			while [ -n "$(cat /proc/net/ip_conntrack | \
				awk '	BEGIN {FS=" +|="}
					$7 == "'$vpn_gw'" && $11 == "1600"  && !/dst='"$wanaddr"'/' )" ]; do
				$DEBUG && logger -t check_usergateway "waiting for registered connections to suspend"
				sleep 5;
			done
			echo 30 > /proc/sys/net/ipv4/netfilter/ip_conntrack_udp_timeout
			echo 180 > /proc/sys/net/ipv4/netfilter/ip_conntrack_udp_timeout_stream
			$DEBUG && logger -t check_usergateway "done. all connections updated"
		fi
	done	
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

if [ "$on_share_internet" = "on" ] && [ ! -e /var/run/openvpn.opennet_ugw.pid ]; then
	/etc/init.d/S80openvpn start opennet_ugw
fi

rm /tmp/lock/check_usergateway.sh
