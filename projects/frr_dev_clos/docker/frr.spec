# configure options
#
# Some can be overridden on rpmbuild commandline with:
# rpmbuild --define 'variable value'
#   (use any value, ie 1 for flag "with_XXXX" definitions)
#
# E.g. rpmbuild --define 'release_rev 02' may be useful if building
# rpms again and again on the same day, so the newer rpms can be installed.
# bumping the number each time.

#################### FRRouting (FRR) configure options #####################
# with-feature options
%{!?with_babeld:        %global  with_babeld        0 }
%{!?with_bfdd:          %global  with_bfdd          0 }
%{!?with_bgp_vnc:       %global  with_bgp_vnc       0 }
%{!?with_cumulus:       %global  with_cumulus       0 }
%{!?with_eigrpd:        %global  with_eigrpd        1 }
%{!?with_fpm:           %global  with_fpm           0 }
%{!?with_ldpd:          %global  with_ldpd          0 }
%{!?with_multipath:     %global  with_multipath     256 }
%{!?with_nhrpd:         %global  with_nhrpd         0 }
%{!?with_ospfapi:       %global  with_ospfapi       0 }
%{!?with_ospfclient:    %global  with_ospfclient    0 }
%{!?with_pam:           %global  with_pam           0 }
%{!?with_pbrd:          %global  with_pbrd          0 }
%{!?with_pimd:          %global  with_pimd          0 }
%{!?with_vrrpd:         %global  with_vrrpd         0 }
%{!?with_rpki:          %global  with_rpki          0 }
%{!?with_rtadv:         %global  with_rtadv         0 }
%{!?with_watchfrr:      %global  with_watchfrr      0 }

# user and group
%{!?frr_user:           %global  frr_user           frr }
%{!?vty_group:          %global  vty_group          frrvty }

# path defines
%define     configdir   %{_sysconfdir}/%{name}
%define     _sbindir    /usr/lib/frr
%define     zeb_src     %{_builddir}/%{name}-%{frrversion}
%define     zeb_rh_src  %{zeb_src}/redhat
%define     zeb_docs    %{zeb_src}/doc
%define     frr_tools   %{zeb_src}/tools

# defines for configure
%define     rundir  %{_localstatedir}/run/%{name}

############################################################################

#### Version String tweak
# Remove invalid characters form version string and replace with _
%{expand: %%global rpmversion %(echo '7.3-dev-slankdev' | tr [:blank:]- _ )}
%define         frrversion   7.3-dev-slankdev

#### Check for systemd or init.d (upstart)
# Check for init.d (upstart) as used in CentOS 6 or systemd (ie CentOS 7)
%if 0%{?fedora} || 0%{?rhel} >= 7 || 0%{?suse_version} >= 1210
    %global initsystem systemd
%else
%if 0%{?rhel} && 0%{?rhel} < 7
    %global initsystem upstart
%else
    %{expand: %%global initsystem %(if [[ `/sbin/init --version 2> /dev/null` =~ upstart ]]; then echo upstart; elif [[ `readlink -f /sbin/init` = /usr/lib/systemd/systemd ]]; then echo systemd; elif [[ `systemctl` =~ -\.mount ]]; then echo systemd; fi)}
%endif
%endif

# If init system is systemd, then always enable watchfrr
%if "%{initsystem}" == "systemd"
    %global with_watchfrr 1
%endif

#### Check for RedHat 6.x or CentOS 6.x - they are too old to support PIM.
####   Always disable it on these old systems unconditionally
#
# if CentOS / RedHat and version < 7, then disable PIMd (too old, won't work)
%if 0%{?rhel} && 0%{?rhel} < 7
    %global  with_pimd  0
%endif

# misc internal defines
%{!?frr_uid:            %global  frr_uid            92 }
%{!?frr_gid:            %global  frr_gid            92 }
%{!?vty_gid:            %global  vty_gid            85 }

%define daemon_list zebra ripd ospfd bgpd isisd ripngd ospf6d pbrd staticd bfdd fabricd

