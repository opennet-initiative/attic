#!/bin/sh

# helper functions
startswith() { local str="$1"; local substr="$2";
	[ -n "$str" -a -z "${str##$substr*}" ] && echo 1 || echo 0; }


lan_addr="$(ifconfig $(nvram get lan_ifname) 2>/dev/null| awk 'BEGIN{FS=" +|:"} $2 == "inet" {print $4; exit}')"

if [ -n "$(grep $(nvram get lan_ifname) /var/etc/olsrd.conf)" ]; then
	warn="<b>ACHTUNG:</b> LAN ist mit IP $lan_addr Teil des Opennet. OLSR auf LAN aktiviert."

elif [ -n "$lan_addr" ] && [ $(startswith "$lan_addr" "172.16.0") = 0 ]; then
	warn="<b>ACHTUNG:</b> Dein AccessPoint hat im LAN die Adresse $lan_addr. Zukünftige Firmware-Versionen werden den für LAN verfügbaren Adressbereich einschränken. Achte genau auf die Ausgaben bei Firmware-Aktualisierungen oder versuche bereits jetzt die Adresse ins Netz 172.16.0.X (Netzmaske 255.255.255.0) zu legen, also bspw. 172.16.0.1."

else
	lan_addrs="$(cat /proc/net/arp | awk '$6 == "'$(nvram get lan_ifname)'" {print $1}')"

	for addr in $lan_addrs; do
		# check if address was recieved via dhcp
		[ -n "$(grep $addr /var/run/dhcp.leases)" ] && continue
		if [ $(startswith "$addr" "172.16.0") = 0 ]; then
			warn="<b>ACHTUNG:</b> In Deinem LAN existiert(e) die Adresse $addr. Zukünftige Firmware-Versionen werden den für LAN verfügbaren Adressbereich einschränken. Achte genau auf die Ausgaben bei Firmware-Aktualisierungen oder versuche bereits jetzt diese Adresse ins Netz 172.16.0.X (Netzmaske 255.255.255.0) zu verlegen."
			break;
		fi
	done
fi

[ -n "$warn" ] && echo $warn >/tmp/lan_warning