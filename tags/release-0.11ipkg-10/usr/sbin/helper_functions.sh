#!/bin/sh

# helper function
get_NETPRE() {
	dev=$(nvram get $1"_ifname")
	get_NETPRE_dev $dev
}

get_NETPRE_dev() {
	dev_ipaddr=$(ifconfig $1 2>/dev/null| awk 'BEGIN{FS=" +|:"} $2 == "inet" {print $4; exit}')
	dev_netmask=$(ifconfig $1 2>/dev/null| awk 'BEGIN{FS=" +|:"} $2 == "inet" {print $8; exit}')
	
	if [ -n "$dev_ipaddr" ]; then
		erg="$(ipcalc $dev_ipaddr $dev_netmask | awk 'BEGIN{FS="="} { if ($1=="NETWORK") net=$2; if ($1="PREFIX") pre=$2;} END{print net"/"pre}')"
		if [ "$erg" != "0.0.0.0/-8" ]; then echo $erg; fi
	fi
}
