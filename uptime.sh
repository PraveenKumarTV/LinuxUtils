#!/bin/bash

# Get the durations from last reboot entries for today (excluding still running)
durations=$(last -x | grep "system boot" | grep "$(date '+%b %e')" | grep -v "still running" | awk '{ if ($NF ~ /^\([0-9]{2}:[0-9]{2}\)$/) { gsub(/[()]/, "", $NF); print $NF } }')

# Initialize total hours and minutes
total_hours=0
total_minutes=0

# Loop through each duration and sum hours and minutes
while IFS=: read -r h m; do
  total_hours=$((total_hours + 10#$h))
  total_minutes=$((total_minutes + 10#$m))
done <<< "$durations"

# Convert minutes to hours if more than 60
extra_hours=$((total_minutes / 60))
total_minutes=$((total_minutes % 60))
total_hours=$((total_hours + extra_hours))

# Print total uptime
printf "Total uptime: %02d:%02d (hh:mm)\n" $total_hours $total_minutes

