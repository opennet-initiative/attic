#!/bin/sh

# WARNING: busybox-netcat has no timeout-option, so this script may way really long

########################################################################
# getting the default gateway of any other node
########################################################################
# this is done by parsing the output of the status-routes page

if [ -n "$1" ]; then target=$1;
else target=127.0.0.1; fi

page=$(nc $target 80 2>/dev/null <<-EOF
POST /cgi-bin-status.html HTTP/1.1
Content-type: application/x-www-form-urlencoded
Content-Length: 17

post_route=Routen

EOF
)

echo $page | awk 'BEGIN {RS="<TR>";FS="<|>"} $3 == "0.0.0.0" && /192.168/ {print $9; exit}'
