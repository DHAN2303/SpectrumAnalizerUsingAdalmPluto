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
filtre_btn1 = tk.Radiobutton(filtre_Ayarlari_frame,text="Filtresiz",command='', font="Verdana 15", variable=filtre_degeri,value=1,pady=5)
filtre_btn1.grid(row=1, column=0, sticky=tk.NSEW)
filtre_btn2 = tk.Radiobutton(filtre_Ayarlari_frame,text="Hann Filtresi",command='', font="Verdana 15", variable=filtre_degeri,value=2,pady=5)
filtre_btn2.grid(row=2, column=0, sticky=tk.NSEW)
filtre_btn3 = tk.Radiobutton(filtre_Ayarlari_frame,text="Blackman Filtresi",command='', font="Verdana 15", variable=filtre_degeri,value=3,pady=5)
filtre_btn3.grid(row=3, column=0, sticky=tk.NSEW)
filtre_btn4 = tk.Radiobutton(filtre_Ayarlari_frame,text="Hamming Filtresi",command='', font="Verdana 15", variable=filtre_degeri,value=4,pady=5)
filtre_btn4.grid(row=4, column=0, sticky=tk.NSEW)

'''--------------------------- Gorunum Ayarlari ---------------------------------'''
gorunum_Ayarlari_frame = tk.Frame(sol_canvas, relief=tk.GROOVE, padx=int(width_r) * 0.03)
gorunum_Ayarlari_frame.grid(row=1, column=0, sticky=tk.NSEW)
sol_canvas.create_window(0, 200, window=gorunum_Ayarlari_frame, anchor='nw')

gorunum_Ayarlari = tk.Label(gorunum_Ayarlari_frame, text="Görünüm Ayarları", font=("Muna", 19))
gorunum_Ayarlari.grid(row=0, column=0,columnspan=2, sticky=tk.NSEW)

color_map_ayari = tk.IntVar()
color_map_ayari.set(1)
color_map_ayari_btn1 = tk.Radiobutton(gorunum_Ayarlari_frame,text="Jet",command='', font="Verdana 15", variable=color_map_ayari,value=1,pady=5)
color_map_ayari_btn1.grid(row=1, column=0,columnspan=2, sticky=tk.NSEW)
color_map_ayari_btn2 = tk.Radiobutton(gorunum_Ayarlari_frame,text="Siyah - Kırmızı",command='', font="Verdana 15", variable=color_map_ayari,value=2,pady=5)
color_map_ayari_btn2.grid(row=2, column=0,columnspan=2, sticky=tk.NSEW)
color_map_ayari_btn3 = tk.Radiobutton(gorunum_Ayarlari_frame,text="Viridis",command='', font="Verdana 15", variable=color_map_ayari,value=3,pady=5)
color_map_ayari_btn3.grid(row=3, column=0,columnspan=2, sticky=tk.NSEW)

color_map_ayari_label = tk.Label(gorunum_Ayarlari_frame, text="Vmax:", font=("Muna", 15))
color_map_ayari_label.grid(row=4, column=0, sticky=tk.W)

color_map_ayari_vra = tk.StringVar(value='4000')
color_map_ayari_kutusu = ttk.Entry(gorunum_Ayarlari_frame, width=4,textvariable=color_map_ayari_vra)
color_map_ayari_kutusu.grid(row=4, column=1, sticky=tk.NSEW)

color_map_ayari_scale = tk.Scale(gorunum_Ayarlari_frame, from_=100, to=20000, resolution=100, orient='horizontal')
color_map_ayari_scale.grid(row=6, column=0,columnspan=2, sticky=tk.NSEW)
color_map_ayari_scale.set(value='4000')

color_map_ayari_dugmesi = tk.Button(gorunum_Ayarlari_frame, text='Pozisyon Degistir', command=lambda: pozisyon_degistir(color_map_ayari_kutusu, color_map_ayari_scale))
color_map_ayari_dugmesi.grid(row=7, column=0,columnspan=2, sticky=tk.NSEW)

