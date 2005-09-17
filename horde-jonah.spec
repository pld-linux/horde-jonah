%define	_hordeapp jonah
%define	_snap	2005-09-17
#define	_rc		rc1
%define	_rel	0.5
#
%include	/usr/lib/rpm/macros.php
Summary:	Jonah is the Horde portal project
Name:		horde-%{_hordeapp}
Version:	0.2
Release:	%{?_rc:0.%{_rc}.}%{?_snap:0.%(echo %{_snap} | tr -d -).}%{_rel}
License:	GPL
Group:		Applications/WWW
Source0:	ftp://ftp.horde.org/pub/snaps/%{_snap}/%{_hordeapp}-HEAD-%{_snap}.tar.gz
# Source0-md5:	3a9bd2b9c1eab41832c3d5783fa8b589
Source1:	%{name}.conf
URL:		http://www.horde.org/jonah/
BuildRequires:	rpm-php-pearprov >= 4.0.2-98
BuildRequires:	rpmbuild(macros) >= 1.226
BuildRequires:	tar >= 1:1.15.1
Requires:	apache >= 1.3.33-2
Requires:	apache(mod_access)
Requires:	horde >= 3.0
Requires:	php-mysql
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# horde accesses it directly in help->about
%define		_noautocompressdoc	CREDITS
%define		_noautoreq	'pear(Horde.*)'

%define		hordedir	/usr/share/horde
%define		_sysconfdir	/etc/horde.org
%define		_appdir		%{hordedir}/%{_hordeapp}

%description
Jonah is the Horde portal project. It currently provides a framework
for collecting headlines from any site that provides an RSS summary of
their content. Future plans include a full-fledged my.netscape type
portal with user preferences, stocks, news, weather, and any other
content source that users want.

%prep
%setup -q -c -T -n %{?_snap:%{_hordeapp}-%{_snap}}%{!?_snap:%{_hordeapp}-%{version}%{?_rc:-%{_rc}}}
tar zxf %{SOURCE0} --strip-components=1

# considered harmful (horde/docs/SECURITY)
rm -f test.php

rm -f {locale,po}/.htaccess

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_sysconfdir}/%{_hordeapp} \
	$RPM_BUILD_ROOT%{_appdir}/{docs,lib,locale,templates,themes} \
	$RPM_BUILD_ROOT%{_appdir}/{channels,delivery,lists,stories}

cp -a *.php			$RPM_BUILD_ROOT%{_appdir}
for i in config/*.dist; do
	cp -a $i $RPM_BUILD_ROOT%{_sysconfdir}/%{_hordeapp}/$(basename $i .dist)
done
echo '<?php ?>' >		$RPM_BUILD_ROOT%{_sysconfdir}/%{_hordeapp}/conf.php
cp -p config/conf.xml	$RPM_BUILD_ROOT%{_sysconfdir}/%{_hordeapp}/conf.xml
touch					$RPM_BUILD_ROOT%{_sysconfdir}/%{_hordeapp}/conf.php.bak

cp -pR lib/*			$RPM_BUILD_ROOT%{_appdir}/lib
cp -pR locale/*			$RPM_BUILD_ROOT%{_appdir}/locale
cp -pR templates/*		$RPM_BUILD_ROOT%{_appdir}/templates
cp -pR themes/*			$RPM_BUILD_ROOT%{_appdir}/themes
cp -pR channels/*		$RPM_BUILD_ROOT%{_appdir}/channels
cp -pR delivery/*		$RPM_BUILD_ROOT%{_appdir}/delivery
cp -pR lists/*			$RPM_BUILD_ROOT%{_appdir}/lists
cp -pR stories/*		$RPM_BUILD_ROOT%{_appdir}/stories

ln -s %{_sysconfdir}/%{_hordeapp} $RPM_BUILD_ROOT%{_appdir}/config
ln -s %{_docdir}/%{name}-%{version}/CREDITS $RPM_BUILD_ROOT%{_appdir}/docs
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/apache-%{_hordeapp}.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ ! -f %{_sysconfdir}/%{_hordeapp}/conf.php.bak ]; then
	install /dev/null -o root -g http -m660 %{_sysconfdir}/%{_hordeapp}/conf.php.bak
fi

if [ "$1" = 1 ]; then
%banner %{name} -e <<-EOF
	IMPORTANT:
	If you are installing Jonah for the first time, You may need to
	create the Klutz database tables. To do so run:
	zcat %{_docdir}/%{name}-%{version}/scripts/sql/%{_hordeapp}.sql.gz | mysql horde
EOF
fi

%triggerin -- apache1 >= 1.3.33-2
%apache_config_install -v 1 -c %{_sysconfdir}/apache-%{_hordeapp}.conf

%triggerun -- apache1 >= 1.3.33-2
%apache_config_uninstall -v 1

%triggerin -- apache >= 2.0.0
%apache_config_install -v 2 -c %{_sysconfdir}/apache-%{_hordeapp}.conf

%triggerun -- apache >= 2.0.0
%apache_config_uninstall -v 2

%files
%defattr(644,root,root,755)
%doc LICENSE README docs/* scripts
%attr(750,root,http) %dir %{_sysconfdir}/%{_hordeapp}
%attr(640,root,root) %config(noreplace) %{_sysconfdir}/apache-%{_hordeapp}.conf
%attr(660,root,http) %config(noreplace) %{_sysconfdir}/%{_hordeapp}/conf.php
%attr(660,root,http) %config(noreplace) %ghost %{_sysconfdir}/%{_hordeapp}/conf.php.bak
%attr(640,root,http) %config(noreplace) %{_sysconfdir}/%{_hordeapp}/[!c]*.php
%attr(640,root,http) %{_sysconfdir}/%{_hordeapp}/conf.xml

%dir %{_appdir}
%{_appdir}/*.php
%{_appdir}/config
%{_appdir}/docs
%{_appdir}/lib
%{_appdir}/locale
%{_appdir}/templates
%{_appdir}/themes

%{_appdir}/channels
%{_appdir}/delivery
%{_appdir}/lists
%{_appdir}/stories
