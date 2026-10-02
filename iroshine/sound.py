"""
iroshine.sound — a tiny numpy synth that writes cached WAV notes for Manim.

Values are ranked and mapped onto a musical scale, so a list of any numbers
turns into a melody that stays in key.
"""

import hashlib
import wave
from pathlib import Path

import numpy as np

SR = 44100

SCALES = {
    "pentatonic": [0, 2, 4, 7, 9],
    "major":      [0, 2, 4, 5, 7, 9, 11],
    "minor":      [0, 2, 3, 5, 7, 8, 10],
    "dorian":     [0, 2, 3, 5, 7, 9, 10],
    "lydian":     [0, 2, 4, 6, 7, 9, 11],
    "hirajoshi":  [0, 2, 3, 7, 8],
    "blues":      [0, 3, 5, 6, 7, 10],
}
KEYS = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6,
        "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}

#                 partials (freq multiple, amplitude)            decay  attack
INSTRUMENTS = {
    "harp":      ([(1, 1), (2, .18), (3, .07), (4, .03)],        1.5,   .004),
    "bell":      ([(1, 1), (2.76, .25), (5.4, .09), (8.9, .03)],  2.6,   .003),
    "marimba":   ([(1, 1), (4, .22), (10, .05)],                 .55,   .002),
    "music_box": ([(1, 1), (3, .12), (6.1, .05)],                1.1,   .002),
    "soft_sine": ([(1, 1)],                                     1.2,   .02),
    "tick":      ([(1, 1), (3, .2)],                             .10,   .002),
    # wooden knocks: inharmonic partials of a struck wooden bar, a short noisy click on the attack,
    # a tiny pitch drop, and a gentle low-pass so they sound dull and warm rather than bright
    "wood":      ([(1, 1), (2.57, .28), (4.3, .08)],             .22,   .001, {"click": .35, "drop": .05, "dark": .55}),
    "wood_soft": ([(1, 1), (2.57, .16)],                         .28,   .002, {"click": .15, "drop": .03, "dark": .7}),
    "log_drum":  ([(1, 1), (1.5, .3), (2.9, .1)],                .65,   .002, {"click": .2, "drop": .08, "dark": .6}),
    # water: air bubbles ringing in water (van den Doel's liquid-sound model): each bubble is a sine
    # that decays fast and rises slightly in pitch as it rings. Tuned to the scale, so they stay in key.
    #   bubbles: (start s, pitch ratio, loudness)   damp: <1 rings longer than a real bubble
    "drip":      ([], .45, .001, {"bubbles": [(0, 1.0, 1.0)], "damp": .30, "splash": .10}),
    "plop":      ([], .45, .001, {"bubbles": [(0, .75, 1.0)], "damp": .45, "splash": .06}),
    "pour":      ([], .95, .001, {"bubbles": [(0.00, .80, .55), (0.05, .86, .75), (0.11, .90, .9), (0.16, .95, 1.0),
                                              (0.22, 1.00, .9), (0.27, 1.06, .8), (0.33, 1.12, .7), (0.39, 1.19, .6)],
                                  "damp": .38, "splash": .05, "stream": .035, "jitter": .025}),
    "drop_bell": ([], 1.4, .001, {"bubbles": [(0, 1.0, 1.0)], "damp": .09, "splash": .05}),
    # a splash, in three layers (impact, body, droplets): see Sound._splash
    "splash":    ([], .9, .001, {"splash_fx": True}),            # (v1: dark and roomy; kept for reference)
    # v2 splashes: bright and dry. What makes water sound like water is a cloud of many tiny bubbles
    # popping (1.5–5 kHz fizz) plus a few larger tuned bubbles; low rumble + long reverb = explosion.
    "plish":     ([], .5, .001, {"splash2": {"slap": .8, "fizz": 26, "fizz_len": .20, "bloops": 2, "size": 1.0},
                                 "reverb": .06}),
    "sploosh":   ([], .7, .001, {"splash2": {"slap": 1.0, "fizz": 40, "fizz_len": .32, "bloops": 3, "size": .75},
                                 "reverb": .08}),
    "trickle":   ([], .7, .001, {"splash2": {"slap": .25, "fizz": 18, "fizz_len": .40, "bloops": 5, "size": 1.2},
                                 "reverb": .06}),
    # the sploosh, warmer: the same layers pulled down into the middle of the spectrum (the fizz and
    # spray sit at 0.8–2.8 kHz instead of up to 6 kHz) and rolled off above ~4 kHz, so it stays wet
    # without the rough, hissy top
    "sploosh_mid": ([], .7, .001, {"splash2": {"slap": .9, "fizz": 30, "fizz_len": .30, "bloops": 3, "size": .75,
                                               "slap_band": (600, 2800), "fizz_band": (800, 2600),
                                               "wash_band": (500, 2200), "bloop_mul": 3, "top": 4200},
                                   "reverb": .08}),
    # a soft, wet collapse, for things that squash, spoil or deflate. Designed for phone speakers:
    #   body   a pitched tone that starts a little sharp and sags (a falling pitch reads as "deflating"),
    #          with strong 2nd–4th harmonics so its pitch is heard even where a phone can't play the
    #          fundamental (the missing-fundamental effect)
    #   juice  a 30 ms burst of band-limited noise (0.7–2.2 kHz) and a few tiny crackles
    #   nothing above ~3 kHz (the 2.5–5.5 kHz band is the one heard as harsh) and no reverb (dry = close)
    "squish":     ([], .30, .002, {"squish": {"sag": .10, "juice": .9, "crackles": 4}}),
    "squish_big": ([], .55, .002, {"squish": {"sag": .16, "juice": 1.1, "crackles": 7, "tail": 1.8}}),
}


