# Аналоги Omi Pendant: сравнительное исследование

> Дата: 2026-10-11. Исследование аналогов Omi Pendant (Based Hardware, ex-Friend Pendant) — носимого ИИ-кулона, записывающего разговоры, транскрибирующего их и создающего ИИ-саммари.
>
> Главный вывод: полноценного независимого открытого аналога не существует. Omi сам по себе — единственный полностью open-source продукт класса (железо + прошивка + приложение + backend, MIT). Остальные аналоги открыты частично или закрыты.

## Критерии сравнения

| Критерий | Что оценивается |
|---|---|
| Открытость слоёв | Железо (схемы/PCB), прошивка, приложение, backend — отдельно, с лицензией |
| Доступ к сырому аудио | Можно ли забрать исходный поток (Opus/PCM) с устройства |
| Зависимость от облака | Насколько критичен SaaS производителя, заменяем ли |
| Основа | Девборд vs плата собственной разработки |
| Автономность | Заявленное время работы при постоянной записи (⚠ = оценка, не проверено) |
| Зрелость | Активность проекта / статус продукта |
| Обработка аудио | Где физически идёт транскрипция и LLM (локально / своё облако / облако производителя) |

Легенда открытости: ✅ открыт (исходники + лицензия) · ⚠️ частично · ❌ закрыто · ➖ отсутствует.

## Сводная таблица

