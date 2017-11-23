#!/usr/bin/python2.3
# -*- coding: ISO-LATIN-1 -*-

# icons under creative commons licence
# http://www.famfamfam.com/lab/icons/

# generate tmp file only?
develop = 0

# imports
from string import *
from time import *
from datetime import *
from os import listdir,stat,popen,rename
from stat import ST_MTIME
from psycopg import connect
from re import compile,sub

# db config
DSN = "dbname=openvpn-status user=opennet password=amkabuz"
insert_sql = "insert into status(name, tx_overall, rx_overall, tx_latest, rx_latest, firstseen, lastseen) values (%s, %i, %i, %i, %i, now(), now())"
select_sql = "select * from status where name = %s"
update_sql = "update status set tx_overall = tx_overall + %i, rx_overall = rx_overall + %i, tx_latest = %i, rx_latest = %i, lastseen = now() where name = %s"
select_uptime_sql = "select * from uptime where name = %s"
insert_uptime_sql = "insert into uptime(name, uptime_overall, firstseen, lastseen, online, uptime_current) values (%s, 0, now(), now(), true, 0)"
update_uptime_sql1 = "update uptime set uptime_overall = uptime_overall + (extract(epoch from (now() - lastseen))/60), uptime_current = uptime_current + (extract(epoch from (now() - lastseen))/60), lastseen = now(), online = true where name = %s"
update_uptime_sql2 = "update uptime set lastseen = now(), online = false, uptime_current = 0 where name = %s"

# file config
file_vpnstatus = "/var/log/openvpn/opennet_gateways.status.log"
file_output = "/var/www/on_webstat/vpn_gateways.html"
file_tmptail = ".tmp"
activepath = "/etc/openvpn/acl/opennet_gateways/"
inactivepath = "/etc/openvpn/acl/opennet_gateways_disabled/"
pidfile_openvpn = "/var/run/openvpn.opennet_gateways.pid"
pidfile_ppp = "/var/run/ppp0.pid"

# frontend config
host = 'izumi.on'
wikiurl = 'http://wiki.opennet-initiative.de/index.php/'
text_head = 'VPN-Status Gateways'
text_footer = ''
text_index = 'Index:'
text_head_conn = 'Eingehende Verbindungen'
text_head_cert = 'Installierte Zertifikate'
text_head_lege = 'Legende'
text_link_conn = 'Verbindungen'
text_link_cert = 'Zertifikate'
text_link_lege = 'Legende'
text_timestamp = 'Zuletzt aktualisiert:'
text_clients = 'Clients:'
text_avgrate = 'Mittl.:'
text_currate = 'Akt.:'
text_uptime = 'Uptime:'
text_openvpn = 'VPN-Server'
text_ppp = 'DSL-Verbindung'
text_certs = 'Zertifikate:'
text_icons = 'Symbole:'
text_tbl_name = 'Name'
text_tbl_source = 'Quelle'
text_tbl_tx = 'TX'
text_tbl_rx = 'RX'
text_tbl_conn = 'Verbunden seit'
text_tbl_avgrate = 'Mittl. Rate'
text_tbl_currate = 'Akt. Rate'
text_tbl_unmo = 'Unverändert'
text_tbl_connfirst = 'Erste Verbindung'
text_tbl_connlast = 'Zuletzt verbunden'
text_tbl_rate = 'Mittl. Rate'
text_tbl_stat = 'Status'
icon_route = 'opennet-openvpn-route.png'
icon_route_alt = 'Erreichbar'
icon_cert_a = 'opennet-openvpn-unlocked.png'
icon_cert_a_alt = 'Freigeschaltet'
icon_cert_i = 'opennet-openvpn-locked.png'
icon_cert_i_alt = 'Gesperrt'
icon_conn = 'opennet-openvpn-connect.png'
icon_conn_alt = 'Verbunden'
icon_size = 15 
network_aps = '192.168.1'
network_mob = '192.168.7'

