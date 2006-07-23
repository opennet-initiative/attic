#!/bin/sh
# script to check, if nagare is reachable via WANDEV or if IP of nagare has changed
# if called with parameter "quick", only availablility of WANDEV and special routes are checked
# if WAN-device is active, policy-routing for WANDEV is activated

# the existing route table 5 indicates that it is possible to share your wan-connection
central_gateways="nagare.on-i.de"


DEBUG=true

# $1 enthält entweder 'add' oder 'del'
# $2 enthält die remote-adresse des WAN-Interfaces
# $3 enthält die IP-Zieladresse
usergateway_route()
{
	if [ "$1" = "add" ]; then
		test $DEBUG && logger -t check_usergateway "aktiviere policy-routing für usergateway $3 per table 5"
		ip route add $3 via $2 table 5
	else
		test $DEBUG && logger -t check_usergateway "entferne policy-routing für usergateway per table 5"
		if [ -z "$3" ]; then
			ip route flush table 5 2>/dev/null
		else
			ip route del $3 via $2 table 5
		fi
	fi
}

# $1 enthält entweder 'add' oder 'del'
# $2 enthält die remote-adresse des WAN-Interfaces
wan_route()
{
	if [ "$1" = "add" ]; then
		test $DEBUG && logger -t check_usergateway "aktiviere policy-routing für wan per table 4"
		ip route flush table 4 2>/dev/null
		lan_ipaddr=$(nvram get lan_ipaddr)
		if [ -n "$lan_ipaddr" ]; then LANNET_PRE=$(ipcalc $lan_ipaddr $(nvram get lan_netmask) | awk 'BEGIN{FS="="} { if ($1=="NETWORK") net=$2; if ($1="PREFIX") pre=$2;} END{print net"/"pre}'); fi
		wifi_ipaddr=$(nvram get wifi_ipaddr)
		if [ -n "$wifi_ipaddr" ]; then WIFINET_PRE=$(ipcalc $wifi_ipaddr $(nvram get wifi_netmask) | awk 'BEGIN{FS="="} { if ($1=="NETWORK") net=$2; if ($1="PREFIX") pre=$2;} END{print net"/"pre}'); fi
		
		if [ -n "$lan_ipaddr" ]; then ip route add throw $LANNET_PRE table 4; fi
		if [ -n "$wifi_ipaddr" ]; then ip route add throw $WIFINET_PRE table 4; fi
		ip route add default via $2 table 4
	else
		test $DEBUG && logger -t check_usergateway "entferne policy-routing für wan per table 4"
		ip route flush table 4 2>/dev/null
	fi
}


# if internet-sharing is temporary blocked, counter will be decreased every minute.
on_share_internet_blocked=$(nvram get on_share_internet_blocked)
if [ "$1" = "quick" ] && [ -n "$on_share_internet_blocked" ]; then
	nvram set on_share_internet_blocked=$(($on_share_internet_blocked-1))
	# if counter reaches zero, ugw is (re)activated
	if [ "$on_share_internet_blocked" = "0" ]; then
		nvram unset on_share_internet_blocked
		nvram set on_share_internet="on"
		nvram commit
		/etc/init.d/S80openvpn start opennet_ugw
	fi
fi

# prüfe ob WANDEV Teil des WIFI-Netzes ist. Wenn ja, dann sofort abbrechen
if [ "$(ipcalc $(nvram get wan_ipaddr) $(nvram get wan_netmask)|grep "NETWORK")" = "$(ipcalc $(nvram get wifi_ipaddr) $(nvram get wifi_netmask)|grep "NETWORK")" ]; then
	test $DEBUG && logger -t check_usergateway "WANNET Teil von WIFINET"
	/etc/init.d/S80openvpn stop opennet_ugw
	wan_route del
	usergateway_route del
	return
fi	

# check if there is a default route over the WAN-device, if so, activate policy-routing for WAN
WANDEV=$(nvram get wan_ifname)
ip_remote=$(route -n | awk '$8 == "'$WANDEV'"  && $1 == "0.0.0.0" { print $2; exit }')
table_5=$(ip route show table 5)

