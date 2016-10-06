#!/bin/sh -x
PATH=$PATH:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin

# 1) PULL DATA FROM SERVER
python download_data.py
rm ../UserData/.DS_Store

# 2) SEPARATE DATA INTO SENSORS AND SLEEP
python run_sleep_as_android.py

# 3) FORMAT DATA IN A VIEWER-FRIENDLY WAY
python pullinfo.py

# 6) GENERATE AND SEND SLEEP UPDATE
python get_daily_updates.py
rm daily_updates/.DS_Store