# file init
r = open(file_vpnstatus, "r")
w = open(file_output + file_tmptail, "w+")

# db init
dbconn = connect(DSN)
dbconn.autocommit(1)
dbcurs = dbconn.cursor()

# ----------- helper ----------------

# wiki-url from on-hostnames
def on_link(fqhn):
	result = fqhn
	if fqhn.count('.on'):
		host = fqhn.split('.')[0]
		if fqhn.count('aps.on'):
			result = "<a href=\"%sAP%s\">%s</a>" % (wikiurl, host, fqhn)
	return result

# even/odd tr style
def tr_style(num):
	result = 'even'
	if (num % 2):
		result = 'odd'
	return result

# build status icons
def cert_icon(cert):
	result = ''
	if cert[3].count('inactive'):
		result = '<img src=\"%s\" height=\"%d\" alt=\"%s\" />' % (icon_cert_i, icon_size, icon_cert_i_alt)
	else:
		result = '<img src=\"%s\" height=\"%d\" alt=\"%s\" />' % (icon_cert_a, icon_size, icon_cert_a_alt)
	return result
	
# build ip from hostname
def ip(cert):
	result = ''
	fqhn = cert[0]
	if fqhn.count('aps.on'):
		host = int( fqhn.split('.')[0] )
		result = '%s.%d' % (network_aps, host)
	if fqhn.count('mobile.on'):
		host = int( fqhn.split('.')[0] )
		result = '%s.%d' % (network_mob, host)
	return result

# check routing to ip
def is_online(ip):
	result = 0
	f = popen('/sbin/route -n | /bin/grep "%s "' % ip)
	if len( f.read(1) ) > 0:
		result = 1
	return result	

# build online-check icon (via routing table)
def routing_icon(cert):
	result = ''
	if cert[9] == 1:
		result = '<img src=\"%s\" height=\"%d\" alt=\"%s\"/>' % (icon_route, icon_size, icon_route_alt)
	return result

# build connect icon
def connect_icon(cert, connections):
	result = ''
	if build_key( cert[0] ) in connections:
		result = '<img src=\"%s\" height=\"%d\" alt=\"%s\"/>' % (icon_conn, icon_size, icon_conn_alt)
	return result

# merge icons
def icons(cert, connections):
	return '%s %s %s' % (cert_icon(cert), routing_icon(cert), connect_icon(cert, connections))

# update db with latest connection infos / return calc cur-rate
def db_connupdate(connections, dbcursor, localtime):
	rate_cur = 0
	keys = connections.keys()
	for k in keys:
		con = connections[k]
		name = str( con[0] )
		tx = int( con[2] ) / 1024 # kb 
		rx = int( con[3] ) / 1024
		dbcursor.execute(select_sql, (name,))
		if dbcursor.rowcount > 0:
			res = dbcursor.fetchone()
			tx_latest = int( res[3] )
			rx_latest = int( res[4] )
			if (tx < tx_latest or rx < rx_latest):
				# reconnect detected
				tx_diff = tx
				rx_diff = rx
			else:
				# no reconnect since last run, calc diff
				tx_diff = tx - tx_latest
				rx_diff = rx - rx_latest
				# sanity (rounding issue)
				if tx_diff < 0:
					tx_diff = 0
				if rx_diff < 0:
					rx_diff = 0
			# store tx/rx-diffs
			dbcursor.execute(update_sql, (tx_diff, rx_diff, tx, rx, name))
			# calc latest rate
			t = strptime(str((res[6])).split('.')[0], '%Y-%m-%d %H:%M:%S')
			rate = round((tx_diff + rx_diff) / (mktime(localtime) - mktime(t)), 1)
			rate_tx = round(tx_diff / (mktime(localtime) - mktime(t)), 1)
			rate_rx = round(rx_diff / (mktime(localtime) - mktime(t)), 1)
		else:
			dbcursor.execute(insert_sql, (name, tx, rx, tx, rx))
			rate = con[6]
			rate_tx = 0
			rate_rx = 0
		# update connection with latest rate
		con.insert(9, rate)
		con.insert(10, rate_tx)
		con.insert(11, rate_rx)
		connections[k] = con
		# calc overall rate
		rate_cur = rate_cur + rate
	return rate_cur

