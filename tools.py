import subprocess
import tkinter as tk
import re
from tkinter.ttk import *
from tkinter import * 
import time
import sys

# shows info at text area in main app
def addToolInfo(T, msg):
    if(T):
        T.config(state=NORMAL)
        T.insert(END, msg)
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

# stops the program and warns user about missing libraries/tools/requirements
def stop_and_warn(root, flag):
    if root:
        root.withdraw()
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
    Exit = tk.Button(exitsure, text="Okay :(", command=quit)
    Exit.grid(column=0, row=2)


def enable_monitor(interface):
    new_name = ''
    try:
        res = ""
        process = subprocess.Popen(["airmon-ng start " + str(interface)], shell=True, stdout=subprocess.PIPE)
        process.wait()

        for line in process.stdout:
            res += line.decode()
        res = clean(res.split("\n"))
        
        if "monitor mode vif enabled for" in res[-2]:
            line = re.sub('\s+',' ',res[-2])
            new_name = line[0:-1].split(' ')[-1].split(']')[1]
    except:
        return -1

    return new_name 

    
def disbale_monitor(interface):
    try:
        subprocess.run(['airmon-ng', 'stop', interface], capture_output=True)
    except:
        return -1 
    return 0


def execute_search(interface, info_area):

    return 0


def execute_scan(interface, info_area):
    addToolInfo(info_area, "Executing scan, please wait...\n\n")
    new_name = enable_monitor(interface)

    if new_name == -1: # should not be the case but to be safe...
        stop_and_warn(None, 99)
    else:
        addToolInfo(info_area, str(interface) + " is now in monitor mode, at " + new_name + "\n\n")

    # perform scan
    addToolInfo(info_area, "Searching for wireless networks...\n\n")
    execute_search(interface, info_area)
    addToolInfo(info_area, "Search done.\n\n")

    if disbale_monitor(new_name) != -1:
        addToolInfo(info_area, "Monitor mode disabled for " + str(interface) + "\n\n")
    else:
        stop_and_warn(None, 99)

    return 0