| Устройство / проект | Страница продукта | Исходники | Основа: девборд / своя плата | Железо | Прошивка | Приложение | Backend | Сырое аудио | Зависимость от облака | Автономность (пост. запись) | Зрелость | Обработка аудио |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Omi** (upstream) — эталон класса | [omi.me/omi](https://www.omi.me/omi) | [BasedHardware/omi](https://github.com/BasedHardware/omi), MIT, 13,7k★, активен | Обе: DevKit = девборд XIAO nRF52840 Sense; серийный кулон = своя открытая плата (KiCad) | ✅ MIT | ✅ Zephyr/C, MIT | ✅ Flutter, MIT | ✅ FastAPI, MIT, self-host | ✅ (BLE, Opus-стрим) | нет — облако открыто и заменяемо | ~10–14 ч | высокая | облако Omi **или своё** |
| **Omi + nytka-server** (self-host) | — | [nytka-app/server](https://github.com/nytka-app/server), [nytka-app/android](https://github.com/nytka-app/android), Apache-2.0 | Железо Omi (девборд/серийная плата) | ✅ | ✅ | ✅ Kotlin | ✅ свой сервер | ✅ | нет | как у Omi | ранняя (0★, активно пушится) | своё облако |
| **myomi** (форк Omi) | — | [emingenc/myomi](https://github.com/emingenc/myomi), MIT | Железо Omi | ✅ | ✅ | ⚠️ свой APK | ⚠️ docker-compose + OpenAI API | ✅ | частично (свой LLM-провайдер) | как у Omi | персональный проект | свой LLM-провайдер |
| **Owl** (OwlAIProject) | — | [OwlAIProject/Owl](https://github.com/OwlAIProject/Owl), MIT, 666★ | Девборд XIAO ESP32-S3 Sense; своя плата «Bee» не опубликована (404) | ⚠️ | ✅ | ✅ iOS/watchOS | ✅ локально Ollama + Whisper/Deepgram | ✅ | нет | н/д | **заброшен с 2024** | локально ✅ |
| **limitless-libre** | — (железо Limitless снято с продажи) | [shade-familiar/limitless-libre](https://github.com/shade-familiar/limitless-libre), Apache-2.0 | Чужое закрытое железо (Limitless) | ❌ | ✅ | ➖ | ⚠️ свой | ✅ (перенаправление аудио) | нет | ~2 дня (заявлено Limitless) | 1 коммит, зрелость не доказана | своё (проект) |
| **xiaozhi-esp32** | [xiaozhi.me](https://xiaozhi.me) (облако по умолчанию) | [78/xiaozhi-esp32](https://github.com/78/xiaozhi-esp32) (30k★, MIT), [сервер](https://github.com/xinnan-tech/xiaozhi-esp32-server) (MIT) | Любой девборд ESP32-S3 (поддержка десятков плат, свою плату можно развить) | ✅ схемы в экосистеме | ✅ MIT | ✅ MIT | ✅ свой сервер | ⚠️ не нотейкер | нет (при self-host) | зависит от платы | очень высокая | свой сервер / обл. Xiaozhi |
| **Voice-Wearable-Pendant** | — | [Mayankpratapsingh022/Voice-Wearable-Pendant-Offline-inference](https://github.com/Mayankpratapsingh022/Voice-Wearable-Pendant-Offline-inference), **без лицензии** | Свой макет ESP32-S3 (дисплей, тач, мики, динамик) | ❌ | ❌ | ⚠️ Flutter | ➖ | ✅ BLE-стрим | нет | н/д | 4 коммита, прототип; офлайн-инференс **не реализован** | планировалась локальная — не реализована |
| **AI Buddy** (DigiKey) | [DigiKey Maker](https://www.digikey.com/en/maker/projects/build-an-open-source-ai-buddy-a-diy-ai-companion-for-kids/e48bc486a9ba45efbd35fd70d19026c3) | [MukeshSankhla/AI-Buddy](https://github.com/MukeshSankhla/AI-Buddy), **CC BY-NC-SA 4.0** (некоммерческая) | Девборд UNIHIKER K10 (ESP32-S3) + своя BMS-плата (Gerbers ✅) | ⚠️ открытая BMS, остальное девборд | ⚠️ бинарник (исходники Xiaozhi, MIT) | ➖ | ⚠️ обл. Xiaozhi | ⚠️ | да, Xiaozhi (xiaozhi.me) | н/д | хобби-проект, 5★ | облако Xiaozhi |
| **DIY AI Pin** (Instructables) | [instructables.com/DIY-AI-Pin-a-Wearable-VisionVoice-Assistant](https://www.instructables.com/DIY-AI-Pin-a-Wearable-VisionVoice-Assistant/) | прошивка — готовый бинарник, исходников нет | Девборд XIAO ESP32S3 Sense + MAX98357A + 3D-корпус | ⚠️ скачиваемых файлов нет | ❌ | ➖ | ⚠️ обл. Xiaozhi | ❌ | да, жёсткая | н/д | гайд-уровень | облако Xiaozhi |
| **CircuitDigest ESP32CAM Pendant** | [circuitdigest.com/microcontroller-projects/esp32cam-ai-vision-assistant-pendant](https://circuitdigest.com/microcontroller-projects/esp32cam-ai-vision-assistant-pendant) | [Circuit-Digest/ESP32CAM_AI_PENDANT](https://github.com/Circuit-Digest/ESP32CAM_AI_PENDANT), **без лицензии** | Девборд ESP32-CAM | ❌ | ❌ | ➖ | ❌ CircuitDigest Cloud + Sarvam TTS | ❌ | да, жёсткая | н/д | контент-проект | чужое облако |
| **Limitless Pendant** | Продажи остановлены; Meta купила Limitless 05.12.2025 | закрыто | Своя плата | ❌ | ❌ | ❌ | ❌ | ❌ (только API/экспорт) | да | ~2 дня | **закрыт (Meta, 12.2025)** | облако Limitless |
| **Bee / Bee Pioneer** | [bee.computer/bee-pioneer](https://bee.computer/bee-pioneer) ($49,99, распродан) | закрыто | Своя плата | ❌ | ❌ | ❌ | ❌ | ❌ | да (Amazon) | до 7 дней (заявлено, за счёт offload) | куплена Amazon 07.2025 | облако Bee/Amazon |
| **Plaud NotePin** | [plaud.ai/products/plaud-notepin](https://www.plaud.ai/products/plaud-notepin) ($159) | закрыто | Своя плата | ❌ | ❌ | ❌ | ❌ | ⚠️ ограниченный экспорт, 300 мин/мес | да | ~20 ч ⚠ | в продаже, лидер сегмента | облако Plaud |
| **Friend** (friend.com) | [friend.com](https://friend.com) | железо закрыто, код — форк-линия Omi | Своя плата | ❌ | ⚠️ | ⚠️ | ❌ | ⚠️ | да (Gemini) | н/д | шипуется медленно, отзывы разгромные | облако Friend |
| **Taya Necklace** | прямая страница не подтверждена (taya.ai → 404) | закрыто | Своя плата | ❌ | ❌ | ❌ | ❌ | ❌ («пишет только ваш голос») | да | н/д | предзаказы 2026, $5M seed | облако Taya |
| **iFLYTEK P1 / Mobvoi TicNote** | [mobvoi.com](https://www.mobvoi.com/products/ticnote); iFLYTEK — искать на [global.iflytek.com](https://global.iflytek.com) | закрыто | Своя плата | ❌ | ❌ | ❌ | ❌ | ❌ | да (подписка 300–600 мин/мес) | P1 ~8–10 ч ⚠; TicNote ~15 ч ⚠ | в продаже | облако производителя |

## Open-source экосистема вокруг Omi (детали)

- **Upstream:** [BasedHardware/omi](https://github.com/BasedHardware/omi) — KiCad-железо, прошивка Zephyr, приложения Flutter, бэкенд Python/FastAPI/Deepgram.
- **Полезные форки:** `emingenc/myomi` (self-host + смарт-очки Even Realities G1), `hovtgc/omi-macos-python` (локальная транскрипция Whisper на Mac), `AaronPutting/omi` (прошивка «press-to-listen» с записью на SD), `nothintoulouse/LARK` (Android-BLE рекордер с VAD).
- **Self-hosted бэкенды:** nytka-app/server (C#, Apache-2.0), `cgallic/omi-pendant-chronicle` (BLE-клиент + Python-коллектор), `wynn-dev/hearloom`.
- **Официальный DIY-гайд (Hackster.io):** [Opensource AI Wearable Recording Device](https://www.hackster.io/kodjima33/opensource-ai-wearable-recording-device-b68b10) — XIAO nRF52840 Sense + батарея 250 мАч, сборка ~2 часа.
- **Краудфандинг:** Kickstarter «Friend: Open Source AI Wearable» (апрель–май 2024) — $49 868 при цели $5 000 (997%), 712 бэкеров; кампания выросла в Omi. Других значимых краудфандинговых кампаний в нише нет (на Crowd Supply аналогов нет).

## Важные уточнения (проверено, октябрь 2026)

1. **Два разных «Friend»** — не путать: Based Hardware (Kickstarter → Omi) и friend.com Avi Schiffmann (Tab → Friend, $129–249, отзывы разгромные: NYT «Everyone Hates 'Friend'»).
2. **«Bee Pioneer» приписан чужому домену:** продукт существует, но на [bee.computer/bee-pioneer](https://bee.computer/bee-pioneer); umevo.ai — чужой Shopify-магазин диктофонов.
3. **Limitless больше не «главный конкурент»:** куплена Meta 05.12.2025, продажи остановлены, сервис отключается по регионам.
4. **«Открытость» ≠ «нет облака»:** у AI Buddy и DIY AI Pin прошивка открыта (Xiaozhi, MIT), но по умолчанию они подключаются к облачной платформе xiaozhi.me. AI Buddy — под CC BY-NC-SA 4.0 (некоммерческая).
5. **Проекты без LICENSE-файла юридически «all rights reserved»:** Voice-Wearable-Pendant, CircuitDigest ESP32CAM_AI_PENDANT — брать их код как основу нельзя.

## Выводы для проекта на ESP32 (ESP-IDF)

- **Практичный маршрут №1:** DevKit Omi (или самопайка на XIAO nRF52840 Sense по Hackster-гайду) + self-hosted бэкенд (nytka-app/server). Всё MIT/Apache.
- **Практичный маршрут №2:** своя плата на ESP32-S3 поверх [xiaozhi-esp32](https://github.com/78/xiaozhi-esp32) + собственный [xiaozhi-esp32-server](https://github.com/xinnan-tech/xiaozhi-esp32-server) — самая живая и большая открытая база кода, но форм-фактор кулона делается самостоятельно.
- **Незанятая ниша:** полностью офлайн-кулон (кулон шлёт только исходный Opus на свой сервер/локальный хаб, без SaaS) пока не существует в готовом виде.
- **Ограничитель автономности:** всегда-включённый микрофон + кодирование съедает батарею; для своего устройства на ESP32-S3 обязательны Opus-кодирование на чипе и duty-cycle.
