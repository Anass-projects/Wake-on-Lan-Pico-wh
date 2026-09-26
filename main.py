import network
import socket
import struct
import time
import machine
import gc

# --- CONFIGURATION ---
WIFI_SSID = '*************'
WIFI_PASSWORD = '*************'
MAC_DESKTOP = '*************'
BROADCAST_IP = '*************'
SEC_LINK = "/wake_*************" 
SERVER_PORT = 80
# ---------------------

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    
    print('Connecting to WiFi...')
    
    # Give the Pico a maximum of 15 seconds to connect
    max_wait = 15 
    while max_wait > 0:
        if wlan.isconnected():
            break # Break out of the loop if connection is successful!
        max_wait -= 1
        time.sleep(1)
        
    # If time is up and still no connection: hard reset the Pico
    if not wlan.isconnected():
        print("No WiFi found! Rebooting the Pico now...")
        machine.reset()
        
    print('Successfully connected!')
    print('The local IP address of the Pico is:', wlan.ifconfig()[0])
    return wlan.ifconfig()[0]

def wake_on_lan(mac, broadcast_ip):
    # Clean the MAC address
    mac_clean = mac.replace(':', '')
    
    # Build the magic Wake-on-LAN packet (6x FF followed by 16x the MAC address)
    data = b'FFFFFFFFFFFF' + (mac_clean * 16).encode()
    send_data = b''
    for i in range(0, len(data), 2):
        send_data += struct.pack('B', int(data[i: i + 2], 16))
        
    # Send the packet over the network (via UDP port 9)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(send_data, (broadcast_ip, 9))
    s.close()
    print("Magic packet successfully sent locally to:", mac)

def start_server(ip):
    # Start a simple web server on the Pico
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # 0.0.0.0 so it accepts all incoming connections. 
    # NOTE: Change SERVER_PORT if you use another specific port in your router!

    s.bind(('0.0.0.0', SERVER_PORT)) 
    s.listen(1)
    
    # Ensure the server waits a maximum of 1 second for a visitor
    s.settimeout(1.0) 
    
    # Activate the hardware watchdog timer (max 8 seconds)
    wdt = machine.WDT(timeout=8000)
    
    print(f"Server is running! Access locally via browser: http://{ip}{SEC_LINK}")

    while True:
        # Feed the watchdog every loop iteration to prevent resets
        wdt.feed() 
        client = None  # Reset the client variable every loop
        
        try:
            # Wait max 1 second for a connection
            client, addr = s.accept()
            client.settimeout(2.0) # Wait a maximum of 2 seconds for the browser
            
            request = client.recv(1024).decode()
            
            # Check if the secret link is in the request
            if SEC_LINK in request:
                wake_on_lan(MAC_DESKTOP, BROADCAST_IP)
                response = "HTTP/1.1 200 OK\n\nSuccess! The desktop is waking up."
            else:
                # Safe and generic error for wrong/missing codes
                response = "HTTP/1.1 403 Forbidden\n\nAccess Denied."
            
            client.send(response.encode())
            
        except OSError:
            # No visitor within 1 second, or connection dropped? Ignore and loop again.
            pass
            
        finally:
            # ALWAYS close the connection properly, but ONLY if a client actually connected
            if client:
                client.close()
                
        # Force the Garbage Collector to clean up unused RAM immediately
        gc.collect()

# Start the entire process
pico_ip = connect_wifi()
start_server(pico_ip)
