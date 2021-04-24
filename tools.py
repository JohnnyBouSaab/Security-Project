import subprocess
import tkinter as tk
import re
from tkinter.ttk import *
from tkinter import * 
import time
import sys
import os
import globs

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