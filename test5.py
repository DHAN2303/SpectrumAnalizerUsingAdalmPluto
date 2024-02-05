import tkinter as tk
from tkinter import ttk
from datetime import datetime
import numpy as np
import adi
import threading
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.colors import LinearSegmentedColormap
import time
matplotlib.use('TkAgg')

# Define the colors for the colormap
colors = [(0, 0, 0), (0.5, 0, 0.5), (1, 0, 0)]  # black, purple, red
# Create the colormap
cmap_name = 'black_purple_red'
new_cmap = LinearSegmentedColormap.from_list(cmap_name, colors)

update_thread = None
is_running = False

'''----------------------- Arayüz ----------------------------'''

# GUI Ayarları
root = tk.Tk()
resolution = "1660x960"
# resolution = "1920x1080"
root.geometry(resolution)
root.title("Spektrum Analizör")
width_r, height_r = resolution.split("x")[0], resolution.split("x")[1]
plt.style.use('dark_background')
# root.iconbitmap()
ana_frame = tk.Frame(root)
ana_frame.pack(fill=tk.BOTH)

''' -------------------------------------- ekranın sol tarafı -------------------------------------------------------'''

sol_frame = tk.Frame(ana_frame, width=int(width_r) * 0.2, height=height_r)
sol_frame.pack(side="left", fill=tk.BOTH)

style = ttk.Style()
style.configure("Vertical.TScrollbar", background="black", bordercolor="black", arrowcolor="white")

sol_scrollbar = ttk.Scrollbar(sol_frame, style="Vertical.TScrollbar")
sol_scrollbar.grid(row=0, column=1, sticky=tk.NSEW)

sol_canvas = tk.Canvas(sol_frame, height=height_r, yscrollcommand=sol_scrollbar.set)
sol_canvas.grid(row=0, column=0, sticky=tk.NSEW)
sol_scrollbar.config(command=sol_canvas.yview)

'''------------------------------ayar menüsü-----------------------------------'''

'''----------------------------- filtre Ayarlari ------------------------------'''
filtre_Ayarlari_frame = tk.Frame(sol_canvas, relief=tk.GROOVE, padx=int(width_r) * 0.03)
filtre_Ayarlari_frame.grid(row=0, column=0, sticky=tk.NSEW)
sol_canvas.create_window(0, 0, window=filtre_Ayarlari_frame, anchor='nw')

filtre_Ayarlari = tk.Label(filtre_Ayarlari_frame, text="Filtre Ayarları",  font=("Muna", 19),pady=10)
filtre_Ayarlari.grid(row=0, column=0, sticky=tk.NSEW)

filtre_degeri = tk.IntVar()
filtre_degeri.set(1)
filtre_btn1 = tk.Radiobutton(filtre_Ayarlari_frame, text="Filtresiz", command='', font="Verdana 15", variable=filtre_degeri, value=1, pady=5)
filtre_btn1.grid(row=1, column=0, sticky=tk.NSEW)
filtre_btn2 = tk.Radiobutton(filtre_Ayarlari_frame, text="Hann Filtresi", command='', font="Verdana 15", variable=filtre_degeri, value=2, pady=5)
filtre_btn2.grid(row=2, column=0, sticky=tk.NSEW)
filtre_btn3 = tk.Radiobutton(filtre_Ayarlari_frame, text="Hamming Filtresi", command='', font="Verdana 15", variable=filtre_degeri, value=3, pady=5)
filtre_btn3.grid(row=3, column=0, sticky=tk.NSEW)
filtre_btn4 = tk.Radiobutton(filtre_Ayarlari_frame, text="Blackman-Harris Filtresi", command='', font="Verdana 15", variable=filtre_degeri, value=4, pady=5)
filtre_btn4.grid(row=4, column=0, sticky=tk.NSEW)
filtre_btn5 = tk.Radiobutton(filtre_Ayarlari_frame, text="Flattop Filtresi", command='', font="Verdana 15", variable=filtre_degeri, value=5, pady=5)
filtre_btn5.grid(row=5, column=0, sticky=tk.NSEW)

