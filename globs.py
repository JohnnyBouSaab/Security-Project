
import tkinter as tk

def init():

    global stop_scanning
    global stop_attack
    global spoof_mac
    global spoof_option
    global interface_list

    stop_scanning = False 
    stop_attack = False
    spoof_mac = tk.IntVar()
    
    # Will define these in main app
    spoof_option = None 
    interface_list = None