#!/bin/sh
LC_ALL=de_DE

OUT='/var/www/on_webstat/traffic_graph.html'

echo "<HTML><HEAD><TITLE>Traffic-Graphen izumi.on</TITLE><LINK HREF="opennet.css" REL="StyleSheet" TYPE="text/css" /></HEAD><BODY><h1>Traffic-Graphen <i>izumi.on</i></h1><p>" > $OUT

echo "<h2>Aktuell</h2><img src="traffic_status/izumi_traffic__1h_ppp+.png"><h2>Letzte 24h</h2><img src="traffic_status/izumi_traffic__1d_ppp+.png"><h2>Letzte Woche</h2><img src="traffic_status/izumi_traffic__7d_ppp+.png"><h2>Letzter Monat</h2><img src="traffic_status/izumi_traffic__30d_ppp+.png"><h2>Letztes Jahr</h2><img src="traffic_status/izumi_traffic__365d_ppp+.png">" >> $OUT

echo "<p>" >>$OUT
echo "Zuletzt aktualisiert: " >> $OUT
date --reference=/var/www/traffic_status/izumi_traffic__1h_ppp+.png >> $OUT
echo "</p>" >> $OUT

echo "</BODY></HTML>" >> $OUT
