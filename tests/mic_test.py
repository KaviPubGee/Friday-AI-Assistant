import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np

SAMPLE_RATE = 48000
RECORD_SECONDS = 5
MIC_DEVICE_INDEX = 20
CHANNELS = 1

print(sd.query_devices())

print("Recording...")
recording = sd.rec(
    int(RECORD_SECONDS * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=CHANNELS,
    dtype="int16",
    device=MIC_DEVICE_INDEX
)

sd.wait()

if len(recording.shape) > 1:
    recording = recording.mean(axis=1)

max_volume = np.max(np.abs(recording))
print("Max volume before normalization:", max_volume)

if max_volume > 0:
    recording = recording / max_volume * 30000

recording = recording.astype(np.int16)

max_volume_after = np.max(np.abs(recording))
print("Max volume after normalization:", max_volume_after)

file_name = f"mic_test_device_{MIC_DEVICE_INDEX}.wav"
write(file_name, SAMPLE_RATE, recording)

print(f"Saved {file_name}")