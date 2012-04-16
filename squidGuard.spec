%define _hardened_build 1
%define _default_patch_fuzz 2
# $Id: squidGuard.spec,v 1.22 2009/10/26 13:30:17 limb Exp $

%define			_dbtopdir		%{_var}/%{name}
%define			_dbhomedir		%{_var}/%{name}/blacklists
%define			_cgibin			/var/www/cgi-bin

Name:			squidGuard
Version:		1.4
Release:		12%{?dist}
Summary:		Filter, redirector and access controller plugin for squid

Group:			System Environment/Daemons
License:		GPLv2

Source0:		http://www.squidguard.org/Downloads/squidGuard-%{version}.tar.gz
Source1:		squidGuard.logrotate
Source2:		http://squidguard.mesd.k12.or.us/blacklists.tgz
Source3:		http://cuda.port-aransas.k12.tx.us/squid-getlist.html

# K12LTSP stuff
Source100:		squidGuard.conf
Source101:		update_squidguard_blacklists
Source102:		squidguard
Source103:		transparent-proxying

# SELinux (taken from K12LTSP package)
#Source200:		squidGuard.te
#Source201:		squidGuard.fc

#Patch0:			squidGuard-upstream.patch
#Patch1:			squidGuard-paths.patch
Patch2:			squid-getlist.html.patch
Patch3:			squidGuard-perlwarning.patch
#Patch4:			squidGuard-sed.patch
Patch5:			squidGuard-makeinstall.patch
#Patch6:			squidGuard-1.3-SG-2008-06-13.patch
Patch7:			squidGuard-1.4-20091015.patch
Patch8:			squidGuard-1.4-20091019.patch

URL:			http://www.squidguard.org/

BuildRoot:		%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:	bison, byacc, openldap-devel, flex, libdb-devel
Requires:		squid
#Requires(post):	%{_bindir}/chcon
Requires(post):	/sbin/chkconfig

%description
squidGuard can be used to 
- limit the web access for some users to a list of accepted/well known
  web servers and/or URLs only.
- block access to some listed or blacklisted web servers and/or URLs
  for some users.
- block access to URLs matching a list of regular expressions or words
  for some users.
- enforce the use of domainnames/prohibit the use of IP address in
  URLs.
- redirect blocked URLs to an "intelligent" CGI based info page.
- redirect unregistered user to a registration form.
- redirect popular downloads like Netscape, MSIE etc. to local copies.
- redirect banners to an empty GIF.
- have different access rules based on time of day, day of the week,
  date etc.
- have different rules for different user groups.
- and much more.. 

Neither squidGuard nor Squid can be used to
- filter/censor/edit text inside documents 
- filter/censor/edit embeded scripting languages like JavaScript or
  VBscript inside HTML

%prep
%setup -q
%{__cp} %{SOURCE3} .
#%patch0 -p1
#%patch1 -p1 -b .paths
%patch2 -p0
%patch3 -p2
#%patch4 -p1
%patch5	-p1
#%patch6 -p0
%patch7 -p0
%patch8 -p0

%{__cp} %{SOURCE100} ./squidGuard.conf.k12ltsp.template
%{__cp} %{SOURCE101} ./update_squidguard_blacklists.k12ltsp.sh

%build
%configure \
	--with-sg-config=%{_sysconfdir}/squid/squidGuard.conf \
	--with-sg-logdir=%{_var}/log/squidGuard \
	--with-sg-dbhome=%{_dbhomedir} \
	--with-db-inc=%{_includedir}/db4.6.21 \
	--with-db-lib=%{_libdir}/db4.6.21
	
#%{__make} %{?_smp_mflags}
%{__make}

pushd contrib
%{__make} %{?_smp_mflags}
popd

%install
%{__rm} -rf $RPM_BUILD_ROOT

#%{__make} DESTDIR=$RPM_BUILD_ROOT install
# This broke as of 1.2.1.
%{__install} -p -D -m 0755 src/squidGuard $RPM_BUILD_ROOT%{_bindir}/squidGuard

%{__install} -p -D -m 0644 %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/squidGuard
%{__install} -p -D -m 0644 samples/sample.conf $RPM_BUILD_ROOT%{_sysconfdir}/squid/squidGuard.conf
%{__install} -p -D -m 0644 %{SOURCE2} $RPM_BUILD_ROOT%{_dbtopdir}/blacklists.tar.gz

# Don't use SOURCE3, but use the allready patched one #165689
%{__install} -p -D -m 0755 squid-getlist.html $RPM_BUILD_ROOT%{_sysconfdir}/cron.daily/squidGuard

#%{__install} -p -D %{SOURCE200} $RPM_BUILD_ROOT%{_sysconfdir}/selinux/targeted/src/policy/domains/program/squidGuard.te
#%{__install} -p -D %{SOURCE201} $RPM_BUILD_ROOT%{_sysconfdir}/selinux/targeted/src/policy/file_contexts/program/squidGuard.fc

