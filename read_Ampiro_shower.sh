#!/bin/bash
cd /home/pi/amphiro_oras_bluetooth_shower_hub/

# Log applications errors into a file. (Also rotate last 5000 lines)
echo "" >> run_log.txt
echo "----------------" >> run_log.txt
date >> run_log.txt
echo "----------------" >> run_log.txt
/usr/bin/python3 read_Ampiro_shower.py >> run_log.txt

tail -5000 run_log.txt > run_log.txt_
mv run_log.txt_ run_log.txt

echo "----------------" >> run_log.txt

