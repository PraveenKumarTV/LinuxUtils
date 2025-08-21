#!/bin/bash

read -rp "Calculate uptime for past 1 day or 1 week? (enter 1 or 7): " days

if [[ "$days" != "1" && "$days" != "7" ]]; then
  echo "Invalid input. Please enter 1 or 7."
  exit 1
fi

# Function to sum durations from a list of hh:mm strings
sum_durations() {
  local durations=("$@")
  local total_h=0
  local total_m=0
  for d in "${durations[@]}"; do
    IFS=: read -r h m <<< "$d"
    (( total_h += 10#$h ))
    (( total_m += 10#$m ))
  done
  (( total_h += total_m / 60 ))
  (( total_m %= 60 ))
  echo "$total_h:$total_m"
}

if [ "$days" -eq 1 ]; then
  # For 1 day, just calculate total uptime for today
  date_str="$(date '+%b %e')"
  durations=$(last -x | grep "system boot" | grep "$date_str" | grep -v "still running" | \
  awk '{ if ($NF ~ /^\([0-9]{2}:[0-9]{2}\)$/) { gsub(/[()]/, "", $NF); print $NF } }')

  # sum durations
  mapfile -t dur_array <<< "$durations"
  total=$(sum_durations "${dur_array[@]}")

  printf "Total uptime in past 1 day (%s): %02d:%02d (hh:mm)\n" "$date_str" ${total//:/ }
else
  # For 7 days, calculate uptime per day and total for week
  total_week_h=0
  total_week_m=0
  declare -a week_durations

  echo "Uptime per day for past 7 days:"

  for i in {0..6}; do
    date_str=$(date -d "-$i days" '+%b %e')
    durations=$(last -x | grep "system boot" | grep "$date_str" | grep -v "still running" | \
    awk '{ if ($NF ~ /^\([0-9]{2}:[0-9]{2}\)$/) { gsub(/[()]/, "", $NF); print $NF } }')

    mapfile -t dur_array <<< "$durations"
    if [ ${#dur_array[@]} -eq 0 ]; then
      # No uptime recorded for this day
      day_total="00:00"
    else
      day_total=$(sum_durations "${dur_array[@]}")
    fi

    # Add to weekly total
    IFS=: read -r dh dm <<< "$day_total"
    (( total_week_h += 10#$dh ))
    (( total_week_m += 10#$dm ))

    printf "%s: %02d:%02d (hh:mm)\n" "$date_str" ${day_total//:/ }
  done

  # Normalize weekly total
  (( total_week_h += total_week_m / 60 ))
  (( total_week_m %= 60 ))

  printf "Total uptime in past 7 days: %02d:%02d (hh:mm)\n" $total_week_h $total_week_m
fi

