
import tkinter as tk

def init():

    global stop_scanning
    global stop_attack
    global spoof_mac
    global spoof_option
    global interface_list
    global recommended_vendors
    global recommended_names

    stop_scanning = False 
    stop_attack = False
    spoof_mac = tk.IntVar()

    # Some explanations for these recommendations can be found in sheet attached to this project, but here are some:
    # TP-link default pass attacks - router may have default 8-digit password
    # After some experience with ralink routers (vendors), many of them are vulnerable to pixie dust
    # After some research, NETGEAR routers seem to have a pattern for default passwords :D
    recommended_vendors = {"ralink": "Pixie Dust", "realtek": "Pixie Dust", \
                            "rtl8192ce": "Pixie Dust", "rtl8192er": "Pixie Dust", "rtl8812ar": "Pixie Dust", \
                            "rt": "Pixie Dust", 'mt': "Pixie Dust"}
    recommended_names = {'tp_link': "8-digit Dictionary", 'tp-link': "8-digit Dictionary", \
                            "netgear": 'adjective + noun + 3 digits', 'alfa': 'Pixie Dust', 'huawei': "Pixie Dust", \
                            "linksys": "Pixie Dust" }
    
    # Will define these in main app
    spoof_option = None 
    interface_list = None