%{__install} -p -d $RPM_BUILD_ROOT%{_cgibin}
%{__install} samples/squid*cgi $RPM_BUILD_ROOT%{_cgibin}

%{__install} contrib/hostbyname/hostbyname $RPM_BUILD_ROOT%{_bindir}
%{__install} contrib/sgclean/sgclean $RPM_BUILD_ROOT%{_bindir}

%{__install} -p -D -m 0755 %{SOURCE102} $RPM_BUILD_ROOT%{_initrddir}/squidGuard
%{__install} -p -D -m 0755 %{SOURCE103} $RPM_BUILD_ROOT%{_initrddir}/transparent-proxying

#pushd $RPM_BUILD_ROOT%{_dbhomedir}
tar xfz $RPM_BUILD_ROOT%{_dbtopdir}/blacklists.tar.gz
#popd

sed -i "s,dest/adult/,blacklists/porn/,g" $RPM_BUILD_ROOT%{_sysconfdir}/squid/squidGuard.conf

%{__install} -p -D -m 0644 samples/babel.* $RPM_BUILD_ROOT%{_cgibin}

mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/log/squidGuard
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/log/squid
ln -s ../squidGuard/squidGuard.log  $RPM_BUILD_ROOT%{_localstatedir}/log/squid/squidGuard.log

%clean
%{__rm} -rf $RPM_BUILD_ROOT

%post
# fix SELinux bits
#%{_bindir}/chcon -R system_u:object_r:squid_cache_t /var/squidGuard >/dev/null 2>&1
#%{_bindir}/chcon -R system_u:object_r:squid_log_t /var/log/squidGuard >/dev/null 2>&1

# do we need a new config file?
if [ -s %{_sysconfdir}/squid/squidGuard.conf ]; then
	CONFFILE="%{_sysconfdir}/squid/squidGuard.conf.rpmnew"
    echo "/etc/squid/squidGuard.conf created as /etc/squid/squidGuard.conf.rpmnew"
else
	CONFFILE="/etc/squid/squidGuard.conf"
fi
cat %{_docdir}/%{name}-%{version}/squidGuard.conf.k12ltsp.template | \
	sed s/SERVERNAME/$HOSTNAME/g > $CONFFILE

/sbin/chkconfig --add squidGuard
/sbin/chkconfig --add transparent-proxying

# reload SELinux policies
#echo "Loading new SELinux policy"
#pushd %{_sysconfdir}/selinux/targeted/src/policy/
#%{__make} load &> /dev/null
#popd

#### End of %post

%preun
if [ $1 = 0 ] ; then
    service squidGuard stop >/dev/null 2>&1
    /sbin/chkconfig --del squidGuard
	/sbin/chkconfig --del transparent-proxying
fi

