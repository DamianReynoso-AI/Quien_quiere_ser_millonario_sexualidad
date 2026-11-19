"""Genera los efectos de la mesa de sonidos (originales, sintetizados con numpy).

Uso:  python3 sonidos.py   (escribe sonidos/*.wav, mono 24 kHz)
build.py los mete dentro de index.html.
"""
import numpy as np, wave, os

SR = 24000
rng = np.random.default_rng(11)


def T(d): return np.arange(int(d * SR)) / SR


def filt(x, lo=None, hi=None):
    n = len(x); X = np.fft.rfft(x); f = np.fft.rfftfreq(n, 1 / SR); g = np.ones_like(f)
    if hi: g *= 1 / np.sqrt(1 + (f / hi) ** 4)
    if lo: g *= 1 / np.sqrt(1 + (lo / np.maximum(f, 1e-3)) ** 4)
    return np.fft.irfft(X * g, n=n)


def band(x, fc, q=6):
    return filt(x, lo=fc * (1 - 1 / q), hi=fc * (1 + 1 / q))


def reverb(x, secs=1.2, mix=0.25):
    t = T(secs); ir = rng.standard_normal(len(t)) * np.exp(-t * 4)
    ir = filt(ir, lo=200, hi=5000); ir /= np.sqrt((ir ** 2).sum()) * 3
    y = np.convolve(x, ir)[: len(x) + len(t)]
    out = np.zeros(len(y)); out[: len(x)] += x
    return out + y * mix


def saw(f, t):
    ph = 2 * np.pi * np.cumsum(np.broadcast_to(f, t.shape)) / SR
    return sum(np.sin(k * ph) / k for k in range(1, 20)) * 0.6


def norm(x, peak=0.9):
    x = x - np.mean(x)
    return x / (np.max(np.abs(x)) + 1e-9) * peak


def fade(x, a=0.005, r=0.05):
    ai, ri = int(a * SR), int(r * SR); x = x.copy()
    if ai: x[:ai] *= np.linspace(0, 1, ai)
    if ri: x[-ri:] *= np.linspace(1, 0, ri)
    return x


def clap_one():
    t = T(0.08); return band(rng.standard_normal(len(t)), rng.uniform(900, 2200), 2.5) * np.exp(-t * rng.uniform(45, 80))


def aplausos(d=3.6, n=520):
    out = np.zeros(int((d + 0.2) * SR))
    for _ in range(n):
        tt = rng.uniform(0, d) ** 0.9
        c = clap_one(); i = int(tt * SR); out[i:i + len(c)] += c * rng.uniform(.4, 1)
    env = np.minimum(1, T(d + 0.2) / 0.3) * np.exp(-np.maximum(0, T(d + 0.2) - 2.2) * 1.6)
    return reverb(out * env, mix=0.3)


def voces(f0s, d, formantes, glide=None, vib=5.5):
    t = T(d); out = np.zeros(len(t))
    for f0 in f0s:
        g = 1 + (glide(t) if glide else 0)
        f = f0 * g * (1 + 0.012 * np.sin(2 * np.pi * (vib + rng.uniform(-1, 1)) * t + rng.uniform(0, 6)))
        out += saw(f, t) * rng.uniform(.6, 1)
    y = sum(band(out, fc, 5) * a for fc, a in formantes)
    return y


def ovacion():
    a = aplausos(4.0, 700)
    v = voces(rng.uniform(220, 420, 14), 3.2, [(800, 1), (1200, .7), (2600, .3)],
              glide=lambda t: 0.25 * np.sin(np.pi * np.minimum(t / 3.2, 1)))
    v = v * np.minimum(1, T(3.2) / 0.25) * np.exp(-np.maximum(0, T(3.2) - 2.2) * 2)
    out = np.zeros(len(a)); out[: len(v)] += norm(v, .55); out += norm(a, .8)
    # silbido
    t = T(0.9); w = np.sin(2 * np.pi * np.cumsum(1800 + 900 * np.sin(np.pi * t / .9)) / SR) * np.sin(np.pi * t / .9) * .25
    i = int(0.5 * SR); out[i:i + len(w)] += w
    return out


def oooh():
    d = 2.0
    v = voces(rng.uniform(150, 300, 16), d, [(450, 1), (800, .6), (2400, .1)],
              glide=lambda t: 0.12 * np.sin(np.pi * t / d) - 0.1 * (t / d) ** 2)
    return reverb(v * np.sin(np.pi * np.minimum(T(d) / d, 1)) ** 0.7, mix=.35)