%if %{with_ldpd}
    %define daemon_ldpd ldpd
%else
    %define daemon_ldpd ""
%endif

%if %{with_pimd}
    %define daemon_pimd pimd
%else
    %define daemon_pimd ""
%endif

%if %{with_pbrd}
    %define daemon_pbrd pbrd
%else
    %define daemon_pbrd ""
%endif

%if %{with_nhrpd}
    %define daemon_nhrpd nhrpd
%else
    %define daemon_nhrpd ""
%endif

%if %{with_eigrpd}
    %define daemon_eigrpd eigrpd
%else
    %define daemon_eigrpd ""
%endif

%if %{with_babeld}
    %define daemon_babeld babeld
%else
    %define daemon_babeld ""
%endif

%if %{with_vrrpd}
    %define daemon_vrrpd vrrpd
%else
    %define daemon_vrrpd ""
%endif

%if %{with_watchfrr}
    %define daemon_watchfrr watchfrr
%else
    %define daemon_watchfrr ""
%endif

%if %{with_bfdd}
    %define daemon_bfdd bfdd
%else
    %define daemon_bfdd ""
%endif

%define all_daemons %{daemon_list} %{daemon_ldpd} %{daemon_pimd} %{daemon_nhrpd} %{daemon_eigrpd} %{daemon_babeld} %{daemon_watchfrr} %{daemon_pbrd} %{daemon_bfdd} %{daemon_vrrpd}

#release sub-revision (the two digits after the CONFDATE)
%{!?release_rev:        %global  release_rev        01 }

Summary: Routing daemon
Name:           frr
Version:        %{rpmversion}
Release:        %{release_rev}%{?dist}
License:        GPLv2+
Group:          System Environment/Daemons
Source0:        https://github.com/FRRouting/frr/archive/%{name}-%{frrversion}.tar.gz
URL:            https://www.frrouting.org
Requires(pre):  shadow-utils
Requires(preun): info
Requires(post): info
BuildRequires:  bison >= 2.7
BuildRequires:  c-ares-devel
BuildRequires:  flex
BuildRequires:  gcc
BuildRequires:  json-c-devel
BuildRequires:  libcap-devel
BuildRequires:  make
BuildRequires:  ncurses-devel
BuildRequires:  readline-devel
BuildRequires:  texinfo
BuildRequires:  libyang-devel >= 0.16.74
%if 0%{?rhel} && 0%{?rhel} < 7
#python27-devel is available from ius community repo for RedHat/CentOS 6
BuildRequires:  python27-devel
BuildRequires:  python27-sphinx
%else
BuildRequires:  python-devel >= 2.7
BuildRequires:  python-sphinx
%endif
Requires:       initscripts
%if %{with_pam}
BuildRequires:  pam-devel
%endif
%if %{with_rpki}
BuildRequires:  librtr-devel >= 0.5
%endif
%if "%{initsystem}" == "systemd"
BuildRequires:      systemd
BuildRequires:      systemd-devel
Requires(post):     systemd
Requires(preun):    systemd
Requires(postun):   systemd
%else
Requires(post):     chkconfig
Requires(preun):    chkconfig
# Initscripts > 5.60 is required for IPv6 support
Requires(pre):      initscripts >= 5.60
%endif
Provides:           routingdaemon = %{version}-%{release}
Obsoletes:          gated mrt zebra frr-sysvinit
Conflicts:          bird


%description
FRRouting is a free software that manages TCP/IP based routing
protocol. It takes multi-server and multi-thread approach to resolve
the current complexity of the Internet.

FRRouting supports BGP4, OSPFv2, OSPFv3, ISIS, RIP, RIPng, PIM, LDP
NHRP, Babel, PBR, EIGRP and BFD.

FRRouting is a fork of Quagga.


%package contrib
Summary: contrib tools for frr
Group: System Environment/Daemons

%description contrib
Contributed/3rd party tools which may be of use with frr.


%package pythontools
Summary: python tools for frr
BuildRequires: python
Requires: python-ipaddress
Group: System Environment/Daemons

