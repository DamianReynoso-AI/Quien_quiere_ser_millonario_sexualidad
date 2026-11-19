"""Genera las 3 pistas de música del juego (originales, sintetizadas con numpy).

Estilo EDM / hype de cuenta regresiva en La menor (Am–F–C–G), 8 compases por pista,
pensadas para repetirse sin cortes:
  nivel1.wav  120 BPM  intro: pad, arpegio, bombo a medio tiempo
  nivel2.wav  128 BPM  build: bombo 4x4, palmas, acordes con sidechain, riser
  nivel3.wav  138 BPM  drop: todo + melodía principal, hats en semicorcheas, redoble y platillo

Uso:  python3 musica.py   (escribe musica/nivel1.wav, nivel2.wav, nivel3.wav)
"""
import numpy as np, wave, os

SR = 32000
rng = np.random.default_rng(7)

def hz(m): return 440.0 * 2 ** ((m - 69) / 12)

def fft_filter(x, lo=None, hi=None):
    """Filtro pasa-bandas suave en el dominio de la frecuencia (x: mono o (n,2))."""
    n = x.shape[0]
    X = np.fft.rfft(x, axis=0)
    f = np.fft.rfftfreq(n, 1 / SR)
    g = np.ones_like(f)
    if hi: g *= 1 / np.sqrt(1 + (f / hi) ** 4)
    if lo: g *= 1 / np.sqrt(1 + (lo / np.maximum(f, 1e-3)) ** 4)
    if x.ndim == 2: g = g[:, None]
    return np.fft.irfft(X * g, n=n, axis=0)

def env_adsr(n, a, d, s, r):
    t = np.arange(n) / SR
    e = np.ones(n) * s
    ai = int(a * SR); di = int(d * SR); ri = int(r * SR)
    if ai: e[:ai] = np.linspace(0, 1, ai)
    if di: e[ai:ai + di] = np.linspace(1, s, len(e[ai:ai + di]))
    if ri: e[-ri:] *= np.linspace(1, 0, ri)
    return e

def saw(freq, n, phase=0.0):
    t = np.arange(n) / SR
    return 2 * ((freq * t + phase) % 1.0) - 1

def supersaw(midis, dur, detune=(-22, -12, -5, 0, 5, 12, 22), cut=4000):
    n = int(dur * SR); out = np.zeros((n, 2))
    for m in midis:
        for k, c in enumerate(detune):
            v = saw(hz(m) * 2 ** (c / 1200), n, rng.random())
            pan = 0.5 + (k - 3) / 7
            out[:, 0] += v * (1 - pan); out[:, 1] += v * pan
    out /= (len(midis) * len(detune)) ** 0.5 * 2.2
    return fft_filter(out, lo=80, hi=cut)

def pluck(m, dur):
    n = int(dur * SR); t = np.arange(n) / SR; f = hz(m); y = np.zeros(n)
    for k in range(1, 24):
        if f * k > SR / 2.2: break
        y += np.sin(2 * np.pi * f * k * t) / k * np.exp(-t * (6 + 2.2 * k))
    return y * 0.5

def kick(dur=0.45):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) * np.exp(-t * 7.5)
    y[:120] += rng.standard_normal(120) * 0.35 * np.linspace(1, 0, 120)
    return np.tanh(y * 1.8) * 0.9

def clap(dur=0.35):
    n = int(dur * SR); t = np.arange(n) / SR
    nz = fft_filter(rng.standard_normal(n), lo=900, hi=4500)
    e = np.zeros(n)
    for d in (0, 0.011, 0.022):
        i = int(d * SR); e[i:] += np.exp(-(t[: n - i]) * 70)
    e += np.exp(-t * 14) * 0.5
    return nz * e * 0.45

def hat(dur=0.05, open_=False):
    n = int(dur * SR); t = np.arange(n) / SR
    nz = fft_filter(rng.standard_normal(n), lo=7000)
    return nz * np.exp(-t * (18 if open_ else 90)) * 0.25

