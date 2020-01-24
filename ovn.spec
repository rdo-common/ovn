# Uncomment these for snapshot releases:
# commit0 is the git sha of the last commit
# date is the date YYYYMMDD of the snapshot
#%%global commit0 f11b99776c46831184ac30065c6cdf911061bb5a
#%%global date 20190223
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

# If libcap-ng isn't available and there is no need for running OVS
# as regular user, specify the '--without libcapng'
%bcond_without libcapng

# option to build ovn-docker package
%bcond_with ovn_docker

# Enable PIE, bz#955181
%global _hardened_build 1

# We would see rpmlinit error - E: hardcoded-library-path in '% {_prefix}/lib'.
# But there is no solution to fix this. Using {_lib} macro will solve the
# rpmlink error, but will install the files in /usr/lib64/.
# OVN pacemaker ocf script file is copied in /usr/lib/ocf/resource.d/ovn/
# and we are not sure if pacemaker looks into this path to find the
# OVN resource agent script.
%global ovnlibdir %{_prefix}/lib

# Use python3 on fedora/rhel8 and python2 on rhel7/centos.
# The same spec file will be used to build OVN
# pacakges for CentOS - RDO and it doesn't have
# python3 yet.
%if 0%{?rhel} > 7 || 0%{?fedora}
# Use Python3
%global with_python3 1
%endif

# openvswitch in RDO has epoch set. So set epoch if built for rhel/centos.
# Otherwise, the ovn packages build by this spec file,  doesn't obsolete
# openvswitch-ovn* packages.
%if 0%{?rhel}
%global epoch_ovs 1
%endif

Name: ovn
Summary: Open Virtual Network support
URL: http://www.openvswitch.org/
Version: 2.12.0
Release: 10%{?commit0:.%{date}git%{shortcommit0}}%{?dist}
Obsoletes: openvswitch-ovn-common < %{?epoch_ovs:%{epoch_ovs}:}2.11.0-8
Provides: openvswitch-ovn-common = %{?epoch:%{epoch}:}%{version}-%{release}

# Nearly all of openvswitch is ASL 2.0.  The bugtool is LGPLv2+, and the
# lib/sflow*.[ch] files are SISSL.
License: ASL 2.0 and LGPLv2+ and SISSL

%if 0%{?commit0:1}
Source: https://github.com/openvswitch/ovs/archive/%{commit0}.tar.gz#/openvswitch-%{shortcommit0}.tar.gz
%else
Source: https://www.openvswitch.org/releases/ovn-%{version}.tar.gz
%endif

# The OVN commit used for 2.12.0-4 is 0a51bb04f8d6194b2c706558d434b09a89196e26.
# Update the above commit whenever the sources is updated.

# Set the ovsversion to 2.12.90 which is the latest master. We always compile
# OVN with the latest OVS master. Otherwise we will see compilation issues.
# OVS is used only for compilation. The actual OVS binaries - ovs-vswitchd, ovsdb-server etc
# comes from openvswitch package.
# The ovs commit used is 91157afbd83aefb0c9f558d2841fece388b3b0cb.
# The ovs tarball is generated manually by running - "make dist" in the ovs repository.
%define ovsver 2.12.90
%define ovsdir openvswitch-%{ovsver}

Source10: https://openvswitch.org/releases/openvswitch-%{ovsver}.tar.gz

# ovn-patches

# OVN (including OVS if required) backports (0 - 399)

# OpenvSwitch backports (400-) if required.
# Address crpto policy for fedora
%if 0%{?fedora}
Patch400: 0001-fedora-Use-PROFILE-SYSTEM-in-SSL_CTX_set_cipher_list.patch
%endif

BuildRequires: gcc autoconf automake libtool
BuildRequires: systemd openssl openssl-devel

%if 0%{?with_python3}
BuildRequires: python3-devel python3-six python3-setuptools
%else
BuildRequires: python2-devel python2-six python2-setuptools
%endif

BuildRequires: /usr/bin/sphinx-build
BuildRequires: desktop-file-utils
BuildRequires: groff-base graphviz
BuildRequires: unbound-devel
# make check dependencies
BuildRequires: procps-ng