def trombon():
    notas = [(311.1, .45), (293.7, .45), (277.2, .45), (261.6, 1.6)]
    out = []
    for k, (f, d) in enumerate(notas):
        t = T(d)
        fm = f * (1 + (0.03 * np.sin(2 * np.pi * 6 * t) * np.minimum(1, t / .3) if k == 3 else 0)) * (1 - (0.03 * t if k == 3 else 0))
        y = saw(fm, t)
        wah = filt(y, hi=600 + 1400 * np.sin(np.pi * min(1, d) / 2))
        env = np.minimum(1, t / .04) * np.minimum(1, (d - t) / .08)
        out.append(wah * env)
    return reverb(np.concatenate(out), mix=.2)


def buzzer():
    t = T(0.9); f = 110
    y = np.sign(np.sin(2 * np.pi * f * t)) * .6 + np.sign(np.sin(2 * np.pi * f * 1.5 * t)) * .4
    y = filt(y, hi=2500) * np.minimum(1, (0.9 - t) / .05)
    return np.tanh(y * 2)


def bocina():
    out = []
    for d in (0.22, 0.12, 0.22, 0.12, 0.9):
        t = T(d); f = 466 * (1 - 0.04 * np.exp(-t * 30))
        y = sum(saw(f * 2 ** (c / 1200), t) for c in (-18, 0, 15)) + saw(f * 1.5, t) * .5
        y = np.tanh(filt(y, lo=200, hi=4500) * 3) * np.minimum(1, t / .01) * np.minimum(1, (d - t) / .03)
        out.append(y); out.append(np.zeros(int(0.03 * SR)))
    return reverb(np.concatenate(out), mix=.15)


def boom():
    t = T(2.4); f = 38 + 70 * np.exp(-t * 9)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.6)
    y += filt(rng.standard_normal(len(t)), hi=900) * np.exp(-t * 25) * .4
    return reverb(np.tanh(y * 2.5), secs=2, mix=.4)


def redoble():
    d = 2.4; out = np.zeros(int((d + 2.6) * SR)); t0 = 0.0; k = 0
    while t0 < d:
        t = T(0.12); h = filt(rng.standard_normal(len(t)), lo=1500, hi=8000) * np.exp(-t * 35) + np.sin(2 * np.pi * 200 * t) * np.exp(-t * 40) * .3
        i = int(t0 * SR); out[i:i + len(h)] += h * (0.2 + 0.8 * (t0 / d) ** 1.5)
        t0 += 0.045; k += 1
    t = T(2.5); cr = filt(rng.standard_normal(len(t)), lo=3500) * np.exp(-t * 1.8) * 1.2
    kk = np.sin(2 * np.pi * np.cumsum(50 + 90 * np.exp(-t * 25)) / SR) * np.exp(-t * 6)
    i = int(d * SR); out[i:i + len(t)] += cr + kk
    return reverb(out, mix=.2)


def grillos():
    d = 3.2; t = T(d); out = np.zeros(len(t))
    for f0, off in ((4500, 0.0), (4800, 0.37)):
        g = np.zeros(len(t))
        for c in np.arange(off, d - .3, 0.9):
            for p in range(4):
                s = c + p * 0.045; i = int(s * SR); n = int(0.03 * SR)
                g[i:i + n] += np.sin(np.pi * np.arange(n) / n)
        out += np.sin(2 * np.pi * f0 * t) * g * (1 + .5 * np.sin(2 * np.pi * 90 * t))
    return reverb(out, secs=1.5, mix=.5)


def badum():
    out = np.zeros(int(2.0 * SR))
    def tom(f, d=.35):
        t = T(d); return np.sin(2 * np.pi * np.cumsum(f * (1 + .6 * np.exp(-t * 30))) / SR) * np.exp(-t * 9) + filt(rng.standard_normal(len(t)), lo=1000, hi=5000) * np.exp(-t * 40) * .3
    for tt, x in ((0, tom(180)), (0.18, tom(120))):
        i = int(tt * SR); out[i:i + len(x)] += x
    t = T(1.5); cy = filt(rng.standard_normal(len(t)), lo=5000) * np.exp(-t * 3) * .9
    cy += np.sin(2 * np.pi * 120 * t) * np.exp(-t * 25) * .5
    i = int(0.42 * SR); out[i:i + len(t)] += cy
    return reverb(out, mix=.15)


