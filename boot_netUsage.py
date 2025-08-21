import matplotlib.pyplot as plt

def get_network_bytes(interface):
    with open('/proc/net/dev', 'r') as f:
        lines = f.readlines()
    for line in lines:
        if interface in line:
            parts = line.strip().split()
            rx_bytes = int(parts[1])
            tx_bytes = int(parts[9])
            return rx_bytes, tx_bytes
    return None, None

def bytes_to_mb(bytes_val):
    return bytes_val / 1024 / 1024

def plot_total_usage(rx_mb, tx_mb, interface):
    labels = ['Download (RX)', 'Upload (TX)']
    values = [rx_mb, tx_mb]
    colors = ['blue', 'green']

    plt.figure(figsize=(6, 4))
    plt.bar(labels, values, color=colors)
    plt.title(f'Total Network Usage Since Boot on {interface}')
    plt.ylabel('Data (MB)')
    for i, v in enumerate(values):
        plt.text(i, v + 1, f'{v:.2f} MB', ha='center')
    plt.tight_layout()
    plt.show()

def main():
    interface = input("Enter your network interface (default: wlan0): ") or "wlan0"
    rx_bytes, tx_bytes = get_network_bytes(interface)

    if rx_bytes is None:
        print(f"Interface '{interface}' not found.")
        return

    rx_mb = bytes_to_mb(rx_bytes)
    tx_mb = bytes_to_mb(tx_bytes)

    print(f"Total network usage on interface '{interface}' since boot:")
    print(f"Downloaded (RX): {rx_mb:.2f} MB")
    print(f"Uploaded   (TX): {tx_mb:.2f} MB")

    plot_total_usage(rx_mb, tx_mb, interface)

if __name__ == "__main__":
    main()

