#!/bin/sh
# script to check, if usergateway is reachable via WANDEV
# if it is reachable via WANDEV, a special routing rule is added in table 5
# if there are user-vpn-connections to the central gateway trough the usergateway-tunnel,
# they will be routed around to prevent tunnel-in-tunnel traffic.
# fianlly decrement the internet_sharing-blocking-counter every minute.
. /usr/sbin/helper_functions.sh

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

ugw_update_snat () {
	WIFINET_PRE=$(get_NETPRE wifi)
	
	# remove old rule
	RULENUM=$(iptables -L POSTROUTING -t nat --line-numbers -n | awk 'BEGIN{FS=" +|:"} $5 == "'$WIFINET_PRE'" && /dpt:1600/ {print $1; exit}')
	[ -n "$RULENUM" ] && iptables -D POSTROUTING $RULENUM -t nat
	
	iptables -t nat -A POSTROUTING -o $(nvram get wan_ifname) -s $WIFINET_PRE -d $on_ugw_ip -p udp --dport 1600 -j SNAT --to-source $wanaddr
}

ugw_update_dnat () {
	# remove old rule
	RULENUM=$(iptables -L PREROUTING -t nat --line-numbers -n | awk '/192.168.0.251/ && /dpt:1600/ {print $1; exit}')
	[ -n "$RULENUM" ] && iptables -D PREROUTING $RULENUM -t nat

	iptables -t nat -A PREROUTING -d 192.168.0.251 -p udp --dport 1600 -j DNAT --to-destination $on_ugw_ip
}

table_4_default_route=$(ip route show table 4 | awk '$1 == "default" {print $3}')
on_ugw=$(nvram get on_ugw)
on_ugw_ip=$(nslookup $on_ugw 2>/dev/null | tail -n 1 | awk '{ print $2 }')
wanaddr="$(ip addr show primary $(nvram get wan_ifname) | awk 'BEGIN{FS=" +|/"} $2 == "inet" { print $3 }')"

if [ -n "$table_4_default_route" ]; then
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

# check if current usergateway-ip has an DNAT-rule in PREROUTING (might got lost if IP of usergateway has changed)
if [ -n "$on_ugw_ip" ] && \
	[ "$(iptables -L PREROUTING -t nat -n | awk 'BEGIN{FS=" +|:"} /192.168.0.251/ && /dpt:1600/ {print $10; exit}')" != "$on_ugw_ip" ]; then
	$DEBUG && logger -t check_usergateway "aktualisiere DNAT für usergateway"
	ugw_update_dnat
fi

# check if current usergateway-ip has an SNAT-rule in POSTROUTING (might got lost if IP of WANDEVICE has changed)
if [ -n "$on_ugw_ip" ] && \
	[ "$(iptables -L POSTROUTING -t nat --line-numbers -n | awk 'BEGIN{FS=" +|:"} $6 == "'$on_ugw_ip'" && /dpt:1600/ {print $11; exit}')" != "$wanaddr" ]; then
	$DEBUG && logger -t check_usergateway "aktualisiere SNAT für usergateway"
	ugw_update_snat
fi

# check if there are any connections trough a usergateway-tunnel which are double-tunneld
if [ "$1" != "checkonly" ] && [ -n "$(ip route show table 5)" ]; then
	wanaddr="$(ip addr show primary $(nvram get wan_ifname) | awk 'BEGIN{FS=" +|/"} $2 == "inet" { print $3 }')"
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
