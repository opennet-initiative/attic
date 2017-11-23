#!/bin/sh

DEST='/var/www/on_webstat/firmware_status2.html'
OUT='/var/www/on_webstat/firmware_status.html.tmp'
TARGETVERSION='0.10'
MAXNODE=140
IMG_OKAY='<img src="opennet-fwstatus-okay.png">'
IMG_FAILED='<img src="opennet-fwstatus-failed.png">'

echo "<HTML><HEAD><TITLE>Firmware-Status izumi.on</TITLE><LINK HREF="opennet.css" REL="StyleSheet" TYPE="text/css" /></HEAD><BODY><h1>Firmware-Status <i>izumi.on</i></h1>" > $OUT

echo "<table><tr><th>Node</th><th>Status</th><th>Firmware Version</th></tr>" >> $OUT

fw_okay=0
fw_old=0

for ap in $(seq 1 $MAXNODE);
do
	if [[ $(($ap % 2)) -eq 1 ]]
	then tr_style="odd"
	else tr_style="even"
	fi
	echo "<tr class=\"$tr_style\"><td align=\"right\"><a href=\"http://wiki.opennet-initiative.de/index.php/AP$ap\">$ap.aps.on</a></td><td align=\"center\">" >> $OUT
	version=`wget -q -O - $ap.aps.on | tr -d "\"" | grep -a1 "Firmware [V|v]ersion"| tr "\n" " "| awk '{
		if (index($0,"Opennet-Firmware"))
		{
			n1 = index($0, "Opennet-Firmware")
			n2 = index($0, "</b>")
			print substr($0, n1, n2-n1)
		}
		else if (index($0,"Opennet-OpenVPN Firmware"))
		{
			n1 = index($0, "Opennet-OpenVPN Firmware")
			n2 = index($0, "</b>")
			print substr($0, n1, n2-n1)
		}
		else if (index($0, "Freifunk Firmware"))
		{
			n1 = index($0, "Freifunk Firmware")
			n2 = index($0, ". ")
			print substr($0, n1, n2-n1)
		}
		else print "Unbekannte Firmware"
	}'|grep -v '^$'`
	echo $ap " - " $version  " - " `[[ "$version" =~ "$TARGETVERSION" ]] && echo "okay"`
	if [ -n "$version" ]
	then
		[[ "$version" =~ "$TARGETVERSION" ]] && {
			 echo $IMG_OKAY >> $OUT
			 fw_okay=$(($fw_okay+1))
		} || {
			echo $IMG_FAILED >> $OUT
			fw_old=$(($fw_old+1))
		}
	fi
	echo "</td><td>$version</td></tr>" >> $OUT
done

echo "</table>" >> $OUT

fw_unknown=$(($MAXNODE-$fw_okay-$fw_old))
echo "<p>$fw_okay aktuell, $fw_old veraltet, $fw_unknown unbekannt</p>" >> $OUT

echo "<p>" >>$OUT
echo "Zuletzt aktualisiert: " >> $OUT
date >> $OUT
echo "</p>" >> $OUT

echo "</body></html>" >> $OUT

mv $OUT $DEST
