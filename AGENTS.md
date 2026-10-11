# AGENTS.md — инструкции для coding agent (репозиторий audio)

> Дополнение к корневому `E:\tmp\tmc2_ver2\AGENTS.md`. Здесь — правила именно этого репозитория.

## Что это за репозиторий

Проект **Local Memory Pendant** — кулон-память разговоров без облака (см. [docs/local_memory_pendant.md](docs/local_memory_pendant.md)). Целевая платформа прошивки: ESP32-P4, ESP-IDF. Пока в репо — только исследования, дизайн-документы и настольные прототипы инструментов.

## Структура

- `omi_pendant_alternatives.md` — сравнительное исследование аналогов Omi Pendant.
- `docs/local_memory_pendant.md` — идея устройства.
- `docs/vad_design.md` — дизайн энергетического VAD в задаче чтения I2S (FreeRTOS).
- `tools/` — настольные прототипы на Python (только stdlib, никаких pip-зависимостей).
- `artifacts/` — сохранённые страницы-артефакты исследований; не редактировать.

## Команды

```bash
# Синтетическая запись «речь + шум» с известной разметкой (ground truth)
python tools/gen_synth_audio.py synth.wav --labels synth.labels.json --dur 30

# Прогон энергетического VAD и сверка с ground truth
python tools/vad_sim.py synth.wav --labels synth.labels.json
```

Константы VAD в `tools/vad_sim.py` должны совпадать с константами из `docs/vad_design.md` и будущего кода прошивки — при изменении параметров править все три места.

## Соглашения

- Код прошивки (когда появится): логирование только через ESP_LOGI/W/E, ошибки через ESP_ERROR_CHECK/ESP_RETURN_ON_ERROR, задачи через xTaskCreate, новые компоненты по образцу существующих (CMakeLists.txt + include/).
- Настольные инструменты: только стандартная библиотека Python, без сторонних пакетов; воспроизводимость через `--seed`.
- Ссылки на источники адаптированных решений — обязательно в тексте.
- Коммитить можно; **push на GitHub — только по явному указанию пользователя**.
- Артефакты сохранённых web-страниц складывать в `artifacts/`, не в корень.

## Скилл

Предметный skill агента: `.agents/skills/energy-vad-prototyping/SKILL.md` — когда прототипируете/тюните VAD, читайте его сначала.
