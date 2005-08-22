#!/usr/bin/perl -w

use Fcntl ':mode';

use constant DEFODIR => "./out";        # Default output directory
use constant DEFLANG => "de";           # Default language
use constant BAKLANG => "en";           # Fallback language (only attrs)

local %TPLFST = ();                     # First templates with -s

sub Getopts($) {
  local($argumentative) = @_;
  local(@args,$_,$first,$rest);
  local($errs) = 0;
  local($[) = 0;

  @args = split( / */, $argumentative );
  while(@ARGV && ($_ = $ARGV[0]) =~ /^-(.)(.*)/) {
    ($first,$rest) = ($1,$2);
    $pos = index($argumentative,$first);
    if($pos >= $[) {
      if($args[$pos+1] eq ':') {
        shift(@ARGV);
        if($rest eq '') {
          ++$errs unless(@ARGV);
          $rest = shift(@ARGV);
        }
        eval "
        push(\@opt_$first, \$rest);
        if(\$opt_$first eq '') {
          \$opt_$first = \$rest;
        }
        else {
          \$opt_$first .= ' ' . \$rest;
        }
        ";
      }
      else {
        eval "\$opt_$first = 1";
        if($rest eq '') {
          shift(@ARGV);
        }
        else {
          $ARGV[0] = "-$rest";
        }
      }
    }
    else {
      print STDERR "Unknown option: $first\n";
      ++$errs;
      if($rest ne '') {
        $ARGV[0] = "-$rest";
      }
      else {
        shift(@ARGV);
      }
    }
  }
  $errs == 0;
}

sub copy_ref {
  my $src = shift;
  my $dst = shift;
  my $lng = shift;

  my $dstdir = $dst;
  $dstdir =~ s#[\\\:\/]#/#gs;
  $dstdir =~ s#(\./)?[^/]+$##s;
  mkdir($dstdir) if (! -d $dstdir);
  if ($src =~ m#[\\\/]$#s) {
    # Special: We reference a directory. Since the OpenWRT
    # cannot make directory index, we generate one here
    open(IDX, '>'.$dst."index.html") || die("Cannot write ".$dst."index.html");
    print IDX '<HTML><HEAD><TITLE>Index of '.$src.'</TITLE></HEAD><BODY>'."\n";
    print IDX '<H1>Index of '.$src.'</H1><PRE>'."\n";
    opendir(DIR, $src) || die("Cannot opendir ".$src);
    while(my $ent = readdir(DIR)) {
      if ($ent ne "index.html") {
        print IDX '<A HREF="'.$ent.'">'.$ent.'</A>';
        if (-f $src.$ent) {
          @src = stat($src.$ent);
          for(my $i = length($ent); $i <= 40; $i++) {
            print IDX ' ';
          }
          print IDX ' '.$src[7];
          for(my $i = length($src[7]); $i <= 8; $i++) {
            print IDX ' ';
          }
          print IDX ' '.localtime($src[9]);
          copy_ref($src.$ent, $dst.$ent, 0);
        }
        print IDX "\n";
      }
    }
    closedir(DIR);
    print IDX '</PRE><HR></BODY></HTML>'."\n";
    close(IDX);
  }
  else {
    my @src = stat($src);
    my @dst = stat($dst);
    if (0 > $#src) {
      print STDERR "Copy: no ".$src."\n";
    }
    elsif (0 > $#dst || $src[9] > $dst[9]) {
      #print "Copy $src to $dst\n";
      open(INF, $src) || die("Cannot read to copy ".$src);
      binmode(INF);
      $_ = join('', <INF>);
      close(INF);
      $_ = filter_lang(\$_, '') if ($lng);
      open(OUT, ">".$dst) || die("Cannot write to copy ".$dst);
      binmode(OUT);
      print OUT $_;
      close(OUT);
      utime($src[9], $src[9], $dst) || die("Cannot utime($dst)");
      chown($src[4], $src[5], $dst) || die("Cannot chown($dst)");
      chmod($src[2] & 07777, $dst) || die("Cannot chmod($dst)");
    }
  }
}

sub work_ref($$$$) {
  my $ret = shift;
  my $dir = shift;
  my $clk = shift;
  my $lng = shift;

  if (!($ret =~ m#^\s*[^:]+:#s) && !($ret =~ m#^\s*\##s) && !($ret=~m#^\s*sven\-ola\*ät\*gmx\*de#)) {
    # This should be a local reference
    if (!($ret =~ m#\.html?#is) && -e $dir."/".$ret) {
      copy_ref($dir."/".$ret, $opt_o."/".$dir."/".$ret, $lng);
      $_ = $ret;
      if (s/_white\.gif$/_red.gif/is) {
        copy_ref($dir."/".$_, $opt_o."/".$dir."/".$_, 0);
      }
      # Special for onclick wich popups bigger screenshots
      if ($clk =~ m#replace\s*\((([^\(]+\([^\)]+\))?[^\)]+)#s) {
        my $clk = $1;
        if ($clk =~ m#'([^']+)'.*?'([^']+)'#s) {
          my $s = $1."\$";
          my $r = $2;
          $s =~ s/\\+//gs;
          $s =~ s/\./\\$&/gs;
          $_ = $ret;
          if (s/$s/$r/is) {
            if (-f $dir."/".$_) {
              copy_ref($dir."/".$_, $opt_o."/".$dir."/".$_, 0);
            }
            else {
              print STDERR "Copy_ref: no ".$dir."/".$_."\n";
            }
          }
        }
      }
    }
    elsif(!($ret =~ m#\.html?(\?.*)?$#is) &&
      !($ret =~ m#rrd\-img/%s$#is) &&          # No msg if rrd link (cube-nylon)
      !($ret =~ m#cgi\-bin/index$#is))         # No msg if admin link (cube-mtx)
    {
      print STDERR "Test: no ".$dir."/".$ret."\n";
    }
  }
  return $ret;
}

sub work_lang_att($) {
  my $ret = shift;
  my @lng = split(/(!([a-z\-]{2,5}):)/io, $ret);
  my $fnd = "";
  my $bak = "";
  for(my $i = 1; $i <= $#lng; $i += 3) {
    if (uc($lng[$i + 1]) eq uc($opt_l)) {
      $fnd = $lng[0].$lng[$i + 2];
      if (defined($opt_p) && $opt_p) {
        print PRT "$fnd\n";
      }
    }
    elsif (uc($lng[$i + 1]) eq uc(BAKLANG)) {
      $bak = $lng[0].$lng[$i + 2];
    }
  }
  if ("" ne $fnd) {
    $ret = $fnd;
  }
  elsif("" ne $bak) {
    $ret = $bak;
  }
  return $ret;
}

sub work_att($$$$$$) {
  my $ret = shift;
  my $att = shift;
  my $dir = shift;
  my $clk = shift;
  my $lng = shift;
  my $sep = shift;

  if ($dir ne '' && ($att =~ m#^(src|href|action|background)$#is)) {
    $ret = work_ref($ret, $dir, $clk, $lng);
  }
  elsif ($att =~ m#^(title|alt|value)$#is) {
    $ret = work_lang_att($ret);
    $att_alt = $ret if ($att =~ m#^(alt)$#is);
    $att_tit = $ret if ($att =~ m#^(title)$#is);
  }
  if ($ret =~ s#&quot;#"#gs) {
    die("Attr with wrong separator: $ret") if ($ret =~ m#'#s);
    $sep = "'";
  }
  $ret =~ s#&gt;#>#gs;
  $ret =~ s#&lt;#<#gs;
  $ret =~ s#&amp;#&#gs;
  return $sep.$ret.$sep;
}

sub work_tag($$) {
  my $ret = shift;
  my $dir = shift;

  my $clk = "";
  if ($ret =~ m#\bonclick\s*=\s*"([^"]+)"#is) {
    # Filter warning messages built in to ONCLICK handlers for pictures such as
    # ONCLICK="if(0<=this.src.search(new RegExp('\\.jpg'))){this.width=368;this.height=446;this.src=this.src.replace(new RegExp('\\.jpg'),'.gif');}else{this.width=123;this.height=149;this.src=this.src.replace(new RegExp('\\.gif'),'.jpg');}return false;"
    $clk = $1;
  }
  my $lng = ($ret =~ m#\brel\s*=\s*"multilang"#is);
  local $att_alt = "";
  local $att_tit = "";
  $ret =~ s#(\b([^\s=>]+)\s*=\s*)((["'])([^\4]*?)\4|(\S+))#$1.(defined($4)?work_att($5, $2, $dir, $clk, $lng, $4):work_att($6, $2, $dir, $clk, $lng, ''))#iegs;
  if ("" ne $att_alt && "" eq $att_tit) {
    my $sep=$4;
    $ret =~ s#(/\s*)?>\s*$# TITLE=$sep$att_alt$sep$&#s;
  }
  return $ret;
}

sub work_lang_span($$$) {
  my $beg = shift;
  my $txt = shift;
  my $end = shift;
  if ($beg =~ s#\s*\blang\s*=\s*((["'])([^\2]*?)\2|(\S+))##is) {
    my $lng = defined($2)?$3:$4;
    $lng =~ s#^\s+##s;
    $lng =~ s#\s+$##s;
    if (lc($lng) ne lc($opt_l)) {
      return '';
    }
    if ($beg =~ m#^\s*<\s*span\s*>\s*$#is) {
      $beg = '';
      $end = '';
    }
  }
  return $beg.$txt.$end;
}

sub work_onload($$) {
  my $att = shift;
  my $ret = shift;
  if (($att =~ m/^\s*if\s*\(/s) && ($att =~ m/\balert\s*\(/s)) {
    # Delete the image size alerts for WRT output
    $ret = "";
  }
  return $ret;
}

sub del_crlf($) {
  my $ret = shift;
  $ret =~ s#[\s\r\n]+# #gs;
  return $ret;
}

sub unentity($) {
  my $ret = shift;
  $ret =~ s/&#(\d+);/chr($1)/iegs;
  return $ret;
}

sub unentity_quotes($) {
  my $ret = shift;
  return "&amp;" if (38 == $ret);
  return "&lt;" if (60 == $ret);
  return "&gt;" if (62 == $ret);
  return chr($ret);
}

sub filter_lang($$) {
  my $ref = shift; # Reference to source html
  my $dir = shift; # Output directory (or '' if unused)

  my @htm = split(/(<\s*script\b[^>]*>.*?<\s*\/\s*script\b[^>]*>)/is, $$ref);
  for(my $i = 0; $i <= $#htm; $i++) {
    if (0 == $i % 2) {
      $htm[$i] =~ s/&#x00A0;/ /igs;
      @_ = split(/(<[^>]*>)/, $htm[$i]);
      for(my $j = 0; $j <= $#_; $j+=2) {
        $_[$j] =~ s/&#(\d+);/unentity_quotes($1)/iegs;
      }
      $htm[$i] = join('', @_);
      # Copy all files in HREF and SRC attributes
      ($htm[$i] =~ s#<\s*[^\s>]+\b[^>]*>#work_tag($&, $dir)#iegs) if ('' ne $dir);
      # Filter language <SPAN> and <OPTION> tags
      $htm[$i] =~ s#(<\s*span\b[^>]*>)(.*?)(<\s*/\s*span\b[^>]*>)#work_lang_span($1, $2, $3)#iegs;
      $htm[$i] =~ s#(<\s*option\b[^>]*>)(.*?)(<\s*/\s*option\b[^>]*>)#$1.work_lang_att($2).$3#iegs;
    }
    else {
      $htm[$i] =~ s#\%\%LANG\%\%#$opt_l#gs;
    }
  }
  return join('', @htm);
}

sub filter_rrd($) {
  my $ref = shift; # Reference to source html
  return '#!/usr/bin/rrdcgi'."\n".
    "\n".
    '<RRD::GOODFOR -600>'."\n".
    "\n".
    $$ref;
}

sub filter_cgi($$) {
  my $ref = shift; # Reference to source html
  my $oct = shift; # Output content type?
  # Shell commands are written in comments, activate them
  my @arr = split(/\s*<\s*SCRIPT\s+language\s*=\s*"shell"[^>]*>(.*?)<\s*\/\s*SCRIPT\b[^>]*>\s*/is, $$ref);
  for(my $i = 0; $i <= $#arr; $i++) {
    $arr[$i] =~ s/^\s*//s;
    $arr[$i] =~ s/\s*$//s;
    if (1 == ($i % 2)) {
      $arr[$i] = "\n".$arr[$i]."\n";
    }
    else {
      $arr[$i] =~ s#'([^'"%]+)\%ENDATTR\%([^']*)'#"'".$1."' ".unentity($2)#iegs;
      $arr[$i] =~ s#"([^'"%]+)\%ENDATTR\%([^"]*)"#'"'.$1.'" '.unentity($2)#iegs;
      $arr[$i] =~ s#\$\([^\)]+\)#del_crlf($&)#egs;
      if ("" ne $arr[$i]) {
        $arr[$i] = "\ncat<<EOF\n".$arr[$i]."\nEOF\n";
      }
    }
  }
  my $ret = '#!/bin/sh'."\n";
  if ($oct) {
    $ret .= 'echo Content-type: text/html'."\n";
    $ret .= "echo\n";
  }
  $ret .= join('', @arr);
  $ret =~ s#\s*<\s*SCRIPT\s+language\s*=\s*"inline"[^>]*>(.*?)<\s*/\s*SCRIPT\b[^>]*>\s*#$1#igs;
  while($ret =~ s#((/\s*)?>)\s*<\s*SCRIPT\s+language\s*=\s*"inlineattribut"[^>]*>(.*?)<\s*/\s*SCRIPT\b[^>]*>\s*#$3$1#igs) {}
  return $ret;
}

sub work_include($$$$$) {
  my $dir = shift;
  my $beg = shift;
  my $ref = shift;
  my $end = shift;
  my $ref_idx = shift;
  if ($ref =~ m#\bclass\s*=\s*"color"#is) {
    if ($beg =~ m#\bid\s*=\s*"idx\-(\d+)"#is) {
      $$ref_idx = $1;
    }
    else {
      $$ref_idx += 5;
    }
    ($ref =~ m#\bhref\s*=\s*"([^"]+)"#is) || die("Oops: No HREF");
    my $url = $1;
    if (!($url =~ m#[\\/:]#is)) {
      $url =~ s#\.[^\.]*$##is;
      $url = sprintf("%02d-%s", $$ref_idx, $url);
      open(OUT, ">".$opt_o."/".$dir."/".$url) ||
        die("Cannot write ".$opt_o."/".$dir."/".$url);
      print OUT $beg.$ref.$end;
      close(OUT);
      $beg = '';
      $ref = $incret;
      $end = '';
      $incret = '';
    }
  }
  return $beg.$ref.$end;
}

sub filter_formtable($$$) {
  my $beg = shift;
  my $cnt = shift;
  my $end = shift;
  if (!($end =~ m#^<\s*/#s)) {
    print STDERR "Warning: table in table used\n";
  }
  else {
    for(my $i = 2; $i >=0 ; $i--) {
      $beg = '<TABLE CLASS="shadow'.$i.'" CELLPADDING="0" CELLSPACING="0"><TR><TD>'.$beg;
      $end .= '</TD></TR></TABLE>';
    }
  }
  return $beg.$cnt.$end;
}

sub work_file($$) {
  my $dir = shift;
  my $inf = shift;

  if (!($inf =~ m/^template[^\.]*\.html?$/is)) {
    #print "Read(".$dir."/".$inf.")\n";
    open(INF, $dir."/".$inf) || die("Cannot read ".$dir."/".$inf);
    my $pag = join("", <INF>);
    close(INF);

    $pag =~ s#(<\s*script\b[^>]*>)\s*<!\[CDATA\[#$1#gs;
    $pag =~ s#\]\]>\s*(<\s*/\s*script\b[^>]*>)#$1#gs;
    $pag =~ s/\s+onload\s*=\s*"([^"]+)"/work_onload($1, $&)/egis;
    $pag =~ s#(<\s*table\b[^>]*?\s+class\s*=\s*["']form[^"']*["'][^>]*>)(.*?)(<\s*/?\s*table\b[^>]*>)#filter_formtable($1, $2, $3)#egis;
    ($pag =~ m/<\s*h1\b[^>]*>(.*?)<\s*\/\s*h1\b[^>]*>/is) || die("No H1 in $inf");
    my $tit = $1;
    $tit = filter_lang(\$tit, '');
    $tit =~ s#<[^>]+>##gs;
    $tit =~ s#\(\s*\)##gs;
    $tit =~ s#^\s+##gs;
    $tit =~ s#\s+$##gs;

    my $htm = $TPLHTM;
    ($pag =~ m/<\s*body\b[^>]*>(.*?)<\s*\/\s*body\b[^>]*>/is) || die;
    my $hed = $`;
    my $bdy = $1;
    my $oct = 1;
    if (!(defined($opt_c) && $opt_c) &&
      (defined($opt_s) && $opt_s ||
       defined($opt_S) && $opt_S) &&
      ($dir =~ m#[\/\\\:]cgi\-bin$#s))
    {
      if (!defined($TPLFST{$opt_o."/".$dir})) {
        $TPLFST = $opt_o."/".$dir = 1;
        $htm =~ s/\%DATE\%/\$DATE/igs;
        $htm =~ s/\%TITLE\%/\$TITLE/igs;
        $htm = filter_lang(\$htm, $dir);
        my $pat =
          '(<\s*TR\b[^>]*>\s*'.
          '<\s*TD\b[^>]*>\s*'.
          '<\s*DIV\b[^>]*>\s*'.
          '<\s*A\b)([^>]*)(>\s*'.
          '<\s*IMG\b[^>]*>.*?'.
          '<\s*/\s*A\b[^>]*>\s*'.
          '<\s*/\s*DIV\b[^>]*>\s*'.
          '<\s*/\s*TD\b[^>]*>\s*'.
          '<\s*/\s*TR\b[^>]*>\s*)';
        my $idx = 0;
        local $incret = '<SCRIPT LANGUAGE="shell">for inc in /www/cgi-bin/[0-9][0-9]-*;do cat $inc;done</SCRIPT>';
	$htm =~ s#$pat#work_include($dir, $1, $2, $3, \$idx)#oiegs;
        if (defined($opt_s) && $opt_s) {
          # Do not write cgi-bin-(pre|post).sh if opt_S
          my @htm = split(/\%BODY\%/is, $htm);
          (1 == $#htm) || die("No \%BODY\$ in template.html");
          for(my $i = 0; $i < 2; $i++) {
            my $out = ($i == 0 ? "cgi-bin-pre.sh" : "cgi-bin-post.sh");
            if (!defined($TPLFST{$opt_o."/".$dir."/".$out})) {
              $TPLFST{$opt_o."/".$dir."/".$out} = 1;
              open(OUT, ">".$opt_o."/".$dir."/".$out) ||
                die("Cannot write ".$opt_o."/".$dir."/".$out);
              binmode(OUT); # Windows: Do not change \n to \r\n
              $htm[$i] =~ s/[\t ]*\r\n[\t ]*/\n/gs;
              print OUT filter_cgi(\$htm[$i], $oct);
              close(OUT);
            }
            $oct = 0;
          }
        }
      }
      $htm = '<SCRIPT LANGUAGE="shell">export DATE="%DATE%"'."\n".
        'export TITLE="%TITLE%"'."\n".'. ${0%/*}/cgi-bin-pre.sh</SCRIPT>'.
        $bdy.'<SCRIPT LANGUAGE="shell">. ${0%/*}/cgi-bin-post.sh</SCRIPT>';
    }
    else {
      ($htm =~ s/\%BODY\%/$bdy/is) || die("No \%BODY\% in template.html");
    }
    my @tme = localtime((stat($dir."/".$inf))[9]);
    my $tme = $tme[3].".".(1 + $tme[4]).".".(1900 + $tme[5]);
    $htm =~ s/\%DATE\%/$tme/igs;
    $htm =~ s/\%TITLE\%/$tit/igs;

    # Copy files mentioned in <link> attributes
    $hed =~ s#<\s*link\b[^>]*>#work_tag($&, $dir)#iegs;

    $htm = filter_lang(\$htm, $dir);

    # Special for cgi-bin urls (will be executed from httpd)
    if (!(defined($opt_c) && $opt_c) && (($inf =~ m#cgi\-bin#s) ||
      ($dir =~ m#[\/\\\:]cgi\-bin$#s)))
    {
      if ($inf =~ m#\.rrd\.html?#is) {
        $htm = filter_rrd(\$htm);
      }
      else {
        $htm = filter_cgi(\$htm, $oct);
      }
    }

    #print "Write(".$opt_o."/".$dir."/".$inf.")\n";
    open(OUT, ">".$opt_o."/".$dir."/".$inf) ||
      die("Cannot write ".$opt_o."/".$dir."/".$inf);
    binmode(OUT); # Windows: Do not change \n to \r\n
    $htm =~ s/[\t ]*\r\n[\t ]*/\n/gs;
    print OUT $htm;
    close(OUT);
  }
}

sub work_dir {
  my $dir = shift;
  local $TPLHTM = "";
  my $dstdir = $opt_o."/".$dir;
  $dstdir =~ s#\.+$##s;
  mkdir($dstdir) if (! -d $dstdir);
  if (opendir(DIR, $dir)) {
    my @dir = readdir(DIR);
    closedir(DIR);
    foreach my $ent(@dir) {
      if (-d $dir."/".$ent) {
        my $pat = $opt_o;
        my $end = "";
        $pat =~ s#^([^\\\/\:]*[\\\/\:])*##s;
        if ($pat =~ s#\-[0-9a-z]{2,4}$#-#is) {
          $end = '[0-9a-z]{2,4}';
        }
        $pat=~ s#[^a-z0-9]#\\$&#igs;
        $pat = '^'.$pat.$end.'$';
        if (!($ent =~ m#$pat#is) && lc($ent) ne "cvs" && $ent ne "." &&
          $ent ne ".." && $dir."/".$ent ne "./_deleted")
        {
          work_dir($dir."/".$ent);
        }
      }
      elsif(-f $dir."/".$ent && ($ent =~ m/\.html?$/is)) {
        if ($TPLHTM eq "") {
          my $add = '';
          if (defined($opt_t) && "" ne $opt_t) {
            $add = '-'.$opt_t;
          }
          open(INF, $dir."/template$add.html") ||
            die("Cannot read ".$dir."/template$add.html");
          $TPLHTM = join("", <INF>);
          close(INF);
          # Firefix: No <TABLE HEIGTH="100%"> if unknown doctype
          $TPLHTM =~ s#<\s*!\s*doctype\b[^>]*>\s*##igs;
          $TPLHTM =~ s#(<\s*script\b[^>]*>)\s*<!\[CDATA\[#$1#gs;
          $TPLHTM =~ s#\]\]>\s*(<\s*/\s*script\b[^>]*>)#$1#gs;
        }
        work_file($dir, $ent);
      }
    }
  }
}

$SIG{__WARN__} = sub {};
Getopts("cl:o:p:sSt:hh") || die;
$SIG{__WARN__} = '';
$opt_l = DEFLANG if (!defined($opt_l) || !$opt_l);
$opt_o = DEFODIR."-".$opt_l if (!defined($opt_o) || !$opt_o);

if (defined($opt_h) && $opt_h) {
  print STDERR "*** HTML Template merger ***\n";
  print STDERR "\n";
  print STDERR "USAGE:\t$0 Merges HTML to $opt_o\n";
  print STDERR "-c\tno Cgi-Convert for preview\n";
  print STDERR "-h\tHelp message\n";
  print STDERR "-l xx\tLanguage filter\n";
  print STDERR "-o dir\tOutput directory\n";
  print STDERR "-p file\tPrint Title|Alt|Value to file\n";
  print STDERR "-s\tSplit /cgi-bin/ to several scripts\n";
  print STDERR "-S\tSplit /cgi-bin/ but dont add scripts\n";
  print STDERR "-t add\tTemplate filename addon\n";
  exit;
}

if (defined($opt_p) && $opt_p) {
  undef $opt_p if (!open(PRT, ">$opt_p"));
}
work_dir(".");
if (defined($opt_p) && $opt_p) {
  close(PRT);
}