'''------------------------------------------------ ekranın orta tarafı ---------------------------------------------'''
han_filtre = 1
filtresiz = 1
hamming_filtre = 1
blackman_filtre = 1
viridis = 1
siyah_kirimzi = 1
jet = 1
def filtre_uygula():
    global blackman_filtre, hamming_filtre, filtresiz, han_filtre, se_filtre
    if filtre_degeri.get() == 1:
        se_filtre = 1
        if filtresiz == 1:
            msg_log_txt.delete("1.0", tk.END)
            log_date = datetime.now().strftime("%H:%M:%S")
            msg_log_txt.configure(state="normal")
            msg_log_txt.insert("1.0", f"[{log_date}]:Filtre uygulanmadı.\n", "green")
            msg_log_txt.configure(state="disabled")
            filtresiz = 0
            hamming_filtre = 1
            blackman_filtre = 1
            han_filtre = 1

    elif filtre_degeri.get() == 2:
        se_filtre = np.hanning(pluto.rx_buffer_size)
        if han_filtre == 1:
            msg_log_txt.delete("1.0", tk.END)
            log_date = datetime.now().strftime("%H:%M:%S")
            msg_log_txt.configure(state="normal")
            msg_log_txt.insert("1.0", f"[{log_date}]: Hann filtresi \nuygulandı.\n", "green")
            msg_log_txt.configure(state="disabled")
            filtresiz = 1
            hamming_filtre = 1
            blackman_filtre = 1
            han_filtre = 0


    elif filtre_degeri.get() == 3:
        se_filtre = np.blackman(pluto.rx_buffer_size)
        if blackman_filtre == 1:
            msg_log_txt.delete("1.0", tk.END)
            log_date = datetime.now().strftime("%H:%M:%S")
            msg_log_txt.configure(state="normal")
            msg_log_txt.insert("1.0", f"[{log_date}]: Blackman filtresi \nuygulandı.\n", "green")
            msg_log_txt.configure(state="disabled")
            filtresiz = 1
            hamming_filtre = 1
            blackman_filtre = 0
            han_filtre = 1


    elif filtre_degeri.get() == 4:
        se_filtre = np.hamming(pluto.rx_buffer_size)
        if hamming_filtre == 1:
            msg_log_txt.delete("1.0", tk.END)
            log_date = datetime.now().strftime("%H:%M:%S")
            msg_log_txt.configure(state="normal")
            msg_log_txt.insert("1.0", f"[{log_date}]: Hamming filtresi \nuygulandı.\n", "green")
            msg_log_txt.configure(state="disabled")
            filtresiz = 1
            hamming_filtre = 0
            blackman_filtre = 1
            han_filtre = 1

def colormap_degistir():
    global jet, siyah_kirimzi, viridis
    if color_map_ayari.get() == 1:
        spectrogram_image.set_cmap('jet')
        if jet == 1:
            msg_log_txt.delete("1.0", tk.END)
            log_date = datetime.now().strftime("%H:%M:%S")
            msg_log_txt.configure(state="normal")
            msg_log_txt.insert("1.0", f"[{log_date}]:Cmap değiştirildi.\n", "green")
            msg_log_txt.configure(state="disabled")
            jet = 0
            siyah_kirimzi = 1
            viridis = 1

    elif color_map_ayari.get() == 2:
        spectrogram_image.set_cmap(new_cmap)
        if siyah_kirimzi == 1:
            msg_log_txt.delete("1.0", tk.END)
            log_date = datetime.now().strftime("%H:%M:%S")
            msg_log_txt.configure(state="normal")
            msg_log_txt.insert("1.0", f"[{log_date}]: Cmap değiştirildi.\n", "green")
            msg_log_txt.configure(state="disabled")
            jet = 1
            siyah_kirimzi = 0
            viridis = 1


    elif color_map_ayari.get() == 3:
        spectrogram_image.set_cmap('viridis')
        if viridis == 1:
            msg_log_txt.delete("1.0", tk.END)
            log_date = datetime.now().strftime("%H:%M:%S")
            msg_log_txt.configure(state="normal")
            msg_log_txt.insert("1.0", f"[{log_date}]: Cmap değiştirildi.\n", "green")
            msg_log_txt.configure(state="disabled")
            jet = 1
            siyah_kirimzi = 1
            viridis = 0