%if 0%{?with_python3}
BuildRequires: python3-pyOpenSSL
%else
BuildRequires: pyOpenSSL
%endif

%if %{with libcapng}
BuildRequires: libcap-ng-devel
%endif

Requires: openssl hostname iproute module-init-tools openvswitch libibverbs
%{?systemd_requires}

# to skip running checks, pass --without check
# (amoralej) - skip tests in centos8 - https://bugs.centos.org/view.php?id=16969
%bcond_with check

%description
OVN, the Open Virtual Network, is a system to support virtual network
abstraction.  OVN complements the existing capabilities of OVS to add
native support for virtual network abstractions, such as virtual L2 and L3
overlays and security groups.

%package central
Summary: Open Virtual Network support
License: ASL 2.0
Requires: ovn = %{?epoch:%{epoch}:}%{version}-%{release}
Requires: firewalld-filesystem
Obsoletes: openvswitch-ovn-central < %{?epoch_ovs:%{epoch_ovs}:}2.11.0-8
Provides: openvswitch-ovn-central = %{?epoch:%{epoch}:}%{version}-%{release}

%description central
OVN DB servers and ovn-northd running on a central node.

%package host
Summary: Open Virtual Network support
License: ASL 2.0
Requires: ovn = %{?epoch:%{epoch}:}%{version}-%{release}
Requires: firewalld-filesystem
Obsoletes: openvswitch-ovn-host < %{?epoch_ovs:%{epoch_ovs}:}2.11.0-8
Provides: openvswitch-ovn-host = %{?epoch:%{epoch}:}%{version}-%{release}

%description host
OVN controller running on each host.

%package vtep
Summary: Open Virtual Network support
License: ASL 2.0
Requires: ovn = %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes: openvswitch-ovn-vtep < %{?epoch_ovs:%{epoch_ovs}:}2.11.0-8
Provides: openvswitch-ovn-vtep = %{?epoch:%{epoch}:}%{version}-%{release}

%description vtep
OVN vtep controller

%if %{with ovn_docker}
%package docker
Summary: Open Virtual Network support
License: ASL 2.0
Requires: ovn = %{?epoch:%{epoch}:}%{version}-%{release} %{_py}-openvswitch
Obsoletes: openvswitch-ovn-docker < %{?epoch_ovs:%{epoch_ovs}:}2.11.0-8
Provides: openvswitch-ovn-docker = %{?epoch:%{epoch}:}%{version}-%{release}

%description docker
Docker network plugins for OVN.
%endif

%prep
%if 0%{?commit0:1}
%autosetup -v -n ovs-%{commit0} -p 1
%else
%autosetup -n ovn-%{version} -a 10 -p 1
%endif

%build
%if 0%{?commit0:1}
# fix the snapshot unreleased version to be the released one.
sed -i.old -e "s/^AC_INIT(openvswitch,.*,/AC_INIT(openvswitch, %{version},/" configure.ac
%endif
./boot.sh

# OVN source code is now separate.
# Build openvswitch first.
# Build openvswitch first
cd openvswitch-%{ovsver}
./boot.sh
%configure \
%if %{with libcapng}
        --enable-libcapng \
%else
        --disable-libcapng \
%endif
        --enable-ssl \
        --with-pkidir=%{_sharedstatedir}/openvswitch/pki \
%if 0%{?with_python3}
        PYTHON3=%{__python3} \
        PYTHON=%{__python3}
%else
        PYTHON=%{__python2}
%endif

make %{?_smp_mflags}
cd -

# Build OVN.
%configure \
        --with-ovs-source=$PWD/openvswitch-%{ovsver} \
%if %{with libcapng}
        --enable-libcapng \
%else
        --disable-libcapng \
%endif
        --enable-ssl \
        --with-pkidir=%{_sharedstatedir}/openvswitch/pki \
%if 0%{?with_python3}
        PYTHON3=%{__python3} \
        PYTHON=%{__python3}
%else
        PYTHON=%{__python2}
%endif

make %{?_smp_mflags}

%install
%make_install

install -p -D -m 0644 \
        rhel/usr_share_ovn_scripts_systemd_sysconfig.template \
        $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/ovn

