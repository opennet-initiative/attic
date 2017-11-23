#!/bin/sh
LC_ALL=de_DE

OUT='/var/www/on_webstat/traffic_status.html'

echo "<HTML><HEAD><TITLE>Traffic-Status izumi.on</TITLE><LINK HREF="opennet.css" REL="StyleSheet" TYPE="text/css" /></HEAD><BODY><h1>Traffic-Status <i>izumi.on</i></h1><p>" > $OUT

echo "<h2>Letzte 24h</h2><pre>" >> $OUT 
/usr/bin/vnstat -s -h | tail -n9 >> $OUT
echo "</pre>" >> $OUT 

echo "<h2>Letzter Monat</h2><pre>" >> $OUT 
echo "            Tag         RX      |     TX      |    Summe" >> $OUT
/usr/bin/vnstat -s -d |grep -F " "|grep -F -v "estimated" |grep -F -v "day" >> $OUT
echo "</pre>" >> $OUT 

echo "<h2>Wochenvergleich</h2><pre>" >> $OUT 
echo "                            RX      |       TX      |    Summe" >> $OUT
/usr/bin/vnstat -s -w |grep -F " "|grep -F -v "estimated" |grep -F -v "total" >> $OUT
echo "</pre>" >> $OUT 

echo "<h2>Monatsvergleich</h2><pre>" >> $OUT 
echo "                        RX      |       TX      |    Summe" >> $OUT
/usr/bin/vnstat -s -m |grep -F " "|grep -F -v "estimated" |grep -F -v "total" >> $OUT
echo "</pre>" >> $OUT 

echo "<h2>Top-10</h2><pre>" >> $OUT 
echo "                  Tag           RX      |     TX      |    Summe" >> $OUT
/usr/bin/vnstat -s -t |grep -F " "|grep -F -v "eth"|grep -F -v "total" >> $OUT
echo "</pre>" >> $OUT 

echo "<p>" >>$OUT
echo "Zuletzt aktualisiert: " >> $OUT
date >> $OUT
echo "</p>" >> $OUT

echo "</BODY></HTML>" >> $OUT