def snare(dur=0.2):
    n = int(dur * SR); t = np.arange(n) / SR
    nz = fft_filter(rng.standard_normal(n), lo=1200, hi=8000)
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30)
    return (nz * np.exp(-t * 22) * 0.4 + body * 0.3)

def crash(dur=2.5):
    n = int(dur * SR); t = np.arange(n) / SR
    nz = fft_filter(rng.standard_normal((n, 2)), lo=4000)
    return nz * np.exp(-t * 1.6)[:, None] * 0.22

def riser(dur):
    n = int(dur * SR); out = np.zeros(n); blk = int(0.05 * SR)
    nz = rng.standard_normal(n + blk)
    for i in range(0, n, blk):
        k = i / n; c = 400 * (16 ** k)
        seg = fft_filter(nz[i:i + blk * 2], lo=c * 0.6, hi=c * 1.6)[:blk]
        out[i:i + blk] = seg[: len(out[i:i + blk])] * (k ** 2)
    return out * 0.5

def reverb(x, secs=2.2, mix=0.25):
    n = int(secs * SR); t = np.arange(n) / SR
    ir = rng.standard_normal((n, 2)) * np.exp(-t * 3.2)[:, None]
    ir = fft_filter(ir, lo=200, hi=6000); ir /= np.abs(ir).sum(axis=0) ** 0.5 * 8
    L = x.shape[0] + n
    N = 1 << (L - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, N, axis=0) * np.fft.rfft(ir, N, axis=0), N, axis=0)[:x.shape[0]]
    return x + y * mix

CH = [[57, 60, 64, 69], [53, 57, 60, 65], [55, 60, 64, 67], [55, 59, 62, 67]]
ROOT = [33, 29, 36, 31]
HOOK = [  # (midi o None) en corcheas, 8 por compás
    [76, None, 76, 74, 72, None, 71, 72],
    [69, None, None, 72, None, 69, 72, 74],
    [76, None, None, 79, None, 76, 74, 72],
    [74, None, 71, None, 67, None, 71, 74],
    [76, None, 76, 74, 72, None, 71, 72],
    [69, None, None, 72, None, 69, 72, 74],
    [76, None, None, 79, None, 81, 79, 76],
    [74, None, 76, None, 79, None, 81, None],
]

