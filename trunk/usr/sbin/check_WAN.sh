#!/bin/sh
# check if WAN-device is available and there is a default-route trough it. If so, activate policy-routing. If not, deactivate it.
. /usr/sbin/helper_functions.sh

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
		TAPNET_PRE=$(get_NETPRE_dev tap0)
		# if TAP not available set rule to the predefined value to enable routing from Usergateways.
		[ -z "$TAPNET_PRE" ] && TAPNET_PRE="10.2.0.0/16"

		ip route flush table 4 2>/dev/null
		
		ip route add throw $TAPNET_PRE table 4
		[ -n "$LANNET_PRE" ] && ip route add throw $LANNET_PRE table 4
		[ -n "$WIFINET_PRE" ] && ip route add throw $WIFINET_PRE table 4
		ip route add throw $WANNET_PRE table 4
		ip route add default via $wan_default_route dev $WANDEV table 4
	else
		$DEBUG && logger -t check_WAN "entferne policy-routing für WAN per table 4"
		ip route flush table 4 2>/dev/null
	fi
}


# if WANDEV is not activated, return immediately
WANDEV=$(nvram get wan_ifname)
if [ -z "$WANDEV" ]; then return; fi


# if olsrd is running on WAN return immediately
if [ -n "$(grep $WANDEV /var/etc/olsrd.conf)" ]; then return; fi

# if interface have died recently, remove temporarily stored wan_default_route
if [ -z "$(ip addr | grep $WANDEV)" ]; then
	rm -r /tmp/wan_default_route
fi

# add/update rules to exclude WAN-traffic from user and usergateway-tunnel traffic
WANNET_PRE=$(get_NETPRE wan)
old_wannet_pre=$(cat /tmp/wan_net_pre 2>/dev/null)
if [ "$WANNET_PRE" != "$old_wannet_pre" ]; then
	# check if wan_ipaddr was set by dhcp and is part of any restricted networks
	wan_proto="$(nvram get wan_proto)"
	wan_ipaddr=$(ifconfig $(nvram get wan_ifname) 2>/dev/null| awk 'BEGIN{FS=" +|:"} $2 == "inet" {print $4; exit}')
	if [ "$wan_proto" = "dhcp" ] || "$wan_proto" = "pppoe" ]; then
		rm -f /tmp/wan_error; rm -f /tmp/wan_warning;
		wan_netmask=$(ifconfig $(nvram get wan_ifname) 2>/dev/null| awk 'BEGIN{FS=" +|:"} $2 == "inet" {print $8; exit}')
		
		same_NET_addr_mask() {
			dev1_net="$(ipcalc $1 $2 | grep NETWORK=)"
			dev1_net2="$(ipcalc $1 $4 | grep NETWORK=)"
			dev2_net="$(ipcalc $3 $4 | grep NETWORK=)"
			dev2_net1="$(ipcalc $3 $2 | grep NETWORK=)"
			
			[ "$dev1_net" = "$dev2_net1" ] && echo $dev1_net
			[ "$dev2_net" = "$dev1_net2" ] && echo $dev2_net
		}
		
		check_net() {
			if [ -n "$(same_NET_addr_mask $wan_ipaddr $wan_netmask $1 $2)" ]; then
				echo "Das WAN-device hat per DHCP (automatischer Adressvergabe) eine Adresse ($wan_ipaddr/$wan_netmask) erhalten, die in einem im Opennet für andere Zwecke reservierten Bereich ($1/$2) liegt."
			fi
		}
		
		err=$(check_net 192.168.0.0 255.255.0.0)
		[ -z "$err" ] && err=$(check_net 10.2.0.0 255.255.0.0)
		[ -z "$err" ] && err=$(check_net 10.1.0.0 255.255.0.0)
		[ -z "$err" ] && warn=$(check_net 10.0.0.0 255.0.0.0)
		
		if [ -n "$err" ]; then
			nvram set wan_proto=disabled
			nvram commit
			ifdown wan
			echo "<b>FEHLER:</b> "$err" Das WAN-device wurde daraufhin deaktiviert." >/tmp/wan_error
			return;
		elif [ -n "$warn" ]; then
			echo "<b>ACHTUNG:</b> "$warn" Dieser Bereich wird allerdings im Moment (Jan. 07) noch nicht genutzt, dennoch kann dies in Zukunft Probleme verursachen." >/tmp/wan_warning
		fi
	fi

	WIFIDEV=$(nvram get wifi_ifname)
	WIFINET_PRE=$(get_NETPRE wifi)
	wifi_ipaddr=$(ifconfig $WIFIDEV 2>/dev/null| awk 'BEGIN{FS=" +|:"} $2 == "inet" {print $4; exit}')

	# remove old firewall rules
	get_rulenum_1() {
		iptables -L FORWARD --line-numbers -n -v | awk '$7 == "'"$WANDEV"'" && $8 == "'"$WIFIDEV"'" && $12 == "state NEW" {print $1; exit}'
	}
	while $(iptables -D OUTPUT $(get_rulenum_1) 2>/dev/null); do : ; done
	get_rulenum_2() {
		iptables -t nat -L POSTROUTING --line-numbers -n -v | awk '$4 == "SNAT" && $8 == "'"$WIFIDEV"'" {print $1; exit}'
	}
	while $(iptables -D OUTPUT $(get_rulenum_2) 2>/dev/null); do : ; done
	
	# check if WAN-IP-address is part of private IP-ranges. If so, allow access to Opennet.
	if [ "$(ipcalc $wan_ipaddr 255.240.0.0 | grep NETWORK=)" = "NETWORK=172.16.0.0" ] ||
	   [ "$(ipcalc $wan_ipaddr 255.0.0.0 | grep NETWORK=)" = "NETWORK=10.0.0.0" ]; then
		$DEBUG && logger -t check_WAN "WAN network is a local network"
		iptables -I FORWARD 2 -i $WANDEV -o $WIFIDEV -s $WANNET_PRE -d $WIFINET_PRE -m state --state NEW -j ACCEPT
		iptables -t nat -A POSTROUTING -o $WIFIDEV -s $WANNET_PRE -d $WIFINET_PRE -j SNAT --to-source $wifi_ipaddr
		$DEBUG && logger -t check_WAN "opened firewall for WAN-Opennet access"
	fi

	ip route del throw $old_wannet_pre table 3 2>/dev/null
	ip route add throw $WANNET_PRE table 3
	ip route del throw $old_wannet_pre table 4 2>/dev/null
	ip route add throw $WANNET_PRE table 4
	echo $WANNET_PRE >/tmp/wan_net_pre
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
	wan_default_route=$(cat /tmp/wan_default_route 2>/dev/null)
fi

table_4_default_route=$(ip route show table 4 | awk '$1 == "default" {print $3}')

# if there is no default route over the WAN-device available deactivate policy-routing for WAN
if [ -z "$wan_default_route" ]; then
	if [ -n "$table_4_default_route" ]; then wan_policyroute del; fi
	return
fi

# check if target of WAN-default route could be reached. If so, activate policy routing. If not, deactivate it.
# one ping not able to reach the target takes appr. 10 seconds, so dont increase the failure-counter to high
# this is a feature for people who might use the opennet-usertunnel as a backup connection.
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