%files
%defattr(-,root,root)
%doc samples/*.conf
%doc samples/*.cgi
%doc samples/dest/blacklists.tar.gz
%doc COPYING GPL 
%doc doc/*.txt doc/*.html doc/*.gif
%doc squidGuard.conf.k12ltsp.template
%{_bindir}/*
%config(noreplace) %{_sysconfdir}/squid/squidGuard.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/squidGuard
%config(noreplace) %{_sysconfdir}/cron.daily/squidGuard
%{_dbtopdir}/
#%{_sysconfdir}/selinux/targeted/src/policy/domains/program/squidGuard.te
#%{_sysconfdir}/selinux/targeted/src/policy/file_contexts/program/squidGuard.fc
%attr(0755,root,root) %{_cgibin}/*.cgi
%config(noreplace) %{_cgibin}/squidGuard.cgi
%{_cgibin}/babel.*
%{_initrddir}/squidGuard
%{_initrddir}/transparent-proxying
%{_localstatedir}/log/squidGuard
%{_localstatedir}/log/squid/squidGuard.log

%changelog
* Mon Apr 16 2012 Jon Ciesla <limburgher@gmail.com> - 1.4-12
- Build against libdb again.

* Fri Apr 13 2012 Jon Ciesla <limburgher@gmail.com> - 1.4-11
- Add hardened build.

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Oct 26 2009 Jon Ciesla <limb@jcomserv.net> - 1.4-8
- Applying upstream patches for CVE-2009-3700, BZ 530862.

* Thu Sep 24 2009 Jon Ciesla <limb@jcomserv.net> - 1.4-7
- Make squidGuard.cgi config(noreplace)
- Relocated logs, updated logrotate file.
- Updated blacklist URL.

* Wed Sep 09 2009 Jon Ciesla <limb@jcomserv.net> - 1.4-6
- Include babel files, BZ 522038.

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Mar 05 2009 Jon Ciesla <limb@jcomserv.net> - 1.4-4
- Initscript cleanup, BZ 247065.

* Tue Feb 24 2009 Jon Ciesla <limb@jcomserv.net> - 1.4-3
- Drop chcon Req.

* Mon Feb 23 2009 Jon Ciesla <limb@jcomserv.net> - 1.4-2
- Dropping selinux policy and chcon, BZ 486634.
- Fixed URL of Source0.

* Wed Feb 18 2009 Jon Ciesla <limb@jcomserv.net> - 1.4-1
- Update to 1.4, BZ 485530.
- Building against compat-db46 until next version.

* Wed Feb 11 2009 Jon Ciesla <limb@jcomserv.net> - 1.3-1
- Update to 1.3.
- Dropped paths, sed patches, applied upstream.
- New SG-2008-06-13 patch.
 
* Wed Feb 11 2009 Jon Ciesla <limb@jcomserv.net> - 1.2.1-2
- Fix sg-2008-06-13, BZ 452467.

* Wed Feb 11 2009 Jon Ciesla <limb@jcomserv.net> - 1.2.1-1
- Update to 1.2.1,  BZ 245377.
- Dropped upstream patch.
- Updated blacklists.

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1.2.0-18
- Autorebuild for GCC 4.3

* Wed Dec 05 2007 Release Engineering <rel-eng at fedoraproject dot org> - 1.2.0-17
 - Rebuild for deps

* Fri Nov 16 2007 John Berninger <john at ncphotography dot com> 1.2.0-16
- Fix perms on cgi-bin files

* Mon Mar 26 2007 John Berninger <jwb at redhat dot com>	1.2.0-15
- Assert ownership of /var/squidGuard - bz 233915

* Tue Aug 29 2006 John Berninger <jwb at redhat dot com>	1.2.0-14
- Bump release 'cause I forgot to add a patch file that's required

* Tue Aug 29 2006 John Berninger <jwb at redhat dot com>	1.2.0-13
- general updates to confirm build on FC5/FC6
- updates to BuildRequires

* Fri Sep 09 2005 Oliver Falk <oliver@linux-kernel.at>		- 1.2.0-12
- Make it K12LTSP compatible, so a possible upgrade doesn't break
  anything/much...
  - Add SELinux stuff
  - Move dbdir to /var/squidGuard/blacklists, instead of /var/lib/squidGuard
  - Added update script and template config from/for K12
  - Add perlwarnings and sed patch
  - Install cgis in /var/www/cgi-bin
  - Added initrd stuff
- Remove questionable -ldb from make
- Remove questionable db version check

* Tue Sep 06 2005 Oliver Falk <oliver@linux-kernel.at>		- 1.2.0-11
- More bugs from Bug #165689
  Install cron script with perm 755
  Don't use SOURCE3 in install section, we need to use the patched one
  
* Mon Sep 05 2005 Oliver Falk <oliver@linux-kernel.at>		- 1.2.0-10
- Include GPL in doc section

* Mon Sep 05 2005 Oliver Falk <oliver@linux-kernel.at>		- 1.2.0-9
- More 'bugs' from Bug #165689
  Make changed on squid-getlist.html a patch, as sources should
  match upstream sources, so they are wget-able...

* Mon Sep 05 2005 Oliver Falk <oliver@linux-kernel.at>		- 1.2.0-8
- Bug #165689

* Thu May 19 2005 Oliver Falk <oliver@linux-kernel.at>		- 1.2.0-7
- Update blacklists
- Cleanup specfile

* Fri Apr 08 2005 Oliver Falk <oliver@linux-kernel.at>		- 1.2.0-6
- Fix build on RH 8 with db 4.0.14, by not applying the db4 patch

* Mon Feb 21 2005 Oliver Falk <oliver@linux-kernel.at> 		- 1.2.0-5
- Specfile cleaning
- Make it build with db4 again, by adding the db4-patch

* Mon Apr 12 2002 Oliver Pitzeier <oliver@linux-kernel.at>	- 1.2.0-4
- Tweaks

* Mon Apr 08 2002 Oliver Pitzeier <oliver@linux-kernel.at> 	- 1.2.0-3
- Rebuild

* Mon Apr 08 2002 Oliver Pitzeier <oliver@linux-kernel.at> 	- 1.2.0-2
- Updated the blacklists and put it into the right place
  I also descompress them
- Added a new "forbidden" script - the other ones are too
  old and don't work.  

* Fri Apr 05 2002 Oliver Pitzeier <oliver@linux-kernel.at> 	- 1.2.0-1
- Update to version 1.2.0

* Fri Jun  1 2001 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de>
- cleaned up for rhcontrib

* Fri Oct 13 2000 Enrico Scholz <enrico.scholz@informatik.tu-chemnitz.de>
- initial build
