Name: xymon-client
Version: 4.3.30
#Release: 1
Release: %{version}
URL: http://xymon.sourceforge.net/
License: GPL-2.0
Source: xymon-%{version}.tar.gz
Source2: xymon.logrotate
Source3: prepare-env.sh
Source4: xymon-client.default
Source5: xymon-client.service

#Summary: Xymon network monitor

Requires: shadow-utils
Requires: systemd
%{?systemd_requires}

BuildRoot: /tmp/xymon-root

BuildRequires: libtirpc-devel
%if %{defined suse_version}
BuildRequires: pwdutils
BuildRequires: libopenssl-devel
BuildRequires: openldap2-devel
%else
BuildRequires: shadow-utils
BuildRequires: openssl-devel
BuildRequires: openldap-devel
%endif

BuildRequires: pcre-devel
BuildRequires: rrdtool-devel
BuildRequires: systemd

Summary: Xymon client reporting data to the Xymon server
Group: Applications/System
Conflicts: xymon


%description
This package contains a client for the Xymon (previously known
as Hobbit) monitor. Clients report data about the local system to
the monitor, allowing it to check on the status of the system
load, filesystem utilisation, processes that must be running etc.


%changelog
* Mon Oct 02 2019 Jochen Becker <jochen.becker@tu-darmstadt.de> 1
- Updated to xymon version 4.3.30
* Thu Oct 10 2018 Jan Hohmann <jochen.becker@hrz.tu-darmstadt.de> 1
- Patch for SLES 15 and LEAP 15 see http://lists.xymon.com/archive/2017-February/044369.html 
* Thu Jul 27 2017 Jan Hohmann <jan.hohmann@hrz.tu-darmstadt.de> 1
- Migrated from SysVinit to systemd
* Mon May 30 2017 Jochen Becker <jochen.becker@hrz.tu-darmstadt.de> 1
- Updated to xymon version 4.3.28
- fixed License Information to SuSE buildservice notation
- recommend for logrotate added for SuSE Versions
* Mon May 29 2017 Jochen Becker <jochen.becker@hrz.tu-darmstadt.de> 1
- SLES 12.2 added
* Thu Apr 28 2016 Jan Hohmann <jan.hohmann@hrz.tu-darmstadt.de> 1
- Updated to xymon version 4.3.27
* Fri Mar 13 2015 Mike Williams <mike.williams@comodo.com> 1
- Initial RPM release


%prep

%setup -n xymon-%{version}
	ENABLESSL=y \
	ENABLELDAP=y \
	ENABLELDAPSSL=y \
	XYMONUSER=xymon \
	XYMONTOPDIR=/usr/lib/xymon/client \
	XYMONVAR=/var/lib/xymon \
	XYMONLOGDIR=/var/log/xymon \
	XYMONHOSTNAME=localhost \
	XYMONHOSTIP=127.0.0.1 \
	MANROOT=/usr/share/man \
	CONFTYPE=server \
	./configure --client


%build
PKGBUILD=1 make


%install
INSTALLROOT=$RPM_BUILD_ROOT PKGBUILD=1 make install
MANROOT=$RPM_BUILD_ROOT/usr/share/man PKGBUILD=1 make -C common install-man
mkdir -p $RPM_BUILD_ROOT/etc/logrotate.d
cp %{SOURCE2} $RPM_BUILD_ROOT/etc/logrotate.d/xymon-client
mkdir -p $RPM_BUILD_ROOT/etc/default
cp %{SOURCE4} $RPM_BUILD_ROOT/etc/default/xymon-client
rmdir $RPM_BUILD_ROOT/usr/lib/xymon/client/tmp
mkdir $RPM_BUILD_ROOT/tmp
cd $RPM_BUILD_ROOT/usr/lib/xymon/client && ln -sf /tmp tmp
rmdir $RPM_BUILD_ROOT/usr/lib/xymon/client/logs
mkdir -p $RPM_BUILD_ROOT/var/log/xymon
cd $RPM_BUILD_ROOT/usr/lib/xymon/client && ln -sf ../../../../var/log/xymon logs
mv $RPM_BUILD_ROOT/usr/lib/xymon/client/etc/xymonclient.cfg /tmp/xymonclient.cfg.$$
cat /tmp/xymonclient.cfg.$$ | \
sed -e 's!^XYMSRV=.*!include /var/run/xymonclient-runtime.cfg!' | \
sed -e 's!^XYMSERVERS=.*!include /etc/default/xymon-client!' \
>$RPM_BUILD_ROOT/usr/lib/xymon/client/etc/xymonclient.cfg
rm /tmp/xymonclient.cfg.$$
install -D -m 644  %{SOURCE5} %{buildroot}%{_unitdir}/xymon-client.service

cp %{SOURCE3} $RPM_BUILD_ROOT/usr/lib/xymon/client/prepare-env.sh
chmod +x $RPM_BUILD_ROOT/usr/lib/xymon/client/prepare-env.sh

%clean
rm -rf $RPM_BUILD_ROOT


%pre
getent group xymon 1>/dev/null 2>&1
if [ $? -ne 0 ]
then
	groupadd -r xymon || true
fi
id xymon 1>/dev/null 2>&1
if [ $? -ne 0 ]
then
	useradd -r -g xymon -c "Xymon user" -d /usr/lib/xymon xymon
fi
%service_add_pre xymon-client.service

%post
/usr/bin/systemctl enable xymon-client
#%service_add_post xymon-client.service

%preun
%service_del_preun xymon-client.service

%postun
%service_del_postun xymon-client.service

%files
%defattr(-, root, root)
%attr(-, root, root) %doc README README.CLIENT Changes* COPYING CREDITS RELEASENOTES
%{_unitdir}/xymon-client.service
%attr(-, root, root) %config /etc/logrotate.d/xymon-client
%attr(644, root, root) %config /etc/default/xymon-client
%attr(-, xymon, xymon) /usr/lib/xymon
%attr(755, xymon, xymon) %dir /var/log/xymon/
%attr(644, root, root) %doc /usr/share/man/man1/*.1.gz
%attr(644, root, root) %doc /usr/share/man/man5/*.5.gz
%attr(644, root, root) %doc /usr/share/man/man7/*.7.gz
%attr(644, root, root) %doc /usr/share/man/man8/*.8.gz