def render(level):
    bpm = {1: 120, 2: 128, 3: 138}[level]
    beat = 60 / bpm; s16 = beat / 4; bars = 8; bar = beat * 4
    L = int(bars * bar * SR); tail = int(3 * SR)
    mix = np.zeros((L + tail, 2)); side = np.zeros((L + tail, 2)); drums = np.zeros((L + tail, 2))

    def put(buf, x, t, gain=1.0, pan=0.5):
        i = int(round(t * SR))
        if x.ndim == 1: x = np.stack([x * (1 - pan) * 2 ** .5, x * pan * 2 ** .5], 1) * 0.7
        j = min(len(buf), i + len(x)); buf[i:j] += x[: j - i] * gain

    K = kick(); C = clap(); Hc = hat(); Ho = hat(0.18, True); Sn = snare()
    for b in range(bars):
        t0 = b * bar; ci = b % 4; ch = CH[ci]; root = ROOT[ci]
        # pad / acordes
        if level == 1:
            p = supersaw(ch, bar * 1.02, cut=1400) * env_adsr(int(bar * 1.02 * SR), 0.4, 0.2, 0.8, 0.3)[:, None]
            put(side, p, t0, 0.55)
        else:
            p = supersaw(ch, bar * 1.0, cut=3200 if level == 2 else 5500) * env_adsr(int(bar * SR), 0.01, 0.1, 0.9, 0.08)[:, None]
            put(side, p, t0, 0.6 if level == 2 else 0.55)
        # bajo
        if level == 1:
            n = int(bar * SR); tt = np.arange(n) / SR
            put(side, np.sin(2 * np.pi * hz(root + 12) * tt) * env_adsr(n, 0.05, 0.1, 0.9, 0.2) * 0.5, t0, 1.0)
        else:
            for e in range(8):
                if e % 2 == 1 or level == 3:
                    n = int(beat / 2 * SR * 0.9); tt = np.arange(n) / SR
                    m = root + 12 + (12 if (level == 3 and e % 4 == 3) else 0)
                    y = np.sin(2 * np.pi * hz(m) * tt) * 0.55 + fft_filter(saw(hz(m), n), hi=500) * 0.25
                    put(side, y * env_adsr(n, 0.005, 0.05, 0.85, 0.03), t0 + e * beat / 2, 1.0)
        # arpegio pluck
        step = s16 if level >= 2 else s16 * 2
        pat = [0, 2, 1, 3, 2, 0, 3, 1]
        for k in range(int(bar / step)):
            m = ch[pat[k % 8]] + 12
            put(mix, pluck(m, 0.35), t0 + k * step, 0.22 if level == 1 else 0.17, pan=0.3 if k % 2 else 0.7)
        # melodía (drop)
        if level == 3:
            for e, m in enumerate(HOOK[b]):
                if m is None: continue
                d = beat / 2
                if e + 1 < 8 and HOOK[b][e + 1] is None: d = beat
                ld = supersaw([m], d * 0.95, detune=(-14, -6, 0, 6, 14), cut=7000) * env_adsr(int(d * 0.95 * SR), 0.005, 0.08, 0.8, 0.05)[:, None]
                put(mix, ld, t0 + e * beat / 2, 0.75)
        # batería
        for q in range(4):
            tb = t0 + q * beat
            if level == 1:
                if q in (0, 2): put(drums, K, tb, 0.8)
                if b >= 4: put(drums, Hc, tb + beat / 2, 0.6, 0.6)
            else:
                put(drums, K, tb, 1.0)
                if q in (1, 3): put(drums, C, tb, 0.9)
                put(drums, Ho, tb + beat / 2, 0.55, 0.62)
                if level == 3:
                    for s in (1, 3): put(drums, Hc, tb + s * s16, 0.45, 0.4)
        # redoble y riser en el último compás
        if b == bars - 1 and level >= 2:
            put(mix, riser(bar), t0, 0.9 if level == 3 else 0.7)
            hits = [t0 + bar / 2 + i * s16 for i in range(8)] if level == 2 else \
                   [t0 + i * s16 for i in range(8)] + [t0 + bar / 2 + i * s16 / 2 for i in range(16)]
            for i, th in enumerate(hits): put(drums, Sn, th, 0.25 + 0.6 * i / len(hits))
    if level == 3: put(drums, crash(), 0, 1.0)

    # sidechain (bombeo con el bombo)
    t = np.arange(L + tail) / SR
    ph = (t % beat) / beat
    if level == 1:
        sc = 1 - 0.25 * np.exp(-((t % (beat * 2)) / (beat * 2)) * 12)
    else:
        sc = 1 - 0.65 * np.exp(-ph * 9)
    mix += side * sc[:, None]
    mix = reverb(mix, mix=0.3 if level == 1 else 0.22)
    mix += drums * 0.9
    # loop circular: lo que sobra al final se suma al inicio
    out = mix[:L].copy(); out[:tail] += mix[L:L + tail]
    out = np.tanh(out * 1.4) / np.tanh(1.4)
    out /= np.max(np.abs(out)) / 0.89
    return out

def write_wav(path, x):
    y = (np.clip(x, -1, 1) * 32767).astype('<i2')
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(y.tobytes())

if __name__ == "__main__":
    os.makedirs("musica", exist_ok=True)
    for lv in (1, 2, 3):
        x = render(lv); write_wav(f"musica/nivel{lv}.wav", x)
        print(f"nivel{lv}: {len(x)/SR:.1f}s")
