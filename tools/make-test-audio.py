#!/usr/bin/env python3
"""Stereo test files for CMF-true-stereo (attached to every release).

  LEFT_ONLY_3min.wav    3 minutes of noise in the LEFT channel only, the right
                        channel digital silence. In Stereo only the left side
                        plays: the earpiece, or the speaker when the phone is
                        turned with the earpiece on your right.
  LEFT10s_RIGHT10s.wav  "left", then 10 s of noise in the left channel only;
                        "right", then the same noise in the right channel only.
                        Six rounds. The labels are spoken in both channels.

Noise: pink-ish, 200 Hz - 6 kHz (what both drivers can play), fixed seeds, so
every build of these files is identical. Needs numpy and espeak-ng.
Usage: make-test-audio.py <output dir>
"""
import os, subprocess, sys, tempfile, wave
import numpy as np

SR = 48000


def noise(n, seed):
    rng = np.random.default_rng(seed)
    X = np.fft.rfft(rng.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    X[1:] /= np.sqrt(f[1:])
    X[(f < 200) | (f > 6000)] = 0
    x = np.fft.irfft(X, n)
    return x / np.sqrt(np.mean(x ** 2)) * 0.15


def write(path, left, right):
    st = np.clip(np.stack([left, right], 1) * 32767, -32768, 32767).astype('<i2')
    w = wave.open(path, 'wb')
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(st.tobytes()); w.close()


def speech(word, tmp):
    p = os.path.join(tmp, word + '.wav')
    subprocess.run(['espeak-ng', '-s', '140', '-w', p, word], check=True)
    w = wave.open(p); r = w.getframerate()
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float)
    t = np.arange(int(len(x) * SR / r)) * r / SR
    x = np.interp(t, np.arange(len(x)), x) / 32768
    return x / np.max(np.abs(x)) * 0.5


def left_only(out):
    n = SR * 180
    x = noise(n, 2)
    fd = SR // 10
    x[:fd] *= np.linspace(0, 1, fd); x[-fd:] *= np.linspace(1, 0, fd)
    write(os.path.join(out, 'LEFT_ONLY_3min.wav'), x, np.zeros(n))


def left_right(out, tmp):
    vl, vr = speech('left', tmp), speech('right', tmp)
    n = SR * 10
    nz = noise(n, 1)
    fade = int(SR * 0.05)
    env = np.ones(n); env[:fade] = np.linspace(0, 1, fade); env[-fade:] = np.linspace(1, 0, fade)
    nz *= env
    sil = lambda d: np.zeros(int(SR * d))
    L, R = [], []
    for _ in range(6):
        for a, b in ((vl, vl), (sil(0.7), sil(0.7)), (nz, np.zeros(n)), (sil(2), sil(2)),
                     (vr, vr), (sil(0.7), sil(0.7)), (np.zeros(n), nz), (sil(2), sil(2))):
            L.append(a); R.append(b)
    write(os.path.join(out, 'LEFT10s_RIGHT10s.wav'), np.concatenate(L), np.concatenate(R))


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    os.makedirs(out, exist_ok=True)
    left_only(out)
    with tempfile.TemporaryDirectory() as tmp:
        left_right(out, tmp)
