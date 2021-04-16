from tools import addToolInfo, enable_monitor, disable_monitor
import socket
from itertools import product
import subprocess

# Frame types
BEACON_FRAME = b'\x80\x00'
ASSOCIATION_RESP_FRAME = b'\x10\x00'
HANDSHAKE_AP_FRAME = b'\x88\x02' # handshake message from access point (AP)
HANDSHAKE_STA_FRAME = b'\x88\x01' # handshake message from connecting device (STA)

def crack_password(mac_address, ssid, channel, interface, info_area):
    """
    Cracks the given network's password using an offline WPA attack, and returns the obtained password.
    
    Mode of action: First intercept the handshake, then use the captured info to crack the password offline.
    """
    
    
    password="---"

    # TODO find the password lol
    addToolInfo(info_area, f"Cracking complete for network {ssid}.\nPassword is: {password}\n")

    return 0
    
