# Cosmos — Project Context for Claude Code

> **How to use this file:** Save it as `CLAUDE.md` in the project root and
> Claude Code will load it automatically each session. It captures every
> decision made so far so we don't
> re-litigate settled choices. Read the "Locked decisions" section before
> proposing architecture changes.

---

## 1. What we're building

**Cosmos** is a compact, cute, tracked robot companion — think *baby robot + tiny
dump truck + emotional pet*. It is a **desk companion**, designed to feel like a
little living presence rather than a tool. It has a
big animated face (glowing cyan eyes on black), two glowing teal antennae, a front
scoop that picks up tiny objects, and a rear dump bed those objects get tipped into.

- **Personality target:** baby-cute, playful, mischievous, curious, emotionally
  expressive, a little goofy, intelligent-but-adorable. A *pet*, not a gadget.
- **Aesthetic:** glossy white + soft teal, rounded/soft, premium toy-like. Black
  glossy face, cyan eyes only (no mouth). Compact — "small and cute" is a hard
  constraint; everything must fit a small body.
- **Build window:** ~2 months. Willing to cut features that don't fit. Priority is
  **highest-impact / lowest-effort first.**

(Project was originally named "Carl," renamed to **Cosmos**. Always use Cosmos.)

## 2. Who's building it / division of labor

- **Builder.** Very experienced at **3D modeling and printing** — handles
  **ALL mechanical/printed parts** (chassis, tracks, scoop, arms,
  linkage, bed, face lens). Do **not** generate CAD or mechanical parts. When mechanics
  come up, give *geometry/constraint advice* only (see §7).
- **Where Claude Code helps:** electronics wiring, firmware/software (Python on the
  Pi), component selection, the emotion/AI system, RC, and project docs.
- **Existing files:** `cosmos-build-roadmap.md`, `cosmos-bom.xlsx`.

## 3. Locked decisions (do not reverse without being asked)

| Decision | Choice | Why |
|---|---|---|
| **Brain** | **Raspberry Pi Zero 2 W**, headless Pi OS Lite 64-bit | Small, Wi-Fi/BLE, Linux, enough for current scope |
| **Architecture (now)** | **Pi-only.** No ESP32 in the loop yet | For the current features (emotion engine + gesture ML) the Pi alone is enough; one board/one language is simpler |
| **ESP32-S3** | Owned, held in reserve as a future co-processor | Add it **only** when we need reliable wheel **encoders** or a hard-real-time **cliff-stop** (Tier 3+). Not before |
| **Pi 5** | Rejected | Overkill: power, heat, size — fights "small and cute" |
| **Waveshare all-in-one display boards** | Rejected as the brain | GPIO-starved; the C6 one is single-core + no PSRAM. Fine as face modules, bad as brains |
| **Face (prototype)** | 2.0" **ST7789V** IPS LCD, 240×320, SPI (owned) | Cheap, good enough to build the eyes on NOW. (It's an IPS LCD despite the "OLED" listing — backlit, dark-grey blacks) |
| **Face (final, maybe)** | Possibly swap to a 2.x" **AMOLED** later | True blacks for the glossy-black face look. Not required for v1 |
| **Charging dock** | Cut from v1 | Charge by plugging in. Everything else comes first |
| **Camera / vision** | Deferred to v2 | High effort; not needed for v1 |
| **Emotion approach (current)** | **Option A + Option B** (see §6) | Lifelike emotion without a local LLM |
| **Local LLM on the Pi** | Not feasible | 512MB RAM can't fit a useful model. Personality "soul" LLM, if ever, is **cloud over Wi-Fi** (Tier 5/v2) |

## 4. Feature roadmap (priority order)

Build philosophy: **body → drivable → RC → interactive.** Stop anywhere and still
have something charming.

- **Tier 1 — Core:** tracked drive (2 motors, skid-steer) · RC over phone (Wi-Fi/BLE
  web UI) · **animated eyes** (the soul — top priority).
- **Tier 2 — Charm:** scoop + dump-bed servos · antenna LEDs + beeps/sounds ·
  petting reaction (touch → happy/purr) · pickup/shake reactions (IMU).
- **Tier 3 — Stretch:** front distance sensor (boop/back-away) · cliff sensors +
  autonomous wander/avoid. *(This is where the ESP32 co-processor may get added for
  encoders / hard-real-time cliff-stop.)*
