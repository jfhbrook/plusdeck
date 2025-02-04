Name: plusdeck
Version: 3.0.0
Release: 2%{?dist}
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
mkdir -p %{buildroot}%{_prefix}/lib/systemd/system
install -p -m 644 systemd/plusdeck.service %{buildroot}%{_prefix}/lib/systemd/system


%check


%files
%{_prefix}/lib/systemd/system/plusdeck.service

%changelog