if [ -z "$WANDEV" ] || [ -z "$ip_remote" ]; then
	# keine default-route gefunden, entferne policy-routing und stoppe tunnel
	# AcHTUNG: wenn nicht per hand, wird der tunnel zu nagare (table 5) erst wieder durch cron-hourly gestartet
	test $DEBUG && logger -t check_usergateway "WAN-default route fehlt, stoppe opennet_usergateway tunnel (wenn gestartet)"
	/etc/init.d/S80openvpn stop opennet_ugw
	wan_route del
	usergateway_route del
	return
elif [ -z "$table_5" ]; then
	logger -t check_usergateway "table 5 ist nicht vorhanden, prüfe ob tunnel aktiv ist und stoppe den"
	if [ -e /var/run/openvpn.opennet_ugw.pid ]; then
		test $DEBUG && logger -t check_usergateway "stopping opennet_usergateway tunnel (route table 5 empty)"
		/etc/init.d/S80openvpn stop opennet_ugw >/dev/null
	fi
fi

table_4=$(ip route show table 4)
# default route über WAN ist vorhanden, nun prüfe, ob WAN-Gegenstelle erreicht werden kann.
if $(ping -c 1 $ip_remote >/dev/null 2>/dev/null); then
	test $DEBUG && logger -t check_usergateway "ok, WAN-Gegenstelle $ip_remote kann extern erreicht werden"
	if [ -z "$table_4" ]; then wan_route add $ip_remote; fi
else
	test $DEBUG && logger -t check_usergateway "no, WAN-Gegenstelle $ip_remote kann nicht extern erreicht werden"
	/etc/init.d/S80openvpn stop opennet_ugw
	wan_route del
	usergateway_route del
	return
fi

if [ "$1" = "quick" ]; then return; fi

# WAN-Gegenstelle kann erreicht werden, nun prüfe, ob Usergateway(s) erreicht werden können
# dies wird nur jede Stunde durchgeführt, da aufgrund der Namensauflösung etwas mehr Zeit benötigt wird
# wenn das erfolgreich ist, wird der tunnel gestartet
##### ACHTUNG: Aktuell wird bei einer Änderung der IP des Gateways die Liste nur ergänzt, nicht gelöscht.
gws_table_5=$(ip route show table 5| awk '{print $1}')

for central_gw in $central_gateways; do
	# besorge die IP-addresse von nagare
	central_gw_ip=$(nslookup $central_gw 2>/dev/null | tail -n 1 | awk '{ print $2 }')
	#old way to get IP using ping
	#central_gw_ip=$(ping -c 1 $central_gw 2>/dev/null | grep PING);
	#central_gw_ip=${central_gw_ip#*\(};
	#central_gw_ip=${central_gw_ip%%\)*};
	if [ -n "$central_gw_ip" ]; then
		if [ -z "$(echo $gws_table_5 | grep $central_gw_ip)" ]; then
			# route noch nicht vorhanden
			usergateway_route add $ip_remote $central_gw_ip
		fi
		# prüfe ob gateway über wan erreicht werden kann
		if $(ping -c 1 $central_gw_ip >/dev/null 2>/dev/null); then
			test $DEBUG && logger -t check_usergateway "ok, $central_gw kann extern erreicht werden"
			# start opennet_ugw tunnel (only if inet-sharing is not blocked)
			if [ -z "$(nvram get on_share_internet_blocked)" ]; then
				/etc/init.d/S80openvpn start opennet_ugw
			fi
		else
			test $DEBUG && logger -t check_usergateway "no, nagare kann nicht extern erreicht werden"
			/etc/init.d/S80openvpn stop opennet_ugw
			usergateway_route del $ip_remote $central_gw_ip
		fi
	else
		test $DEBUG && logger -t check_usergateway "no, konnte IP-adresse von $central_gw nicht ermitteln"
	fi
done