def pedo():
    d = 1.15; n = int(d * SR); out = np.zeros(n + SR // 4); t0 = 0.0
    while t0 < d:
        k = t0 / d
        f = 75 + 25 * np.sin(2 * np.pi * 2.3 * t0) + 40 * k ** 3 + rng.uniform(-12, 12)
        t = T(0.05); r = 160 + 140 * k + rng.uniform(-20, 20)
        p_ = np.sin(2 * np.pi * r * t) * np.exp(-t * 90) + np.sin(2 * np.pi * r * 2.7 * t) * np.exp(-t * 160) * .4
        a = np.sin(np.pi * min(1, k * 1.15)) ** .4 * rng.uniform(.6, 1)
        i = int(t0 * SR); out[i:i + len(p_)] += p_ * a
        t0 += 1 / f
    nz = filt(rng.standard_normal(len(out)), lo=150, hi=900) * .08
    y = np.tanh(filt(out + nz * np.abs(out), hi=1100) * 3)
    return reverb(y, secs=.4, mix=.08)


def payaso():
    out = []
    for f0, d in ((520, .22), (440, .32)):
        t = T(d); f = f0 * (1 + .25 * np.exp(-t * 25)) * (1 - .06 * t / d)
        y = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) + .5 * saw(f * 2.01, t)
        y = band(y, 1400, 1.6) + band(y, 2800, 2) * .5
        y = np.tanh(y * 4) * np.minimum(1, t / .01) * np.minimum(1, (d - t) / .03)
        out += [y, np.zeros(int(.08 * SR))]
    return np.concatenate(out)


def silbato():
    d = 1.1; t = T(d)
    f = 1900 * (300 / 1900) ** ((t / d) ** 1.3) * (1 + .015 * np.sin(2 * np.pi * 7 * t))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) + filt(rng.standard_normal(len(t)), lo=1000, hi=4000) * .05
    y *= np.minimum(1, t / .03) * np.minimum(1, (d - t) / .05)
    t2 = T(.35); thud = np.sin(2 * np.pi * np.cumsum(90 + 60 * np.exp(-t2 * 20)) / SR) * np.exp(-t2 * 12)
    return np.concatenate([y, np.zeros(int(.05 * SR)), thud * 1.2])


def bonk():
    t = T(.5)
    y = (np.sin(2 * np.pi * np.cumsum(330 * (1 + .5 * np.exp(-t * 60))) / SR) * np.exp(-t * 14)
         + np.sin(2 * np.pi * 870 * t) * np.exp(-t * 30) * .5
         + filt(rng.standard_normal(len(t)), lo=800, hi=4000) * np.exp(-t * 120) * .6)
    return reverb(np.tanh(y * 1.5), secs=.6, mix=.15)


def abucheo():
    d = 2.8
    v = voces(rng.uniform(95, 190, 18), d, [(320, 1), (700, .5), (2300, .05)],
              glide=lambda t: -0.12 * (t / d))
    env = np.minimum(1, T(d) / .25) * np.exp(-np.maximum(0, T(d) - 2.0) * 2.5)
    return reverb(v * env, mix=.35)


def risa():
    sil = [(.5, 1.0, 600)] + [(.17, .82 - i * .06, 800) for i in range(6)] + [(.6, .5, 750)]
    out = []
    for d, rel, f1 in sil:
        t = T(d); f0 = 125 * rel * (1 + .03 * np.sin(2 * np.pi * 6 * t)) * (1 - .1 * t / d)
        src = saw(f0, t) + filt(rng.standard_normal(len(t)), lo=500, hi=3000) * .25 * np.exp(-t * 25)
        y = band(src, f1, 4) + band(src, 1200, 5) * .7 + band(src, 2600, 6) * .2
        env = np.minimum(1, t / .015) * np.exp(-t * (2 if d > .3 else 9))
        out += [y * env, np.zeros(int(.04 * SR))]
    return reverb(np.tanh(np.concatenate(out) * 2), secs=2.4, mix=.45)


def boing():
    d = 1.0; t = T(d)
    f = 180 * (1 + .9 * t / d) * (1 + .35 * np.sin(2 * np.pi * 22 * t) * np.exp(-t * 3))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) + .3 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    return y * np.minimum(1, t / .005) * np.exp(-t * 3.2)


SONIDOS = {
    "pedo": pedo, "payaso": payaso, "silbato": silbato, "trombon": trombon, "bonk": bonk, "abucheo": abucheo,
    "risa": risa, "boing": boing, "boom": boom, "grillos": grillos, "badum": badum, "aplausos": aplausos,
}


def write_wav(path, x):
    y = (np.clip(fade(norm(x)), -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(y.tobytes())


if __name__ == "__main__":
    os.makedirs("sonidos", exist_ok=True)
    for k, fn in SONIDOS.items():
        x = fn(); write_wav(f"sonidos/{k}.wav", x); print(k, f"{len(x)/SR:.1f}s")