for service in ovn-controller ovn-controller-vtep ovn-northd; do
        install -p -D -m 0644 \
                        rhel/usr_lib_systemd_system_${service}.service \
                        $RPM_BUILD_ROOT%{_unitdir}/${service}.service
done

install -d -m 0755 $RPM_BUILD_ROOT/%{_sharedstatedir}/ovn

install -d $RPM_BUILD_ROOT%{ovnlibdir}/firewalld/services/
install -p -m 0644 rhel/usr_lib_firewalld_services_ovn-central-firewall-service.xml \
        $RPM_BUILD_ROOT%{ovnlibdir}/firewalld/services/ovn-central-firewall-service.xml
install -p -m 0644 rhel/usr_lib_firewalld_services_ovn-host-firewall-service.xml \
        $RPM_BUILD_ROOT%{ovnlibdir}/firewalld/services/ovn-host-firewall-service.xml

install -d -m 0755 $RPM_BUILD_ROOT%{ovnlibdir}/ocf/resource.d/ovn
ln -s %{_datadir}/ovn/scripts/ovndb-servers.ocf \
      $RPM_BUILD_ROOT%{ovnlibdir}/ocf/resource.d/ovn/ovndb-servers

install -p -D -m 0644 rhel/etc_logrotate.d_ovn \
        $RPM_BUILD_ROOT/%{_sysconfdir}/logrotate.d/ovn