%description pythontools
Contributed python 2.7 tools which may be of use with frr.


%package devel
Summary: Header and object files for frr development
Group: System Environment/Daemons
Requires: %{name} = %{version}-%{release}

%description devel
The frr-devel package contains the header and object files neccessary for
developing OSPF-API and frr applications.


%prep
%setup -q -n frr-%{frrversion}


%build

# For standard gcc verbosity, uncomment these lines:
#CFLAGS="%{optflags} -Wall -Wsign-compare -Wpointer-arith"
#CFLAGS="${CFLAGS} -Wbad-function-cast -Wwrite-strings"

# For ultra gcc verbosity, uncomment these lines also:
#CFLAGS="${CFLAGS} -W -Wcast-qual -Wstrict-prototypes"
#CFLAGS="${CFLAGS} -Wmissing-declarations -Wmissing-noreturn"
#CFLAGS="${CFLAGS} -Wmissing-format-attribute -Wunreachable-code"
#CFLAGS="${CFLAGS} -Wpacked -Wpadded"

%configure \
    --sbindir=%{_sbindir} \
    --sysconfdir=%{configdir} \
    --localstatedir=%{rundir} \
    --disable-static \
    --disable-werror \
    --enable-irdp \
%if %{with_multipath}
    --enable-multipath=%{with_multipath} \
%endif
    --enable-vtysh \
%if %{with_ospfclient}
    --enable-ospfclient \
%else
    --disable-ospfclient\
%endif
%if %{with_ospfapi}
    --enable-ospfapi \
%else
    --disable-ospfapi \
%endif
%if %{with_rtadv}
    --enable-rtadv \
%else
    --disable-rtadv \
%endif
%if %{with_ldpd}
    --enable-ldpd \
%else
    --disable-ldpd \
%endif
%if %{with_pimd}
    --enable-pimd \
%else
    --disable-pimd \
%endif
%if %{with_pbrd}
    --enable-pbrd \
%else
    --disable-pbrd \
%endif
%if %{with_nhrpd}
    --enable-nhrpd \
%else
    --disable-nhrpd \
%endif
%if %{with_eigrpd}
    --enable-eigrpd \
%else
    --disable-eigrpd \
%endif
%if %{with_babeld}
    --enable-babeld \
%else
    --disable-babeld \
%endif
%if %{with_vrrpd}
	--enable-vrrpd \
%else
	--disable-vrrpd \
%endif
%if %{with_pam}
    --with-libpam \
%endif
%if 0%{?frr_user:1}
    --enable-user=%{frr_user} \
    --enable-group=%{frr_user} \
%endif
%if 0%{?vty_group:1}
    --enable-vty-group=%{vty_group} \
%endif
%if %{with_fpm}
    --enable-fpm \
%else
    --disable-fpm \
%endif
%if %{with_watchfrr}
    --enable-watchfrr \
%else
    --disable-watchfrr \
%endif
%if %{with_cumulus}
    --enable-cumulus \
%endif
%if %{with_bgp_vnc}
    --enable-bgp-vnc \
%else
    --disable-bgp-vnc \
%endif
    --enable-isisd \
%if "%{initsystem}" == "systemd"
    --enable-systemd \
%endif
%if %{with_rpki}
    --enable-rpki \
%else
    --disable-rpki \
%endif
%if %{with_bfdd}
    --enable-bfdd \
%else
    --disable-bfdd \
%endif
    # end

make %{?_smp_mflags} MAKEINFO="makeinfo --no-split"

pushd doc
make info
popd


%install
mkdir -p %{buildroot}%{_sysconfdir}/{frr,sysconfig,logrotate.d,pam.d,default} \
         %{buildroot}%{_localstatedir}/log/frr %{buildroot}%{_infodir}
make DESTDIR=%{buildroot} INSTALL="install -p" CP="cp -p" install

# Remove this file, as it is uninstalled and causes errors when building on RH9
rm -rf %{buildroot}/usr/share/info/dir

