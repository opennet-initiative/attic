#!/bin/sh

########################################################################
# automatic adaption of transmission power in a freifunk-olsr network
########################################################################

echo -e "*** Auto-Adapting Transmission Power (v.0.3) ***"
echo    "*** Test time $(date)"

#################### Description  ###########################################
#
# Comand line parameters: [options, see -h for info] [List of IP-addresses to which optimize transmission power]
#
# If adresses are given onthe command line, the transmission power is set so that all targets might
# have a acceptable (user-defined) packet-loss rate.
# If no adresses are given on the command line, the program increases the transmission power to 
# the accepted maximum, than waits for a user-defined time to let neighbors adapt to the new
# situation. After this it checks, if any of those neighbors is interested in using the recent AP as an
# default gateway for his communication. The transmission power is optimized for acceptable
# packet-loss to the own default gateway and any of those interested neighbors.
#
########################################################################


#################### PARAMETERS ########################################
# some default values for parameters
NumberOfPings=100	# number of pings for the testcase
Accepted_PacketLoss=5	# percentage of packets which might get lost while accepting connection
DownloadTest=0		# activate download-Test (1 means active, anything else inactive)

# time to wait before checking, if anybody else needs me as a gateway in seconds
# retrieved from my own olsrd.conf (HelloInterval*WindowSize/2)
# assumption, that others are using near values
Wait=$(($(awk 'BEGIN {ORS="*"} /HelloInterval|LinkQualityWinSize/ {print $2}' /var/etc/olsrd.conf | cut -d"." -f1)/2))
if [ -z "$Wait" ] || [ $Wait -lt 1 ]; then Wait=120; fi

# maximal transmission power - limited by german law to 100mW = 20dBm
# you might destroy your AccessPoint and your and others Health by choosing inappropriate values
# Rappl-Omni 8dB
MaximalPower=19; # 19mW = 12dBm
# AccessPoint-Antenna 1dB
# MaximalPower=84; # 84mW = 19dBm
########################################################################

# check command line parameters
count=1; ip_list=
while [ $count -le $# ] ; do
	param=$(eval echo \$$count); : $((count++)); next_param=$(eval echo \$$count);
	case "$param" in
	"-c")	NumberOfPings=$next_param; : $((count++)); ;;
	"-l")	Accepted_PacketLoss=$next_param; : $((count++)); ;;
	"-d")	DownloadTest=1; ;;
	"-p")	MaximalPower=$next_param; : $((count++)); ;;
	"-w")   Wait=$next_param; : $((count++)); ;;
	"-h")	echo -e "\
Usage: adapt_txpower.sh [OPTION|IP]...
Options:
  -c number       number of pings per TestCase (default 100)
  -d              enable download test (default off)
  -l number       max percentage of packets to loose while accepting the
                  connetion (default 5%)
  -p power        set maximal power to use. Warning: inappropriate 
	          values might destroy your equipmnet as well as your
	          and others health.
  -w seconds      time to wait after increasing power for neighbors to
                  adapt to the changed value
  -h              this help

if a paramter is not recognized as an option, it is used as a IP to 
optimize the transmission to. If there is no IP added, transmission
will optimized to the used openvpn gateway and all neighbors who are 
interested in using this AccessPoint as a gateway."; exit; ;;
	*)	ip_list="$ip_list $next_param";
	esac
done

echo "* number of pings per testcase: "$NumberOfPings
echo "* maximal accepted packet loss: "$Accepted_PacketLoss" packets"
echo -e "* maximal transmission power:   "$MaximalPower"mW\n"



min_pwr=0; # this is set to a value which is known not to work. the result has to be higher, at least 1

