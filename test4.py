import tkinter as tk
import adi
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time
matplotlib.use('TkAgg')

class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")


class SpectrumAnalyzerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Real-time Spectrum Analyzer GUI")
        self.geometry("1200x1200")

        self._init_widgets()
        self._init_spectrum_analyzer()

    def _init_widgets(self):
        self.quit_button = tk.Button(self, text="Quit", command=self.quit)
        self.quit_button.pack()

        self.fig, (self.ax_spectrum, self.ax_spectrogram) = plt.subplots(2, 1, figsize=(8, 12))
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.settings_frame = tk.Frame(self)
        self.settings_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=0)

        self.adalm_pluto_settings = ScrollableFrame(self.settings_frame)
        self.adalm_pluto_settings.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.adalm_pluto_settings_label = tk.Label(self.adalm_pluto_settings.scrollable_frame, text="ADALM-Pluto Settings", font=("Arial", 16))
        self.adalm_pluto_settings_label.pack()

        self.filter_settings = ScrollableFrame(self.settings_frame)
        self.filter_settings.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)
        self.filter_settings_label = tk.Label(self.filter_settings.scrollable_frame, text="Filter Settings", font=("Arial", 16))
        self.filter_settings_label.pack()

    def _init_spectrum_analyzer(self):
        self.spectrum_analyzer = adi.Pluto("ip:192.168.2.1")  # Replace with the correct IP address or URI
        # self.spectrum_analyzer.rx_lo = int(2.4e9)  # Set the LO frequency
        # self.spectrum_analyzer.sample_rate = int(20e6)  # Set the sample rate
        # self.spectrum_analyzer.rx_buffer_size = 2**11  # Set the buffer size (reduced for faster updates)
        self.spectrogram_data = []
        self.running = True

    def plot_spectrum(self):
        while self.running:
            samples = self.spectrum_analyzer.rx()
            spectrum = 20 * np.log10(np.abs(np.fft.fftshift(np.fft.fft(samples))))
            frequencies = np.fft.fftshift(np.fft.fftfreq(len(samples), 1 / self.spectrum_analyzer.sample_rate))

            self.ax_spectrum.clear()
            self.ax_spectrum.plot(frequencies, spectrum)
            self.ax_spectrum.set_title("Real-time Spectrum")
            self.ax_spectrum.set_xlabel("Frequency (Hz)")
            self.ax_spectrum.set_ylabel("Magnitude (dB)")

            self.spectrogram_data.append(spectrum)
            if len(self.spectrogram_data) > 15:
                self.spectrogram_data.pop(0)

            self.ax_spectrogram.clear()
            self.ax_spectrogram.pcolormesh(frequencies, np.arange(len(self.spectrogram_data)),
                                           np.array(self.spectrogram_data), cmap='viridis')
            self.ax_spectrogram.set_title("Spectrogram")
            self.ax_spectrogram.set_xlabel("Frequency (Hz)")
            self.ax_spectrogram.set_ylabel("Time")

            self.canvas.draw()
            time.sleep(0.05)

    def start_plotting(self):
        self.plot_thread = threading.Thread(target=self.plot_spectrum)
        self.plot_thread.start()

    def quit(self):
        self.running = False
        self.plot_thread.join()
        self.spectrum_analyzer._ctx.destroy()
        self.destroy()


if __name__ == "__main__":
    app = SpectrumAnalyzerGUI()

    # Add sample ADALM-Pluto settings
    settings = [
        ("LO Frequency", "2.4 GHz"),
        ("Sample Rate", "20 MHz"),
        ("Buffer Size", "2048"),
    ]
    for setting, value in settings:
        row = tk.Frame(app.adalm_pluto_settings.scrollable_frame)
        label = tk.Label(row, text=f"{setting}:")
        entry = tk.Entry(row)
        entry.insert(0, value)
        row.pack(fill="x", padx=5, pady=5)
        label.pack(side="left")
        entry.pack(side="right")

    # Add sample filter settings
    filters = [
        ("Low-pass", "5 MHz"),
        ("High-pass", "2 MHz"),
        ("Band-pass", "3 MHz - 4 MHz"),
    ]
    for flt, value in filters:
        row = tk.Frame(app.filter_settings.scrollable_frame)
        label = tk.Label(row, text=f"{flt}:")
        entry = tk.Entry(row)
        entry.insert(0, value)
        row.pack(fill="x", padx=5, pady=5)
        label.pack(side="left")
        entry.pack(side="right")

    # Rearrange frames
    app.settings_frame.pack_forget()
    app.canvas.get_tk_widget().pack_forget()

    app.filter_settings.pack(side=tk.LEFT, fill=tk.BOTH, expand=0)
    app.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
    app.adalm_pluto_settings.pack(side=tk.RIGHT, fill=tk.BOTH, expand=0)
    app.settings_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=0)
    app.filter_settings.pack(side=tk.LEFT, fill=tk.BOTH, expand=0)

    app.start_plotting()
    app.mainloop()
