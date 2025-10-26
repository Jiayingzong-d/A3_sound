# mic_input.py


import sounddevice as sd
import numpy as np
import threading

class MicInput:
    def __init__(self, device_index=2, sensitivity=0.03, smooth=0.8):
        """
        device_index: Microphone number
        sensitivity: Trigger sensitivity
        smooth: Smoothing factor (higher means more stable)
        """
        self.device_index = device_index
        self.sensitivity = sensitivity
        self.smooth = smooth
        self.volume = 0.0
        self.running = False
        self.thread = None

    def _callback(self, indata, frames, time, status):
        # Calculate volume (RMS root mean square)
        vol = float(np.sqrt(np.mean(indata**2)))
        # Smoothing: reduce spikes
        self.volume = self.smooth * self.volume + (1 - self.smooth) * vol

    def start(self):
        """Start microphone listening thread"""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._listen, daemon=True)
        self.thread.start()
        print("MicInput started on device", self.device_index)

    def _listen(self):
        """Background listening loop"""
        with sd.InputStream(device=self.device_index, channels=1, callback=self._callback, samplerate=44100):
            while self.running:
                sd.sleep(100)

    def stop(self):
        """Stop listening"""
        self.running = False
        print(" MicInput stopped")

    def get_volume(self):
        """Get real-time volume (0~1)"""
        return min(1.0, max(0.0, self.volume))

    def is_speaking(self):
        """Check if speaking"""
        return self.get_volume() > self.sensitivity


# Independent run test (optional)
if __name__ == "__main__":
    mic = MicInput(device_index=2)
    mic.start()
    try:
        while True:
            vol = mic.get_volume()
            if mic.is_speaking():
                print(f" You are speaking! Volume: {vol:.3f}")
            else:
                print(f"💤 Muted... Volume: {vol:.3f}")
            sd.sleep(300)
    except KeyboardInterrupt:
        mic.stop()
