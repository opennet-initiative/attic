#!/bin/sh
LC_ALL=de_DE

IN='/tmp/olsr_status.html'
OUT='/var/www/on_webstat/olsr_status.html'

wget -q -O - http://127.0.0.1:8080/all > $IN

echo "<HTML><HEAD><TITLE>OLSR-Status izumi.on</TITLE><LINK HREF="opennet.css" REL="StyleSheet" TYPE="text/css" /></HEAD><BODY><h1>OLSR-Status <i>izumi.on</i></h1><p>" > $OUT
cat $IN | awk '/uptime/, /<br>/ {
gsub("Olsrd uptime", "Uptime")
gsub("day\(s\)", "Tage")
gsub("hours", "Stunden")
gsub("minutes", "Minuten")
gsub("<i>", "")
gsub("<\/i>", "")
gsub("<br>", "")
print $1 " " $2 " " $3 " " $4 " " $5 ","
}' >> $OUT
echo "Zuletzt aktualisiert: " >> $OUT
date >> $OUT
echo "<br>Version: " >> $OUT
/usr/sbin/olsrd --help 2>/dev/null|awk '/-/, /http/ { 
gsub("- ", "")
gsub("\*\*\*", "") 
gsub("Build date:", "- gebaut")
gsub("http://www.olsr.org", "")
print 
}' >> $OUT
echo "</p>" >> $OUT

cat $IN | awk '/<h2>Announced HNA entries/, /<\/table>/ {
gsub("Announced HNA entries","Veröffentlichte HNAs")
gsub("width=\"100%\"", "width=500")
gsub("BORDER=0 CELLSPACING=0 CELLPADDING=0", "")
gsub("ALIGN=center", "")
gsub("<select", "<select name=none")
print
}' >> $OUT

cat /tmp/olsr_status.html|awk '/<h2>Topology entries/, /<\/div>/ {
gsub("Topology entries", "Topologie Einträge")
gsub("HNA entries", "HNAs Einträge")
gsub("MID entries", "MID Einträge")
gsub("width=\"100%\"", "width=500")
gsub("BORDER=0 CELLSPACING=0 CELLPADDING=0", "")
gsub("ALIGN=center", "")
gsub("<select", "<select name=none")                                          
print                                                                           
}' >> $OUT

rm $IN
