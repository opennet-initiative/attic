#!/bin/sh
LC_ALL=de_DE

DEST='/var/www/on_webstat/gateway_status.html'
OUT='/var/www/on_webstat/gateway_status.html.tmp'
IMG_OKAY='<img src="opennet-gwstatus-okay.png">'
IMG_FAILED='<img src="opennet-gwstatus-failed.png">'

echo "<HTML><HEAD><TITLE>Gateway-Status izumi.on</TITLE><LINK HREF="opennet.css" REL="StyleSheet" TYPE="text/css" /></HEAD><BODY><h1>Gateway-Status <i>izumi.on</i></h1>" > $OUT

echo "<h2>CPU / Ram</h2><p>&nbsp;Load Average: " >> $OUT
cat /proc/loadavg >> $OUT
echo "&middot;" >> $OUT
cat /proc/meminfo | grep MemFree >> $OUT
echo "</p>" >> $OUT

echo "<h2>Uptime</h2>" >> $OUT
echo "<table>" >> $OUT
/usr/lib/cgi-bin/uprecords.cgi |fgrep -v "Content-type" |fgrep -v "uptimed"|fgrep -v "<table border=1>" >> $OUT

echo "<h2>Dienste</h2><table><tr><th>Dienst</th><th>&nbsp;Status&nbsp;</th><th>Details</th><th>Aufgabe</th></tr>" >> $OUT

echo "<tr class=\"odd\"><td>postgresql</td><td>" >> $OUT
ps -C postmaster >/dev/null && pg_lsclusters -h | grep online > /dev/null && {
	echo $IMG_OKAY >> $OUT
} || {
	echo $IMG_FAILED >> $OUT
}
echo "</td><td></td><td>Datenbank</td></tr>" >> $OUT

echo "<tr class=\"even\"><td>apache2</td><td>" >> $OUT
ps -C apache2 >/dev/null && /usr/sbin/apache2ctl status | grep "Alert!" > /dev/null && {
	echo $IMG_FAILED >> $OUT
} || {
	echo $IMG_OKAY >> $OUT
}
echo "</td><td><a href=\"/server-status\">Server-Status</a></td><td>Webserver</td></tr>" >> $OUT

echo "<tr class=\"odd\"><td>uptimed</td><td>" >> $OUT
ps -C uptimed > /dev/null && {
        echo $IMG_OKAY >> $OUT
} || {
        echo $IMG_FAILED >> $OUT
}
echo "</td><td></td><td>Uptime Statistik</td></tr>" >> $OUT

echo "<tr class=\"even\"><td>bind</td><td>" >> $OUT
ps -C named >/dev/null && sudo /usr/sbin/rndc status >/dev/null && {
        echo $IMG_OKAY >> $OUT
} || {
        echo $IMG_FAILED >> $OUT
}
echo "</td><td></td><td>Nameserver</td></tr>" >> $OUT

echo "<tr class=\"odd\"><td>olsrd</td><td>" >> $OUT
ps -C olsrd >/dev/null && /usr/bin/wget --delete-after -q http://localhost:8080/ > /dev/null && {
        echo $IMG_OKAY >> $OUT
} || {
        echo $IMG_FAILED >> $OUT
}
echo "</td><td><a href=\"olsr_status.html\">Routen</a></td><td>Routing</td></tr>" >> $OUT

echo "<tr class=\"even\"><td>pppd</td><td>" >> $OUT
ps -C pppd >/dev/null && cat /proc/net/dev | grep ppp0 >/dev/null && {
        echo $IMG_OKAY >> $OUT
} || {
        echo $IMG_FAILED >> $OUT
}
echo "</td><td></td><td>DSL-Zugang</td></tr>" >> $OUT

echo "<tr class=\"odd\"><td>ntpd</td><td>" >> $OUT
ps -C ntpd >/dev/null && /usr/bin/ntptrace 2>/dev/null | grep "sync" >/dev/null && {
        echo $IMG_OKAY >> $OUT
} || {
        echo $IMG_FAILED >> $OUT
}
echo "</td><td></td><td>Timeserver</td></tr>" >> $OUT

echo "<tr class=\"even\"><td>openvpn gws</td><td>" >> $OUT
ps -f -C openvpn | grep opennet_gateways >/dev/null && cat /proc/net/dev | grep tap_gs >/dev/null && {
        echo $IMG_OKAY >> $OUT
} || {
        echo $IMG_FAILED >> $OUT
}
echo "</td><td><a href="vpn_gateways.html">Verbindungen</a></td><td>VPN Gateways</td></tr>" >> $OUT

echo "<tr class=\"odd\"><td>openvpn users</td><td>" >> $OUT
ps -f -C openvpn | grep opennet_users >/dev/null && cat /proc/net/dev | grep tun0 >/dev/null && {
        echo $IMG_OKAY >> $OUT
} || {
        echo $IMG_FAILED >> $OUT
}
echo "</td><td><a href="vpn_users.html">Verbindungen</a></td><td>VPN Mitglieder</td></tr>" >> $OUT

echo "<tr class=\"even\"><td>teucrium</td><td>" >> $OUT
ps -f -C python | fgrep teucrium_init.py >/dev/null && {
        echo $IMG_OKAY >> $OUT
} || {
        echo $IMG_FAILED >> $OUT
}
echo "</td><td><a href="traffic_graph.html">Graphen</a></td><td>Traffic Graphen</td></tr>" >> $OUT

echo "<tr class=\"odd\"><td>sshd</td><td>" >> $OUT
ps -C sshd >/dev/null && {
        echo $IMG_OKAY >> $OUT
} || {
        echo $IMG_FAILED >> $OUT
}
echo "</td><td></td><td>SSH Zugang</td></tr>" >> $OUT

echo "<tr class=\"even\"><td>postfix</td><td>" >> $OUT
ps -C master >/dev/null && {
        echo $IMG_OKAY >> $OUT
} || {
        echo $IMG_FAILED >> $OUT
}
echo "</td><td></td><td>Mail Transfer</td></tr>" >> $OUT

echo "<tr class=\"odd\"><td>vnstat</td><td>" >> $OUT
ts_now=$(date +%s) 
ts_dir=$(date --reference=/var/lib/vnstat/eth0 +%s) 
age=$((ts_now - ts_dir)) # in seconds 
if [ $age -gt 300  ]
	then echo $IMG_FAILED >> $OUT
	else echo $IMG_OKAY >> $OUT
fi
echo "</td><td><a href="traffic_status.html">Auswertung</a></td><td>Traffic Summen</td></tr>" >> $OUT

echo "<tr class=\"odd\"><td>firmware-stat</td><td>" >> $OUT
echo "</td><td><a href="firmware_status.html">Auswertung</a></td><td>FW-Update Status</td></tr>" >> $OUT


echo "</table>" >> $OUT

echo "<p>" >>$OUT
echo "Zuletzt aktualisiert: " >> $OUT
date >> $OUT
echo "</p>" >> $OUT

echo "</BODY></HTML>" >> $OUT

mv $OUT $DEST