def spectrogram_al(alinan_sinyal_spek):
    global color_map_ayari_scale
    spectrogram_data.append(alinan_sinyal_spek)
    if len(spectrogram_data) > 15:
        spectrogram_data.pop(0)
    spectrogram_image.set_data(spectrogram_data)
    spectrogram_image.set_extent([(-fs_fs / 2 / 1e3), (fs_fs / 2 / 1e3), 0, pluto.rx_buffer_size / fs_fs])
    spectrogram_image.set_clim(vmin=0, vmax=int(color_map_ayari_scale.get()))
    colormap_degistir()

def gencelle_alinan_sinyal():
    global fs_fs, spectrogram_image
    spectrogram_image = ax2.imshow([[]], aspect='auto', origin='lower', extent=[0, 0, 0, 0], vmin=0, cmap='jet')
    while is_running:

        # filtre seçimi
        filtre_uygula()

        # pluto cihazına ayarları gönderme
        pluto.gain_control_mode_chan0 = attack_mode
        pluto.rx_lo = int(frekans_scale.get()) * 1000000
        pluto.rx_rf_bandwidth = int(bant_scale.get())
        pluto.rx_hardwaregain_chan0 = int(kazanc_scale.get())

        # frekans ayarlama ve filtrelenmiş sinyalın spektrumu çizdirme
        fs_fs = pluto.rx_rf_bandwidth
        frekans_fs = np.arange((fs_fs / -2), (fs_fs / 2), fs_fs / pluto.rx_buffer_size)
        alinan_sinyal = pluto.rx() * se_filtre
        alinan_sinyal_spek = np.abs(np.fft.fftshift(np.fft.fft(alinan_sinyal)))
        line1.set_ydata(alinan_sinyal_spek)
        line1.set_xdata(frekans_fs/1e3)
        yeksen_ust_limit = int(yeksen_scale.get())
        ax1.set_ylim(0,yeksen_ust_limit)
        ax1.set_xlim((fs_fs / -2)/1e3, (fs_fs / 2)/1e3)

        # spectrogramı alma ve waterfall ekranı oluşturme
        spectrogram_al(alinan_sinyal_spek)

        anlik_grafik_canvas.draw_idle()
        time.sleep(0.05)

# figure aç
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11/1, 9.5/1), layout="tight")

orta_frame = tk.Frame(ana_frame, height=height_r)
orta_frame.pack(side="left")

'''------------------------ Anlik sinyal ve spektrum akış zaman  Grafik ----------------------------------'''
anlik_grafik = tk.Frame(orta_frame, height=int(height_r) * 0.5)
anlik_grafik.pack(side="bottom", fill=tk.BOTH)
anlik_grafik_canvas = FigureCanvasTkAgg(fig, anlik_grafik)
anlik_grafik_canvas.get_tk_widget().pack(fill=tk.BOTH)
anlik_grafik_canvas._tkcanvas.pack(side="bottom", fill=tk.BOTH, expand=1)

toolbar_frame = tk.Frame(orta_frame)
toolbar_frame.pack(side="top", fill=tk.BOTH)

toolbar = NavigationToolbar2Tk(anlik_grafik_canvas, toolbar_frame)
toolbar.update()
toolbar.pack(side="left", fill=tk.BOTH)


'''-------------------------------------------- ekranın sağ tarafı --------------------------------------------------'''
sag_frame = tk.Frame(ana_frame, width=int(width_r) * 0.3, height=height_r)
sag_frame.pack(side="left", fill=tk.BOTH)

sag_scrollbar = ttk.Scrollbar(sag_frame, style="Vertical.TScrollbar")
sag_scrollbar.grid(row=0, column=0, sticky=tk.NSEW)

sag_canvas = tk.Canvas(sag_frame, height=height_r, yscrollcommand=sag_scrollbar.set)
sag_canvas.grid(row=0, column=1, sticky=tk.E)
sag_scrollbar.config(command=sag_canvas.yview)


