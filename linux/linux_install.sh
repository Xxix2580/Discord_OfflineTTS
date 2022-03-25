#!/bin/bash

ROOT_UID=0
E_NOTROOT=67

REL_PATH=`dirname "$0"`
CANONICAL_PATH=`readlink -f $REL_PATH`

if [ "$UID" -ne "$ROOT_UID" ]
then
    echo "Install Script must be executed on Root privilege."
    exit $E_NOTROOT
fi


cd /etc/systemd/system

#Making a Service.
echo "#Autocreated by installer." > discord_pytts.service

#Service Unit Info.
echo "[Unit]" >> discord_pytts.service
echo "Description=Python Offline TTS Bot for Discord" >> discord_pytts.service
echo "" >> discord_pytts.service

#Service Info.
echo "[Service]" >> discord_pytts.service
echo "Type=simple" >> discord_pytts.service
echo "ExecStart=$CANONICAL_PATH/server_start.sh" >> discord_pytts.service
echo "Restart=on-failure" >> discord_pytts.service
echo "" >> discord_pytts.service

#Service Install Info.
echo "[Install]" >> discord_pytts.service
echo "WantedBy=multi-user.target" >> discord_pytts.service