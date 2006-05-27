#!/bin/sh
# scritp to check, if nagare is reachable via WANDEV or if IP of nagare has changed
# if called with parameter "quick", only availablility of WANDEV and special routes are checked

DEBUG=true

table_5=$(ip route show table 5)
if [ "$1" = "quick" ] && [ -z "$table_5" ] && ! [ -e /var/run/openvpn.dsl.pid ]; then return; fi

eval $(netparam)

ip_remote=$(route -n | awk '$8 == "'$WANDEV'"  && $1 == "0.0.0.0" { print $2; exit }')

if [ -z "$WANDEV" ] || [ -z "$ip_remote" ] || [ -z "$table_5" ]; then
	# es gibt kein WANDEV mehr, keine default route über WANDEV oder keine spezifische Route zu nagare
	test $DEBUG && logger -t check_nagare "stoppe opennet_dsl tunnel (wenn gestartet)"
	/etc/init.d/S80openvpn stop opennet_dsl
	ip route flush table 5 2>/dev/null
fi	

if [ "$1" = "quick" ] || [ -z "$WANDEV" ] || [ -z "$ip_remote" ]; then return; fi

nagare_old_ip=$(echo $table_5 | cut -d' ' -f1)
old_ip_remote=$(echo $table_5 | cut -d' ' -f3)

nagare_ip=$(ping -c 1 nagare.on-i.de 2>/dev/null | grep PING);
nagare_ip=${nagare_ip#*\(};
nagare_ip=${nagare_ip%%\)*};
if [ -z "$nagare_ip" ]; then return; fi # veraendere nix, vielleicht nur vorübergehend nicht erreichbar

if [ -n "$nagare_old_ip" ] && [ "$nagare_ip" != "$nagare_old_ip" ]; then
	test $DEBUG && logger -t check_nagare "route vorhanden, ip von nagare hat sich geändert"
	# route  vorhanden, ip von nagare hat sich geändert
	ip route flush table 5
	ip route add $nagare_ip via $ip_remote table 5
	
	# restart opennet_dsl tunnel
	/etc/init.d/S80openvpn restart opennet_dsl
fi

if [ "$ip_remote" != "$old_ip_remote" ]; then
	test $DEBUG && logger -t check_nagare "route noch nicht vorhanden oder ziel-IP von WANDEV hat sich geändert"
	# route noch nicht vorhanden oder ziel-IP von WANDEV hat sich geändert
	
	# check if WANADR is part of WIFINET
	if [ "$(ipcalc $WANADR $WIFIMSK|grep "NETWORK")" = "$(ipcalc $WIFIADR $WIFIMSK|grep "NETWORK")" ]; then
		test $DEBUG && logger -t check_nagare "WANNET Teil von WIFINET"
		/etc/init.d/S80openvpn stop opennet_dsl
		ip route flush table 5 2>/dev/null
	else
		ip route flush table 5 2>/dev/null
		ip route add $nagare_ip via $ip_remote table 5
	
		# check if nagare could still be reached
		if $(ping -c 1 $nagare_ip >/dev/null 2>/dev/null); then
			test $DEBUG && logger -t check_nagare "ok, nagare kann extern erreicht werden"
			# (re)start opennet_dsl tunnel
			/etc/init.d/S80openvpn restart opennet_dsl
		else
			test $DEBUG && logger -t check_nagare "no, nagare kann nicht extern erreicht werden"
			/etc/init.d/S80openvpn stop opennet_dsl
			ip route flush table 5
		fi
	fi
fi
