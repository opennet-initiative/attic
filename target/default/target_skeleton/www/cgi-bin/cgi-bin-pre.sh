#!/bin/sh
echo Content-type: text/html
echo

cat<<EOF
<HTML>

<HEAD>
<TITLE>Freifunk.Net - $TITLE</TITLE>
<META CONTENT="text/html; charset=iso-8559-1" HTTP-EQUIV="Content-Type">
<META HTTP-EQUIV="cache-control" CONTENT="no-cache" />
<LINK HREF="../ff.css" REL="StyleSheet" TYPE="text/css">
<LINK HREF="sven-ola*ät*gmx*de" REV="made" TITLE="Sven-Ola">
EOF

unescape()
{
echo $1|awk '
BEGIN {
hextab["0"]=0; hextab["1"]=1;
hextab["2"]=2; hextab["3"]=3;
hextab["4"]=4; hextab["5"]=5;
hextab["6"]=6; hextab["7"]=7;
hextab["8"]=8; hextab["9"]=9;
hextab["A"]=hextab["a"]=10;
hextab["B"]=hextab["b"]=11;
hextab["C"]=hextab["c"]=12;
hextab["D"]=hextab["d"]=13;
hextab["E"]=hextab["e"]=14;
hextab["F"]=hextab["f"]=15;
}
{
decoded="";
i=1;
len=length($0);
while (i<=len) {
c=substr($0, i, 1);
if (c=="%") {
if (i+2<=len) {
c1=substr($0, i+1, 1);
c2=substr($0, i+2, 1);
if (hextab[c1]==""||hextab[c2]=="") {
print "WARNING: invalid hex encoding: %" c1 c2|"cat>&2";
}
else {
code=0+hextab[c1]*16+hextab[c2]+0;
c=sprintf("%c", code);
i=i+2;
}
}
else {
print "WARNING: invalid % encoding: " substr($0, i, len-i);
}
}
else if (c=="+") {
c=" ";
}
decoded=decoded c;
++i;
}
print decoded;
}'
}
checkbridge()
{
ret=0
. /etc/functions.sh
dev=$(nvram get wifi_ifname)
if [ -n "$dev" ]; then
fnd=
old="$(nvram get lan_ifnames)"
for i in $old; do
test "$i" = "$dev" && fnd=1
done
wbr=
adr=$(nvram get wifi_ipaddr)
if [ -z "$adr" ] || [ "$adr" = "$(nvram get lan_ipaddr)" ];then
# WIFI dev should be in the bridge list
wbr=1
fi
if [ "$wbr" != "$fnd" ]; then
if [ -z "$wbr" ]; then
new=
for i in $old; do
test "$i" != "$dev" && new="$new $i"
done
new=${new# }
else
new="$old $dev"
fi
/usr/sbin/nvram set lan_ifnames="$new"
if [ -z "$(/usr/sbin/nvram get lan_ifname)" ]; then
lan=$(nvram get lan_ifname)
test -z "$lan" || lan=br0
nvram set lan_ifname=$lan
fi
ret=1
fi
fi
return $ret
}

cat<<EOF
<SCRIPT LANGUAGE="JavaScript" TYPE="text/javascript"><!--
function navarr(){}
navset=new navarr();
navres=new navarr();
function set(idx){
if(!!navset[idx]){
document.images[idx].src=navset[idx].src;
}
}
function res(idx){
if(!!navres[idx]){
document.images[idx].src=navres[idx];
}
}
function ini() {
if (!!document.images){
for(var idx=0; idx<document.images.length; idx++){
var src=document.images[idx].src;
var pos=src.indexOf('_white.gif');
if (0<pos) {
navres[idx]=src;
src=src.substring(0, src.indexOf('_white.gif'))+'_red.gif';
navset[idx]=new Image(document.images[idx].width, document.images[idx].height);
navset[idx].src=src;
document.images[idx].onmouseover=new Function("if(!!window.set)set("+idx+");");
document.images[idx].onmouseout=new Function("if(!!window.res)res("+idx+");");
}
else if (!document.images[idx].mozbug && !!src.search &&
0<=src.search(new RegExp('progress[0-9]+\\.gif$')))
{
document.images[idx].mozbug=1;
document.images[idx].src='';
document.images[idx].src=src;
}
}
}
}
function help(e) {
if (!e) e = event;
// (virt)KeyVal is Konqueror, charCode is Moz/Firefox, else MSIE, Netscape, Opera
if (26 == e.virtKeyVal || !e.keyVal && !e.charCode && 112 == (e.which || e.keyCode)) {
var o = null;
if (e.preventDefault) {
if (e.cancelable) e.preventDefault();
o = e.target;
}
else {
e.cancelBubble = true;
o = e.srcElement;
}
while(!!o && '' == o.title) o = o.parentNode;
if (!!o) alert(o.title);
}
}
if (document.all) {
document.onkeydown = help;
document.onhelp = function(){return false;}
}
else {
document.onkeypress = help;
}
//--></SCRIPT>
</HEAD>

<BODY ONLOAD="if(null!=window.ini)window.ini()">
<TABLE BORDER="0" CELLPADDING="0" CELLSPACING="0" CLASS="body">
<TBODY>
<TR>
<TD CLASS="color" COLSPAN="5" HEIGHT="19"><SPAN CLASS="color"><A CLASS="color" HREF="../index.html">Home</A></SPAN><IMG ALT="" HEIGHT="10" HSPACE="2" SRC="../images/vertbar.gif" WIDTH="1"><SPAN CLASS="color"><A CLASS="color" HREF="../cgi-bin-contact.html">Kontakt</A></SPAN></TD>
</TR>
<TR>
<TD HEIGHT="5" WIDTH="150"></TD>
<TD HEIGHT="5" WIDTH="5"> </TD>
<TD HEIGHT="5"></TD>
<TD HEIGHT="5" WIDTH="5"></TD>
<TD HEIGHT="5" WIDTH="150"></TD>
</TR>
<TR>
<TD HEIGHT="33" WIDTH="150"></TD>
<TD HEIGHT="33" WIDTH="5"></TD>
<TD ALIGN="right" HEIGHT="33"><A HREF="http://www.opennet-initiative.de/"><IMG ALT="" BORDER="0" HEIGHT="33" SRC="../images/lgo_ffn_1l.gif" WIDTH="106"></A></TD>
<TD ALIGN="right" HEIGHT="33" WIDTH="5"><A HREF="http://www.opennet-initiative.de/"><IMG ALT="" BORDER="0" HEIGHT="33" SRC="../images/lgo_ffn_1m.gif" WIDTH="5"></A></TD>
<TD HEIGHT="33" WIDTH="150"><A HREF="http://www.opennet-initiative.de/"><IMG ALT="" BORDER="0" HEIGHT="33" SRC="../images/lgo_ffn_1r.gif" WIDTH="150"></A></TD>
</TR>
<TR>
<TD CLASS="magenta" COLSPAN="4" HEIGHT="19"> </TD>
<TD CLASS="magenta" HEIGHT="19" WIDTH="150"><A HREF="http://www.opennet-initiative.de/"><IMG ALT="" BORDER="0" HEIGHT="19" SRC="../images/lgo_ffn_2.gif" WIDTH="150"></A></TD>
</TR>
<TR>
<TD HEIGHT="5" WIDTH="150"></TD>
<TD HEIGHT="5" WIDTH="5"></TD>
<TD HEIGHT="5"></TD>
<TD HEIGHT="5" WIDTH="5"></TD>
<TD CLASS="color" HEIGHT="5" ROWSPAN="2" VALIGN="top" WIDTH="150"><A HREF="http://www.opennet-initiative.de/"><IMG ALT="" BORDER="0" HEIGHT="94" SRC="../images/lgo_ffn_3.gif" WIDTH="150"></A></TD>
</TR>
<TR>
<TD CLASS="color" VALIGN="top" WIDTH="150">
<TABLE BORDER="0" CELLPADDING="0" CELLSPACING="7" WIDTH="150">
<TBODY>
<TR>
<TD>

<H1 CLASS="color">Verwalten</H1></TD>
</TR>
EOF

for inc in /www/cgi-bin/[0-9][0-9]-*;do cat $inc;done

cat<<EOF
</TBODY>
</TABLE>
<DIV CLASS="white"></DIV>
<TABLE BORDER="0" CELLPADDING="0" CELLSPACING="7" WIDTH="150">
<TBODY>
<TR>
<TD>
<DIV CLASS="color"><A CLASS="color" HREF="../index.html"><IMG ALIGN="right" ALT="" BORDER="0" HEIGHT="15" SRC="../images/icn_arrow_white.gif" WIDTH="12">Zur&uuml;ck</A></DIV></TD>
</TR></TBODY>
</TABLE>
<DIV CLASS="white"></DIV></TD>
<TD VALIGN="top" WIDTH="5"></TD>
<TD VALIGN="top">
EOF