# update certs with seen-timestamps from db
def db_certupdate(certs, dbcursor):
	keys = certs.keys()
	for k in keys:
		cert = certs[k]
		name = str( cert[0] )
		dbcursor.execute(select_sql, (name,))
		if dbcursor.rowcount > 0:
			res = dbcursor.fetchone()
			firstseen = str( res[5] ).split('.')[0]
			lastseen = str ( res[6] ).split('.')[0]
			tx = int( res[1] ) # in kb
			rx = int( res[2] )
                        t1 = strptime(firstseen, '%Y-%m-%d %H:%M:%S')
			t2 = strptime(lastseen, '%Y-%m-%d %H:%M:%S')
			rate = (tx + rx) / (mktime(t2) - mktime(t1))
		else:
			firstseen = ''
			lastseen = ''
			tx = 0
			rx = 0
			rate = 0
		cert.insert(4, firstseen)
		cert.insert(5, lastseen)
		cert.insert(6, round(tx / 1024, 1)) # in MB
		cert.insert(7, round(rx / 1024, 1))
		cert.insert(8, round(rate, 1))
		cert.insert(9, is_online(ip(cert)))
		certs[k] = cert

# update online-status in online table
def db_onlineupdate(certs, dbcursor):
	keys = certs.keys()
	for k in keys:
		cert = certs[k]
		name = str( cert[0] )
		dbcursor.execute(select_uptime_sql, (name,))
		if dbcursor.rowcount > 0:
			if cert[9] == 1:
				# online now
				dbcursor.execute(update_uptime_sql1, (name,))
			else:
				# offline now
				dbcursor.execute(update_uptime_sql2, (name,))
				
		else:
			if cert[9] == 1:
				# first time online
				dbcursor.execute(insert_uptime_sql, (name,))

# return uptime of process (via pid-file)
def pid_uptime(pidfile, localtime):
	try:	
		modtime = ctime( stat(pidfile)[ST_MTIME] )
		t = strptime(modtime, '%a %b %d %H:%M:%S %Y')
		y,m,d,h,mi,s = t[:6]
		orig = datetime(y,m,d,h,mi,s)
		uptime = localtime - orig
		return uptime
	except:
		return "down"

# return a (sortable) key from fqhn 
def build_key(name):
	key = name
	if name.count('aps'):
		key = 'ap%03da' % int( (split(name, '.')[0]) )
	if key.count('mobile'):
		key = 'mo%03da' % int( (split(name, '.')[0]) )
	return key

# translato timediff string to german
def format_timediff(diffstr):
	diffstr = str( diffstr )
	p = compile('days') # use 'regex'
	diffstr = p.sub('Tage', diffstr, 1)
	p = compile('day')
	diffstr = p.sub('Tag', diffstr, 1)
	return diffstr 
	
# --- parse openvpn status log data ---

num = 0
connections = {}
rate_avg = 0

n = localtime()
y,m,d,h,mi,s = n[:6]
now = datetime(y,m,d,h,mi,s)

while 1:
	line = replace(r.readline(), "\n", "")

	# print last update
	if line.count("Updated"):
		timestamp = replace(line, "Updated,", "")
		num = 1
	
	# last line - stop parsing...
	if line.count("ROUTING TABLE"):
		break

	if num > 0:
		num=num+1
		if num > 3:
			
			data = split(line, ",")
			
			# calc uptime
			t = strptime(data[4], '%a %b %d %H:%M:%S %Y')
			y,m,d,h,mi,s = t[:6]
			orig = datetime(y,m,d,h,mi,s)
			uptime = format_timediff( now - orig )
			data.insert(5, uptime)
			
			# calc rate
			tx = round(int(data[2]) / 1024, 1) # KB
			rx = round(int(data[3]) / 1024, 1)
			rate = round((tx + rx) / (mktime(n) - mktime(t)), 1)
			data.insert(6, rate) # KB/sec
			data.insert(7, round(tx / 1024, 1)) # MB
			data.insert(8, round(rx / 1024, 1))
			
			# calc overall avg rate
			rate_avg = rate_avg + rate
			
			# push to dict
			key = build_key( data[0] )
			connections[key] = data

