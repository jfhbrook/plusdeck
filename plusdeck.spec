Name: plusdeck
Version: 3.0.0
Release: 1%{?dist}
License: MPL-2.0
Summary: Serial client and Linux service for Plus Deck 2C PC Cassette Deck

URL: https://github.com/jfhbrook/plusdeck
Source0: %{name}-%{version}.tar.gz
BuildArch: noarch

Requires: python-plusdeck

%description


%prep
%autosetup


%build
tar -xzf %{SOURCE0}


%install
mkdir -p %{buildroot}%{_libdir}/systemd/system
install -p -m 644 systemd/plusdeck.service %{buildroot}%{_libdir}/systemd/system


%check


%files
%{_libdir}/systemd/system/plusdeck.service

%changelog
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
