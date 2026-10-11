# Дизайн энергетического VAD в задаче чтения I2S (ESP32-P4, FreeRTOS)

> Дизайн для кулона Local Memory Pendant ([local_memory_pendant.md](local_memory_pendant.md)).
> Настольный референс алгоритма: `tools/vad_sim.py` — логика и константы идентичны C-коду ниже.

## Суть

VAD не выделяется в отдельную задачу: одна задача читает из DMA-буфера I2S готовые
блоки и в том же цикле считает энергию, ведёт адаптивный пол шума и решает
«речь/тишина». На ESP32-P4 это единицы процента CPU.

Блок = один Opus-фрейм: **20 мс, 16 кГц, mono, int16 = 320 сэмплов = 640 байт**.
Выравнивание на фрейм Opus избавляет от пересинхронизации — VAD-флаг приклеивается
к каждому фрейму.

## Четыре механизма

1. **Энергия блока.** Средний модуль сэмпла (`Σ|s|/N`) — только abs и накопление,
   целочисленно; в дБFS: `20·log10(ma/32768)`.
2. **Адаптивный пол шума.** В тишине пол подтягивается к уровню экспонентой
   (τ ≈ 1 с); во время речи — заморожен. Решение по SNR `level − noise`,
   а не по абсолютному порогу — переносимо между помещениями.
3. **Гистерезис.** Открытие при SNR > 10 дБ, закрытие при SNR < 5 дБ.
4. **Атака + hangover.** 2 блока подряд выше порога на открытие (против щелчков);
   hangover 300 мс после последнего активного блока (иначе режутся затухания).
   Для головы слова — предролл: кольцо последних ~100–200 мс, вливается в поток
   при открытии VAD (на P4 кольцо делается 2D-DMA в PSRAM без копий).

## С-скетч (логика, переносимая в прошивку)

```c
#define VAD_BLOCK_SAMPLES   (16000 / 50)        // 320 = 20 мс
#define VAD_OPEN_SNR_DB     10.0f
#define VAD_CLOSE_SNR_DB    5.0f
#define VAD_HANGOVER_MS     300
#define VAD_ATTACK_BLOCKS   2
#define VAD_NOISE_ALPHA     0.01f

typedef struct {
    float noise_db;
    bool  active;
    int   attack;
    int   hangover;      // в блоках
} vad_t;

static inline float block_level_db(const int16_t *s, int n)
{
    int64_t acc = 0;
    for (int i = 0; i < n; i++) acc += abs(s[i]);
    float ma = (float)acc / n / 32768.0f;
    return 20.0f * log10f(ma + 1e-6f);
}

static bool vad_process(vad_t *v, const int16_t *s, int n)
{
    float level = block_level_db(s, n);
    float snr = level - v->noise_db;

    if (v->active) {
        if (snr < VAD_CLOSE_SNR_DB) {
            if (--v->hangover <= 0) v->active = false;
        } else {
            v->hangover = VAD_HANGOVER_MS / 20;
        }
    } else {
        v->noise_db += (level - v->noise_db) * VAD_NOISE_ALPHA; // только в тишине
        if (snr > VAD_OPEN_SNR_DB) {
            if (++v->attack >= VAD_ATTACK_BLOCKS) v->active = true;
        } else {
            v->attack = 0;
        }
    }
    return v->active;
}
```

## Интеграция в задачу

```c
static void i2s_vad_task(void *arg)
{
    static int16_t buf[VAD_BLOCK_SAMPLES];   // статики, без malloc
    vad_t vad = { .noise_db = -60.0f };
    int cal = 25;                            // 0.5 с калибровки пола шума

    for (;;) {
        size_t bytes;
        ESP_ERROR_CHECK(i2s_channel_read(rx_chan, buf, sizeof(buf), &bytes, portMAX_DELAY));
        if (cal > 0) {                        // калибровка: пол шума сходится,
            float lvl = block_level_db(buf, VAD_BLOCK_SAMPLES); // решения отключены
            vad.noise_db += (lvl - vad.noise_db) * 0.2f;
            cal--;
            continue;
        }
        bool speech = vad_process(&vad, buf, VAD_BLOCK_SAMPLES);
        xRingbufferSend(ring, buf, sizeof(buf), portMAX_DELAY);  // все блоки в кольцо
        // события segment_open / segment_close — отдельная очередь кодеру/писателю
    }
}
```

- Задача блокируется в `i2s_channel_read` (`portMAX_DELAY`): между блоками спит,
  DMA пишет сам. Приоритет — средний: выше писателя в SD, ниже кодера.
- Кодеру и писателю нужны пары событий «открылся/закрылся сегмент», не 50 флагов/с.
  По открытию вливается предролл, по закрытию флашится Opus-кодер.
- **DC-смещение микрофона** ведите бегущим средним и вычитайте до расчёта энергии.
- Первые 0,5–1 с после включения — мусор: пол шума инициализировать −60 дБFS,
  ранние сегменты отбрасывать.

## Аппаратная обвязка на P4 (фишки)

- **BitScrambler** как препроцессор DMA-пути: деинтерлив стерео → mono и
  упаковка 24-в-32-слоте → int16 без CPU-циклов в hot path задачи.
- **2D-DMA кольцо в PSRAM** — непрерывный захват без копий; предролл бесплатно.
- **Апгрейд-путь:** esp-dsp (оптимизирован под P4) для спектрального VAD;
  ESP-SR AFE (AEC/NS/нейро-VAD, официально на P4); esp-nn/esp-dl для int8-модели.

## Честные ограничения

Энергетический VAD не отличает речь от музыки/ТВ/клавиатуры — для диктофона это
терпимо (лишние секунды дешевле потерянного слова, Whisper вернёт пустую строку).
Дешёвый следующий шаг в той же петле — ZCR или спектральная плоскостность по
64-точечному окну.

**Без железа не проверяется:** абсолютные уровни дБFS и поведение на реальном
шуме помещения (самошум микрофона, DC-смещение, реверберация) и реальный
тайминг DMA/I2S. Симулятор валидирует алгоритм и константы-отношения, но
абсолютные пороги калибруются только на живом устройстве.
