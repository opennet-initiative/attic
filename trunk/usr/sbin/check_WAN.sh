#!/bin/sh
# check if WAN-device is available and there is a default-route trough it. If so, activate policy-routing. If not, deactivate it.

DEBUG="false"	# Dump dropped packets to klog, show with "dmesg -c"
if [ -n "$(nvram get on_fw_debug)" ]; then DEBUG=$(nvram get on_fw_debug); fi

# $1 enthält entweder 'add' oder 'del'
wan_policyroute() {
	if [ "$1" = "add" ]; then
		# check if route is still there
		[ "$table_4_default_route" = "$wan_default_route" ] && return
		
		$DEBUG && logger -t check_WAN "aktiviere policy-routing für WAN per table 4"
		
		LANNET_PRE=$(get_NETPRE lan)
		WIFINET_PRE=$(get_NETPRE wifi)
		TAPADDR_NET="$(ifconfig tap0 2>/dev/null| awk 'BEGIN{FS=" +|:"} $2 == "inet" {print $4" " $8; exit}')"
		[ -n "$TAPADDR_NET" ] && TAPNET_PRE="$(ipcalc $TAPADDR_NET | awk 'BEGIN{FS="="} { if ($1=="NETWORK") net=$2; if ($1="PREFIX") pre=$2;} END{print net"/"pre}')"
		
		ip route flush table 4 2>/dev/null
		
		[ -n "$TAPNET_PRE" ] && ip route add throw $TAPNET_PRE table 4
		[ -n "$LANNET_PRE" ] && ip route add throw $LANNET_PRE table 4
		[ -n "$WIFINET_PRE" ] && ip route add throw $WIFINET_PRE table 4
		ip route add default via $wan_default_route dev $WANDEV table 4
	else
		$DEBUG && logger -t check_WAN "entferne policy-routing für WAN per table 4"
		ip route flush table 4 2>/dev/null
	fi
}

get_NETPRE() {
	dev_ipaddr=$(nvram get $1"_ipaddr")
	dev_netmask=$(nvram get $1"_netmask")
	
	if [ -n "$dev_ipaddr" ]; then
		ipcalc $dev_ipaddr $dev_netmask | awk 'BEGIN{FS="="} { if ($1=="NETWORK") net=$2; if ($1="PREFIX") pre=$2;} END{print net"/"pre}'
	fi
}


# if WANDEV is not activated, return immediately
WANDEV=$(nvram get wan_ifname)
if [ -z "$WANDEV" ]; then return; fi

# if WANDEV is part of WIFIDEV (WANOLSR), return immediately
WANBRD=$(ip addr show primary $WANDEV | awk '$1 == "inet" && $3 == "brd" { print $4; exit }')
WIFIDEV=$(nvram get wifi_ifname)
WIFIBRD=$(ip addr show primary $WIFIDEV | awk '$1 == "inet" && $3 == "brd" { print $4; exit }')
if [ "$WIFIBRD" = "$WANBRD" ]; then return; fi

# if interface have died recently, remove temporarily stored wan_default_route
if [ -z "$(ip addr | grep $WANDEV)" ]; then
	rm -r /tmp/wan_default_route
fi

# if there is a default route over the WAN-device remove this default route and store it in /tmp/wan_default_route
# this route must be removed cause it's no real default route for routing in the OLSR/WIFI network.
# if there is no default route found, see if we stored one before
wan_default_route="$(route -n | awk '$8 == "'$WANDEV'"  && $1 == "0.0.0.0" { print $2; exit }')"
if [ -n "$wan_default_route" ]; then
	echo $wan_default_route >/tmp/wan_default_route
	ip route del default via $wan_default_route
	$DEBUG && logger -t check_WAN "removed default-route trough WAN from default routing table"
else
	wan_default_route=$(cat /tmp/wan_default_route)
fi

table_4_default_route=$(ip route show table 4 | awk '$1 == "default" {print $3}')

# if there is no default route over the WAN-device available deactivate policy-routing for WAN
if [ -z "$wan_default_route" ]; then
	if [ -n "$table_4_default_route" ]; then wan_policyroute del; fi
	return
fi

# check if target of WAN-default route could be reached. If so, activate policy routing. If not, deactivate it.
# one ping not able to reach the target takes appr. 10 seconds, so dont increase the failure-counter to high
max_ping_failure=3
count=1
while [ $((count++)) -le $max_ping_failure ]; do
	if $(ping -c 1 $wan_default_route >/dev/null 2>/dev/null); then
			$DEBUG && logger -t check_WAN "ok, target of WAN-default route ($wan_default_route) could be reached."
			wan_policyroute add ;
			return
	fi
done;

# this is only reached if above pings didn't succeeded
if [ -n "$table_4" ]; then wan_policyroute del; fi