# Remove debian init script if it was installed
rm -f %{buildroot}%{_sbindir}/frr

# kill bogus libtool files
rm -vf %{buildroot}%{_libdir}/frr/modules/*.la
rm -vf %{buildroot}%{_libdir}/*.la
rm -vf %{buildroot}%{_libdir}/frr/libyang_plugins/*.la

# install /etc sources
%if "%{initsystem}" == "systemd"
mkdir -p %{buildroot}%{_unitdir}
install -m644 %{zeb_src}/tools/frr.service %{buildroot}%{_unitdir}/frr.service
%else
mkdir -p %{buildroot}%{_initddir}
ln -s %{_sbindir}/frrinit.sh %{buildroot}%{_initddir}/frr
%endif

install %{zeb_src}/tools/etc/frr/daemons %{buildroot}%{_sysconfdir}/frr
# add rpki module to daemon
%if %{with_rpki}
    sed -i -e 's/^\(bgpd_options=\)\(.*\)\(".*\)/\1\2 -M rpki\3/' %{buildroot}%{_sysconfdir}/frr/daemons
%endif
install -m644 %{zeb_rh_src}/frr.pam %{buildroot}%{_sysconfdir}/pam.d/frr
install -m644 %{zeb_rh_src}/frr.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/frr
install -d -m750 %{buildroot}%{rundir}


%pre
# add vty_group
%if 0%{?vty_group:1}
    getent group %{vty_group} >/dev/null || groupadd -r -g %{vty_gid} %{vty_group}
%endif

# add frr user and group
%if 0%{?frr_user:1}
    # Ensure that frr_gid gets correctly allocated
    getent group %{frr_user} >/dev/null || groupadd -g %{frr_gid} %{frr_user}
    getent passwd %{frr_user} >/dev/null || \
    useradd -r -u %{frr_uid} -g %{frr_user} \
        -s /sbin/nologin -c "FRRouting suite" \
        -d %{rundir} %{frr_user}

    %if 0%{?vty_group:1}
        usermod -a -G %{vty_group} %{frr_user}
    %endif
%endif
exit 0


%post
# zebra_spec_add_service <service name> <port/proto> <comment>
# e.g. zebra_spec_add_service zebrasrv 2600/tcp "zebra service"

zebra_spec_add_service ()
{
    # Add port /etc/services entry if it isn't already there
    if [ -f %{_sysconfdir}/services ] && \
        ! %__sed -e 's/#.*$//' %{_sysconfdir}/services | %__grep -wq $1 ; then
        echo "$1        $2          # $3"  >> %{_sysconfdir}/services
    fi
}

zebra_spec_add_service zebrasrv 2600/tcp "zebra service"
zebra_spec_add_service zebra    2601/tcp "zebra vty"
zebra_spec_add_service staticd  2616/tcp "staticd vty"
zebra_spec_add_service ripd     2602/tcp "RIPd vty"
zebra_spec_add_service ripngd   2603/tcp "RIPngd vty"
zebra_spec_add_service ospfd    2604/tcp "OSPFd vty"
zebra_spec_add_service bgpd     2605/tcp "BGPd vty"
zebra_spec_add_service ospf6d   2606/tcp "OSPF6d vty"
zebra_spec_add_service isisd    2608/tcp "ISISd vty"
%if %{with_ospfapi}
    zebra_spec_add_service ospfapi  2607/tcp "OSPF-API"
%endif
%if %{with_babeld}
    zebra_spec_add_service babeld   2609/tcp "BABELd vty"
%endif
%if %{with_nhrpd}
    zebra_spec_add_service nhrpd    2610/tcp "NHRPd vty"
%endif
%if %{with_pimd}
    zebra_spec_add_service pimd     2611/tcp "PIMd vty"
%endif
%if %{with_pbrd}
    zebra_spec_add_service pbrd     2615/tcp "PBRd vty"
%endif
%if %{with_ldpd}
    zebra_spec_add_service ldpd     2612/tcp "LDPd vty"
%endif
%if %{with_eigrpd}
    zebra_spec_add_service eigrpd   2613/tcp "EIGRPd vty"
%endif
%if %{with_bfdd}
    zebra_spec_add_service bfdd     2617/tcp "BFDd vty"
%endif
zebra_spec_add_service fabricd	2618/tcp "Fabricd vty"
%if %{with_vrrpd}
    zebra_spec_add_service vrrpd    2619/tcp "VRRPd vty"
%endif

%if "%{initsystem}" == "systemd"
    for daemon in %all_daemons ; do
        %systemd_post frr.service
    done
%else
    /sbin/chkconfig --add frr
%endif

# Fix bad path in previous config files
#  Config files won't get replaced by default, so we do this ugly hack to fix it
%__sed -i 's|watchfrr_options=|#watchfrr_options=|g' %{configdir}/daemons 2> /dev/null || true

# With systemd, watchfrr is mandatory. Fix config to make sure it's enabled if
# we install or upgrade to a frr built with systemd
%if "%{initsystem}" == "systemd"
    %__sed -i 's|watchfrr_enable=no|watchfrr_enable=yes|g' %{configdir}/daemons 2> /dev/null || true
%endif

/sbin/install-info %{_infodir}/frr.info.gz %{_infodir}/dir

# Create dummy files if they don't exist so basic functions can be used.
if [ ! -e %{configdir}/zebra.conf ]; then
    echo "hostname `hostname`" > %{configdir}/zebra.conf
%if 0%{?frr_user:1}
    chown %{frr_user}:%{frr_user} %{configdir}/zebra.conf*
%endif
    chmod 640 %{configdir}/zebra.conf*
fi
for daemon in %{all_daemons} ; do
    if [ x"${daemon}" != x"" ] ; then
        if [ ! -e %{configdir}/${daemon}.conf ]; then
            touch %{configdir}/${daemon}.conf
            %if 0%{?frr_user:1}
                chown %{frr_user}:%{frr_user} %{configdir}/${daemon}.conf*
            %endif
        fi
    fi
done
%if 0%{?frr_user:1}
    chown %{frr_user}:%{frr_user} %{configdir}/daemons
%endif

%if %{with_watchfrr}
    # No config for watchfrr - this is part of /etc/sysconfig/frr
    rm -f %{configdir}/watchfrr.*
%endif

if [ ! -e %{configdir}/vtysh.conf ]; then
    touch %{configdir}/vtysh.conf
    chmod 640 %{configdir}/vtysh.conf
%if 0%{?frr_user:1}
    %if 0%{?vty_group:1}
        chown %{frr_user}:%{vty_group} %{configdir}/vtysh.conf*
    %endif
%endif
fi


%postun
if [ "$1" -ge 1 ]; then
    #
    # Upgrade from older version
    #
    %if "%{initsystem}" == "systemd"
        ##
        ## Systemd Version
        ##
        %systemd_postun_with_restart frr.service
    %else
        ##
        ## init.d Version
        ##
        service frr restart >/dev/null 2>&1
    %endif
    :
fi


%preun
%if "%{initsystem}" == "systemd"
    ##
    ## Systemd Version
    ##
    if [ $1 -eq 0 ] ; then
        %systemd_preun frr.service
    fi
%else
    ##
    ## init.d Version
    ##
    if [ $1 -eq 0 ] ; then
        service frr stop  >/dev/null 2>&1
        /sbin/chkconfig --del frr
    fi
%endif
/sbin/install-info --delete %{_infodir}/frr.info.gz %{_infodir}/dir


%files
%doc */*.sample* COPYING
%doc doc/mpls
%doc README.md
/usr/share/yang/*.yang
%if 0%{?frr_user:1}
    %dir %attr(751,%{frr_user},%{frr_user}) %{configdir}
    %dir %attr(750,%{frr_user},%{frr_user}) %{_localstatedir}/log/frr
    %dir %attr(751,%{frr_user},%{frr_user}) %{rundir}
%else
    %dir %attr(750,root,root) %{configdir}
    %dir %attr(750,root,root) %{_localstatedir}/log/frr
    %dir %attr(750,root,root) %{rundir}
%endif
%if 0%{?vty_group:1}
    %attr(750,%{frr_user},%{vty_group}) %{configdir}/vtysh.conf.sample
%endif
%{_infodir}/frr.info.gz
%{_mandir}/man*/*
%{_sbindir}/zebra
%{_sbindir}/staticd
%{_sbindir}/ospfd
%{_sbindir}/ripd
%{_sbindir}/bgpd
%exclude %{_sbindir}/ssd
%if %{with_watchfrr}
    %{_sbindir}/watchfrr