# remove OVS unpackages files
rm -f $RPM_BUILD_ROOT%{_bindir}/ovs*
rm -f $RPM_BUILD_ROOT%{_bindir}/vtep-ctl
rm -f $RPM_BUILD_ROOT%{_sbindir}/ovs*
rm -f $RPM_BUILD_ROOT%{_mandir}/man1/ovs*
rm -f $RPM_BUILD_ROOT%{_mandir}/man5/ovs*
rm -f $RPM_BUILD_ROOT%{_mandir}/man5/vtep*
rm -f $RPM_BUILD_ROOT%{_mandir}/man7/ovs*
rm -f $RPM_BUILD_ROOT%{_mandir}/man8/ovs*
rm -f $RPM_BUILD_ROOT%{_mandir}/man8/vtep*
rm -rf $RPM_BUILD_ROOT%{_datadir}/ovn/python
rm -f $RPM_BUILD_ROOT%{_datadir}/ovn/scripts/ovs*
rm -rf $RPM_BUILD_ROOT%{_datadir}/ovn/bugtool-plugins
rm -f $RPM_BUILD_ROOT%{_libdir}/*.a
rm -f $RPM_BUILD_ROOT%{_libdir}/*.la
rm -f $RPM_BUILD_ROOT%{_libdir}/pkgconfig/*.pc
rm -f $RPM_BUILD_ROOT%{_includedir}/ovn/*
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/bash_completion.d/ovs-appctl-bashcomp.bash
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/bash_completion.d/ovs-vsctl-bashcomp.bash
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/openvswitch
rm -f $RPM_BUILD_ROOT%{_datadir}/ovn/scripts/ovn-bugtool*


%if %{without ovn_docker}
rm -f $RPM_BUILD_ROOT/%{_bindir}/ovn-docker-overlay-driver \
        $RPM_BUILD_ROOT/%{_bindir}/ovn-docker-underlay-driver
%endif

%check
%if %{with check}
    touch resolv.conf
    export OVS_RESOLV_CONF=$(pwd)/resolv.conf
    if make check TESTSUITEFLAGS='%{_smp_mflags} -k ovn' ||
       make check TESTSUITEFLAGS='--recheck -k ovn'; then :;
    else
        cat tests/testsuite.log
    fi
%endif

%pre central
if [ $1 -eq 1 ] ; then
    # Package install.
    /bin/systemctl status ovn-northd.service >/dev/null
    ovn_status=$?
    if [[ "$ovn_status" = "0" ]]; then
        # ovn-northd service is running which means old openvswitch-ovn-central
        # is possibly installed and it will be cleaned up. So start ovn-northd
        # service when posttrans central is called.
        touch %{_localstatedir}/lib/rpm-state/ovn-northd
    fi
fi

%pre host
if [ $1 -eq 1 ] ; then
    # Package install.
    /bin/systemctl status ovn-controller.service >/dev/null
    ovn_status=$?
    if [[ "$ovn_status" = "0" ]]; then
        # ovn-controller service is running which means old
        # openvswitch-ovn-host is possibly installed and it will be cleaned up. So
        # start ovn-controller service when posttrans host is called.
        touch %{_localstatedir}/lib/rpm-state/ovn-controller
    fi
fi

%pre vtep
if [ $1 -eq 1 ] ; then
    # Package install.
    /bin/systemctl status ovn-controller-vtep.service >/dev/null
    ovn_status=$?
    if [[ "$ovn_status" = "0" ]]; then
        # ovn-controller-vtep service is running which means old
        # openvswitch-ovn-vtep is possibly installed and it will be cleaned up. So
        # start ovn-controller-vtep service when posttrans host is called.
        touch %{_localstatedir}/lib/rpm-state/ovn-controller-vtep
    fi
fi

%preun central
%systemd_preun ovn-northd.service

%preun host
%systemd_preun ovn-controller.service

%preun vtep
%systemd_preun ovn-controller-vtep.service

%post
%if %{with libcapng}
if [ $1 -eq 1 ]; then
    sed -i 's:^#OVN_USER_ID=:OVN_USER_ID=:' %{_sysconfdir}/sysconfig/ovn
    sed -i 's:\(.*su\).*:\1 openvswitch openvswitch:' %{_sysconfdir}/logrotate.d/ovn
fi
%endif

%post central
%systemd_post ovn-northd.service

%post host
%systemd_post ovn-controller.service

%post vtep
%systemd_post ovn-controller-vtep.service

%posttrans central
if [ $1 -eq 1 ]; then
    # Package install, not upgrade
    if [ -e %{_localstatedir}/lib/rpm-state/ovn-northd ]; then
        unlink %{_localstatedir}/lib/rpm-state/ovn-northd
        /bin/systemctl start ovn-northd.service >/dev/null 2>&1 || :
    fi
fi

%posttrans host
if [ $1 -eq 1 ]; then
    # Package install, not upgrade
    if [ -e %{_localstatedir}/lib/rpm-state/ovn-controller ]; then
        unlink %{_localstatedir}/lib/rpm-state/ovn-controller
        /bin/systemctl start ovn-controller.service >/dev/null 2>&1 || :
    fi
fi

%posttrans vtep
if [ $1 -eq 1 ]; then
    # Package install, not upgrade
    if [ -e %{_localstatedir}/lib/rpm-state/ovn-controller-vtep ]; then
        unlink %{_localstatedir}/lib/rpm-state/ovn-controller-vtep
        /bin/systemctl start ovn-controller-vtep.service >/dev/null 2>&1 || :
    fi
fi

%files
%{_bindir}/ovn-nbctl
%{_bindir}/ovn-sbctl
%{_bindir}/ovn-trace
%{_bindir}/ovn-detrace
%{_bindir}/ovn-appctl
%dir %{_datadir}/ovn/
%dir %{_datadir}/ovn/scripts/
%{_datadir}/ovn/scripts/ovn-ctl
%{_datadir}/ovn/scripts/ovn-lib
%{_datadir}/ovn/scripts/ovndb-servers.ocf
%{_mandir}/man8/ovn-ctl.8*
%{_mandir}/man8/ovn-appctl.8*
%{_mandir}/man8/ovn-nbctl.8*
%{_mandir}/man8/ovn-trace.8*
%{_mandir}/man1/ovn-detrace.1*
%{_mandir}/man7/ovn-architecture.7*
%{_mandir}/man8/ovn-sbctl.8*
%{_mandir}/man5/ovn-nb.5*
%{_mandir}/man5/ovn-sb.5*
%dir %{ovnlibdir}/ocf/resource.d/ovn/
%{ovnlibdir}/ocf/resource.d/ovn/ovndb-servers
%config(noreplace) %{_sysconfdir}/logrotate.d/ovn
%config(noreplace) %{_sysconfdir}/sysconfig/ovn
%license LICENSE

%if %{with ovn_docker}
%files docker
%{_bindir}/ovn-docker-overlay-driver
%{_bindir}/ovn-docker-underlay-driver
%endif

%files central
%{_bindir}/ovn-northd
%{_mandir}/man8/ovn-northd.8*
%{_datadir}/ovn/ovn-nb.ovsschema
%{_datadir}/ovn/ovn-sb.ovsschema
%{_unitdir}/ovn-northd.service
%{ovnlibdir}/firewalld/services/ovn-central-firewall-service.xml

%files host
%{_bindir}/ovn-controller
%{_mandir}/man8/ovn-controller.8*
%{_unitdir}/ovn-controller.service
%{ovnlibdir}/firewalld/services/ovn-host-firewall-service.xml

%files vtep
%{_bindir}/ovn-controller-vtep
%{_mandir}/man8/ovn-controller-vtep.8*
%{_unitdir}/ovn-controller-vtep.service

%changelog
* Mon Nov 25 2019 Numan Siddique <nusiddiq@redhat.com> - 2.12.0-9
- Use the ovs commit 91157afbd83aefb0c9f558d2841fece388b3b0cb as ovn
  build for centos 7 was still failing.

* Mon Nov 25 2019 Numan Siddique <nusiddiq@redhat.com> - 2.12.0-8
- Reverse the previous commit.
- Fix the compilation error seen in Centos7 by using
  ovs commit - 36e5d97f9b09262ccc584ccb45fb06482b0cfc46.
  The commit 1ca0323e7c29d("Require Python 3 and remove support for Python 2.") removed
  Python 2 support because of which compilation is failing in Centos 7.

* Mon Nov 25 2019 Numan Siddique <nusiddiq@redhat.com> - 2.12.0-7
- Build with python 3 support as ovs requires python 3.

* Mon Nov 25 2019 Numan Siddique <nusiddiq@redhat.com> - 2.12.0-6
- Fix the changelog date errors.

* Wed Nov 06 2019 Numan Siddique <nusiddiq@redhat.com> - 2.12.0-5
- Fix the logrotate issue - (#1769200).

* Tue Oct 29 2019 Numan Siddique <nusiddiq@redhat.com> - 2.12.0-4
- Sync the ovn tar ball to the latest master with the commit - 0a51bb04f8d6194b2c706558d434b09a89196e26.

* Wed Oct 09 2019 Numan Siddique <nusiddiq@redhat.com> - 2.12.0-3
- Sync the ovn tar ball to the latest master with the commit - 1a3e6dfb5e2fd5bbb625f637792f91a02767ff3b.

* Tue Oct 08 2019 Numan Siddique <nusiddiq@redhat.com> - 2.12.0-2
- Use the official openvswitch 2.12.0 tar file.

* Thu Sep 26 2019 Numan Siddique <nusiddiq@redhat.com> - 2.12.0-1
- Apply fedora only patch only on fedora builds.

* Sat Sep 14 2019 Numan Siddique <nusiddiq@redhat.com> - 2.12.0-0
- 2.12.0 from new OVN repo

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 2.11.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Mon Jun 3 2019 Numan Siddique <nusiddiq@redhat.com> - 2.11.1-1
- Fix the version information in configure.ac

* Wed May 29 2019 Numan Siddique <nusiddiq@redhat.com> - 2.11.1-0
- Use the latest openvswitch sources with the commit - 4992e00012e7

* Tue Apr 9 2019 Numan Siddique <nusiddiq@redhat.com> - 2.11.0-9
- Fix epoch issue for RDO.

* Tue Apr 9 2019 Numan Siddique <nusiddiq@redhat.com> - 2.11.0-8
- Fix Obsoletes version

* Mon Apr 8 2019 Numan Siddique <nusiddiq@redhat.com> - 2.11.0-7
- Fix build error on centos builds.

* Mon Apr 8 2019 Numan Siddique <nusiddiq@redhat.com> - 2.11.0-6
- Fix spec file - %if error for centos builds.

* Mon Apr 8 2019 Numan Siddique <nusiddiq@redhat.com> - 2.11.0-5
- Support building OVN packages for Centos7/RDO.

* Fri Apr 5 2019 Numan Siddique <nusiddiq@redhat.com> - 2.11.0-4
- Provide new OVN packages splitting from openvswitch for fedora
