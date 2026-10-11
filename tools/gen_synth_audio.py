#!/usr/bin/env python3
"""Генератор синтетической записи «речь + шум» с известной разметкой.

Имитация сигнала кулона Local Memory Pendant (16 кГц, mono, int16):
  - шумовой пол: low-pass белый шум, уровень задаётся в дБFS;
  - сегменты «речи»: набор формантных синусоид с вибрато, syllable-огибающая
    и шипящая добавка; края сегментов с фейдом 10 мс.
Ground truth (интервалы речи + уровни) пишется в JSON рядом с WAV.

Только стандартная библиотека — без pip-зависимостей.

Использование:
  python tools/gen_synth_audio.py synth.wav --labels synth.labels.json \
      --dur 30 --seed 42 --noise-floor-db -45 --speech-level-db -18
"""

import argparse
import json
import math
import random
import struct
import wave

FS = 16000


def db_to_gain(db):
    return 10 ** (db / 20.0)


def rms_db(samples):
    r = math.sqrt(sum(s * s for s in samples) / len(samples)) / 32768.0
    return 20 * math.log10(r + 1e-12)


def make_noise(n, seed, alpha=0.12):
    """Low-pass белый шум (однополюсный фильтр), нормированный к 1.0 RMS."""
    rnd = random.Random(seed)
    y = 0.0
    out = []
    for _ in range(n):
        y += alpha * (rnd.uniform(-1.0, 1.0) - y)
        out.append(y)
    r = math.sqrt(sum(s * s for s in out) / len(out)) or 1e-12
    return [s / r for s in out]


def make_speech(dur, seed):
    """Сегмент «речи»: формантные синусоиды + вибрато + шипение + огибающая слогов."""
    rnd = random.Random(seed)
    f0 = rnd.uniform(90, 180)
    parts = [(f0 * k, rnd.uniform(0.1, 0.4)) for k in (1.0, 2.0, 3.0, 4.7, 6.3)]
    phases = [rnd.uniform(0, 2 * math.pi) for _ in parts]
    vib_f, vib_a = rnd.uniform(3.5, 6.0), 0.01
    fsyl = rnd.uniform(2.8, 4.2)
    n = int(dur * FS)
    out = []
    for i in range(n):
        t = i / FS
        s = 0.0
        for (f, a), p in zip(parts, phases):
            f_inst = f * (1.0 + vib_a * math.sin(2 * math.pi * vib_f * t))
            s += a * math.sin(2 * math.pi * f_inst * t + p)
        s += 0.35 * rnd.uniform(-1.0, 1.0)          # «шипение» согласных
        env = 0.3 + 0.7 * (max(0.0, math.sin(2 * math.pi * fsyl * t)) ** 2)
        out.append(s * env)
    r = math.sqrt(sum(s * s for s in out) / len(out)) or 1e-12
    return [s / r for s in out]


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("wav", help="выходной WAV-файл")
    p.add_argument("--labels", help="выходной JSON с ground truth (по умолчанию <wav>.labels.json)")
    p.add_argument("--dur", type=float, default=30.0, help="длительность, с")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--noise-floor-db", type=float, default=-45.0)
    p.add_argument("--speech-level-db", type=float, default=-18.0)
    p.add_argument("--segments", type=int, default=7, help="примерное число сегментов речи")
    args = p.parse_args()
    labels_path = args.labels or args.wav.rsplit(".", 1)[0] + ".labels.json"

    rnd = random.Random(args.seed)
    total = int(args.dur * FS)
    buf = [s * db_to_gain(args.noise_floor_db)     # шум к целевому уровню
           for s in make_noise(total, args.seed, alpha=0.12)]

    # Раскладка сегментов: случайные интервалы с зазором >= 400 мс
    min_gap = int(0.4 * FS)
    min_len, max_len = int(1.2 * FS), int(4.0 * FS)
    segments, cursor = [], int(0.6 * FS)   # 0.6 с тишины в начале: усаканивание мика
    for _ in range(args.segments):
        if cursor + min_len > total - min_gap:
            break
        seg_len = rnd.randint(min_len, max_len)
        end = min(cursor + seg_len, total - min_gap)
        speech = make_speech((end - cursor) / FS, rnd.randrange(1 << 30))
        gain = db_to_gain(args.speech_level_db)
        fade = int(0.01 * FS)                       # 10 мс фейды краёв
        for i, s in enumerate(speech):
            w = min(1.0, (i + 1) / fade, (len(speech) - i) / fade)
            buf[cursor + i] += s * gain * w
        segments.append([cursor / FS, end / FS])
        cursor = end + min_gap + rnd.randint(0, int(0.8 * FS))

    samples = [max(-32768, min(32767, int(round(s * 32768.0)))) for s in buf]

    with wave.open(args.wav, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(FS)
        w.writeframes(struct.pack(f"<{len(samples)}h", *samples))

    meta = {
        "fs": FS, "dur_s": args.dur, "seed": args.seed,
        "noise_floor_db": args.noise_floor_db,
        "speech_level_db": args.speech_level_db,
        "segments": segments,
    }
    with open(labels_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(f"OK: {args.wav} ({args.dur:.0f} с, {len(segments)} сегментов речи)")
    print(f"OK: {labels_path} (пол шума {args.noise_floor_db} дБFS, "
          f"речь {args.speech_level_db} дБFS, факт RMS {rms_db(samples[:FS]):.1f} дБFS в 1-й секунде)")


if __name__ == "__main__":
    main()
