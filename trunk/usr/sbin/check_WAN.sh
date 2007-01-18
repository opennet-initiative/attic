#!/bin/sh
# check if WAN-device is available and there is a default-route trough it. If so, activate policy-routing. If not, deactivate it.

DEBUG="false"	# Dump dropped packets to klog, show with "dmesg -c"
if [ -n "$(nvram get on_fw_debug)" ]; then DEBUG=$(nvram get on_fw_debug); fi

# if WANDEV is not activated, return immediately
WANDEV=$(nvram get wan_ifname)
if [ -z "$WANDEV" ]; then return; fi

# if WANDEV is part of WIFIDEV (WANOLSR), return immediately
WANBRD=$(ip addr show primary $WANDEV | awk '$1 == "inet" && $3 == "brd" { print $4; exit }')
WIFIDEV=$(nvram get wifi_ifname)
WIFIBRD=$(ip addr show primary $WIFIDEV | awk '$1 == "inet" && $3 == "brd" { print $4; exit }')
if [ "$WIFIBRD" = "$WANBRD" ]; then return; fi


# $1 enthält entweder 'add' oder 'del'
wan_policyroute() {
	if [ "$1" = "add" ]; then
		if [ -n "$table_4" ]; then
			if [ -n "$(ip route show table 4 | awk '$3 == "'$ip_remote'"')" ]; then
				return;
			else
				wan_policyroute del
			fi
		fi
		
		LANNET_PRE=$(get_NETPRE lan)
		WIFINET_PRE=$(get_NETPRE wifi)
		
		WANADDR=$(ip addr show primary $WANDEV | awk '$1 == "inet" { print $2 }')
		test $DEBUG && logger -t check_WAN "aktiviere policy-routing für WAN per table 4"
		ip route flush table 4 2>/dev/null
		
		ip rule add unicast from $WANADDR table 4
		
		if [ -n "$LANNET_PRE" ]; then ip route add throw $LANNET_PRE table 4; fi
		if [ -n "$WIFINET_PRE" ]; then ip route add throw $WIFINET_PRE table 4; fi
		ip route add default via $ip_remote table 4
	else
		test $DEBUG && logger -t check_WAN "entferne policy-routing für WAN per table 4"

		#dont use recent WANADDR, cause this might have changed by dhcp. Better search for the rule to delete.
		LANNET_PRE=$(get_NETPRE lan)
		WIFINET_PRE=$(get_NETPRE wifi)
		ADDR=$(ip rule show | awk '/lookup 4/ && $3 != "'$LANNET_PRE'" && $3 != "'$WIFINET_PRE'" {print $3}')
		
		ip rule del unicast from $ADDR table 4
		
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

# if there is no default route over the WAN-device deactivate policy-routing for WAN
ip_remote=$(route -n | awk '$8 == "'$WANDEV'"  && $1 == "0.0.0.0" { print $2; exit }')
table_4=$(ip route show table 4)

if [ -z "$ip_remote" ]; then
	if [ -n "$table_4" ]; then wan_policyroute del; fi
	return
fi

# check if target of WAN-default route could be reached. If so, activate policy routing. If not, deactivate it.
# one ping not ble to reach the target tales appr. 10 seconds, so dont increase the failure-counter to high
max_ping_failure=3
count=1
while [ $((count++)) -le $max_ping_failure ]; do
	if $(ping -c 1 $ip_remote >/dev/null 2>/dev/null); then
			$DEBUG && logger -t check_WAN "ok, target of WAN-default route ($ip_remote) could be reached."
			wan_policyroute add ;
			return
	fi
done;

if [ -n "$table_4" ]; then wan_policyroute del; fi
