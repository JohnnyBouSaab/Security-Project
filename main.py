import tkinter as tk
from tkinter import ttk
from tkinter.ttk import *
from tkinter import * 
from ttkthemes import ThemedTk
from tools import *
from constants import *
import pyfiglet
import globs
import attacks

from functools import partial

active_interface = ""

def addInfo(msg):
    if(T):
        T.config(state=NORMAL)
        T.insert(END, msg)
        T.config(state=DISABLED)
        T.see(END)
        T.update()


def stop_scan():
    globs.stop_scanning = True
    scan_btn['state'] = NORMAL
    stop_btn['state'] = DISABLED

def stop_scan2():
    globs.stop_scanning = True
    scan_btn2['state'] = NORMAL
    stop_btn2['state'] = DISABLED


def stop_attack():
    globs.stop_attack = True
    stop_btn['state'] = DISABLED
    scan_btn['state'] = NORMAL

def stop_attack2():
    globs.stop_attack = True
    stop_btn2['state'] = DISABLED
    scan_btn2['state'] = NORMAL


def scan():
    if len(active_interface) == 0: # no active interface:
        addInfo("Please choose an interface above before scanning\n\n")
    else:
        scan_btn['state'] = DISABLED
        stop_btn['state'] = NORMAL
        tree.state(("disabled",))
        tree.unbind("<Button-3>",)
        globs.interface_list['state'] = DISABLED
        execute_scan(active_interface, T, tree)
        globs.interface_list['state'] = NORMAL
        tree.state(("!disabled",))
        tree.bind("<Button-3>", tree_on_right_click)



def interface(new_interface):
    global active_interface
    active_interface = new_interface


# switching between pages
def show_page(page_no):
    if page_no == 1:
        page1.lift()
    
    elif page_no == 2:
        page2.lift()

def search_for_stations(root, T, tree2, sel_item, active_interface):
    global selected_ap

    scan_btn2['state'] = DISABLED
    stop_btn2['state'] = NORMAL
    tree2.state(("disabled",))
    tree2.unbind("<Button-3>",)

    show_page(2)
    list_stations(root, T, tree2, selected_ap, active_interface)

    tree2.state(("!disabled",))
    tree2.bind("<Button-3>", tree2_on_right_click)


# USER INTERFACE SECTION

# root = Tk()

# using ThemedTk to slightly improve the GUI's looks
# to install: 
# python3 -m pip install git+https://github.com/RedFantom/ttkthemes
root = ThemedTk(theme="arc")

# globs 
globs.init()

# styles: buttons, frames, treeview (when disabled)
style = ttk.Style()
style.configure("TButton", background="white", padding=(0, 3), font=('arial', 11, 'normal'), highlightthickness=0, borderwidth=0)
style.configure("page.TFrame", height=300)
style.configure("top.TFrame", background='black', height=100)
style.configure("mid.TFrame", background='#939194', height=200)
style.configure("bottom.TFrame", background='grey', height=400)
style.map('Treeview', foreground=[('disabled', '#a9acb2'), ('selected', '#fff')], background=[('disabled', '#fbfcfc'), ('selected', '#e95420')])
style.configure('TEntry', selectbackground='#e95420', selectforeground="white")

root.geometry('1100x600')
root.configure(background='#000000')
root.title('WiHack :D')

# the window is divided into two sections:
# - a top/mid container frame (which supports containing multiple pages and switching between them)
# - a bottom frame for output

# the top/mid container
top_mid_container = ttk.Frame(root, style="page.TFrame")
top_mid_container.pack(fill=BOTH)

#the bottom container, stays the same when we switch pages
bottom = ttk.Frame(root, style="bottom.TFrame")
bottom.pack(fill=BOTH, expand=True)

#pages
page1 = ttk.Frame(top_mid_container, style="page.TFrame")
page2 = ttk.Frame(top_mid_container, style="page.TFrame")

page1.place(in_=top_mid_container, x=0, y=0, relwidth=1, relheight=1)
page2.place(in_=top_mid_container, x=0, y=0, relwidth=1, relheight=1)

page1.pack(fill=BOTH)
# page2.pack(fill=BOTH)

# show page 1 by default, as app entry point
page1.lift()

# page 1: top and mid secitons
# kept the vars as `top` and `mid`, and not `top1` and `mid1`, in order not to break the original code
top = ttk.Frame(page1, style="top.TFrame")
top.pack(fill=X)
mid = ttk.Frame(page1, style="mid.TFrame")
mid.pack(fill=BOTH)