def pozisyon_degistir(entry_widget, slide_bar):
    value = entry_widget.get()

    if value:
        slide_bar.set(int(value))
    else:
        msg_log_txt.delete("1.0", tk.END)
        log_date = datetime.now().strftime("%H:%M:%S")
        msg_log_txt.configure(state="normal")
        msg_log_txt.insert("1.0", f"[{log_date}]: Değer Girilmemiş.\n", "red")
        msg_log_txt.configure(state="disabled")

def pozisyon_degistir_bant(entry_widget, slide_bar):
    value = entry_widget.get()
    secilmis_birim = birim_ayari_sec_vra.get()
    birim_degeri = [birim_ayar[1] for birim_ayar in birim_ayari if birim_ayar[0] == secilmis_birim][0]

    if value:
        if int(birim_degeri) == 1000 and int(value) > 30000 or int(birim_degeri) == 1000000 and int(value) > 30:
            msg_log_txt.delete("1.0", tk.END)
            log_date = datetime.now().strftime("%H:%M:%S")
            msg_log_txt.configure(state="normal")
            msg_log_txt.insert("1.0", f"[{log_date}]: \nGirilen değer 30MHzdan büyük.\n", "red")
            msg_log_txt.configure(state="disabled")
        else:
            slide_bar.set(int(value) * int(birim_degeri))
    else:
        msg_log_txt.delete("1.0", tk.END)
        log_date = datetime.now().strftime("%H:%M:%S")
        msg_log_txt.configure(state="normal")
        msg_log_txt.insert("1.0", f"[{log_date}]: Değer Girilmemiş.\n", "red")
        msg_log_txt.configure(state="disabled")

'''------------------------ Adalm Pluto Ayarlari ----------------------------------'''
adalmPlutoAyarlari_frame = tk.Frame(sag_canvas, relief=tk.GROOVE, padx=int(width_r) * 0.03)
sag_canvas.create_window(0, 0, window=adalmPlutoAyarlari_frame)

adalmPlutoAyarlari = tk.Label(adalmPlutoAyarlari_frame, text="ADALM-PLUTO AYARLARI", font=("Muna", 16),pady=10)
adalmPlutoAyarlari.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW)

def basla_dugmesi():
    global pluto, line1, a, attack_mode, update_thread, is_running, spectrogram_data

    if button_baslat.get() == "Başlat":
        try:
            pluto = adi.Pluto(uri=f"ip:{ip_entery.get()}")

            log_date = datetime.now().strftime("%H:%M:%S")
            msg_log_txt.configure(state="normal")
            msg_log_txt.insert("1.0", f"[{log_date}]: Cihaz Bağlandı.\n", "green")
            msg_log_txt.configure(state="disabled")

        except:
            msg_log_txt.delete("1.0", tk.END)
            log_date = datetime.now().strftime("%H:%M:%S")
            msg_log_txt.configure(state="normal")
            msg_log_txt.insert("1.0", f"[{log_date}]: Cihaz Bulunmadı.\n", "red")
            msg_log_txt.configure(state="disabled")
            return

        else:
            button_baslat.set("Durdur")
            secilmis_mode = secenek_mode.get()
            attack_mode = [mode[1] for mode in modes if mode[0] == secilmis_mode][0]

            pluto.rx_buffer_size = int(num_samps_entery.get())
            # pluto.sample_rate = int(ornek_frekansi_entery.get()) * 1000

            fs_fs = pluto.rx_rf_bandwidth
            frekans_fs = np.arange((fs_fs / -2), (fs_fs / 2), fs_fs / pluto.rx_buffer_size)

            alinan_sinyal = pluto.rx()
            alinan_sinyal_spek = np.abs(np.fft.fftshift(np.fft.fft(alinan_sinyal)))

            line1, = ax1.plot(frekans_fs/1e3,alinan_sinyal_spek)
            spectrogram_data = []


            ax1.set_ylabel("Magnitude [dB]")
            ax1.set_xlabel("Frequency [kHz]")
            ax2.set_ylabel("Time (s)")

            num_samps_entery.config(state=tk.DISABLED)
            ip_entery.config(state=tk.DISABLED)
            ornek_frekansi_entery.config(state=tk.DISABLED)
            button_baslat1.config(state='disabled')
            root.after(1000, button_baslat1.config, {'state': 'normal'})

            if not is_running:
                is_running = True
                update_thread = threading.Thread(target=gencelle_alinan_sinyal)
                update_thread.daemon = True
                update_thread.start()

