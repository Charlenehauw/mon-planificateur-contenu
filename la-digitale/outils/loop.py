import numpy as np, wave, sys
src, out, dur = sys.argv[1], sys.argv[2], float(sys.argv[3])
w = wave.open(src); sr = w.getframerate(); ch = w.getnchannels()
a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).reshape(-1, ch).astype(np.float64)
d = int(4*sr); T = len(a)
L = a[:T-d].copy()
t = np.linspace(0, np.pi/2, d)[:, None]
L[:d] = a[T-d:]*np.cos(t) + a[:d]*np.sin(t)   # equal-power crossfade
n = int(dur*sr); reps = n//len(L) + 1
y = np.tile(L, (reps, 1))[:n]
f = int(3*sr); y[:f] *= np.linspace(0,1,f)[:,None]; y[-f:] *= np.linspace(1,0,f)[:,None]
o = wave.open(out, 'wb'); o.setnchannels(ch); o.setsampwidth(2); o.setframerate(sr)
o.writeframes(np.clip(y, -32768, 32767).astype(np.int16).tobytes()); o.close()
