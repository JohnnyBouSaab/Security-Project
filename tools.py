import subprocess
import tkinter as tk
import re
from tkinter.ttk import *
from tkinter import * 
import time
import sys
import os
import globs
import socket

# shows info at text area in main app
def addToolInfo(T, msg, tag=""):
    if(T):
        T.config(state=NORMAL)
        T.insert(END, msg, tag)
        T.config(state=DISABLED)
        T.see(END)
        T.update()

# takes a list, removes elements of empty lines / tabs
def clean(lst):
    new = []
    for l in lst:
        if len(l) != 0:
            new.append(l)
    return new

# returns interfaces (names) available. None if none available
def get_interfaces():
    interfaces = []

    try:
        output = subprocess.run(['airmon-ng'], capture_output=True)
        res = clean(output.stdout.decode().split("\n"))
        for line in res[1:]:
            interfaces.append(line.split("\t")[1]) # append interface found

    except:
        return -1 # user probably does not have airmon-ng installed

    return interfaces

def quit_app(root):
    root.destroy()

# stops the program and warns user about missing libraries/tools/requirements
def stop_and_warn(root, flag):
    if root:
        root.withdraw()
        root.update()
    exitsure = tk.Toplevel()
    msg = ""
    if flag == 0:
        msg = "You have missing requirements, please install them then run again"
    elif flag == 1:
        msg = "You have no wireless adapters detected, which is required for this tool"
    else:
        msg = "Something went wrong :(("
    message = tk.Label(exitsure, text=msg)
    message.grid(column=0, row=0)
    Exit = tk.Button(exitsure, text="Okay :(", command = lambda: quit_app(root))
    Exit.grid(column=0, row=2)


def enable_monitor(interface):
    interface_monitor = ''
    try:
        res = ""
        p = subprocess.Popen(["airmon-ng check kill"], shell=True, stdout=subprocess.PIPE)
        p.wait()
        process = subprocess.Popen(["airmon-ng start " + str(interface)], shell=True, stdout=subprocess.PIPE)
        process.wait()

        for line in process.stdout:
            res = line.decode().strip()
            if "monitor mode vif enabled for" in res:
                interface_monitor = res.split(']')[2][0:-1]

    except:
        return -1

    return interface_monitor 

    
def disable_monitor(interface):
    try:
        subprocess.run(['airmon-ng', 'stop', interface], capture_output=True)
        subprocess.run(['service', 'NetworkManager', 'restart'], capture_output=True)
    except:
        return -1 
    return 0


def execute_search(interface, info_area, tree):
    # current dir
    cwd = os.path.dirname(os.path.realpath(__file__)) 

    # path of output csv file
    out_path = os.path.join(cwd, "out-01.csv")
    if os.path.exists(out_path):
        os.remove(out_path)

    airodump = subprocess.Popen(('airodump-ng --output-format csv -w out --write-interval 1 ' + interface).split(" "), \
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, bufsize=1, cwd=cwd)
    
    # wash for wps data
    with open('wps', "w") as wps_file:
        wash = subprocess.Popen(('wash -i ' + interface + ' --all').split(" "), \
                                    stdout=wps_file, stderr=subprocess.STDOUT, universal_newlines=True, bufsize=1, cwd=cwd)
                                    
    while True:
        if os.path.exists(cwd+"/out-01.csv"):
            with open("out-01.csv", "r") as f: 
                networks = []
                for line in f.readlines()[2:]:
                    parts = line.split(", ")
                    if len(parts) < 14:
                        continue
                    networks.append({
                        'name': parts[13],
                        'encryption': parts[5],
                        'power': parts[8],
                        'mac_address': parts[0],
                        'wps': "-", # parts[],
                        'channel': parts[3],
                        'vendor': "-",
                        'recommended': "-"
                    })
                    mac = parts[0]; name = parts[13]
                    # Try to find wps data for this mac address
                    if os.path.exists(cwd+"/wps"):
                        with open("wps", 'r') as wps_file:
                            for wps_line in wps_file.readlines()[2:]:
                                wps_parts = clean(wps_line.split(" "))
                                # found mac ?
                                if wps_parts[0] == mac:
                                    lck = 'nl'
                                    if '1.0' in wps_parts[3] or '2.0' in wps_parts[3]:
                                        if wps_parts[4] != 'No':
                                            lck = 'l'
                                        networks[-1]['wps'] = wps_parts[3] + '('+lck+')'
                                        networks[-1]['vendor'] = wps_parts[5]
                                    else: # WPS disabled, array is of different size. Only need vendor info in this case
                                        networks[-1]['vendor'] = wps_parts[3]

                    # Recommend any attacks?
                    vuln = False
                    for essid in globs.recommended_names:
                        if essid in str(name).lower(): # By name
                            networks[-1]['recommended'] = globs.recommended_names[essid]
                            vuln = True
                            break # One recommendation is enough, for now :)
                    if not vuln: # Or by vendor
                        for vendor in globs.recommended_vendors:
                            if vendor in networks[-1]['vendor'].lower(): 
                                networks[-1]['recommended'] = globs.recommended_vendors[vendor]
                                break

            # update tree
            tree.delete(*tree.get_children())
            for network in networks:
                tree.insert('', 'end', values = (network["name"], network["encryption"], network["power"], \
                                            network["mac_address"], network["wps"], network["channel"], \
                                                network['vendor'], network['recommended']) )
            tree.update()

        # Check for stop scan flag
        if globs.stop_scanning:
            # airodump.terminate()
            airodump.kill()
            # wash.terminate()
            wash.kill()
            globs.stop_scanning = False
            addToolInfo(info_area, "Search done.\n\n")
            if disable_monitor(interface) != -1:
                addToolInfo(info_area, "Monitor mode disabled for " + str(interface) + "\n\n")
            else:
                stop_and_warn(None, 99)
            break
            
        time.sleep(0.5)

    return 0