def durdur_dugmesi():
    global is_running

    if button_baslat.get() == "Durdur":
        is_running = False
        button_baslat.set("Başlat")

        ax1.clear()
        ax2.clear()

        log_date = datetime.now().strftime("%H:%M:%S")
        msg_log_txt.configure(state="normal")
        msg_log_txt.insert("1.0", f"[{log_date}]: Cihaz Durduruldu.\n", "orange")
        msg_log_txt.configure(state="disabled")

        num_samps_entery.config(state=tk.NORMAL)
        ornek_frekansi_entery.config(state=tk.NORMAL)
        ip_entery.config(state=tk.NORMAL)
        button_baslat1.config(state='disabled')
        root.after(1000, button_baslat1.config, {'state': 'normal'})

ip_addr = tk.StringVar()
ip_addr.set("192.168.2.1")
ip_label = tk.Label(adalmPlutoAyarlari_frame, text="             IP Address: ", font="Verdana 15", pady=5)
ip_label.grid(row=1, column=0,sticky=tk.NSEW)
ip_entery = ttk.Entry(adalmPlutoAyarlari_frame, textvariable=ip_addr, width=12)
ip_entery.grid(row=2, column=0, columnspan=2, sticky=tk.NSEW)

num_samps = tk.StringVar()
num_samps.set("1024") # number of samples per call to rx()
num_samps_label = tk.Label(adalmPlutoAyarlari_frame, text="Örnek sayısı:")
num_samps_label.grid(row=3, column=0,sticky=tk.W)
num_samps_entery = ttk.Entry(adalmPlutoAyarlari_frame, textvariable=num_samps, width=5)
num_samps_entery.grid(row=3, column=1, sticky=tk.E)

ornek_frekansi = tk.StringVar()
ornek_frekansi.set("30720") # number of samples per call to rx()
ornek_frekansi_label = tk.Label(adalmPlutoAyarlari_frame, text="Örnekleme frekansı [kHz]:")
ornek_frekansi_label.grid(row=4, column=0,sticky=tk.W)
ornek_frekansi_entery = ttk.Entry(adalmPlutoAyarlari_frame, textvariable=ornek_frekansi, width=5)
ornek_frekansi_entery.grid(row=4, column=1, sticky=tk.E)


button_baslat = tk.StringVar()
button_baslat.set("Başlat")
button_baslat1 = tk.Button(adalmPlutoAyarlari_frame, textvariable=button_baslat, command=lambda: [basla_dugmesi() if not is_running else durdur_dugmesi()], width=2)
button_baslat1.grid(row=7, column=0, columnspan=2, sticky=tk.NSEW)

'''-------------------------------------- Log message ---------------------------'''
msg_log_txt_frame = tk.Frame(sag_canvas, relief=tk.GROOVE, padx=int(width_r) * 0.03)
sag_canvas.create_window(0, 143, window=msg_log_txt_frame)

msg_log_label = tk.Label(msg_log_txt_frame, text="Message Log:", font="Verdana 15")
msg_log_label.grid(row=0, column=0, sticky=tk.NSEW)

msg_log_txt = tk.Text(msg_log_txt_frame, width=30, height=5)
msg_log_txt.grid(row=1, column=0, sticky=tk.NSEW)
msg_log_txt.tag_configure("green", foreground="green")
msg_log_txt.tag_configure("red", foreground="red")
msg_log_txt.tag_configure("orange", foreground="orange")
msg_log_txt.configure(state="disabled")

