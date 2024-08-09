# %%
# This script grabs data and plots a power spectrum
import pyrpl
import matplotlib.pyplot as plt
from scipy import signal
import numpy as np
import gpstime

HOSTNAME = None  # fill in as required
p = pyrpl.Pyrpl(HOSTNAME, gui=False)
r = p.rp

asg = r.asg1
s = r.scope

# %%
acquire_length = 100
t0 = int(gpstime.gpsnow())
w1 = 0
n = 0
stream1 = np.zeros([0], dtype=np.int16)
stream2 = np.zeros([0], dtype=np.int16)

# faster durations capture data quicker. continuous needs to be above 0.1Hz to
# work and gives the fastest stream of ~120kHz sample rate. 8s is the longest
# with 2kHz sample rate

# s.duration = 0.1  # 60kHz Nyquist
s.duration = 8.6  # 1kHz Nyquist

fs = 1 / s.sampling_time
print(f"Sampling at {fs:.1f}Hz")

s._start_acquisition_rolling_mode()

while int(gpstime.gpsnow()) - t0 < acquire_length:
    if n % 10 == 0:
        print(f"Time = {len(stream1) * s.sampling_time:.4f}", end="\r")
    w0 = w1
    w1 = s._write_pointer_current
    stream1 = np.concatenate((stream1, s._rawdata_ch1[w0:w1]))
    stream2 = np.concatenate((stream2, s._rawdata_ch2[w0:w1]))
    n += 1

print(f"Finished = {len(stream1) * s.sampling_time:.4f}", end="\r")

t = np.arange(len(stream1)) * s.sampling_time

np.savez_compressed(f"data_{t0}.npz", t=t, stream1=stream1, stream2=stream2)
# %%
plt.plot(t, stream1)
plt.plot(t, stream2)
plt.show()

# %%
averages = 10
overlap = 0.0

f, Pxx_ch1 = signal.welch(
    stream1 - stream1.mean(),
    fs,
    "blackman",
    nperseg=len(stream1) // averages,
    noverlap=overlap,
)
f, Pxx_ch2 = signal.welch(
    stream2 - stream2.mean(),
    fs,
    "blackman",
    nperseg=len(stream2) // averages,
    noverlap=overlap,
)
# %%
# 1V single sides is 13 bits, ±1V digitised over 14 bits
V_per_cts = 1 / 2**13

plt.loglog(f, np.sqrt(Pxx_ch1) * V_per_cts, label="CH1 (open)")
plt.loglog(f, np.sqrt(Pxx_ch2) * V_per_cts, label="CH2 (50ohm)")
plt.legend()
plt.xlabel("Frequency [Hz]")
plt.ylabel("ASD [V/rtHz]")
plt.grid(which="both", alpha=0.4)
plt.title("Redpitaya ADC noise")
plt.show()