- **Tier 4 — Nice-to-have:** voice commands ("Cosmos, dance / wiggle / turn in a
  circle / what's the weather"→ shown on face). Speech via **phone-app STT** sending
  parsed commands; weather via a Wi-Fi API call.
- **Tier 5 — v2 stretch:** agentic AI "soul" — cloud LLM receives **summarized**
  state, returns **structured behavior intents**; relationship/memory; idle
  "dreaming." No new hardware (Wi-Fi service the Pi talks to).

**Current focus: Tier 1 eyes + the emotion system (§6).**

## 5. Hardware / BOM

Full costed BOM is in `cosmos-bom.xlsx` (core ≈ $228, +stretch ≈ $268). Key parts:

- **Drive:** 2× N20 6V ~150rpm, metal gearbox + encoder (encoders unused until
  Tier 3) · DRV8833 dual H-bridge.
- **Actuators:** 2× MG90S (scoop lift + wrist) · 1× MG90S/SG90 (dump bed) ·
  **PCA9685** 16-ch I²C servo driver (offloads servo PWM from the Pi).
- **Face:** 2.0" ST7789 (now) → AMOLED (maybe later) · WS2812B/SK6812 for antenna
  tips + accent lights.
- **Sensors:** MPU-6050 (or LSM6DS3) 6-axis IMU (I²C) · **MPR121** capacitive touch
  (I²C) for petting.
- **Audio:** MAX98357A I²S amp + 8Ω speaker (alt: DFPlayer Mini for easy SD clips).
- **Power:** 2S LiPo 2200mAh · 5V/5A buck · bulk caps on servo rail · switch +
  connectors · 2S charge board (no dock).
- **Tier 3+:** VL53L1X front ToF · 4× VL53L0X cliff sensors (I²C) · 2× sub-micro
  antenna-wiggle servos. **Tier 4:** INMP441 I²S mic.

### Pi-only hardware gotchas (important)
The Pi (unlike the ESP32 we're not using) has **no ADC and no native capacitive
touch**. Consequences, already accounted for:
- **Petting → must use the MPR121 (I²C).** No "free" native touch like the ESP32 had.
- **Cliff sensors → use I²C ToF (VL53L0X), not analog IR (TCRT5000)** — avoids
  needing an external ADC.
- Most chosen sensors are I²C/digital (IMU, ToF, MPR121), so the no-ADC limit is fine.

### Owned components (from a parts photo)
ESP32-S3 DevKitC-1 v1.1 (reserve co-pro) · Raspberry Pi Pico/RP2040 (backup MCU) ·
ESP32-CAM (spare) · OV2640 cam (spare) · 2× Arduino Nano clones (spare) · the 2.0"
ST7789 display (prototyping the face now).

## 6. The emotion system (current build focus)

Core idea: **lifelike emotion runs on two timescales**, and we are building both
*local, offline* layers now (A + B). The cloud-LLM "soul" is later (Tier 5).

### Option A — Affect engine (no ML) — BUILD FIRST
How Cozmo/Vector actually work, and ~85% of the "alive" feeling on its own:
- Model mood as a small **valence/arousal** pair plus a few **needs** (attention,
  stimulation, rest).
- **Sensor events nudge** those numbers (petted → +valence; ignored → attention
  need rises; picked up → arousal spike).
- Values **decay/drift over time** so mood evolves on its own when idle — this drift
  is the secret to feeling like it *wants* things, not just reacting.
- Add small **Perlin-noise jitter** so it never reacts identically twice.
- Current mood → picks an **eye expression + movement/sound**.
- Pure Python, offline, instant, free. Runs great headless.

### Option B — TinyML gesture classifier — BUILD SECOND
- **Not an LLM.** A small **TensorFlow Lite** net that classifies
  **pet vs. tap vs. shake vs. pick-up vs. bump** from IMU + touch streams.
- Runs in microseconds; trivial footprint.
- **Train on Cosmos's actual assembled body** (signatures depend on his mass/shape),
  so data collection happens after the chassis exists.
- Makes the reflex layer nuanced ("gentle stroke" vs "grab") and feeds clean events
  into the affect engine.

### Design principle: degrade gracefully
Reflexes (A + B) are **always local and offline** — the lights never fully go out.
Any future cloud layer (Tier 5) sits **on top** and is optional.

### Eye expressions to support (drives the renderer)
happy · sleepy · excited · shy · sad/lonely · curious · confused · heart-eyes ·
blushing · proud · mischievous · searching/thinking · surprised. Eyes carry **all**
emotion (no mouth).

## 7. Mechanical constraints (builder handles these — advise only)

- **Scoop → bed transfer is the hardest geometry.** Layout is scoop-front,
  head-middle, bed-rear. To deposit into the bed, the bucket must **lift up and tip
  backward, clearing the top of the head.**
  - Preferred: **four-bar parallel linkage, 1 servo** (auto-tips the bucket at the
    top of the stroke). Fallback: **2 servos** (lift arm + wrist tip) — start here,
    it's more forgiving.
  - **CAD rule:** bucket must clear the head at full lift. If not → lengthen arm,
    raise pivots, or shorten head.
- **Dump bed:** 1 servo + pushrod linkage (gives the "hydraulic piston" look), tilts
  up at the front like a real dump truck.
- **Treads:** the least forgiving element. Printed TPU can slip / have tension
  issues. Prototype early. Fallback: hidden drive wheels behind a tread-look shell.
- **No head tilt** — solid body/head unit (expression comes from the face, not a
  moving head).
- **Packaging:** biggest space hogs are battery, display, 2 drive motors, servos —
  lay the internal volume out around those five first.

## 8. Software environment & wiring (already set up)

- **OS:** Raspberry Pi OS **Lite 64-bit**, **headless**, SSH enabled. Hostname
  `cosmos` → reachable at `cosmos.local`. **SPI + I²C enabled** via `raspi-config`.
- **Language:** Python. On Bookworm, `pip install ... --break-system-packages` or use
  a venv.
- **Libraries:** `adafruit-blinka`, `adafruit-circuitpython-rgb-display` (ST7789),
  `pigpio` (DMA motor PWM), `rpi_ws281x` (LEDs), Adafruit PCA9685 lib (servos),
  `tflite-runtime` (gesture model), `Pillow` (eye rendering), I²C libs for sensors.
- **Why Pi-only is OK for timing:** PCA9685 handles servo PWM in hardware; pigpio
  gives DMA-timed motor PWM; rpi_ws281x drives LEDs via DMA. If servos twitch or LEDs
  flicker under ML load, that's the Linux-timing tax → signal to add the ESP32.

### ST7789 display wiring (tested working — red/green/blue + cyan crescent eyes)
3.3V logic only. Note the board's naming quirk: **"SDA" = MOSI, "SCL" = clock.**

| Display pin | Pi (BCM) | Physical pin |
|---|---|---|
| VCC | 3.3V | 1 |
| GND | GND | 6 |
| SCL / SCK | GPIO11 (SCLK) | 23 |
| SDA / MOSI | GPIO10 (MOSI) | 19 |
| RES / RST | GPIO25 | 22 |
| DC | GPIO24 | 18 |
| CS | GPIO8 (CE0) | 24 |
| BLK / BL | 3.3V (always on for now) | 17 |

Init that worked: `st7789.ST7789(board.SPI(), width=240, height=320, rotation=90,
cs=CE0, dc=D24, rst=D25, baudrate=24000000)`. If the image is shifted/cut off, tune
`rotation` (0/90/180/270) and add `x_offset`/`y_offset`. If red/blue are swapped,
apply the BGR fix.

## 9. Immediate next steps (suggested order)

1. **Affect engine (Option A)** in Python — mood axes, event→nudge map, decay/drift
   loop, Perlin jitter, mood→expression mapping. Buildable now, before the chassis.
2. **Eye renderer** on the ST7789 — the 13 expressions above, animated (blink,
   transitions). Pillow-drawn or a RoboEyes-style approach.
3. **Wire A → renderer** so mood actually drives the eyes.
4. **Drive + servos + LEDs** control modules (pigpio / PCA9685 / rpi_ws281x).
5. **RC web UI** (Tier 1).
6. **Gesture classifier (Option B)** once the body exists to collect real data.

## 10. Working preferences

- Prioritize **lowest-effort / highest-impact**; cut anything that won't fit 2 months.
- Don't suggest reversing §3 decisions unless asked.
- Don't produce CAD/mechanical parts; give constraints when asked.
- Keep the emotion system **local and offline** for now; cloud is a later, optional layer.
- Prioritize the "feels alive and remembers its owner" experience over spec-sheet power.