%endif
%{_sbindir}/ripngd
%{_sbindir}/ospf6d
%if %{with_pimd}
    %{_sbindir}/pimd
%endif
%if %{with_pbrd}
    %{_sbindir}/pbrd
%endif
%if %{with_vrrpd}
    %{_sbindir}/vrrpd
%endif
%{_sbindir}/isisd
%{_sbindir}/fabricd
%if %{with_ldpd}
    %{_sbindir}/ldpd
%endif
%if %{with_eigrpd}
    %{_sbindir}/eigrpd
%endif
%if %{with_nhrpd}
    %{_sbindir}/nhrpd
%endif
%if %{with_babeld}
    %{_sbindir}/babeld
%endif
%if %{with_bfdd}
    %{_sbindir}/bfdd
%endif
%{_libdir}/lib*.so.0
%{_libdir}/lib*.so.0.*
%if %{with_fpm}
    %{_libdir}/frr/modules/zebra_fpm.so
%endif
%if %{with_rpki}
    %{_libdir}/frr/modules/bgpd_rpki.so
%endif
%{_libdir}/frr/modules/zebra_irdp.so
%{_libdir}/frr/modules/bgpd_bmp.so
%{_bindir}/*
%config(noreplace) %{configdir}/[!v]*.conf*
%config(noreplace) %attr(750,%{frr_user},%{frr_user}) %{configdir}/daemons
%if "%{initsystem}" == "systemd"
    %{_unitdir}/frr.service
%else
    %{_initddir}/frr
%endif
%config(noreplace) %{_sysconfdir}/pam.d/frr
%config(noreplace) %{_sysconfdir}/logrotate.d/frr
%{_sbindir}/frr-reload
%{_sbindir}/frrcommon.sh
%{_sbindir}/frrinit.sh
%{_sbindir}/watchfrr.sh


%files contrib
%doc tools


%files pythontools
%{_sbindir}/generate_support_bundle.py
%{_sbindir}/generate_support_bundle.pyc
%{_sbindir}/generate_support_bundle.pyo
%{_sbindir}/frr-reload.py
%{_sbindir}/frr-reload.pyc
%{_sbindir}/frr-reload.pyo


%files devel
%{_libdir}/lib*.so
%dir %{_includedir}/%{name}
%{_includedir}/%{name}/*.h
%dir %{_includedir}/%{name}/ospfd
%{_includedir}/%{name}/ospfd/*.h
%if %{with_ospfapi}
    %dir %{_includedir}/%{name}/ospfapi
    %{_includedir}/%{name}/ospfapi/*.h
%endif
%if %{with_eigrpd}
    %dir %{_includedir}/%{name}/eigrpd
    %{_includedir}/%{name}/eigrpd/*.h
%endif


%changelog
* Sun May 28 2018 Rafael Zalamena <rzalamena@opensourcerouting.org> - %{version}
- Add BFDd support

* Sun May 20 2018 Martin Winter <mwinter@opensourcerouting.org>
- Fixed RPKI RPM build

* Sun Mar  4 2018 Martin Winter <mwinter@opensourcerouting.org>
- Add option to build with RPKI (default: disabled)

* Tue Feb 20 2018 Martin Winter <mwinter@opensourcerouting.org>
- Adapt to new documentation structure based on Sphinx

* Fri Oct 20 2017 Martin Winter <mwinter@opensourcerouting.org>
- Fix script location for watchfrr restart functions in daemon config
- Fix postun script to restart frr during upgrade

* Mon Jun  5 2017 Martin Winter <mwinter@opensourcerouting.org>
- added NHRP and EIGRP daemon

* Mon Apr 17 2017 Martin Winter <mwinter@opensourcerouting.org>
- new subpackage frr-pythontools with python 2.7 restart script
- remove PIMd from CentOS/RedHat 6 RPM packages (won't work - too old)
- converted to single frr init script (not per daemon) based on debian init script
- created systemd service file for systemd based systems (which uses init script)
- Various other RPM package fixes for FRR 2.0

* Fri Jan  6 2017 Martin Winter <mwinter@opensourcerouting.org>
- Renamed to frr for FRRouting fork of Quagga

* Thu Feb 11 2016 Paul Jakma <paul@jakma.org>
- remove with_ipv6 conditionals, always build v6
- Fix UTF-8 char in spec changelog
- remove quagga.pam.stack, long deprecated.

* Thu Oct 22 2015 Martin Winter <mwinter@opensourcerouting.org>
- Cleanup configure: remove --enable-ipv6 (default now), --enable-nssa,
    --enable-netlink
- Remove support for old fedora 4/5
- Fix for package nameing
- Fix Weekdays of previous changelogs (bogus dates)
- Add conditional logic to only build tex footnotes with supported texi2html
- Added pimd to files section and fix double listing of /var/lib*/quagga
- Numerous fixes to unify upstart/systemd startup into same spec file
- Only allow use of watchfrr for non-systemd systems. no need with systemd

