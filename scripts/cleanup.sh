#!/bin/bash
/usr/local/speedtest-monitor-results/scripts/prune_image_files.sh
cd /usr/local/speedtest-monitor-results
git add . && git commit -m "Housekeeping" && git push origin main