# --- build cert status ----

certs = {}

dir = listdir(activepath)
for file in dir:
	modtime = ctime( stat(activepath+file)[ST_MTIME] )
	t = strptime(modtime, '%a %b %d %H:%M:%S %Y')
	y,m,d,h,mi,s = t[:6]
	orig = datetime(y,m,d,h,mi,s)
	uptime = now - orig
	key = build_key(file)
	if file.count('aps'):
		certs[key] = [file, modtime, uptime, 'active']
	if file.count('mobile'):
		certs[key] = [file, modtime, uptime, 'active']
	
dir = listdir(inactivepath)
for file in dir:
	modtime = ctime( stat(inactivepath+file)[ST_MTIME] )
	t = strptime(modtime, '%a %b %d %H:%M:%S %Y')
	y,m,d,h,mi,s = t[:6]
	orig = datetime(y,m,d,h,mi,s)
	uptime = now - orig
	key = build_key(file)
	if file.count('aps'):
		certs[key] = [file, modtime, uptime, 'inactive']
	if file.count('mobile'):
		certs[key] = [file, modtime, uptime, 'inactive']

# --- update via database ----

rate_cur = db_connupdate(connections, dbcurs, n)
db_certupdate(certs, dbcurs)
db_onlineupdate(certs, dbcurs)

# --- fetch common informations ---

uptime_openvpn = pid_uptime(pidfile_openvpn, now)
uptime_ppp = pid_uptime(pidfile_ppp, now)

# --------- write output ---------------

w.write("<?xml version=\"1.0\" encoding=\"iso-8859-1\" ?>\n")
w.write("<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\">\n")
w.write("<html xmlns=\"http://www.w3.org/1999/xhtml\" lang=\"en\" xml:lang=\"en\">\n")
w.write("<head>\n")
w.write("<title>%s %s</title>\n" % (text_head, host))
w.write("<link rel=\"stylesheet\" type=\"text/css\" href=\"opennet.css\" />")
w.write("</head>\n")
w.write("<body>\n")

w.write("<h1>%s <i>%s</i></h1>\n" % (text_head, host))
w.write("<p><strong>%s</strong> <a href=\"#%s\">%s</a> &middot; <a href=\"#%s\">%s</a> &middot; <a href=\"#%s\">%s</a></p>\n" % (text_index, text_link_conn, text_head_conn, text_link_cert, text_head_cert, text_link_lege, text_head_lege))
w.write("<h2><a name=\"%s\"></a>%s</h2>\n" % (text_link_conn, text_head_conn))
w.write("<p>%s %s, %s %s KB/sec, %s %s KB/sec, %s %s<br/>%s %s %s, %s %s</p>\n" % (text_clients, len(connections), text_avgrate, rate_avg, text_currate, rate_cur, text_timestamp, timestamp, text_uptime, text_ppp, uptime_ppp, text_openvpn, uptime_openvpn))
w.write("<p>\n<table>\n")
w.write("<tr><th>&nbsp;%s&nbsp;</th><th>&nbsp;%s&nbsp;</th><th>&nbsp;%s&nbsp;</th><th>&nbsp;%s&nbsp;</th><th>&nbsp;%s&nbsp;</th><th>&nbsp;%s&nbsp;</th><th>&nbsp;%s&nbsp;</th><th>&nbsp;(%s/%s)&nbsp;</th></tr>\n" % (text_tbl_name, text_tbl_source, text_tbl_tx, text_tbl_rx, text_tbl_conn, text_tbl_avgrate, text_tbl_currate, text_tbl_tx, text_tbl_rx))

