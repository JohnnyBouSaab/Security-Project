import tools
import subprocess
import os 
import globs
from tkinter import DISABLED, NORMAL

# some gui operations when attack is launched
def attack_launched(tree, scan_btn, stop_attack_btn):
    scan_btn['state'] = DISABLED
    stop_attack_btn['state'] = NORMAL
    tree.state(("disabled",))
    tree.unbind("<Button-3>")

def stopped_attack(tree, scan_btn, stop_attack_btn, tree_on_right_click):
    tree.state(("!disabled",))
    tree.bind("<Button-3>", tree_on_right_click)
    stop_attack_btn['state'] = DISABLED
    scan_btn['state'] = NORMAL

# Handshake
def try_handshake(root, scan_btn, stop_attack_btn, T, tree, interface, tree_on_right_click, passive=True):

    attack_launched(tree, scan_btn, stop_attack_btn)

    tools.addToolInfo(T, "Executing handshake operation...\n\n")
    monitor_interface = tools.enable_monitor(interface)
    tools.addToolInfo(T, str(interface) + " is now in monitor mode, at " + monitor_interface + "\n\n")

    current_item = tree.item(tree.focus())

    # TODO some bug, will fix later
    if len(current_item['values']) == 0:
        tools.addToolInfo(T, "Please try the attack again, something went wrong\n\n")
        stop_attack_btn(tree, scan_btn, stop_attack_btn, tree_on_right_click)
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
        root.update()
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
                        elif globs.stop_attack: # user clicked stopped attack button
                            globs.stop_attack = False
                            airodump.terminate()
                            tools.addToolInfo(T, "Stopped handshake operation.\n\n")
                            captured = True # not really :)
                            break


        # If not passive (active), try to de-auth and capture 
        if not passive:
            #TODO implement de-auth using aireplay
            print("LATER")

    tools.disable_monitor(monitor_interface)
    tools.addToolInfo(T, "Monitor mode disabled for " + str(interface) + "\n\n")

    stopped_attack(tree, scan_btn, stop_attack_btn, tree_on_right_click)

    return 0