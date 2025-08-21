import time
import matplotlib.pyplot as plt

def get_network_bytes(interface):
    with open('/proc/net/dev', 'r') as f:
        lines = f.readlines()
    for line in lines:
        if interface in line:
            data = line.strip().split()
            rx_bytes = int(data[1])
            tx_bytes = int(data[9])
            return rx_bytes, tx_bytes
    return None, None

def bytes_to_mb(bytes_val):
    return bytes_val / 1024 / 1024  # Convert to MB

def monitor_network(interface='wlan0', interval=5, duration=60):
    rx_list = []
    tx_list = []
    timestamps = []

    print(f"Monitoring interface '{interface}' every {interval}s for {duration}s...")

    start_time = time.time()
    last_rx, last_tx = get_network_bytes(interface)
    if last_rx is None:
        print(f"Error: Interface '{interface}' not found.")
        return

    while True:
        time.sleep(interval)
        current_time = time.time()
        elapsed = current_time - start_time

        rx, tx = get_network_bytes(interface)
        rx_diff = bytes_to_mb(rx - last_rx)
        tx_diff = bytes_to_mb(tx - last_tx)

        rx_list.append(rx_diff)
        tx_list.append(tx_diff)
        timestamps.append(round(elapsed))

        last_rx, last_tx = rx, tx

        print(f"[{round(elapsed)}s] RX: {rx_diff:.2f} MB, TX: {tx_diff:.2f} MB")

        if elapsed >= duration:
            break

    plot_usage(timestamps, rx_list, tx_list, interface)

def plot_usage(timestamps, rx_data, tx_data, interface):
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, rx_data, label='Download (RX)', color='blue', marker='o')
    plt.plot(timestamps, tx_data, label='Upload (TX)', color='green', marker='x')

    plt.title(f'Network Usage Over Time on {interface}')
    plt.xlabel('Time (s)')
    plt.ylabel('Usage (MB)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Customize these as needed
    interface = input("Enter your network interface (default: wlan0): ") or "wlan0"
    interval = int(input("Sampling interval in seconds (default: 5): ") or 5)
    duration = int(input("Total monitoring duration in seconds (default: 60): ") or 60)

    monitor_network(interface, interval, duration)

