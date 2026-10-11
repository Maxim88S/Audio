#!/usr/bin/env python3
"""Настольный симулятор энергетического VAD (референс алгоритма из docs/vad_design.md).

Реализует ту же логику, что планируется в задаче чтения I2S на ESP32-P4:
блок 20 мс, энергия как средний модуль, адаптивный пол шума (EMA только в
тишине), гистерезис SNR, атака 2 блока, hangover. Сверяет найденные сегменты
с ground truth из labels-JSON генератора и печатает precision/recall/F1.

Только стандартная библиотека — без pip-зависимостей.

Использование:
  python tools/vad_sim.py synth.wav --labels synth.labels.json \
      [--open-snr 10] [--close-snr 5] [--hangover-ms 300] [--attack-blocks 2]
"""

import argparse
import json
import math
import struct
import wave

FS = 16000
BLOCK = FS // 50            # 320 сэмплов = 20 мс
INIT_NOISE_DB = -60.0       # «глухая» инициализация пола шума
NOISE_ALPHA = 0.01          # EMA пола шума за блок (~1 с усреднения)
CAL_BLOCKS = 25             # фаза калибровки: 0.5 с измерения без решений


def read_wav(path):
    with wave.open(path, "rb") as w:
        if (w.getnchannels(), w.getsampwidth(), w.getframerate()) != (1, 2, FS):
            raise SystemExit(f"ожидался mono int16 {FS} Гц, а не так: {w.getparams()}")
        return struct.unpack(f"<{w.getnframes()}h", w.readframes(w.getnframes()))


def run_vad(samples, open_snr, close_snr, hangover_blocks, attack_blocks):
    """Идентично C-скетчу в docs/vad_design.md. Возврат: сегменты [(s0,s1)], пол шума."""
    noise_db = INIT_NOISE_DB
    active, attack, hangover = False, 0, 0
    segments, seg_start = [], None

    for blk in range(0, len(samples) - BLOCK + 1, BLOCK):
        chunk = samples[blk:blk + BLOCK]
        ma = sum(abs(s) for s in chunk) / BLOCK / 32768.0
        level_db = 20.0 * math.log10(ma + 1e-12)
        snr = level_db - noise_db

        if blk < CAL_BLOCKS * BLOCK:          # калибровка: пол шума сходится,
            noise_db += (level_db - noise_db) * 0.2   # решения отключены
            continue

        if active:
            if snr < close_snr:
                hangover -= 1
                if hangover <= 0:
                    active = False
                    segments.append((seg_start, (blk + BLOCK) / FS))
                    seg_start = None
            else:
                hangover = hangover_blocks
        else:
            noise_db += (level_db - noise_db) * NOISE_ALPHA   # только в тишине
            if snr > open_snr:
                attack += 1
                if attack >= attack_blocks:
                    active, attack = True, 0
                    seg_start = blk / FS
            else:
                attack = 0

    if active:
        segments.append((seg_start, len(samples) / FS))
    return segments, noise_db


def match(pred, gt, overlap_frac=0.5):
    """Сегмент считается найденным, если предсказание перекрывает >=50% GT."""
    tp, start_offs, missed, extra = 0, [], [], list(pred)
    for g0, g1 in gt:
        hit = None
        for i, (p0, p1) in enumerate(extra):
            if min(g1, p1) - max(g0, p0) >= overlap_frac * (g1 - g0):
                hit = i
                break
        if hit is not None:
            p0, p1 = extra.pop(hit)
            tp += 1
            start_offs.append(p0 - g0)
        else:
            missed.append((g0, g1))
    return tp, start_offs, missed, extra


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("wav")
    p.add_argument("--labels", required=True)
    p.add_argument("--open-snr", type=float, default=10.0)
    p.add_argument("--close-snr", type=float, default=5.0)
    p.add_argument("--hangover-ms", type=float, default=300.0)
    p.add_argument("--attack-blocks", type=int, default=2)
    args = p.parse_args()

    with open(args.labels, encoding="utf-8") as f:
        labels = json.load(f)
    gt = [tuple(s) for s in labels["segments"]]

    samples = read_wav(args.wav)
    hangover_blocks = max(1, int(args.hangover_ms / 1000 * FS / BLOCK))
    pred, noise_db = run_vad(samples, args.open_snr, args.close_snr,
                             hangover_blocks, args.attack_blocks)

    tp, offs, missed, extra = match(pred, gt)
    precision = tp / max(1, len(pred))
    recall = tp / max(1, len(gt))
    f1 = 2 * precision * recall / max(1e-9, precision + recall)
    mean_off = sum(offs) / len(offs) if offs else float("nan")

    print(f"Параметры: open={args.open_snr} дБ, close={args.close_snr} дБ, "
          f"hangover={args.hangover_ms:.0f} мс, attack={args.attack_blocks} бл.")
    print(f"Пол шума: оценённый {noise_db:.1f} дБFS / истинный "
          f"{labels['noise_floor_db']} дБFS")
    print(f"Найдено сегментов: {len(pred)} (GT: {len(gt)})")
    for p0, p1 in pred:
        print(f"  речь {p0:6.2f} … {p1:6.2f} с")
    for g0, g1 in missed:
        print(f"  ПРОПУЩЕН сегмент GT {g0:.2f} … {g1:.2f} с")
    for p0, p1 in extra:
        print(f"  ЛОЖНЫЙ сегмент {p0:.2f} … {p1:.2f} с")
    print(f"Precision {precision:.2f} | Recall {recall:.2f} | F1 {f1:.2f} | "
          f"смещение старта {mean_off * 1000:+.0f} мс (сред.)")
    print("ПРИЁМКА:", "PASS" if (precision >= 0.9 and recall >= 0.9
          and abs(noise_db - labels["noise_floor_db"]) <= 3) else "FAIL")


if __name__ == "__main__":
    main()