# page 2: top and mid sections
top2 = ttk.Frame(page2, style="top.TFrame")
top2.pack(fill=X)
mid2 = ttk.Frame(page2, style="mid.TFrame")
mid2.pack(fill=BOTH)

# Scan button
scan_btn = ttk.Button(top, text='Scan', style="TButton", command=scan)
scan_btn.pack(side=LEFT, padx=15, pady=15)

# Stop Scan Button
stop_btn = ttk.Button(top, text="Stop", style="TButton", command = stop_scan)
stop_btn.pack(side=LEFT, padx=15, pady=15)
stop_btn['state'] = DISABLED

# Stop Attack Button
stop_attack_btn = ttk.Button(top, text="Stop Attack", style="TButton", command = stop_attack)
stop_attack_btn.pack(side=RIGHT, padx=15, pady=15)
stop_attack_btn['state'] = DISABLED

# Back button, to go back to page 1
back_btn = ttk.Button(top2, text="Back", style="TButton", command = lambda: show_page(1))
back_btn.pack(side=RIGHT, padx=15, pady=15)
back_btn['state'] = NORMAL

# Next button, go forward to page 2
# I commented out this button since I don't think it is really needed  --Anis

# next_btn = ttk.Button(top, text="Next", style="TButton", command = lambda: show_page(2))
# next_btn.pack(side=RIGHT, padx=15, pady=15)
# next_btn['state'] = NORMAL

#page 2 buttons
# Scan button
scan_btn2 = ttk.Button(top2, text='Scan', style="TButton", command=lambda: search_for_stations(root, T, tree2, selected_ap, active_interface))
scan_btn2.pack(side=LEFT, padx=15, pady=15)

# Stop Scan Button
stop_btn2 = ttk.Button(top2, text="Stop", style="TButton", command = stop_scan2)
stop_btn2.pack(side=LEFT, padx=15, pady=15)
stop_btn2['state'] = DISABLED

# Stop Attack Button
stop_attack_btn2 = ttk.Button(top2, text="Stop Attack", style="TButton", command = stop_attack2)
stop_attack_btn2.pack(side=RIGHT, padx=15, pady=15)
stop_attack_btn2['state'] = DISABLED

# Interface option
variable = StringVar(root)
interfaces = get_interfaces()

if interfaces == -1: # user does not have requirements (in this case probably aircrack tools)
    stop_and_warn(root, 0)

elif len(interfaces) > 0: # user has no wifi interfaces 
    variable.set("Interface") 
    # interface_list = OptionMenu(top, variable, interfaces, command=interface)
    globs.interface_list = ttk.OptionMenu(top, variable, *(["Interface"] + interfaces), command=interface)
    globs.interface_list.pack(side=LEFT)
else:
    stop_and_warn(root, 1)
    

tree = ttk.Treeview(mid, columns = (1,2,3,4,5,6,7,8), show = "headings")
tree.pack(side = 'left')

tree.heading(1, text="Name")
tree.heading(2, text="Encryption")
tree.heading(3, text="Power")
tree.heading(4, text="Mac Address")
tree.heading(5, text="WPS?")
tree.heading(6, text="Channel")
tree.heading(7, text="Vendor")
tree.heading(8, text="Recommended Attacks")

# width = tree.winfo_width() 
tree.column(1, width = 160)
tree.column(2, width = 100)
tree.column(3, width = 80)
tree.column(4, width = 300)
tree.column(5, width = 80)
tree.column(6, width = 80)
tree.column(7, width = 100)
tree.column(8, width = 160)

# tree 2
tree2 = ttk.Treeview(mid2, columns = (1,2,3,4,5,6,7,8), show = "headings")
tree2.pack(side = 'left')

tree2.heading(1, text="Name")
tree2.heading(2, text="Power")
tree2.heading(3, text="Device Mac Address")
tree2.heading(4, text="AP Mac Address")
tree2.heading(5, text="Channel")

tree2.column(1, width = 160)
tree2.column(2, width = 100)
tree2.column(3, width = 300)
tree2.column(4, width = 300)

scroll = ttk.Scrollbar(mid, orient="vertical", command=tree.yview)
scroll.pack(side = 'right', fill = 'y')

tree.configure(yscrollcommand=scroll.set)

# BEGIN right click menu stuff

#the right-click event
selected_iid = None
selected_ap = None

