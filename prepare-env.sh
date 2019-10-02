#! /bin/sh

PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
DAEMON=/usr/lib/xymon/client/runclient.sh
NAME=xymon-client
DESC=xymon-client

if [ -f /etc/default/xymon-client ] ; then
	. /etc/default/xymon-client
else
	echo "Installation failure - missing /etc/default/xymon-client"
	exit 1
fi

if [ "$XYMONSERVERS" = "" ]; then
	echo "Please configure XYMONSERVERS in /etc/default/xymon-client"
	exit 1
fi

set $XYMONSERVERS
if [ $# -eq 1 ]; then
	echo "XYMSRV=\"$XYMONSERVERS\"" >/var/run/xymonclient-runtime.cfg
else
	echo "XYMSRV=\"0.0.0.0\"" >/var/run/xymonclient-runtime.cfg
fi

if [ "$CLIENTHOSTNAME" != "" ]; then
	echo "MACHINEDOTS=\"${CLIENTHOSTNAME}\"" >> /var/run/xymonclient-runtime.cfg
	echo "MACHINE=\"${CLIENTHOSTNAME}\"" | sed -e s/\\./,/g >> /var/run/xymonclient-runtime.cfg
fi
if [ "$CLIENTOS" != "" ]; then
	DMNOPTS="${DMNOPTS} --os=${CLIENTOS}"
fi


exit 0
