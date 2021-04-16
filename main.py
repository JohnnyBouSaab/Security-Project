import tkinter as tk
from tkinter import ttk
from tkinter.ttk import *
from tkinter import * 
from ttkthemes import ThemedTk
from tools import *
from constants import *
import pyfiglet
import globs

from attacks import crack_password
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


def scan():
    if len(active_interface) == 0: # no active interface:
        addInfo("Please choose an interface above before scanning\n\n")
    else:
        scan_btn['state'] = DISABLED
        stop_btn['state'] = NORMAL
        execute_scan(active_interface, T, tree)
        # updating the treeview table:

        # a- clear the tree's old info

        # b- add the new info

        # dummy test data
        # result.append({
        #         'name': 'Test Name',
        #         'encryption': 'WPA2',
        #         'power': '-75',
        #         'mac_address': '11:11:11:11:11:11',
        #         'wps': "-", # parts[],
        #         'channel': "6",
        # })



def interface(new_interface):
    global active_interface
    active_interface = new_interface



# USER INTERFACE SECTION

# root = Tk()
root = ThemedTk(theme="arc")

# styles
style = ttk.Style()
style.configure("TButton", background="white", padding=0, font=('arial', 11, 'normal'), highlightthickness=0, borderwidth=0)

root.geometry('800x600')
root.configure(background='#000000')
root.title('WiHack :D')

# Frames & Layout
top = Frame(root, height=100, bg='black')
top.pack(fill=X)
mid = Frame(root, height=200, bg='#939194')
mid.pack(fill=BOTH)
bottom = Frame(root, height=400, bg='grey')
bottom.pack(fill=BOTH, expand=True)

# Scan button
scan_btn = ttk.Button(top, text='Scan', style="TButton", command=scan)
scan_btn.pack(side=LEFT, padx=15, pady=15)

# Stop Scan Button
stop_btn = ttk.Button(top, text="Stop", style="TButton", command = stop_scan)
stop_btn.pack(side=LEFT, padx=15, pady=15)
stop_btn['state'] = DISABLED

# Interface option
variable = StringVar(root)
interfaces = get_interfaces()

if interfaces == -1: # user does not have requirements (in this case probably aircrack tools)
    stop_and_warn(root, 0)

elif len(interfaces) > 0: # user has no wifi interfaces 
    variable.set("Interface") 
    # interface_list = OptionMenu(top, variable, interfaces, command=interface)
    interface_list = ttk.OptionMenu(top, variable, *(["Interface"] + interfaces), command=interface)
    interface_list.pack(side=LEFT)
else:
    stop_and_warn(root, 1)

# Scanned Networks - mid
# data = [ ["val1", "val2", "val3"],
#          ["asd1", "asd2", "asd3"],
#          ["bbb1", "bbb3", "bbb4"],
#          ["ccc1", "ccc3", "ccc4"],
#          ["ddd1", "ddd3", "ddd4"],
#          ["eee1", "eee3", "eee4"] ]

tree = ttk.Treeview(mid, columns = (1,2,3,4,5,6), show = "headings")
tree.pack(side = 'left')

tree.heading(1, text="Name")
tree.heading(2, text="Encryption")
tree.heading(3, text="Power")
tree.heading(4, text="Mac Address")
tree.heading(5, text="WPS?")
tree.heading(6, text="Channel")

# width = tree.winfo_width() 
tree.column(1, width = 160)
tree.column(2, width = 100)
tree.column(3, width = 80)
tree.column(4, width = 300)
tree.column(5, width = 80)
tree.column(6, width = 80)

scroll = ttk.Scrollbar(mid, orient="vertical", command=tree.yview)
scroll.pack(side = 'right', fill = 'y')

tree.configure(yscrollcommand=scroll.set)

# BEGIN right click menu stuff

#the right-click event
selected_iid = None

def tree_on_right_click(event):
    selected_iid = tree.identify_row(event.y)
    if selected_iid:
        # mouse pointer over item
        # highlight the row (like for left-click)
        tree.selection_set(selected_iid)
        # contextMenu.post(event.x_root, event.y_root)

        # do something with the row item
        try:
            sel_item = tree.item(selected_iid)
            name = sel_item["values"][0]
            mac_address = sel_item["values"][3]
            channel = sel_item["values"][5]

            # pop-up menu on right click
            popup = tk.Menu(root, tearoff=0)
            popup.add_command(label="Crack Password", command= partial(crack_password, mac_address, name, channel, active_interface, T))
            popup.add_command(label="Other Attack 1")
            popup.add_command(label="Other Attack 2")

            popup.tk_popup(event.x_root, event.y_root, 0)
        finally:
            popup.grab_release()

# attach event for when right-clicking a treeview element
tree.bind("<Button-3>", tree_on_right_click)

# END right click menu stuff


# for val in data:
#     tree.insert('', 'end', values = (val[0], val[1], val[2]) )

# Debug / Info section, bottom
S = tk.Scrollbar(bottom)
T = tk.Text(bottom, height=17, bg="black", fg='white')
S.pack(side=RIGHT, fill=Y)
T.pack(side=LEFT, fill=BOTH, expand=True)
S.config(command=T.yview)
T.config(yscrollcommand=S.set, highlightthickness=0)
info_text = "\n\n" + SKULL + "\n" + pyfiglet.figlet_format("WiHack") + " \n" + pyfiglet.figlet_format("Johnny & Anis") + "\nWelcome to WiHack, we hope you enjoy our simple yet powerful tool :))) \n\n"
T.insert(END, info_text)
T.config(state=DISABLED)
T.see(END)

# run
globs.init()
root.mainloop()