* Fri Sep  4 2015 Paul Jakma <paul@jakma.org>
- buildreq updates
- add a default define for with_pimd

* Mon Sep 12 2005 Paul Jakma <paul@dishone.st>
- Steal some changes from Fedora spec file:
- Add with_rtadv variable
- Test for groups/users with getent before group/user adding
- Readline need not be an explicit prerequisite
- install-info delete should be postun, not preun

* Wed Jan 12 2005 Andrew J. Schorr <ajschorr@alumni.princeton.edu>
- on package upgrade, implement careful, phased restart logic
- use gcc -rdynamic flag when linking for better backtraces

* Wed Dec 22 2004 Andrew J. Schorr <ajschorr@alumni.princeton.edu>
- daemonv6_list should contain only IPv6 daemons

* Wed Dec 22 2004 Andrew J. Schorr <ajschorr@alumni.princeton.edu>
- watchfrr added
- on upgrade, all daemons should be condrestart'ed
- on removal, all daemons should be stopped

* Mon Nov 08 2004 Paul Jakma <paul@dishone.st>
- Use makeinfo --html to generate quagga.html

* Sun Nov 07 2004 Paul Jakma <paul@dishone.st>
- Fix with_ipv6 set to 0 build

* Sat Oct 23 2004 Paul Jakma <paul@dishone.st>
- Update to 0.97.2

