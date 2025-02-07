Name: plusdeck
Version: 3.0.0
Release: 3
License: MPL-2.0
Summary: Serial client and Linux service for Plus Deck 2C PC Cassette Deck

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
install -p -D -m 0644 dbus/org.jfhbrook.plusdeck.conf /etc/dbus-1/system.d/org.jfhbrook.plusdeck.conf


%check


%files
%{_prefix}/lib/systemd/system/plusdeck.service
/etc/dbus-1/system.d/org.jfhbrook.plusdeck.conf

%changelog
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