'''------------------------ Frekans Ayarlari -------------------------------------'''
frekansAyarlari_frame = tk.Frame(sag_canvas, relief=tk.GROOVE, padx=int(width_r) * 0.03)
sag_canvas.create_window(0, 272, window=frekansAyarlari_frame)

frekansAyarlari = tk.Label(frekansAyarlari_frame, text="Merkez Frekans [MHz]", font="Verdana 15", pady=22)
frekansAyarlari.grid(row=0, column=0, sticky=tk.NSEW)

'''------------- Değer girme kutusu ---------------'''
frekans_kutusu_vra = tk.StringVar(value='2400')
frekans_kutusu = ttk.Entry(frekansAyarlari_frame,textvariable=frekans_kutusu_vra)
frekans_kutusu.grid(row=1, column=0, sticky=tk.NSEW)

'''------------- frekans slidebar -----------------'''
frekans_scale = tk.Scale(frekansAyarlari_frame, from_=325, to=3800, resolution=25, orient='horizontal')
frekans_scale.grid(row=2, column=0, sticky=tk.NSEW)
frekans_scale.set("2000")

'''------------- frekans ayarlama düğmesi ---------'''
frekans_dugmesi = tk.Button(frekansAyarlari_frame, text='Pozisyon Degistir', command=lambda: pozisyon_degistir(frekans_kutusu, frekans_scale))
frekans_dugmesi.grid(row=3, column=0, sticky=tk.NSEW)

'''------------------------ Bant Genisligi Ayarlari ----------------------------------'''
bantGenisligiAyarlari_frame = tk.Frame(sag_canvas, relief=tk.GROOVE, padx=int(width_r) * 0.03)
sag_canvas.create_window(0, 434, window=bantGenisligiAyarlari_frame)

bantGenisligiAyarlari = tk.Label(bantGenisligiAyarlari_frame, text="Bant Genişliği", font="Verdana 15", pady=25)
bantGenisligiAyarlari.grid(row=0, column=0,columnspan=2, sticky=tk.NSEW)

bant_kutusu_vra = tk.StringVar(value='4000')
bant_kutusu = ttk.Entry(bantGenisligiAyarlari_frame, width=11,textvariable=bant_kutusu_vra)
bant_kutusu.grid(row=1, column=0, sticky=tk.W)

birim_ayari = [("kHz", "1000"), ("MHz", "1000000")]
birim_ayari_sec_vra = tk.StringVar(value=birim_ayari[0][0])
birim_ayari_sec = ttk.OptionMenu(bantGenisligiAyarlari_frame, birim_ayari_sec_vra, birim_ayari[0][0], birim_ayari[0][0], birim_ayari[1][0])
birim_ayari_sec.grid(row=1, column=1, sticky=tk.E)

bant_scale = tk.Scale(bantGenisligiAyarlari_frame, from_=200000, to=20000000, resolution=1000, orient='horizontal')
bant_scale.set("18000000")
bant_scale.grid(row=2, column=0,columnspan=2, sticky=tk.NSEW)
bant_dugmesi = tk.Button(bantGenisligiAyarlari_frame, text='Pozisyon Degistir', command=lambda: pozisyon_degistir_bant(bant_kutusu, bant_scale))
bant_dugmesi.grid(row=3, column=0,columnspan=2, sticky=tk.NSEW)

'''------------------------------ grafik Y-ekseni ---------------------------------'''
y_ekseni_frame = tk.Frame(sag_canvas, relief=tk.GROOVE, padx=int(width_r) * 0.03)
sag_canvas.create_window(0, 600, window=y_ekseni_frame)

kazancAyarlari = tk.Label(y_ekseni_frame, text="      Y-ekseni Ayarlama     ", font="Verdana 15",pady=25)
kazancAyarlari.grid(row=0, column=0, sticky=tk.NSEW)

yeksen_kutusu_vra = tk.StringVar(value='10000')
yeksen_kutusu = ttk.Entry(y_ekseni_frame, width=4,textvariable=yeksen_kutusu_vra)
yeksen_kutusu.grid(row=1, column=0, sticky=tk.NSEW)