* Sat Oct 23 2004 Andrew J. Schorr <aschorr@telemetry-investments.com>
- Make directories be owned by the packages concerned
- Update logrotate scripts to use correct path to killall and use pid files

* Fri Oct 08 2004 Paul Jakma <paul@dishone.st>
- Update to 0.97.0

* Wed Sep 15 2004 Paul Jakma <paul@dishone.st>
- build snmp support by default
- build irdp support
- build with shared libs
- devel subpackage for archives and headers

* Thu Jan 08 2004 Paul Jakma <paul@dishone.st>
- updated sysconfig files to specify local dir
- added ospf_dump.c crash quick fix patch
- added ospfd persistent interface configuration patch

* Tue Dec 30 2003 Paul Jakma <paul@dishone.st>
- sync to CVS
- integrate RH sysconfig patch to specify daemon options (RH)
- default to have vty listen only to 127.1 (RH)
- add user with fixed UID/GID (RH)
- create user with shell /sbin/nologin rather than /bin/false (RH)
- stop daemons on uninstall (RH)
- delete info file on preun, not postun to avoid deletion on upgrade. (RH)
- isisd added
- cleanup tasks carried out for every daemon

* Sun Nov 2 2003 Paul Jakma <paul@dishone.st>
- Fix -devel package to include all files
- Sync to 0.96.4

