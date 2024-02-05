import tkinter as tk
import adi
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading


class SpectrumAnalyzerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Real-time Spectrum Analyzer GUI")
        self.geometry("1200x800")

        self._init_widgets()
        self._init_spectrum_analyzer()

    def _init_widgets(self):
        self.quit_button = tk.Button(self, text="Quit", command=self.quit)
        self.quit_button.grid(row=1, column=0, columnspan=3, sticky="ew")

        self.fig, (self.ax_spectrum, self.ax_spectrogram) = plt.subplots(2, 1, figsize=(8, 12))
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid(row=0, column=1, sticky="nsew")

        self.filter_settings = tk.LabelFrame(self, text="Filter Settings", padx=5, pady=5)
        self.filter_settings.grid(row=0, column=0, sticky="nsew")

        self.adalm_pluto_settings = tk.LabelFrame(self, text="ADALM-Pluto Settings", padx=5, pady=5)
        self.adalm_pluto_settings.grid(row=0, column=2, sticky="nsew")

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)

        self.rowconfigure(0, weight=1)

    def _init_spectrum_analyzer(self):
        self.spectrum_analyzer = adi.Pluto("ip:192.168.2.1")  # Replace with the correct IP address or URI
        # self.spectrum_analyzer.rx_lo = int(2.4e9)  # Set the LO frequency
        # self.spectrum_analyzer.sample_rate = int(20e6)  # Set the sample rate
        # self.spectrum_analyzer.rx_buffer_size = 2 ** 11  # Set the buffer size (reduced for faster updates)
        self.spectrogram_data = []
        self.running = True


    def plot_spectrum(self):
        spectrum_line, = self.ax_spectrum.plot([], [])
        spectrogram_image = self.ax_spectrogram.imshow([[]], aspect='auto', origin='lower', extent=[0, 0, 0, 0])

        while self.running:
            samples = self.spectrum_analyzer.rx()
            spectrum = 20 * np.log10(np.abs(np.fft.fftshift(np.fft.fft(samples))))
            frequencies = np.fft.fftshift(np.fft.fftfreq(len(samples), 1 / self.spectrum_analyzer.sample_rate))

            self.ax_spectrum.clear()
            self.ax_spectrum.plot(frequencies, spectrum)
            self.ax_spectrum.set_title("Spectrum")
            self.ax_spectrum.set_xlabel("Frequency [Hz]")
            self.ax_spectrum.set_ylabel("Magnitude [dB]")

            self.spectrogram_data.append(spectrum)
            if len(self.spectrogram_data) > 15:
                self.spectrogram_data.pop(0)

            spectrogram_image.set_data(self.spectrogram_data)
            spectrogram_image.set_extent([frequencies[0], frequencies[-1], 0, 15])
            self.ax_spectrogram.set_title("Spectrogram")
            self.ax_spectrogram.set_xlabel("Frequency [Hz]")
            self.ax_spectrogram.set_ylabel("Time [s]")
            self.canvas.draw_idle()

    def start_plotting(self):
        t = threading.Thread(target=self.plot_spectrum)
        t.daemon = True
        t.start()

    def quit(self):
        self.running = False
        super().quit()


if __name__ == "__main__":
    app = SpectrumAnalyzerGUI()
    app.start_plotting()
    app.mainloop()


