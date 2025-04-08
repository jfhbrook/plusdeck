Name: plusdeck
Version: 4.0.1
Release: 1
License: MPL-2.0
Summary: Serial client and Linux service for the Plus Deck 2C PC Cassette Deck

URL: https://github.com/jfhbrook/plusdeck
Source0: %{name}-%{version}.tar.gz
BuildArch: noarch

Requires: python-plusdeck
Requires: python-sdbus

%description


%prep
%autosetup


%build
tar -xzf %{SOURCE0}


%install
mkdir -p %{buildroot}%{_prefix}/lib/systemd/system
install -p -D -m 0644 systemd/plusdeck.service %{buildroot}%{_prefix}/lib/systemd/system/plusdeck.service
install -p -D -m 0644 dbus/org.jfhbrook.plusdeck.conf %{buildroot}%{_prefix}/share/dbus-1/system.d/org.jfhbrook.plusdeck.conf
install -p -m 755 bin/plusdeck-dbus %{buildroot}%{_bindir}/plusdeck

%check


%files
%{_prefix}/lib/systemd/system/plusdeck.service
%{_prefix}/share/dbus-1/system.d/org.jfhbrook.plusdeck.conf
%{_bindir}/plusdeck

%changelog
* Sun Feb 09 2025 Josh Holbrook <josh.holbrook@gmail.com> 4.0.1-1
- Dbus methods now marked as unprivileged
- sdbus library errors have improved logging

* Sat Feb 08 2025 Josh Holbrook <josh.holbrook@gmail.com> 4.0.0-1
  - `plusdeckctl` connects to the system bus by default
  - `plusdeckctl --user` will connect to the user bus
  - `plusdeckd` loads local config by default unless run as root
  - systemd unit fixes
    - Requires `dbus.socket`, starts after `dbus.socket`
    - Wanted by `multiuser.target`
  - dbus access policy
    - Ownership and allowed destination for root
    - Allowed destination for `plusdeck` user

* Thu Feb 06 2025 Josh Holbrook <josh.holbrook@gmail.com> 3.0.0-3
  - Fix install path of systemd unit

* Tue Feb 04 2025 Josh Holbrook <josh.holbrook@gmail.com> 3.0.0-1
  - Remove `appdirs` dependency
  - dbus support:
    - `plusdeck.dbus.DbusInterface` dbus Interface class
    - `plusdeck.dbus.DbusClient` dbus client class
    - `plusdeckd` dbus service CLI
    - `plusdeckctl` dbus client CLI
    - systemd unit for `plusdeckd`
  - `python-plusdeck` COPR package spec
  - `plusdeck` COPR package spec
    - Depends on `python-plusdeck` COPR package
    - Includes systemd unit for `plusdeckd`
  - Tito based release tagging
  - GitHub release tarball
  - Improved documentation