def list_stations(root, info_area, tree, sel_item, interface):
    ap_mac = sel_item["values"][3]
    channel = sel_item["values"][5]

    # current dir
    cwd = os.path.dirname(os.path.realpath(__file__))

    # path of output csv file
    out_path = os.path.join(cwd, "out_sta-01.csv")
    if os.path.exists(out_path):
        os.remove(out_path)

    # preparing for search
    addToolInfo(info_area, "Executing scan, please wait...\n\n")
    interface_monitor = enable_monitor(interface)

    if interface_monitor == -1: # should not be the case but to be safe...
        stop_and_warn(None, 99)
    else:
        addToolInfo(info_area, str(interface) + " is now in monitor mode, at " + interface_monitor + "\n\n")


    # start searching
    addToolInfo(info_area, "Searching for stations...\n\n")

    airodump = subprocess.Popen((f'airodump-ng --output-format csv -w out_sta --write-interval 1 --bssid {ap_mac} --channel {channel} ' + interface_monitor).split(" "), \
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, bufsize=1, cwd=cwd)

    # clear tree
    tree.delete(*tree.get_children())
    tree.update()

    while True:
        if os.path.exists(out_path):
            with open(out_path, "r") as f: 
                devices = []
                lines_read = 0
                for line in f.readlines()[2:]:
                    parts = line.split(", ")
                    if len(parts) > 7 or len(parts) < 5:
                        # not a (valid) STATION line
                        continue

                    if lines_read == 0:
                        # skip the header row
                        lines_read +=1
                        continue

                    dev_mac_address = parts[0]

                    #getting dev name from mac address, using Linux's `oui.txt` lookup table
                    dev_name_line = subprocess.run(f"bash mac-lookup.sh {dev_mac_address}".split(" "), cwd=cwd, capture_output=True).stdout.decode()
                    dev_name_parts = dev_name_line.split("\t\t")

                    dev_name = dev_name_parts[1] if len(dev_name_parts) > 1 else "-"

                    devices.append({
                        'name': dev_name,
                        'dev_mac_address': dev_mac_address,
                        'ap_mac_address': parts[5].replace(",", ""),
                        'power': parts[3],
                        'channel': channel
                    })

                    lines_read +=1

            # update tree
            tree.delete(*tree.get_children())
            for dev in devices:
                tree.insert('', 'end', values = (dev["name"], dev["power"], dev["dev_mac_address"], dev["ap_mac_address"], dev["channel"], "-"))
            tree.update()

        # Check for stop scan flag
        if globs.stop_scanning:
            # airodump.terminate()
            airodump.kill()
            globs.stop_scanning = False
            addToolInfo(info_area, "Search done.\n\n")
            if disable_monitor(interface_monitor) != -1:
                addToolInfo(info_area, "Monitor mode disabled for " + str(interface_monitor) + "\n\n")
            else:
                stop_and_warn(None, 99)
            break
            
        time.sleep(0.5)

    return 0