def tree_on_right_click(event):
    global selected_ap
    selected_iid = tree.identify_row(event.y)

    # The below fixes a bug when item is only right-clicked without a left click prior
    tree.focus(selected_iid) 

    if selected_iid:
        # mouse pointer over item
        # highlight the row (like for left-click)
        tree.selection_set(selected_iid)
        # contextMenu.post(event.x_root, event.y_root)

        # do something with the row item
        try:
            sel_item = tree.item(selected_iid)
            selected_ap = sel_item
            name = sel_item["values"][0]
            mac_address = sel_item["values"][3]
            channel = sel_item["values"][5]

            # pop-up menu on right click
            popup = Menu(root, tearoff=0)
            popup.add_command(label="Handshake (passive/listen)", \
                command = lambda: attacks.try_handshake(root, scan_btn, stop_attack_btn, \
                    T, tree, active_interface, tree_on_right_click))
            popup.add_command(label="Handshake (active/attack)", \
                command = lambda: attacks.try_handshake(root, scan_btn, stop_attack_btn, \
                    T, tree, active_interface, tree_on_right_click, passive=False))
            popup.add_command(label="WPA Dictionary (Offline)", \
                command = lambda: attacks.crack_wpa(root, scan_btn, stop_attack_btn, \
                    T, tree, active_interface, tree_on_right_click))
            popup.add_command(label="WPS Bruteforce", \
                command = lambda: attacks.wps_attack(root, scan_btn, stop_attack_btn, \
                    T, tree, active_interface, tree_on_right_click))
            popup.add_command(label="WPS Pixie Dust", \
                command = lambda: attacks.wps_attack(root, scan_btn, stop_attack_btn, \
                    T, tree, active_interface, tree_on_right_click, pixie = True))
            popup.add_command(label="Denial of Service", \
                command = lambda: attacks.dos(root, scan_btn, stop_attack_btn, \
                    T, tree, active_interface, tree_on_right_click))

            popup.add_separator()

            popup.add_command(label="View Connected Clients", \
                command = lambda: search_for_stations(root, T, tree2, sel_item, active_interface))


            popup.tk_popup(event.x_root, event.y_root, 0)
        finally:
            popup.grab_release()

# attach event for when right-clicking a treeview element
tree.bind("<Button-3>", tree_on_right_click)

# END right click menu stuff


# right-click menu for page 2
# BEGIN right click menu stuff #2

#the right-click event
selected_iid2 = None

def tree2_on_right_click(event):
    selected_iid2 = tree2.identify_row(event.y)

    # The below fixes a bug when item is only right-clicked without a left click prior
    tree2.focus(selected_iid2) 

    if selected_iid2:
        # mouse pointer over item
        # highlight the row (like for left-click)
        tree2.selection_set(selected_iid2)
        # contextMenu.post(event.x_root, event.y_root)

        # do something with the row item
        try:
            sel_item = tree2.item(selected_iid2)
            dev_mac = sel_item["values"][2]
            ap_mac = sel_item["values"][3]
            channel = sel_item["values"][4]

            # pop-up menu on right click
            popup = Menu(root, tearoff=0)

            popup.add_command(label="De-authenticate Client", \
                command = lambda: attacks.deauth_client(dev_mac, ap_mac, channel, root, scan_btn2, stop_attack_btn2, T, tree2, active_interface, tree2_on_right_click))

            popup.add_command(label="ARP Spoof this Client", \
                command = None)

            popup.add_separator()

            popup.tk_popup(event.x_root, event.y_root, 0)
        finally:
            popup.grab_release()

# attach event for when right-clicking a treeview element
tree2.bind("<Button-3>", tree2_on_right_click)

# END right click menu stuff #2



# Debug / Info section, bottom
S = ttk.Scrollbar(bottom)
T = tk.Text(bottom, height=17, bg="black", fg='white')
S.pack(side=RIGHT, fill=Y)
T.pack(side=LEFT, fill=BOTH, expand=True)
S.config(command=T.yview)
T.config(yscrollcommand=S.set, highlightthickness=0)
info_text = "\n\n" + SKULL + "\n" + pyfiglet.figlet_format("WiHack") + " \n" + pyfiglet.figlet_format("Johnny & Anis") + "\nWelcome to WiHack, we hope you enjoy our simple yet powerful tool :))) \n\n"
T.insert(END, info_text)
T.config(state=DISABLED)
T.see(END)


def dis_exit():
    disable_monitor(active_interface+"mon")
    root.destroy() 


# Spoof option
globs.spoof_option = ttk.Checkbutton(top, text='Spoof MAC', variable=globs.spoof_mac)
globs.spoof_option.pack(side=LEFT, padx=15, pady=15)

# disable monitor mode on sudden exit
root.protocol("WM_DELETE_WINDOW", dis_exit)

# run
root.mainloop()