keys = connections.keys()
keys.sort()
i = 0
for k in keys:
	i=i+1
	w.write("<tr class=\"%s\"><td class=\"right\">&nbsp;%s&nbsp;</td><td>&nbsp;%s&nbsp;</td><td class=\"right\">&nbsp;%s MB&nbsp;</td><td class=\"right\">&nbsp;%s MB&nbsp;</td><td class=\"right\">&nbsp;%s&nbsp;</td><td class=\"right\">&nbsp;%s KB/sec&nbsp;</td><td class=\"right\">&nbsp;%s KB/sec&nbsp;</td><td>&nbsp;%s / %s&nbsp;</td></tr>\n" % (tr_style(i), on_link(connections[k][0]), connections[k][1], connections[k][7], connections[k][8], connections[k][5], connections[k][6], connections[k][9], connections[k][10], connections[k][11]))

w.write("</table>\n</p>\n")

w.write("<h2><a name=\"%s\"></a>%s</h2>\n" % (text_link_cert, text_head_cert))
w.write("<p>%s %s</p>\n" % (text_certs, len(certs)))
w.write("<p>\n<table>\n")
w.write("<tr><th>&nbsp;%s&nbsp;</th><th>&nbsp;%s&nbsp;</th><th>&nbsp;%s&nbsp;</th><th>&nbsp;%s&nbsp;</th><th>&nbsp;%s&nbsp;</th><th>&nbsp;%s&nbsp;</th><th>&nbsp;%s&nbsp;</th><th>&nbsp;%s&nbsp;</th></tr>\n" % (text_tbl_name, text_tbl_stat, text_tbl_unmo, text_tbl_connfirst, text_tbl_connlast, text_tbl_tx, text_tbl_rx, text_tbl_rate))

keys = certs.keys()
keys.sort()
i = 0
for k in keys:
	i = i + 1
	w.write("<tr class=\"%s\"><td class=\"right\">&nbsp;%s&nbsp;</td><td class=\"bottom\">%s</td><td class=\"right\">&nbsp;%s&nbsp;</td><td class=\"right\">&nbsp;%s&nbsp;</td><td class=\"right\">&nbsp;%s&nbsp;</td><td class=\"right\">&nbsp;%s MB&nbsp;</td><td class=\"right\">&nbsp;%s MB&nbsp;</td><td class=\"right\">&nbsp;%s KB/sec&nbsp;</td></tr>\n" % (tr_style(i), on_link(certs[k][0]), icons(certs[k], connections), certs[k][2], certs[k][4], certs[k][5], certs[k][6], certs[k][7], certs[k][8]))

w.write("</table>\n</p>\n")

w.write("<h2><a name=\"%s\"></a>%s</h2>\n" % (text_link_lege, text_head_lege))
w.write("<p>%s &nbsp; <img src=\"%s\" alt=\"%s\" />&nbsp; %s &nbsp; <img src=\"%s\" alt=\"%s\" />&nbsp; %s &nbsp; <img src=\"%s\" alt=\"%s\" />&nbsp; %s &nbsp; <img src=\"%s\" alt=\"%s\" />&nbsp; %s</p>\n" % (text_icons, icon_cert_a, icon_cert_a_alt, icon_cert_a_alt, icon_cert_i, icon_cert_i_alt, icon_cert_i_alt, icon_route, icon_route_alt, icon_route_alt, icon_conn, icon_conn_alt, icon_conn_alt))

w.write("<p>&nbsp;</p>\n")
w.write("<p><a href=\"http://validator.w3.org/check?uri=referer\"><img src=\"http://www.w3.org/Icons/valid-xhtml10\" alt=\"Valid XHTML 1.0 Strict\" height=\"31\" width=\"88\" /></a></p>\n")

w.write("</body>\n</html>\n")

# file close
r.close()
w.close()

if develop==0:
	rename(file_output + file_tmptail, file_output)

# db close
dbcurs.close()
dbconn.close()