* Tue Aug 12 2003 Paul Jakma <paul@dishone.st>
- Renamed to Quagga
- Sync to Quagga release 0.96

* Thu Mar 20 2003 Paul Jakma <paul@dishone.st>
- zebra privileges support

* Tue Mar 18 2003 Paul Jakma <paul@dishone.st>
- Fix mem leak in 'show thread cpu'
- Ralph Keller's OSPF-API
- Amir: Fix configure.ac for net-snmp

* Sat Mar 1 2003 Paul Jakma <paul@dishone.st>
- ospfd IOS prefix to interface matching for 'network' statement
- temporary fix for PtP and IPv6
- sync to zebra.org CVS

* Mon Jan 20 2003 Paul Jakma <paul@dishone.st>
- update to latest cvs
- Yon's "show thread cpu" patch - 17217
- walk up tree - 17218
- ospfd NSSA fixes - 16681
- ospfd nsm fixes - 16824
- ospfd OLSA fixes and new feature - 16823
- KAME and ifindex fixes - 16525
- spec file changes to allow redhat files to be in tree

* Sat Dec 28 2002 Alexander Hoogerhuis <alexh@ihatent.com>
- Added conditionals for building with(out) IPv6, vtysh, RIP, BGP
- Fixed up some build requirements (patch)
- Added conditional build requirements for vtysh / snmp
- Added conditional to files for _bindir depending on vtysh

* Mon Nov 11 2002 Paul Jakma <paulj@alphyra.ie>
- update to latest CVS
- add Greg Troxel's md5 buffer copy/dup fix
- add RIPv1 fix
- add Frank's multicast flag fix

* Wed Oct 09 2002 Paul Jakma <paulj@alphyra.ie>
- update to latest CVS
- timestamped crypt_seqnum patch
- oi->on_write_q fix

* Mon Sep 30 2002 Paul Jakma <paulj@alphyra.ie>
- update to latest CVS
- add vtysh 'write-config (integrated|daemon)' patch
- always 'make rebuild' in vtysh/ to catch new commands

* Fri Sep 13 2002 Paul Jakma <paulj@alphyra.ie>
- update to 0.93b

* Wed Sep 11 2002 Paul Jakma <paulj@alphyra.ie>
- update to latest CVS
- add "/sbin/ip route flush proto zebra" to zebra RH init on startup

* Sat Aug 24 2002 Paul Jakma <paulj@alphyra.ie>
- update to current CVS
- add OSPF point to multipoint patch
- add OSPF bugfixes
- add BGP hash optimisation patch

* Fri Jun 14 2002 Paul Jakma <paulj@alphyra.ie>
- update to 0.93-pre1 / CVS
- add link state detection support
- add generic PtP and RFC3021 support
- various bug fixes

* Thu Aug 09 2001 Elliot Lee <sopwith@redhat.com> 0.91a-6
- Fix bug #51336

* Wed Aug  1 2001 Trond Eivind Glomsrød <teg@redhat.com> 0.91a-5
- Use generic initscript strings instead of initscript specific
  ( "Starting foo: " -> "Starting $prog:" )

* Fri Jul 27 2001 Elliot Lee <sopwith@redhat.com> 0.91a-4
- Bump the release when rebuilding into the dist.

* Tue Feb  6 2001 Tim Powers <timp@redhat.com>
- built for Powertools

* Sun Feb  4 2001 Pekka Savola <pekkas@netcore.fi>
- Hacked up from PLD Linux 0.90-1, Mandrake 0.90-1mdk and one from zebra.org.
- Update to 0.91a
- Very heavy modifications to init.d/*, .spec, pam, i18n, logrotate, etc.
- Should be quite Red Hat'isque now.
