#!/usr/bin/env bash

set -e -x

CWD=$(pwd)

BIN_PATH=$(readlink -f $1)
BIN=$(echo $BIN_PATH | awk -F/ '{print $NF}')
VERSION=$2
APP=$3
DIR=$(mktemp -d)


#echo "$CWD" $BIN_PATH $APP

#function cleanup() {
#  rm -rf ${DIR}
#}
#trap cleanup EXIT
#
cd ${DIR}
mkdir -v -p control data/{etc/systemd/system,usr/share/app}
cp -r ${CWD}/* data/usr/share/app/

cat >data/usr/share/app/start.sh <<EOF
#!/usr/bin/env bash
##------
set -e -x

#function golang {
#cd /usr/share/app/
#/usr/share/app/$BIN
#}

#----Python App----------
function python {
cd /usr/share/app/
echo "/usr/share/app/$BIN" "It is working_____!"
}


lang=$4
if [ \$lang = "golang" ]; then
echo golang
elif [ \$lang = "java" ]; then
echo java
elif [ \$lang = "python" ]; then
python
else
echo "This programming language isn't supported now"
fi
EOF

echo "Working directory>>>>>>>"
pwd


cat > data/etc/systemd/system/$APP.service <<EOF
[Unit]
Description=$APP
[Service]
ExecStart=/bin/bash /usr/share/app/start.sh
Type=simple
[Install]
WantedBy=multi-user.target
EOF

echo "/etc/systemd/system/$APP.service" > control/conffiles

cat > control/control <<EOF
Package: $APP
Version: ${VERSION}
Architecture: all
Maintainer: Oleh Palii <oleh_palii@epam.com>
Installed-Size: $(du -ks data/usr/share/app/$BIN | cut -f 1)
Depends: default-jre
Description: $APP
Section: devel
Priority: extra
EOF

pwd

cd data
md5sum usr/share/app/$BIN > ../control/md5sums
cd -

pwd
#
#cat >control/postinst <<EOF
##!/bin/sh
#set -e
#if [ "\$1" = "configure" ] || [ "\$1" = "abort-upgrade" ] || [ "\$1" = "abort-deconfigure" ] || [ "\$1" = "abort-remove" ] ; then
#    systemctl --system daemon-reload
#        systemctl enable $APP
#    systemctl start $APP
#fi
#exit 0
#EOF
#
#cat >control/prerm <<EOF
##!/bin/sh
#set -e
#systemctl stop $APP || exit 1
#EOF
#
#cat >control/postrm <<EOF
##!/bin/sh
#set -e
#APP=$APP
#if [ "\$1" = "purge" ] ; then
#        systemctl disable $APP >/dev/null
#fi
#systemctl --system daemon-reload >/dev/null || true
#systemctl reset-failed
#exit 0
#EOF
#
#cd control
#tar czf ../control.tar.gz .
#cd -
#
#cd data
#tar czf ../data.tar.gz .
#cd -
#
#echo "2.0" >debian-binary
#
#ar r ${CWD}/$APP.deb debian-binary control.tar.gz data.tar.gz
#cd ${CWD}