check_transmission()
{
	echo "optimizing transmission for "$address
	
	max_pwr=$MaximalPower;
	new_pwr=$(wl txpwr | cut -d' ' -f3)
	max_to_loose=$(($Accepted_PacketLoss*$NumberOfPings/100))
	
	echo "initial transmission power is "$new_pwr"mW"

	while [ $new_pwr -gt $min_pwr ] ; do 	# min_pwr is the minimal value known not to work
		wl txpwr $new_pwr
		ping_count=0;
		loss_count=0;
		
		while [ $ping_count -lt $NumberOfPings ] && [ $loss_count -le $max_to_loose ]; do
			if [ $(ping -c 1 -q $address | awk '$8=="packet" {print $4}') = 1 ]; then
				echo -n "."
			else
				echo -n "?"
				: $((loss_count++))
			fi
			: $((ping_count++))
		done;
		echo -n " $loss_count" out of "$ping_count" packets lost
		
		# download-test
		if [ "$DownloadTest" = "1" ]; then
			echo -n " (download-rate: "
			wget -qO /tmp/testdownload "http://$address/cgi-bin-dev-zero.bin" &
			sleep 5
			kill 2>/dev/null $(ps|grep qO|grep -v grep|cut -b 0-5)
			a=$(ls -l /tmp/testdownload|cut -b 30-42);
			let b=a/5120;
			echo $b"kb/s)";
			echo "0" >/tmp/testdownload
		else echo;
		fi;

		if [ $loss_count -gt $max_to_loose ]; then
			# try to increase current transmission power
			# store tested value as new test-minimum
			min_pwr=$new_pwr
			# check if we reached the maximum or a previously working value
			if [ $(($new_pwr+1)) -ge $max_pwr ]; then
				new_pwr=$max_pwr;
				wl txpwr $new_pwr; # we dont need to test max power (just tested or absolute maximum)
				break;
			fi;
			# increase power
			new_pwr=$(($new_pwr+($max_pwr-$new_pwr)/2))
			echo "increased transmission power to "$new_pwr"mW"
		else
			#try to decrease current transmission power
			# store tested value as new test maximum
			max_pwr=$new_pwr
			#check if we reached the minimum or a previously not working value
			if [ $(($new_pwr-1)) = $min_pwr ]; then break; fi
			# decrease power
			new_pwr=$(($new_pwr-($new_pwr-$min_pwr)/2))
			echo "decreased transmission power to "$new_pwr"mW"
		fi;
	done;
}

# restore the old power value if interrupted
USER_INTERRUPT=13
initial_txpwr=$(wl txpwr | cut -d' ' -f3)
trap 'wl txpwr $initial_txpwr; exit $USER_INTERRUPT' TERM INT


ip=$(nvram get wifi_ipaddr)
address=
if [ -n "$ip_list" ]; then
	# if there are command line parameters, optimize the transmission to them
	for address in $ip_list; do
		check_transmission
	done;
else
	if [ -z "$(working_gateways.sh | cut -d' ' -f1)" ]; then
		# shouldn't happen
		echo "### sorry, please configure OpenVPN first."
		exit 1;
	fi;

	# set current power to Maximal Value
	cur_pwr=$(wl txpwr | cut -d' ' -f3)
	wl txpwr $MaximalPower
	if [ $cur_pwr -lt $MaximalPower ]; then
		echo "increased transmission power from "$cur_pwr"mW to maximum ("$MaximalPower"mW)"
		echo -e "wait $Wait seconds for neighbors to adapt to the changed situation\n"
		sleep $Wait
	elif [ $cur_pwr -gt $MaximalPower ]; then
		echo -e "decreased transmission power from "$cur_pwr"mW to maximum ("$MaximalPower"mW)\n";
	else	echo -e "current transmission power is still at maximum ("$MaximalPower"mW)\n";
	fi
	
	# get list of 1-hop neighbors
	echo "check one-hop-neighbors and if they need me to reach their gateway"
	onehop_neighbors=$(route -n | awk '$5 == "1"  && $2 == "0.0.0.0" { print $1 }')
	interested_neighbors=
	for address in $onehop_neighbors; do
		echo -n $address
		gateway=$(get_gateway.sh $address) 
		if [ -n "$gateway" ]; then
			echo -n " next hop to $gateway";
			gateway=$(echo $gateway|cut -d' ' -f2); # use only the address
		else echo -n " (couldnt retrieve information)"; fi
		
		if [ "$gateway" = "$ip" ]; then
			# register this neighbor, he likes to use us as a default gateway
			echo " *"
			interested_neighbors=$interested_neighbors" "$address
		else echo;
		fi
	done;
	if [ -n "$interested_neighbors" ]; then echo "found interested neighbor(s): "$interested_neighbors; fi
	
	# optimize for gateway
	echo -e "\n*** optimizing transmission power for gateway ***"
	
	address=
	count=0
	while [ -z "$address" ] && [ $((count++)) -lt 10 ]; do
		address=$(route -n | awk -v gw="$(working_gateways.sh | cut -d' ' -f1)" '$1 == gw {print $2; exit;}');
		if [ -z "$address" ]; then echo "problem retrieving gateway address"; sleep 2; fi;
	done;
	if [ -n "$address" ]; then
		check_transmission
	else
		echo "### sorry, couldnt find local gateway, you might retry the procedure"
		wl txpwr $initial_txpwr;
		exit 1;
	fi
	
	# optimize for neighbors
	if [ -n "$interested_neighbors" ]; then
		echo -e "\n*** optimizing transmission power for interested neighbors ***"
		for address in $interested_neighbors; do
			check_transmission
		done;
	fi;
fi;

echo -e "\n*** Optimal Transmission Power set to "$new_pwr"mW ***"
nvram set ff_txpwr=$new_pwr;
nvram commit;