class Synth:
    def __init__(self, cfg, all_values, cache_dir):
        self.cfg = cfg
        self.values = sorted(set(v for v in all_values if isinstance(v, (int, float))))
        self.dir = Path(cache_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.steps = SCALES[cfg.scale]

    # value → scale degree → midi → Hz -----------------------------------
    def degree(self, value):
        r = self.values.index(value) if value in self.values else 0
        n, span = len(self.values), 2 * len(self.steps) + 2    # ~2.5 octaves
        return r if n <= span else round(r * (span - 1) / max(1, n - 1))

    def midi(self, deg):
        s = self.steps
        root = 12 * (self.cfg.octave + 1) + KEYS[self.cfg.key]
        return root + 12 * (deg // len(s)) + s[deg % len(s)]

    # rendering ------------------------------------------------------------
    def note(self, instrument, deg, cents=0, variant=0):
        """Path to a WAV for this instrument at this scale degree (rendered once).
        cents / variant: a slightly detuned, differently-seeded copy (so repeats aren't identical)."""
        m = self.midi(max(0, deg))
        key = f"{instrument}-{m}-{self.cfg.reverb:.2f}" + (f"-{cents}-{variant}" if cents or variant else "")
        path = self.dir / (hashlib.md5(key.encode()).hexdigest()[:12] + ".wav")
        if not path.exists():
            self._seed = variant
            self._write(path, instrument, 440.0 * 2 ** ((m - 69 + cents / 100) / 12))
        return str(path)

    def _write(self, path, instrument, f):
        spec = INSTRUMENTS[instrument]
        partials, decay, attack = spec[:3]
        extra = spec[3] if len(spec) > 3 else {}
        t = np.arange(int(SR * (decay + 0.05))) / SR
        if "squish" in extra:
            x = self._squish(f, t, extra["squish"], getattr(self, "_seed", 0))
            x = self._reverb(x, extra.get("reverb", 0.0))
            x = x / (np.max(np.abs(x)) or 1) * 0.3
            with wave.open(str(path), "wb") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
                w.writeframes((x * 32767).astype(np.int16).tobytes())
            return
        if "bubbles" in extra or "splash_fx" in extra or "splash2" in extra:
            if "splash2" in extra:
                x = self._splash2(f, t, extra["splash2"])
            else:
                x = self._splash(f, t) if "splash_fx" in extra else self._bubbles(f, t, extra)
            x = self._reverb(x, extra.get("reverb", self.cfg.reverb))
            x = x / (np.max(np.abs(x)) or 1) * 0.3
            with wave.open(str(path), "wb") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
                w.writeframes((x * 32767).astype(np.int16).tobytes())
            return
        env = np.minimum(1, t / attack) * np.exp(-t * 6.9 / decay)
        # a struck object starts slightly sharp and settles (0 for the tuned instruments)
        bend = 1 + extra.get("drop", 0) * np.exp(-t / 0.012)
        phase = 2 * np.pi * f * np.cumsum(bend) / SR
        x = sum(a * np.sin(m * phase) * np.exp(-t * (m - 1) * 3.0 * bool(extra)) for m, a in partials) * env
        if extra.get("click"):                               # the knock: a few ms of darkened noise
            n = np.random.default_rng(int(f)).standard_normal(len(t))
            n = np.convolve(n, np.ones(6) / 6, mode="same")
            x = x + extra["click"] * n * np.exp(-t / 0.004)
        if extra.get("dark"):                                # one-pole low-pass: warmer, less bright
            a = extra["dark"]
            y = np.empty_like(x); acc = 0.0
            for i, v in enumerate(x):
                acc = a * acc + (1 - a) * v; y[i] = acc
            x = y
        x = self._reverb(x, self.cfg.reverb)
        x = x / (np.max(np.abs(x)) or 1) * 0.3
        with wave.open(str(path), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes((x * 32767).astype(np.int16).tobytes())

    @classmethod
    def _squish(cls, f, t, p, seed=0):
        rng = np.random.default_rng(1000 + seed)
        tail = p.get("tail", 1.0)
        # body: starts ~6% sharp, sags by `sag` over ~80 ms
        bend = (1 + 0.06 * np.exp(-t / 0.012)) * (1 - p["sag"] * (1 - np.exp(-t / 0.08)))
        ph = 2 * np.pi * f * np.cumsum(bend) / SR
        env = np.minimum(1, t / 0.002) * np.exp(-t / (0.07 * tail))
        body = sum(a * np.sin(k * ph) * np.exp(-t * (k - 1) * 3) for k, a in
                   ((1, .45), (2, 1.0), (3, .75), (4, .5), (5, .3), (6, .15)))
        x = body * env
        # juice: a short band of wet noise, 0.7–2.2 kHz
        n = cls._band(rng.standard_normal(len(t)), 700, 2200)
        n /= (np.max(np.abs(n)) or 1)
        x = x + p["juice"] * n * np.exp(-t / 0.03) * np.minimum(1, t / 0.003)
        # crackles: a few tiny pops scattered over the first 60 ms
        for _ in range(p.get("crackles", 0)):
            t0 = rng.uniform(0.004, 0.06 * tail)
            c = cls._band(rng.standard_normal(len(t)), 900, 2600)
            c /= (np.max(np.abs(c)) or 1)
            x = x + rng.uniform(.08, .2) * c * np.exp(-np.maximum(0, t - t0) / 0.0015) * (t >= t0)
        return cls._band(x, 110, 3000, soft=0.25)

    @staticmethod
    def _band(noise, lo, hi, soft=0.35):
        """Band-limit noise in the frequency domain (smooth edges, no ringing)."""
        X = np.fft.rfft(noise)
        fr = np.fft.rfftfreq(len(noise), 1 / SR)
        mask = np.exp(-0.5 * (np.maximum(0, np.log(lo) - np.log(np.maximum(fr, 1))) / soft) ** 2) * \
            np.exp(-0.5 * (np.maximum(0, np.log(np.maximum(fr, 1)) - np.log(hi)) / soft) ** 2)
        return np.fft.irfft(X * mask, len(noise))

    @classmethod
    def _splash(cls, f, t):
        """Water hitting water. Three layers, the way splash effects are built:
          1. impact   a short, dark burst of noise (the slap)
          2. body     a softer wash of noise that swells and fades (the water settling)
          3. droplets a few small bubbles falling back in, scattered over the tail
        f (the note) sets the body's colour and the droplets' pitches, so bigger pools sound deeper."""
        rng = np.random.default_rng(int(f * 7))
        n = len(t)
        x = np.zeros(n)
        k = f / 260.0                                          # 1 at middle C
        imp = cls._band(rng.standard_normal(n), 180 * k, 1600 * k)
        body = cls._band(rng.standard_normal(n), 250 * k, 1100 * k, soft=0.5)
        swell = np.minimum(1, t / 0.03) * np.exp(-np.maximum(0, t - 0.03) / 0.16)
        g = cls._band(rng.standard_normal(n), 8, 40, soft=0.6)
        grain = 0.65 + 0.35 * g / (np.std(g) or 1)                  # a lumpy, uneven wash
        imp /= (np.max(np.abs(imp)) or 1); body /= (np.max(np.abs(body)) or 1)
        x = 1.0 * imp * np.minimum(1, t / 0.002) * np.exp(-t / 0.035)
        x += 0.42 * body * swell * np.clip(grain, 0, 2)
        x /= (np.max(np.abs(x)) or 1)
        drops = Synth._bubbles(f, t, {"bubbles": [(0.07 + 0.35 * rng.random(), r, 0.35 + 0.25 * rng.random())
                                                  for r in (1.0, 1.25, 1.5, 0.84)],
                                      "damp": 0.5, "jitter": 0.04})
        x += 0.45 * drops / (np.max(np.abs(drops)) or 1)
        return x

    @classmethod
    def _splash2(cls, f, t, p):
        """A bright, dry splash: a short slap, a fizz of many tiny bubbles, and a few tuned bloops.
        Everything sits above ~500 Hz, and the whole thing is over in well under half a second."""
        rng = np.random.default_rng(int(f * 13))
        n = len(t)
        # 1. the slap: 10 ms of noise in the 1.2–6 kHz band
        slap = cls._band(rng.standard_normal(n), *p.get("slap_band", (1200, 6000)), soft=0.4)
        slap = slap / (np.max(np.abs(slap)) or 1) * np.minimum(1, t / 0.0008) * np.exp(-t / 0.010)
        x = p["slap"] * slap
        # 2. the fizz: many tiny bubbles (1.5–5 kHz), dense at first and thinning out
        fizz = []
        for k in range(int(p["fizz"])):
            start = p["fizz_len"] * rng.random() ** 1.8          # most of them right after the slap
            fk = rng.uniform(*p.get("fizz_band", (1500, 5000)))
            fizz.append((start, fk / f, 0.18 * (1 - start / p["fizz_len"]) + 0.05))
        fz = Synth._bubbles(f, t, {"bubbles": fizz, "damp": 1.4})
        x += 0.9 * fz / (np.max(np.abs(fz)) or 1)
        # 2b. the wash: the "shh" of water spraying, a short lumpy burst of mid-high noise
        wash = cls._band(rng.standard_normal(n), *p.get("wash_band", (900, 4000)), soft=0.45)
        lump = cls._band(rng.standard_normal(n), 15, 60, soft=0.6)
        lump = np.clip(0.6 + 0.5 * lump / (np.std(lump) or 1), 0, 2)
        wash = wash / (np.max(np.abs(wash)) or 1) * np.minimum(1, t / 0.004) * np.exp(-t / (0.05 + 0.1 * p["fizz_len"])) * lump
        x += 0.55 * p["slap"] * wash
        # 3. a few bigger bubbles, tuned to the note (bigger pool → lower), as the water settles
        big = [(0.02 + 0.2 * rng.random(), p["size"] * r, 0.5 + 0.3 * rng.random())
               for r in (1.0, 1.5, 2.0, 1.25, 3.0)[:p["bloops"]]]
        bl = Synth._bubbles(f * p.get("bloop_mul", 4), t, {"bubbles": big, "damp": 1.0, "jitter": 0.03})
        x += 0.35 * bl / (np.max(np.abs(bl)) or 1)
        # a gentle high-pass so nothing rumbles
        return cls._band(x, 450 if "top" in p else 600, p.get("top", 12000), soft=0.35)

    @staticmethod
    def _bubbles(f, t, extra):
        """A few bubbles: p(t) = a·sin(2π∫f dt)·e^(−d t), f rising as f0(1 + σt).
        Damping d = 0.043 f + 0.0014 f^1.5 and σ = 0.1 d follow van den Doel (2005)."""
        rng = np.random.default_rng(int(f * 10))
        x = np.zeros_like(t)
        jit = extra.get("jitter", 0.0)
        for start, ratio, amp in extra["bubbles"]:
            fk = f * ratio * (1 + rng.uniform(-jit, jit))
            d = (0.043 * fk + 0.0014 * fk ** 1.5) * extra.get("damp", 1.0)
            sig = 0.1 * d / max(extra.get("damp", 1.0), 1e-3) * 0.35   # the little upward chirp of a bubble
            tt = t - start
            on = tt >= 0
            tt = np.where(on, tt, 0)
            phase = 2 * np.pi * fk * (tt + sig * tt ** 2 / 2)
            b = amp * np.sin(phase) * np.exp(-d * tt) * np.minimum(1, tt / 0.0015) * on
            x += b
            if extra.get("splash"):                          # the tiny splash as the bubble forms
                n = rng.standard_normal(len(t))
                n = np.convolve(n, np.ones(9) / 9, mode="same")
                x += extra["splash"] * amp * n * np.exp(-tt / 0.005) * on
        if extra.get("stream"):                              # a soft hiss of running water under a pour
            end = max(s for s, _, _ in extra["bubbles"]) + 0.12
            n = rng.standard_normal(len(t))
            n = np.convolve(n, np.ones(14) / 14, mode="same")
            env = np.clip(t / 0.04, 0, 1) * np.clip((end - t) / 0.12, 0, 1)
            x += extra["stream"] * n * env
        return x

    @staticmethod
    def _reverb(x, wet, seconds=2.0):
        if wet <= 0:
            return x
        n = int(SR * seconds)
        ir = np.random.default_rng(7).uniform(-1, 1, n) * (1 - np.arange(n) / n) ** 3.2
        ir /= np.sqrt(np.sum(ir ** 2))
        size = len(x) + n
        tail = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)
        out = tail * wet
        out[: len(x)] += x * (1 - wet)
        return out

    def gain_db(self, extra=0.0):
        return 20 * np.log10(max(1e-3, self.cfg.volume)) + extra
