import tools
import subprocess
import os 

def crack_password(mac_address, ssid, channel, interface, info_area):
    """
    Cracks the given network's password using an offline WPA attack, and returns the obtained password.
    
    Mode of action: First intercept the handshake, then use the captured info to crack the password offline.
    """
    
    
    password="---"

    # TODO find the password lol
    addToolInfo(info_area, f"Cracking complete for network {ssid}.\nPassword is: {password}\n")

    return 0

# Handshake
def try_handshake(T, tree, interface, passive=True, tree_iid=None):

    tools.addToolInfo(T, "Executing handshake operation...\n\n")
    monitor_interface = tools.enable_monitor(interface)
    tools.addToolInfo(T, str(interface) + " is now in monitor mode, at " + monitor_interface + "\n\n")

    current_item = tree.item(tree.focus())
    # some bug, will fix later
    if len(current_item['values']) == 0:
        # in this case, check for the provided tree_iid var
        if tree_iid:
            current_item = tree.item(tree_iid)
            
            #if still
            if len(current_item['values']) == 0:
                tools.addToolInfo(T, "Please try the attack again, something went wrong\n\n")
                return 0
        else:
            tools.addToolInfo(T, "Please try the attack again, something went wrong\n\n")
            return 0

    mac, wifi_name, enc, channel = current_item['values'][3], current_item['values'][0], \
                current_item['values'][1], current_item['values'][5] 
    tools.addToolInfo(T, "Trying to capture handshake for " + str(wifi_name) + "...\n")

    # Listen using airodump-ng
    cwd = os.path.dirname(os.path.realpath(__file__)) 
    with open(str(wifi_name)+'_output', 'w') as out_file:
        # remove any old temp files
        try : os.system('rm ' + cwd + "/packets_" + str(wifi_name) + "*") 
        except: print("Nothing important...")

        airodump = subprocess.Popen(('airodump-ng -w packets_' + str(wifi_name) + ' --bssid ' + mac + \
                                    ' -c ' + str(channel) + ' ' + monitor_interface).split(" "), \
                                    stdout=out_file, stderr=subprocess.STDOUT, universal_newlines=True, bufsize=1, cwd=cwd)
    
    captured = False
    while not captured:
        if os.path.exists(cwd+"/" + str(wifi_name) + "_output"):
            with open(str(wifi_name) + "_output", "r") as f: 
                for line in f.readlines():
                    if 'Elapsed' in line: # line where we can see when handshake is captured
                        if 'WPA handshake' in line: # handshake captured
                            airodump.terminate()
                            # rename handshake captured to save it for later
                            os.system('mv ' + cwd + '/packets_' + str(wifi_name) +'-01.cap' + ' captured_'+str(wifi_name))
                            tools.addToolInfo(T, "Successfully captued handshake of " + str(wifi_name) + \
                                " !!!.\nCaptured file available at captured_" + str(wifi_name)+'.cap\n\n') 
                            captured = True
                            break
        # If not passive (active), try to de-auth and capture 
        if not passive:
            #TODO implement de-auth using aireplay
            print("LATER")

    tools.disable_monitor(monitor_interface)
    tools.addToolInfo(T, "Monitor mode disabled for " + str(interface) + "\n\n")
    return 0


def wps_bruteforce(T, tree, interface, passive=True, tree_iid=None):
    if not os.path.exists(cwd + f"/{wifi_name}_output"):
        tools.addToolInfo(T, f"No handshake capture was found for network {wifi_name}.\nMake sure you run a handshake capture first before running this attack.")

    
