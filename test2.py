import numpy as np
import adi
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
from scipy import signal
import threading

pluto = adi.Pluto(uri="ip:192.168.2.1")

root = tk.Tk()
root.title("ADALM-PLUTO Real-time Signal and Spectrogram")
plt.style.use('dark_background')

signal_p = np.abs(np.fft.fftshift(np.fft.fft(pluto.rx())))
simple_rate = pluto.sample_rate

# set up initial signal plot
fig, (ax1, ax2) = plt.subplots(2, 1)
line1, = ax1.plot(signal_p)
ax1.set_title('Real-time Signal')
fre, time, sepc = signal.spectrogram(signal_p,fs=simple_rate, nperseg=24, noverlap=12)
spectrogram_data = np.zeros((fre.size, time.size))
a = ax2.imshow(spectrogram_data, aspect='auto', origin='lower', cmap='inferno')

canvas = FigureCanvasTkAgg(fig, root)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()
canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

update_thread = None
is_running = False

# function to continuously update the signal plot in real-time
def update_signal():
    global signal_p, simple_rate, is_running, ddd
    while is_running:
        signal_p = np.abs(np.fft.fftshift(np.fft.fft(pluto.rx())))
        line1.set_ydata(signal_p)
        fre, time, sepc = signal.spectrogram(signal_p,fs=simple_rate, nperseg=24, noverlap=12)

        new_row = sepc[0,:]  # Replace this with your own function to get the latest spectrogram row
        spectrogram_data[:-1] = spectrogram_data[1:]  # Shift all rows down by one
        spectrogram_data[-1] = new_row
        a.set_array(spectrogram_data)
        canvas.draw()

# function to start the signal update thread
def start_update():
    global update_thread, is_running
    if not is_running:
        is_running = True
        update_thread = threading.Thread(target=update_signal)
        update_thread.daemon = True
        update_thread.start()

# function to stop the signal update thread
def stop_update():
    global is_running
    is_running = False

# create a button to start and stop the signal update thread
start_stop_button = tk.Button(master=root, text="Start/Stop Update", command=lambda: [start_update() if not is_running else stop_update()])
start_stop_button.pack(side=tk.BOTTOM)
root.mainloop()
