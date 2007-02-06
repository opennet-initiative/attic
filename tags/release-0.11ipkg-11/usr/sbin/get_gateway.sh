#!/bin/sh

# WARNING: busybox-netcat has no timeout-option, so this script may wait really long

########################################################################
# getting the default gateway of any other node
########################################################################
# this is done by parsing the output of the statuspage and the status-routes page

rm -f /tmp/status

if [ -n "$1" ]; then target=$1;
else target=127.0.0.1; fi

vpn_gateway=

# systeminfo-seite holen
wget -q -O /tmp/status http://$target/cgi-bin-systeminfo.txt 2>/dev/null 
if [ $? = 0 ] && [ -f /tmp/status ]; then
	# firmware >= 0.10 installed
	vpn_gateway=$(awk '$1 == "on_gw" {print $2; exit}' /tmp/status)
fi

if [ -z "$vpn_gateway" ]; then
	# status-seite holen
	wget -q -O /tmp/status http://$target/cgi-bin-status.html 2>/dev/null
	if [ $? != 0 ] || ! [ -f /tmp/status ]; then
		# no route or target not existent.
		rm -rf /tmp/status; exit
	elif [ "$(awk '/00-00-00-00/ {print $1}' /tmp/status)" = "tun0" ]; then
		# ok, tunnel active
		### a hack to find a recent openvpn statement in syslog
		### there is a good chance to find any status message (maybe ping inactivity timeout) in logs
		vpn_gateway=$(awk '/openvpn/ && /:1600/ { for (i=3;i<=NF; i++) if($i ~ /1600/) {erg=$i};} END {gsub(":1600","",erg); print erg}' /tmp/status);
	fi
fi

# ermittel die route (den nächsten hop) zum entprechenden Gateway
page=$(nc $target 80 2>/dev/null <<-EOF
POST /cgi-bin-status.html HTTP/1.1
Content-type: application/x-www-form-urlencoded
Content-Length: 17

post_route=Routen

EOF
)

if [ -n "$page" ]; then
	if [ -z "$vpn_gateway" ]; then
		vpn_gateway="0.0.0.0";  # if no information is available, use default gateway for optimization
		next_hop=$(echo $page | awk 'BEGIN {RS="<TR>";FS="<|>"} $3 == "0.0.0.0" && /192.168/ {print $9; exit}')
		if [ -n "$next_hop" ]; then echo "default_gw $next_hop"; fi
	else
		
		next_hop=$(echo $page | awk -v gw="$vpn_gateway" 'BEGIN {RS="<TR>";FS="<|>"} $5 ~ gw {print $13; exit}')
		if [ -n "$next_hop" ]; then echo "openvpn_gw $next_hop"; fi
	fi
fi
rm -f /tmp/status
