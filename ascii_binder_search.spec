%define name ascii_binder_search
%define version 0.0.1
%define unmangled_version 0.0.1
%define unmangled_version 0.0.1
%define release 1

Summary: A small utility that would help you to get search in asciibinder
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: BSD
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: smit thakkar <smitthakkar96@gmail.com>
Url: https://github.com/smitthakkar96/ascii_binder_search_plugin
Requires: python-beautifulsoup4, python-pyaml, python-xmltodict, python-lxml

%description
This is a small plugin developed to help the opensource projects using asciibinder to implement search functionality in their site. With this plugin it is very convenient to implement search functionality in your documentation site. This plugin ships you a indexer that works on client side but it is easy to extend it's capability by plugging in other supported indexer or build your own indexer that works with the search engine that you want.

%prep
%setup -n %{name}-%{unmangled_version} -n %{name}-%{unmangled_version}

%build
python3 setup.py build

%install
python3 setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
