# BEGIN_ICS_COPYRIGHT8 ****************************************
# 
# Copyright (c) 2015, Intel Corporation
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Intel Corporation nor the names of its contributors
#       may be used to endorse or promote products derived from this software
#       without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 
# END_ICS_COPYRIGHT8   ****************************************

#[ICS VERSION STRING: unknown]
Name: opa-fm
Version: 10.0.0.0
Release: 696
Summary: Intel Omni-Path Fabric Management Software

Group: System Environment/Daemons
License: BSD
Url: http://www.intel.com/
Source0: %{name}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires: rdma

#BuildRequires: libibverbs-devel >= 1.1-1, libibumad-devel, libibmad-devel
AutoReq: no
%if 0%{?rhel}
BuildRequires: expat-devel
Requires: expat, libibmad, libibumad, libibverbs
%else
Requires: libexpat1, libibmad5, libibumad, libibverbs1
BuildRequires: libexpat-devel
%endif

%if 0%{?suse_version} >= 1210 || 0%{?rhel} >= 7
BuildRequires: systemd %{?systemd_requires} %{?BuildRequires}
Requires: systemd %{?systemd_requires}
%else
Requires(post): /sbin/chkconfig
Requires(preun): /sbin/chkconfig
%endif
ExcludeArch: s390, s390x

%if 0%{?suse_version} >= 1110
%debug_package
%endif

%description
The %{name} contains Intel Omni-Path fabric management applications. This 
includes: the Subnet Manager, Baseboard Manager, Performance Manager, 
Fabric Executive, and some fabric management tools.

%prep
%setup -q -c

%build
if [ -d Esm ]; then
	cd Esm
fi
./fmbuild -V %{version}.%{release} 

%install
install -D -m 644 stage.rpm/opafm.service $RPM_BUILD_ROOT/usr/lib/systemd/system/opafm.service
install -D -m 755 stage.rpm/opafmctrl $RPM_BUILD_ROOT/opt/opafm/bin/opafmctrl
install -D -m 755 stage.rpm/opafmd $RPM_BUILD_ROOT/opt/opafm/bin/opafmd

%if 0%{?rhel} && 0%{?rhel} < 7
install -D -m 755 stage.rpm/opafm $RPM_BUILD_ROOT%{_sysconfdir}/init.d/opafm
%endif

install -D -m 644 stage.rpm/opafm.xml $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/opafm.xml
install -D -m 755 stage.rpm/opafm.info $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/opa/opafm.info

install -D stage.rpm/fm_capture $RPM_BUILD_ROOT/opt/opafm/bin/fm_capture
install -D stage.rpm/fm_cmd $RPM_BUILD_ROOT/opt/opafm/bin/fm_cmd
install -D stage.rpm/fm_cmdall $RPM_BUILD_ROOT/opt/opafm/bin/fm_cmdall
install -D stage.rpm/smpoolsize $RPM_BUILD_ROOT/opt/opafm/bin/smpoolsize

install -D stage.rpm/sm $RPM_BUILD_ROOT/opt/opafm/runtime/sm
install -D stage.rpm/fe $RPM_BUILD_ROOT/opt/opafm/runtime/fe

install -D stage.rpm/config_check $RPM_BUILD_ROOT/opt/opafm/etc/config_check
install -D stage.rpm/config_convert $RPM_BUILD_ROOT/opt/opafm/etc/config_convert
install -D stage.rpm/config_diff $RPM_BUILD_ROOT/opt/opafm/etc/config_diff
install -D stage.rpm/config_generate $RPM_BUILD_ROOT/opt/opafm/etc/config_generate
install -D stage.rpm/opafm $RPM_BUILD_ROOT/opt/opafm/etc/opafm
install -D stage.rpm/opafm.arch $RPM_BUILD_ROOT/opt/opafm/etc/opafm.arch
install -D stage.rpm/opafm.info $RPM_BUILD_ROOT/opt/opafm/etc/opafm.info
if [ -d Esm ]; then
	sub_dir=Esm/
else
	sub_dir=
fi
install -D ${sub_dir}ib/src/linux/startup/opafm_src.xml $RPM_BUILD_ROOT/opt/opafm/etc/opafm_src.xml

install -D stage.rpm/opafm.xml $RPM_BUILD_ROOT/opt/opafm/etc/opafm.xml
install -D stage.rpm/opaxmlextract $RPM_BUILD_ROOT/opt/opafm/etc/opaxmlextract
install -D stage.rpm/opaxmlfilter $RPM_BUILD_ROOT/opt/opafm/etc/opaxmlfilter

install -D stage.rpm/opa_ca_openssl.cnf-sample $RPM_BUILD_ROOT/opt/opafm/samples/opa_ca_openssl.cnf-sample
install -D stage.rpm/opa_comp_openssl.cnf-sample $RPM_BUILD_ROOT/opt/opafm/samples/opa_comp_openssl.cnf-sample

mkdir -p $RPM_BUILD_ROOT%{_sbindir}
ln -s /opt/opafm/bin/fm_cmd $RPM_BUILD_ROOT%{_sbindir}/opafmcmd
ln -s /opt/opafm/bin/fm_cmdall $RPM_BUILD_ROOT%{_sbindir}/opafmcmdall

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ $1 = 1 ]; then
	if [ $(command -v systemctl) ]; then
		/bin/systemctl daemon-reload >/dev/null 2>&1 || :
	else
		/sbin/chkconfig --add opafm
	fi
fi
%preun
if [ $1 = 1 ] || [ $1 = 0 ]; then
	if [ $(command -v systemctl) ]; then
		systemctl stop opafm.service >/dev/null 2>&1 || :
	else
		/sbin/chkconfig --del opafm
	fi
fi

%files
%defattr(-,root,root,-)
%doc Esm/README 

%if 0%{?rhel} && 0%{?rhel} < 7
%{_sysconfdir}/init.d/opafm
%endif

/usr/lib/systemd/system/opafm.service
%config(noreplace) %{_sysconfdir}/sysconfig/opafm.xml
%{_sysconfdir}/sysconfig/opa/opafm.info
/opt/opafm/bin/*
/opt/opafm/etc/*
/opt/opafm/runtime/*
/opt/opafm/samples/*
%{_sbindir}/opafmcmd
%{_sbindir}/opafmcmdall


%changelog
* Thu Oct 09 2014 Kaike Wan <kaike.wan@intel.com> - 10.0.0.0-177
- Initial version 


