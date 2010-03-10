#!/bin/sh

# aktualisiere die ipkg-paketliste (um mögliche Abhängigkeiten zu bereinigen)
ipkg update >/dev/null 2>/dev/null

# hole aktuelle paketliste
wget -q -O /tmp/firmware-packages.html http://www.opennet-initiative.de/firmware/packages/ 2>/dev/null;
if [ $? != 0 ] || ! [ -f /tmp/firmware-packages.html ]; then
	# no information recived
	rm -rf /tmp/firmware-packages.html; exit
fi

# opennet-firmware_0.10ipkg-1pre_mipsel.ipk pakete mit dem suffix 'pre' werden in der Auswahlliste des Webfrontends nicht angezeigt

recent=$(ipkg list_installed opennet-firmware | awk 'BEGIN {FS="-|\\."} /opennet-firmware/ {str = sprintf("%03d%03d%03d%03d", $3, $4, $5, $6); print str }')

awk '
	BEGIN {RS="href=\"|\">";FS="_|-|\\."}
	/opennet-firmware/ && /ipkg/ && $0 !~ "info|md5|pre|se505|</a>" {
		printf("%03d%03d%03d%03d:%s\n", $3, $4, $5, $6, $0)
	}' /tmp/firmware-packages.html | \
		sort -nr >/tmp/firmware-packages
rm /tmp/firmware-packages.html

# check if newest found package is newer than installed
best=$(awk 'BEGIN {FS=":"} {print $1; exit}' /tmp/firmware-packages)
recent=$(ipkg list_installed opennet-firmware | awk 'BEGIN {FS="-|\\."} /opennet-firmware/ {str = sprintf("%03d%03d%03d%03d", $3, $4, $5, $6); print str }')

# if there is not the newest version on the ap, show that on the frontpage
if [ $best -gt $recent ]; then
	echo "firmware_update available" >/tmp/firmware-update-available
else rm -f /tmp/firmware-update-available; fi

