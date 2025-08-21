#!/bin/bash

# Function to check if bc is installed
check_bc() {
  if ! command -v bc &> /dev/null; then
    echo "Warning: 'bc' is not installed. MB values will be rounded down to integer KB."
    USE_BC=0
  else
    USE_BC=1
  fi
}

# Convert bytes to MB with 2 decimals if bc is available, else convert to KB integer
bytes_to_mb() {
  local bytes=$1
  if [ $USE_BC -eq 1 ]; then
    echo "scale=2; $bytes / 1024 / 1024" | bc
  else
    echo $((bytes / 1024))  # fallback KB integer
  fi
}

# Read interface from user
read -p "Enter network interface name (default: wlan0): " IFACE
IFACE=${IFACE:-wlan0}

echo "Choose an option:"
echo "1) Monitor usage for a period"
echo "2) Show total usage since boot"
read -p "Enter choice (1 or 2): " choice

get_bytes() {
  awk -v iface="$IFACE" '$1 ~ iface ":" {print $2, $10}' /proc/net/dev
}

show_usage_since_boot() {
  read RX TX <<< $(get_bytes)
  RX_MB=$(bytes_to_mb $RX)
  TX_MB=$(bytes_to_mb $TX)

  echo "Total data used on interface $IFACE since boot:"
  if [ $USE_BC -eq 1 ]; then
    echo "Downloaded (RX): $RX_MB MB"
    echo "Uploaded   (TX): $TX_MB MB"
  else
    echo "Downloaded (RX): $RX_MB KB"
    echo "Uploaded   (TX): $TX_MB KB"
  fi
}

monitor_usage_for_seconds() {
  read -p "Enter monitoring duration in seconds: " duration
  if ! [[ "$duration" =~ ^[0-9]+$ ]]; then
    echo "Error: Duration must be a positive integer."
    exit 1
  fi

  read RX1 TX1 <<< $(get_bytes)
  echo "Monitoring network usage on interface $IFACE for $duration seconds..."
  sleep $duration
  read RX2 TX2 <<< $(get_bytes)

  RX_DIFF=$((RX2 - RX1))
  TX_DIFF=$((TX2 - TX1))

  RX_MB=$(bytes_to_mb $RX_DIFF)
  TX_MB=$(bytes_to_mb $TX_DIFF)

  echo "Data used in last $duration seconds:"
  if [ $USE_BC -eq 1 ]; then
    echo "Downloaded (RX): $RX_MB MB"
    echo "Uploaded   (TX): $TX_MB MB"
  else
    echo "Downloaded (RX): $RX_MB KB"
    echo "Uploaded   (TX): $TX_MB KB"
  fi
}

check_bc

case $choice in
  1)
    monitor_usage_for_seconds
    ;;
  2)
    show_usage_since_boot
    ;;
  *)
    echo "Invalid choice."
    exit 1
    ;;
esac

