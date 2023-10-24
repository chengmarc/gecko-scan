# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
import os
script_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_path)

from gecko_scan_libraries import sys
from gecko_scan_libraries import tkinter as tk
from gecko_scan_libraries import threading as td
from gecko_scan_libraries import config_create, config_read, config_save
from gecko_scan_functions import main1, main2, main3

config_create()

def execute():
    config_save(text1.get(), text2.get(), text3.get())
    if accept1.get() == "Accepted": main1(text1.get())
    if accept2.get() == "Accepted": main2(text2.get())
    if accept3.get() == "Accepted": main3(text3.get())

def thread_execute():
    thread = td.Thread(target=execute) 
    thread.start()

# %% Initialize Window
root = tk.Tk()
root.title("GeckoScan v1.11")
root.geometry("480x320")
root.iconbitmap("gecko_scan_icon.ico")
root.resizable(width=False, height=False)

window = tk.Frame(root)
window.pack(expand=True)

# %% Creating Main Frames
frame1 = tk.LabelFrame(window, text="Extraction Options")
frame2 = tk.LabelFrame(window, text="Save Locations")
button1 = tk.Button(window, text="Execute", command=thread_execute)
button2 = tk.Button(window, text="Exit", command=sys.exit)

frame1.grid(row=1, column=0, sticky="nswe", padx=20, pady=10, columnspan=2)
frame2.grid(row=2, column=0, sticky="nswe", padx=20, pady=10, columnspan=2)
frame2.columnconfigure(1, weight=1)
button1.grid(row=3, column=0, sticky="nswe", padx=20, pady=10)
button2.grid(row=3, column=1, sticky="nswe", padx=20, pady=10)

# %% Defining Functionality - Checkbox
accept1 = tk.StringVar(value="Accepted")
accept2 = tk.StringVar(value="Accepted")
accept3 = tk.StringVar(value="Not Accepted")

check1 = tk.Checkbutton(frame1, text="Daily Snapshot of All Cryptocurrencies",
                        variable=accept1, onvalue="Accepted", offvalue="Not Accepted")
check2 = tk.Checkbutton(frame1, text="Daily Snapshot by Category",
                        variable=accept2, onvalue="Accepted", offvalue="Not Accepted")
check3 = tk.Checkbutton(frame1, text="Database of Historical Prices",
                        variable=accept3, onvalue="Accepted", offvalue="Not Accepted")

check1.grid(row=0, column=0, sticky="w")
check2.grid(row=1, column=0, sticky="w")
check3.grid(row=2, column=0, sticky="w")

# %% Defining Functionality - Save Location
path1 = tk.StringVar(value=config_read("output_path_all_crypto")[0])
path2 = tk.StringVar(value=config_read("output_path_categories")[0])
path3 = tk.StringVar(value=config_read("output_path_database")[0])

label1 = tk.Label(frame2, text="Snapshot (All)")
label2 = tk.Label(frame2, text="Snapshot (Category)  ")
label3 = tk.Label(frame2, text="Database")
text1 = tk.Entry(frame2, textvariable=path1, width=30)
text2 = tk.Entry(frame2, textvariable=path2, width=30)
text3 = tk.Entry(frame2, textvariable=path3, width=30)

label1.grid(row=0, column=0, sticky="w")
label2.grid(row=1, column=0, sticky="w")
label3.grid(row=2, column=0, sticky="w")
text1.grid(row=0, column=1, sticky="e")
text2.grid(row=1, column=1, sticky="e")
text3.grid(row=2, column=1, sticky="e")

# %% Launch User Interface
window.mainloop()
