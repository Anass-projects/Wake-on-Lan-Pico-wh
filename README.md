# Wake-on-LAN Server (Raspberry Pi Pico WH)

A robust, always-on MicroPython Wake-on-LAN (WoL) server for the Raspberry Pi Pico WH. It securely triggers WoL magic packets via a hidden HTTP request, designed to sit securely behind a NAT router.

## Key Features

* **Hardware Watchdog:** Uses `machine.WDT` for automatic recovery from network drops, ensuring continuous uptime.
* **Memory Management:** Implements `gc.collect()` after every cycle to prevent RAM leaks during 24/7 operation.
* **Security by Obscurity:** Rejects unauthorized traffic (403 Forbidden). Only executes upon receiving the exact secret URL path.
* **Port Forwarding Ready:** Listens on local port 80, easily exposed via a custom external port on your router without revealing internal network architecture.

## Configuration

Update the configuration block at the top of `main.py` before flashing to your Pico WH:

```python
# --- CONFIGURATION ---
WIFI_SSID = 'YOUR_WIFI_SSID'
WIFI_PASSWORD = 'YOUR_WIFI_PASSWORD'
MAC_DESKTOP = '00:11:22:33:44:55'
BROADCAST_IP = '192.168.1.255'
SEC_LINK = "/wake_secret_path"
SERVER_PORT = 80
# ---------------------
```

## Usage

1. Flash the updated `main.py` to your Raspberry Pi Pico WH.
2. Configure Port Forwarding on your router (e.g., forward external port `54321` to the Pico's internal IP on port `80`).
3. Wake your target machine from anywhere by accessing: `http://[YOUR_EXTERNAL_IP]:54321/wake_secret_path`