Name: plusdeck
Version: 3.0.0
Release: 2
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
mkdir -p %{buildroot}%{_unitdir}
install -p -D -m 0644 systemd/plusdeck.service %{buildroot}%{_unitdir}/plusdeck.service


%check


%files
%{_unitdir}/plusdeck.service

%changelog
* Thu Feb 06 2025 Josh Holbrook <josh.holbrook@gmail.com> 3.0.0-2
  - Fix install path of systemd unit

