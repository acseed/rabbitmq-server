Name: rabbitmq-server
Version: %%VERSION%%
Release: 1%%RELEASE_OS%%
License: MPLv1.1
Group: Development/Libraries
Source: http://www.rabbitmq.com/releases/rabbitmq-server/v%{version}/%{name}-%{version}.tar.gz
Source1: rabbitmq-server.init
Source2: rabbitmq-server.wrapper
Source3: rabbitmq-server.logrotate
URL: http://www.rabbitmq.com/
Vendor: LShift Ltd., Cohesive Financial Technologies LLC., Rabbit Technlogies Ltd.
%if 0%{?debian}
%else
BuildRequires: erlang, python-simplejson
%endif
Requires: erlang, logrotate
Packager: Hubert Plociniczak <hubert@lshift.net>
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-%{_arch}-root
Summary: The RabbitMQ server
Requires(post): %%REQUIRES%%
Requires(pre): %%REQUIRES%%

%description
RabbitMQ is an implementation of AMQP, the emerging standard for high
performance enterprise messaging. The RabbitMQ server is a robust and
scalable implementation of an AMQP broker.

%define _rabbit_erllibdir %{_libdir}/erlang/lib/rabbitmq_server-%{version}
%define _rabbit_libdir %{_libdir}/rabbitmq

%define _maindir %{buildroot}%{_rabbit_erllibdir}

%pre
if [ $1 -gt 1 ]; then
  #Upgrade - stop and remove previous instance of rabbitmq-server init.d script
  /sbin/service rabbitmq-server stop
  /sbin/chkconfig --del rabbitmq-server
fi

%prep
%setup -n %{name}-%{version}

%build
make

%install
rm -rf %{buildroot}

make install TARGET_DIR=%{_maindir} \
             SBIN_DIR=%{buildroot}%{_rabbit_libdir}/bin \
             MAN_DIR=%{buildroot}%{_mandir}

mkdir -p %{buildroot}/var/lib/rabbitmq/mnesia
mkdir -p %{buildroot}/var/log/rabbitmq
mkdir -p %{buildroot}%{_initrddir}

#Copy all necessary lib files etc.
install -m 0755 %SOURCE1 %{buildroot}%{_initrddir}/rabbitmq-server
chmod 0755 %{buildroot}%{_initrddir}/rabbitmq-server
sed -i 's|/usr/lib/|%{_libdir}/|' %{buildroot}%{_initrddir}/rabbitmq-server

mkdir -p %{buildroot}%{_sbindir}
install -m 0755 %SOURCE2 %{buildroot}%{_sbindir}/rabbitmqctl
sed -i 's|/usr/lib/|%{_libdir}/|' %{buildroot}%{_sbindir}/rabbitmqctl

mkdir -p %{buildroot}/etc/logrotate.d
install -m 0644 %SOURCE3 %{buildroot}/etc/logrotate.d/rabbitmq-server

mkdir -p %{buildroot}/etc/rabbitmq

rm %{_maindir}/LICENSE %{_maindir}/LICENSE-MPL-RabbitMQ %{_maindir}/INSTALL

#Build the list of files
rm -f %{_builddir}/filelist.%{name}.rpm
echo '%defattr(-,root,root, -)' >> %{_builddir}/filelist.%{name}.rpm 
(cd %{buildroot}; \
    find . -type f ! -regex '\./etc.*' \
        ! -regex '\.\(%{_rabbit_erllibdir}\|%{_rabbit_libdir}\).*' \
        | sed -e 's/^\.//' >> %{_builddir}/filelist.%{name}.rpm)

%post
# create rabbitmq group
if ! getent group rabbitmq >/dev/null; then
        groupadd -r rabbitmq
fi

# create rabbitmq user
if ! getent passwd rabbitmq >/dev/null; then
        useradd -r -g rabbitmq --home /var/lib/rabbitmq  rabbitmq
        usermod -c "RabbitMQ messaging server" rabbitmq
fi

chown -R rabbitmq:rabbitmq /var/lib/rabbitmq
chown -R rabbitmq:rabbitmq /var/log/rabbitmq

/sbin/chkconfig --add %{name}
/sbin/service rabbitmq-server start

%preun
if [ $1 = 0 ]; then
  #Complete uninstall
  /sbin/service rabbitmq-server stop
  /sbin/chkconfig --del rabbitmq-server
  
  # We do not remove /var/log and /var/lib directories
  # Leave rabbitmq user and group
fi

%files -f ../filelist.%{name}.rpm
%defattr(-,root,root,-)
%dir /var/lib/rabbitmq
%dir /var/log/rabbitmq
%dir /etc/rabbitmq
%{_rabbit_erllibdir}
%{_rabbit_libdir}
%{_initrddir}/rabbitmq-server
%config(noreplace) /etc/logrotate.d/rabbitmq-server
%doc LICENSE LICENSE-MPL-RabbitMQ INSTALL

%clean
rm -rf %{buildroot}

%changelog
* Mon Jan 19 2009 Ben Hood <0x6e6562@gmail.com> 1.5.1-1
- Maintenance release for the 1.5.x series

* Wed Dec 17 2008 Matthias Radestock <matthias@lshift.net> 1.5.0-1
- New upstream release

* Thu Jul 24 2008 Tony Garnock-Jones <tonyg@lshift.net> 1.4.0-1
- New upstream release

* Mon Mar 3 2008 Adrien Pierard <adrian@lshift.net> 1.3.0-1
- New upstream release

* Wed Sep 26 2007 Simon MacMullen <simon@lshift.net> 1.2.0-1
- New upstream release

* Wed Aug 29 2007 Simon MacMullen <simon@lshift.net> 1.1.1-1
- New upstream release

* Mon Jul 30 2007 Simon MacMullen <simon@lshift.net> 1.1.0-1.alpha
- New upstream release

* Tue Jun 12 2007 Hubert Plociniczak <hubert@lshift.net> 1.0.0-1.20070607
- Building from source tarball, added starting script, stopping

* Mon May 21 2007 Hubert Plociniczak <hubert@lshift.net> 1.0.0-1.alpha
- Initial build of server library of RabbitMQ package
