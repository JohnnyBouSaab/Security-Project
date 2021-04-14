import tkinter as tk
from tkinter import ttk
from tkinter.ttk import *
from tkinter import * 
from tools import *
from constants import *
import pyfiglet

active_interface = ""

def addInfo(msg):
    if(T):
        T.config(state=NORMAL)
        T.insert(END, msg)
        T.see(END)

def scan():
    if len(active_interface) == 0: # no active interface:
        addInfo("Please choose an interface above before scanning\n")
    else:
        result = execute_scan(active_interface)


def interface(new_interface):
    global active_interface
    active_interface = new_interface[0]



# USER INTERFACE SECTION

root = Tk()

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
scan_btn = Button(top, text='Scan', bg='white', font=('arial', 11, 'normal'), command=scan, highlightthickness=0)
scan_btn.pack(side=LEFT, padx=15, pady=15)

# Interface option
variable = StringVar(root)
interfaces = get_interfaces()

if interfaces == -1: # user does not have requirements (in this case probably aircrack tools)
    stop_and_warn(root, 0)

elif len(interfaces) > 0: # user has no wifi interfaces 
    variable.set("Interface") 
    interface_list = OptionMenu(top, variable, interfaces, command=interface)
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
root.mainloop()