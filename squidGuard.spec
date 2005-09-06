# $Id: squidGuard.spec,v 1.1 2005/09/06 10:50:41 oliver Exp $

%define			_dbhomedir		%{_var}/lib/%{name}

%define			_dbrpmver		%(eval "rpm -q --queryformat \"%{VERSION}\" db4")

Name:			squidGuard
Version:		1.2.0
Release:		11
Summary:		Filter, redirector and access controller plugin for squid

Group:			System Environment/Daemons
License:		GPL

Source0:		http://ftp.teledanmark.no/pub/www/proxy/%{name}/%{name}-%{version}.tar.gz
Source1:		squidGuard.logrotate
Source2:		http://ftp.teledanmark.no/pub/www/proxy/%{name}/contrib/blacklists.tar.gz
Source3:		http://cuda.port-aransas.k12.tx.us/squid-getlist.html

Patch0:			squidGuard-destdir.patch
Patch1:			squidGuard-paths.patch
Patch2:			squidguard-1.2.0-db4.patch
Patch3:			squid-getlist.html.patch
URL:			http://www.squidguard.org/

BuildRoot:		%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:	db4-devel
Requires:		squid

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
%patch0 -p1 -b .destdir
%patch1 -p1 -b .paths
%if "%{_dbrpmver}" != "4.0.14"
%patch2 -p0 -b .db4
%endif
%patch3 -p0

%build
%configure \
	--with-sg-config=%{_sysconfdir}/squid/squidGuard.conf \
	--with-sg-logdir=%{_var}/log/squid \
	--with-sg-dbhome=%{_dbhomedir}
	
%{__make} %{?_smp_mflags} LIBS=-ldb

%install
%{__rm} -rf $RPM_BUILD_ROOT

%{__make} DESTDIR=$RPM_BUILD_ROOT install

%{__install} -p -D -m 0644 %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/squidGuard
%{__install} -p -D -m 0644 samples/sample.conf $RPM_BUILD_ROOT%{_sysconfdir}/squid/squidGuard.conf
%{__install} -p -D -m 0644 %{SOURCE2} $RPM_BUILD_ROOT%{_dbhomedir}/blacklists.tar.gz

# Don't use SOURCE3, but use the allready patched one #165689, also install it with perm 755 not 750
%{__install} -p -D -m 0755 squid-getlist.html $RPM_BUILD_ROOT%{_sysconfdir}/cron.daily/squidGuard

pushd $RPM_BUILD_ROOT%{_dbhomedir}
tar xfz $RPM_BUILD_ROOT%{_dbhomedir}/blacklists.tar.gz
popd

sed -i "s,dest/adult/,blacklists/porn/,g" $RPM_BUILD_ROOT%{_sysconfdir}/squid/squidGuard.conf

%clean
%{__rm} -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%doc samples/*.conf
%doc samples/*.cgi
%doc samples/dest/blacklists.tar.gz
%doc COPYING GPL
%doc doc/*.txt doc/*.html doc/*.gif
%{_bindir}/*
%config(noreplace) %{_sysconfdir}/squid/squidGuard.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/squidGuard
%config(noreplace) %{_sysconfdir}/cron.daily/squidGuard
%{_dbhomedir}/

%changelog
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
