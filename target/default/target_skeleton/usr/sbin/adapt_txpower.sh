#!/bin/sh

########################################################################
# automatic adaption of transmission power in a freifunk-olsr network
########################################################################

echo -e "\n*** Auto-Adapting Transmission Power (v.0.1c) ***"

#################### Description  ###########################################
#
# Comand line parameters: List of IP-addresses to which optimize transmission power
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
# some parameters, maybe set later as command-line parameters
NumberOfPings=100	# number of pings for the testcase
Accepted_PacketLoss=5	# percentage of packets which might get lost while accepting connection

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
		
		echo " $loss_count" out of "$ping_count" packets lost
		
		if [ $loss_count -gt $max_to_loose ]; then
			# try to increase current transmission power
			# check if we reached the maximum or a previously working value
			if [ $(($new_pwr+1)) -ge $max_pwr ]; then
				new_pwr=$max_pwr;
				wl txpwr $new_pwr; # we dont need to test max power (just tested or absolute maximum)
				break;
			fi;
			# store tested value as new test-minimum
			min_pwr=$new_pwr
			# increase power
			new_pwr=$(($new_pwr+($max_pwr-$new_pwr)/2))
			echo "increased transmission power to "$new_pwr"mW"
		else
			#try to decrease current transmission power
			#check if we reached the minimum or a previously not working value
			if [ $(($new_pwr-1)) = $min_pwr ]; then break; fi
			# store tested value as new test maximum
			max_pwr=$new_pwr
			# decrease power
			new_pwr=$(($new_pwr-($new_pwr-$min_pwr)/2))
			echo "decreased transmission power to "$new_pwr"mW"
		fi;
	done;
}

ip=$(nvram get wifi_ipaddr)
address=
if [ -n "$1" ]; then
	# if there are command line parameters, optimize the transmission to them
	number=1;
	while [ -n "$(eval echo \$$number)" ]; do
		address="$(eval echo \$$number)";
		check_transmission
		: $((number++))
	done;
else
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
	echo "check one-hop-neighbors and if they need me as a gateway"
	onehop_neighbors=$(route -n | awk '$5 == "1"  && $2 == "0.0.0.0" { print $1 }')
	interested_neighbors=
	for address in $onehop_neighbors; do
		echo -n $address
		gateway=$(get_gateway.sh $address)
		if [ -n "$gateway" ]; then echo -n " using default gateway $gateway";
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
	while [ -z "$address" ]; do address=$(route -n | awk '$1 == "0.0.0.0" && /192.168/ { print $2; exit;}'); done;
	check_transmission
	
	# optimize for neighbors
	if [ -n "$interested_neighbors" ]; then
		echo -e "\n*** optimizing transmission power for interested neighbors ***"
		for address in $interested_neighbors; do
			check_transmission
		done;
	fi;
fi;

echo -e "\n*** Optimal Transmission Power set to "$new_pwr"mW ***"