def execute_scan(interface, info_area, tree):
    addToolInfo(info_area, "Executing scan, please wait...\n\n")
    interface_monitor = enable_monitor(interface)

    if interface_monitor == -1: # should not be the case but to be safe...
        stop_and_warn(None, 99)
    else:
        addToolInfo(info_area, str(interface) + " is now in monitor mode, at " + interface_monitor + "\n\n")

    # perform scan
    addToolInfo(info_area, "Searching for wireless networks...\n\n")
    execute_search(interface_monitor, info_area, tree)

    return 0


def getCurrentWifiSSID():
    try:
        a =  subprocess.check_output(["iwgetid -r"], stderr=subprocess.STDOUT, shell=True)
        return a.decode('utf-8').replace("\n", "")
        
        # a =  subprocess.getoutput("iwgetid -r")
        # return a
    except:
        raise RuntimeError("Could not get the Wifi SSID name. Does your system support the command `iwgetid -r`?")



# TODO - this is the "noisy" active version of doing it. Maybe also provide a passive way, via just packet sniffing
# using e.g. `tcpdump ether host 24:18:1D:62:8A:FE`

def get_client_ip(dev_mac, T, tree2, active_interface):
    """
    Finds a target station's (private) IP address from its known MAC address

    NB: Requires the attacker and target to be connected to the same wifi network.
    """
    # sample command:  nping -H -c 1 --arp-type arp-request --arp-target-mac 24:18:1D:62:8A:FE  192.168.1.* 

    # current dir
    cwd = os.path.dirname(os.path.realpath(__file__))

    # path of output csv file
    out_path = os.path.join(cwd, "temp_nping.txt")
    if os.path.exists(out_path):
        os.remove(out_path)


    machine_ip = get_local_ip()
    ip_range = machine_ip[0: machine_ip.rindex(".") + 1] + "*"
    # to make tests shorter for now
    ip_range = '192.168.1.100-110'

    with open(out_path, 'w') as f:
        nping = subprocess.Popen(f'nping -H -c 1 --arp-type arp-request --arp-target-mac {dev_mac} {ip_range}'.split(" "), \
                                stdin=subprocess.PIPE, stdout=f, stderr=subprocess.STDOUT, universal_newlines=True, bufsize=1, cwd=cwd)

    ip_addr = ''

    while nping.poll() is None:
        with open(out_path, "r") as f:
            lines = f.readlines()
            for l in lines:
                if dev_mac in l:
                    # found!
                    ip_addr = l.split("reply ")[1].split(" is at")[0]
                    globs.stop_scanning=True
                    addToolInfo(T, f'Found client IP address: {ip_addr}\n\n')

                    # update tree entry
                    # sel_item = tree2.item(tree2.focus())
                    # sel_item["values"][5] = ip_addr

                    # tree2.focus() gives us the row ID of the selected element
                    tree2.set(tree2.focus(), 6, ip_addr)
                    tree2.update()
                    break

        # Check for stop scan flag
        if globs.stop_scanning:
            # airodump.terminate()
            nping.kill()
            globs.stop_scanning = False
            addToolInfo(T, "Search done.\n\n")
            # if disable_monitor(interface_monitor) != -1:
            #     addToolInfo(info_area, "Monitor mode disabled for " + str(interface_monitor) + "\n\n")
            # else:
            #     stop_and_warn(None, 99)
            break
            
        time.sleep(5)
    
    if ip_addr == '':
        addToolInfo(T, "Failed to find client IP address. Please try again.\n\n")
        return None
        
    return ip_addr
    
# from https://www.codegrepper.com/code-examples/python/python+get+private+ip
def get_local_ip():
    """
    Returns the (private) IP address of the user's machine.
    """

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def get_router_ip():
    # ip route show
    out =  subprocess.getoutput("ip route show")
    return out[out.index("default via ") + len("default via "): out.index(" dev")]
    # or simply out.split(" ")[2] ? might be buggy though