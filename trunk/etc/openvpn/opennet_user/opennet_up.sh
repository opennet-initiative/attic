#!/bin/sh
eval $(/usr/bin/netparam)

TAPADDR_NET="$(ifconfig tap0 2>/dev/null| awk 'BEGIN{FS=" +|:"} $2 == "inet" {print $4" " $8; exit}')"
[ -n "$TAPADDR_NET" ] && TAPNET_PRE="$(ipcalc $TAPADDR_NET | awk 'BEGIN{FS="="} { if ($1=="NETWORK") net=$2; if ($1="PREFIX") pre=$2;} END{print net"/"pre}')"

ip route flush table 3
[ -n "$TAPNET_PRE" ] && ip route add throw $TAPNET_PRE table 3
ip route add throw $LANNET/$LANPRE table 3
[ -n "$WIFIPRE" ] && ip route add throw $WIFINET/$WIFIPRE table 3
ip route add default via $route_vpn_gateway dev $dev table 3
iptables -t nat -A POSTROUTING -o $dev -s $LANNET/$LANPRE -j SNAT --to-source $ifconfig_local
[ -n "$DHCPWIFIPRE" ] && iptables -t nat -A POSTROUTING -o $dev -s $DHCPWIFINET/$DHCPWIFIPRE -j SNAT --to-source $ifconfig_local
echo "vpn-tunnel active" >/tmp/openvpn_msg.txt	# a short message for the web frontend