'''-------------------------------Frekans Ayarları --------------------------------'''
frekans_Ayarlari_frame = tk.Frame(sol_canvas, relief=tk.GROOVE, padx=int(width_r) * 0.03)
frekans_Ayarlari_frame.grid(row=1, column=0, sticky=tk.NSEW)
sol_canvas.create_window(0, 0, window=frekans_Ayarlari_frame, anchor='nw')

frekans_Ayarlari = tk.Label(frekans_Ayarlari_frame, text="Frekans Ayarları", font=("Muna", 19), pady=10)
frekans_Ayarlari.grid(row=0, column=0, sticky=tk.NSEW)

frekans_text = tk.StringVar()
frekans_label = tk.Label(frekans_Ayarlari_frame, textvariable=frekans_text, font="Verdana 15", pady=5)
frekans_label.grid(row=1, column=0, sticky=tk.NSEW)
frekans_text.set("Frekans: ")

frekans_giris = tk.Entry(frekans_Ayarlari_frame, font="Verdana 15", width=8)
frekans_giris.grid(row=2, column=0, pady=5, sticky=tk.NSEW)

'''------------------------Tarama Ayarları------------------------------------'''
tarama_Ayarlari_frame = tk.Frame(sol_canvas, relief=tk.GROOVE, padx=int(width_r) * 0.03)
tarama_Ayarlari_frame.grid(row=2, column=0, sticky=tk.NSEW)
sol_canvas.create_window(0, 0, window=tarama_Ayarlari_frame, anchor='nw')

tarama_Ayarlari = tk.Label(tarama_Ayarlari_frame, text="Tarama Ayarları", font=("Muna", 19), pady=10)
tarama_Ayarlari.grid(row=0, column=0, sticky=tk.NSEW)

tarama_hizi_text = tk.StringVar()
tarama_hizi_label = tk.Label(tarama_Ayarlari_frame, textvariable=tarama_hizi_text, font="Verdana 15", pady=5)
tarama_hizi_label.grid(row=1, column=0, sticky=tk.NSEW)
tarama_hizi_text.set("Tarama Hızı (ms): ")

tarama_hizi_giris = tk.Entry(tarama_Ayarlari_frame, font="Verdana 15", width=8)
tarama_hizi_giris.grid(row=2, column=0, pady=5, sticky=tk.NSEW)

'''------------------------Kontrol Düğmeleri----------------------------'''
kontrol_dugmeleri_frame = tk.Frame(sol_canvas, relief=tk.GROOVE, padx=int(width_r) * 0.03)
kontrol_dugmeleri_frame.grid(row=3, column=0, sticky=tk.NSEW)
sol_canvas.create_window(0, 0, window=kontrol_dugmeleri_frame, anchor='nw')

start_btn = tk.Button(kontrol_dugmeleri_frame, text="Başlat", font=("Muna", 15), padx=30, pady=10, bg='green', fg='white', command=start_scanning)
start_btn.grid(row=0, column=0, sticky=tk.NSEW)

stop_btn = tk.Button(kontrol_dugmeleri_frame, text="Durdur", font=("Muna", 15), padx=30, pady=10, bg='red', fg='white', command=stop_scanning)
stop_btn.grid(row=0, column=1, sticky=tk.NSEW)

'''----------------------Ana Ekran----------------------------------'''

# Ana ekran ayarları
fig = plt.figure(figsize=(10, 6), dpi=100)
ax = fig.add_subplot(111)
plt.subplots_adjust(left=0.3, right=0.98, top=0.95, bottom=0.1)
ax.set_title("Spektrum Analizörü", fontsize=18)
ax.set_xlabel("Frekans (Hz)", fontsize=14)
ax.set_ylabel("Güç (dBFS)", fontsize=14)
ax.set_xlim(0, 3000)
ax.set_ylim(-100, 0)
canvas = FigureCanvasTkAgg(fig, master=ana_frame)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

root.mainloop()