yeksen_scale = tk.Scale(y_ekseni_frame, from_=1000, to=30000, resolution=1000, orient='horizontal')
yeksen_scale.grid(row=2, column=0, sticky=tk.NSEW)
yeksen_scale.set("70")

yeksen_dugmesi = tk.Button(y_ekseni_frame, text='Pozisyon Degistir', command=lambda: pozisyon_degistir(yeksen_kutusu, yeksen_scale))
yeksen_dugmesi.grid(row=3, column=0, sticky=tk.NSEW)


'''--------------------------------- mode ------------------------------------------'''
mode_frame = tk.Frame(sag_canvas, relief=tk.GROOVE, padx=int(width_r) * 0.03)
sag_canvas.create_window(0, 730, window=mode_frame)

def mod_kazanc(event):
    global attack_mode
    # mode seçimi
    secilmis_mode = secenek_mode.get()
    attack_mode = [mode[1] for mode in modes if mode[0] == secilmis_mode][0]
    if attack_mode != 'manual':
        kazanc_kutusu.config(state='disabled')
        kazanc_scale.config(state='disabled')
        kazanc_dugmesi.config(state='disabled')
    else:
        kazanc_kutusu.config(state='normal')
        kazanc_scale.config(state='normal')
        kazanc_dugmesi.config(state='normal')

modes = [("   Yavaş Mod  ", "slow_attack"), ("    Hızlı Mod    ", "fast_attack"), (" Manuel Mod  ", "manual")]
mode_label = tk.Label(mode_frame, text="Otomatik Kazanç Kontrolü ", font="Verdana 15", pady=25)
mode_label.grid(row=0, column=0,sticky=tk.NSEW)
secenek_mode = tk.StringVar(value=modes[2][0])
secenek_mode_d = ttk.OptionMenu(mode_frame, secenek_mode, modes[2][0], modes[0][0], modes[1][0], modes[2][0])
secenek_mode_d.grid(row=1, column=0)
secenek_mode_d.bind('<Leave>', mod_kazanc)

'''----------------------------- Kazanc Ayarlari -----------------------------------'''
kazancAyarlari_frame = tk.Frame(sag_canvas, relief=tk.GROOVE, padx=int(width_r) * 0.03)
sag_canvas.create_window(0, 860, window=kazancAyarlari_frame)

kazancAyarlari = tk.Label(kazancAyarlari_frame, text="          Kazanç [dB]           ", font="Verdana 15",pady=25)
kazancAyarlari.grid(row=0, column=0, sticky=tk.NSEW)

'''------------- Değer girme kutusu ---------------'''
kazanc_kutusu_vra = tk.StringVar(value='70')
kazanc_kutusu = ttk.Entry(kazancAyarlari_frame, width=4,textvariable=kazanc_kutusu_vra)
kazanc_kutusu.grid(row=1, column=0, sticky=tk.NSEW)

'''----------*-- Kazanç ayarlama slidebar ---------'''
kazanc_scale = tk.Scale(kazancAyarlari_frame, from_=1, to=70, orient='horizontal')
kazanc_scale.grid(row=2, column=0, sticky=tk.NSEW)
kazanc_scale.set("70")

'''------------- Kazanç ayarlama düğmesi -----------'''
kazanc_dugmesi = tk.Button(kazancAyarlari_frame, text='Pozisyon Degistir', command=lambda: pozisyon_degistir(kazanc_kutusu, kazanc_scale))
kazanc_dugmesi.grid(row=3, column=0, sticky=tk.NSEW)






# verilen ayarlara göre sinyalı güncelle
adalmPlutoAyarlari_frame.update_idletasks()
frekansAyarlari_frame.update_idletasks()
bantGenisligiAyarlari_frame.update_idletasks()
kazancAyarlari_frame.update_idletasks()
sag_canvas.config(scrollregion=sag_canvas.bbox('all'))
filtre_Ayarlari_frame.update_idletasks()
gorunum_Ayarlari_frame.update_idletasks()
sol_canvas.config(scrollregion=sol_canvas.bbox('all'))

# GUI çalıştır
root.mainloop()
