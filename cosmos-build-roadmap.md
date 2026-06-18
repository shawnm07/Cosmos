# Cosmos — Build Roadmap

A compact, cute, tracked robot companion (desk companion).
Target build window: **2 months.** Brain: **ESP32-S3** (not a Pi — see below).

> Build philosophy: **body first → drivable → RC → interactive.**
> Features are ranked highest-impact / lowest-effort first. Stop wherever time
> runs out and you still have something wonderful. Everything in Tiers 1–2 runs
> on a single ESP32-S3.

---

## Brain decision: ESP32-S3, no Raspberry Pi

A Pi 5 is overkill and fights the "small and cute" goal — it wants up to 5V/5A,
runs hot enough to need a fan, and is a big board to design a chassis around.

Everything achievable in 2 months (drive, RC, OLED eyes, scoop/dump servos,
petting, pickup reactions, sounds, even voice commands + weather over Wi-Fi)
runs comfortably on an **ESP32-S3**. A Raspberry Pi only earns its place if you
add **camera vision** (face recognition, person-following) — the exact feature
deferred to v2. If vision is ever added later, use a Pi Zero 2 W, never a Pi 5.

---

## Feature priority tiers

| Tier | Feature | Impact | Effort | Verdict |
|---|---|---|---|---|
| **1 — Core** | Tracked drive (2 motors, skid-steer) | High | Med | Foundation |
| **1 — Core** | RC control via phone (Wi-Fi/BLE web UI) | High | Low | Compelling on its own |
| **1 — Core** | Animated OLED eyes | Very high | Low–Med | Cosmos's soul — do not cut |
| **2 — Charm** | Scoop + dump bed servos | High | Med (mech) | Core concept |
| **2 — Charm** | Antenna LEDs + beeps/sounds | High | Low | Big personality per hour |
| **2 — Charm** | Petting reaction (cap touch → happy/purr) | High | Low | Signature trick |
| **2 — Charm** | Pickup/shake reactions (IMU) | Med–High | Low | Nearly free once IMU is in |
| **3 — Stretch** | Front distance sensor (boop / back-away) | Med | Low–Med | If time remains |
| **3 — Stretch** | Cliff sensors + autonomous wander/avoid | Med | High | Hardest to make reliable; attempt last |
| **4 — Nice-to-have** | Voice commands + weather on OLED | High | Med–High | Only if extra time (needs Wi-Fi) |
| **5 — Stretch v2** | Basic AI integration (agentic motor control) | High | Very High | Lowest priority; defer if needed |
| **Cut now** | Camera vision / face recognition / following | High | Very High | Needs a Pi — v2 |
| **Cut now** | Charging dock | Med | Med | Intentionally skipped |

**The realistic 2-month target = all of Tier 1 + Tier 2.** That's a drivable,
RC, big-eyed, scooping, dumping, petting, beeping companion. Tier 3 is gravy.
Tiers 4–5 only if the build runs ahead of schedule.

### Quick-win callout
The single best effort-to-impact item is the **OLED eyes**. Use the ready-made
**FluxGarage RoboEyes** library — Cozmo-style animated moods, blinks, and
expressions on a cheap OLED with almost no custom code. Get this running early;
it's what turns a box on treads into Cosmos.

---

## Tier 4 — Voice commands + weather (nice-to-have)

Cosmos listens for simple spoken commands and reacts. Suggested command set:

- "Cosmos, turn in a circle" → spin in place
- "Cosmos, dance" → choreographed wiggle + LED + eye routine
- "Cosmos, wiggle" → quick body/antenna wiggle
- "Cosmos, what's the weather?" → fetch forecast over Wi-Fi, display on OLED

Implementation notes:
- **Weather** is the easy half: ESP32 hits a weather API over Wi-Fi and renders
  temp/conditions to the OLED. Doable on its own even without speech.
- **Speech** is the hard half. Options, easiest first:
  1. **Phone-app commands** — speech-to-text on the phone, send the parsed
     command to Cosmos over Wi-Fi/BLE. Least work, very reliable.
  2. **Cloud speech** — ESP32 streams mic audio to a cloud STT service, gets
     back text, matches against the command list.
  3. **On-device wake-word + keyword spotting** — hardest; small command
     vocabulary only. Not recommended for a 2-month build.
- Recommended path for v1: **phone-app commands** (option 1). Keeps all the
  hard speech work off the robot.

Requires: mic (or phone), Wi-Fi (built into ESP32-S3), and the existing
motor/LED/OLED subsystems. No new core hardware beyond a mic if going on-device.

---

## Tier 5 — Basic AI integration (lowest priority, stretch v2)

Goal: an AI that has a **direct connection to the motors** and can **improvise
movements it has never run before** by understanding how Cosmos's body works
from live sensor feedback (IMU, motor encoders, etc.).

How it would work:
- ESP32 exposes a small command interface (drive, turn, scoop, dump, wiggle,
  read IMU, read encoders) over Wi-Fi.
- A cloud LLM (e.g. the Anthropic API) is given:
  - a description of Cosmos's body and what each actuator does,
  - live state — IMU orientation, motion, encoder/odometry, stall flags,
  - a natural-language goal ("do a happy spin", "act shy", "wiggle like a
    puppy").
- The LLM generates a **sequence of motor commands**, sends them down, watches
  the resulting sensor feedback, and adjusts — closing the loop so it can
  invent new behaviors from an understanding of the bot rather than canned
  scripts.

Why it's last:
- Needs reliable Wi-Fi + cloud round-trips (latency makes it more "expressive
  performance" than "real-time reflex").
- Should sit **on top of** a safety layer: the ESP32 must always keep local
  limits (don't stall motors, optional cliff-stop) that the AI cannot override.
- Every lower tier must already work, since this just orchestrates them.

No new hardware required beyond what Tiers 1–4 already include — it's a software
layer over the existing command interface.

---

## Bill of materials (rough US prices, hobby quantities)

### Core build — Tier 1 + 2 (the achievable target)

| Component | Phase | Qty | Est. $ |
|---|---|---|---|
| ESP32-S3 dev board (brain) | 1 | 1 | 12 |
| N20 gearmotor, 6V ~150rpm | 1 | 2 | 14 |
| DRV8833 dual motor driver | 1 | 1 | 5 |
| 2S LiPo 1500–2200mAh | 1 | 1 | 14 |
| 5V 3A buck converter | 1 | 1 | 4 |
| Power switch + XT30/JST + wiring | 1 | — | 10 |
| Tracks (printed TPU, or tank-tread kit) | 1 | — | 0–15 |
| MG90S metal-gear servo (scoop + bed) | 2 | 2–3 | 12 |
| 2.42" SSD1309 OLED (or 1.3" SSD1306 ≈ $6) | 1 | 1 | 15 |
| Antenna + accent LEDs (WS2812 + diffused) | 2 | — | 5 |
| MPU-6050 IMU | 2 | 1 | 5 |
| MPR121 cap-touch (or ESP32 native touch = $0) | 2 | 1 | 0–7 |
| DFPlayer Mini + 8Ω speaker (cute sounds) | 2 | 1 | 7 |
| Protoboard / small custom PCB | all | 1 | 8 |
| Misc (screws, bearings, magnets, heat-shrink) | all | — | 12 |
| **Core subtotal** | | | **~$130–145** |

### Tier 3 add-ons (only if time allows)

| Component | Qty | Est. $ |
|---|---|---|
| VL53L1X front ToF distance sensor | 1 | 10 |
| Cliff sensors (4× TCRT5000 IR ≈ $4, or 4× VL53L0X ToF ≈ $20) | 4 | 4–20 |
| Antenna-wiggle micro servos | 2 | 6 |
| **Tier 3 subtotal** | | **~$20–36** |

### Tier 4 add-on (voice)

| Component | Qty | Est. $ |
|---|---|---|
| I2S MEMS mic (INMP441) — only if on-device speech | 1 | 4 |
| *(phone-app command path needs no extra hardware)* | — | 0 |

### Deferred (vision v2, not now)

| Component | Qty | Est. $ |
|---|---|---|
| Pi Zero 2 W | 1 | 15 |
| Camera Module 3 | 1 | 25 |
| Cabling / adapters | — | 10 |
| **v2 subtotal** | | **~$50** |

**Totals:** ~$130 core · ~$160–180 with Tier 3 · comfortably under $200 for the
full achievable robot. Prices are rough US ballpark and fluctuate — treat as
planning numbers.

---

## Mechanical notes (for CAD — solve these before printing)

### Scoop → bed transfer is the hardest geometry
Layout is: **scoop front → head middle → bed rear.** For the scoop to deposit
into the bed, contents must clear the top of the head.

- **Preferred:** mount the scoop on a **four-bar (parallel) linkage** driven by
  one servo, so raising the arms automatically **tips the bucket backward** at
  the top of the stroke, flinging contents rearward over the head into the bed.
  One servo does both lift and dump.
- **Fallback:** two servos — one to raise the arms, one "wrist" to tip the
  bucket.
- **Design rule:** the bucket must clear the top of the head at full extension.
  If it can't, lower/shorten the head or raise the arm pivots.
- The **dump bed** itself is simple: one servo tilts it up at the front, like a
  real dump truck.

### Treads are the least forgiving element on a tight timeline
Printed TPU tracks can be finicky with tension and slip (especially turning on
carpet). Since treads are core to the look:
- Use a proven small tank-tread kit, **or** prototype printed treads in **week 1**
  so problems surface with time to spare.
- Safe fallback: hidden drive wheels behind a tread-look outer shell.

### Packaging
Biggest space hogs, in order: **battery, OLED, the two drive motors, the
servos.** Lay out the internal volume around those five first; the small boards
tuck in anywhere.

---

## Suggested 2-month timeline

| Weeks | Focus |
|---|---|
| 1–2 | CAD + print chassis, mount motors, drive tethered on the bench. **Prototype treads now.** |
| 2–3 | RC over phone working and tuned. |
| 3–5 | OLED eyes integrated and emoting (the soul). |
| 5–6 | Scoop linkage + dump bed working with servos. |
| 6–7 | Petting, pickup/shake reactions, sounds, antenna LEDs, mood state machine. |
| 7–8 | Tier 3 if time → Tier 4 if running ahead → polish, final assembly, finish/paint. Keep buffer; hardware always slips. |

---

## Sensor → personality map (for the mood state machine)

| Behavior | Triggered by |
|---|---|
| Happy / blushing when petted | Capacitive touch → happy/heart eyes + purr |
| Surprised when picked up | IMU lift |
| Dizzy when shaken | IMU shake signature |
| Curious while exploring | distance sensor + wander → curious eyes |
| Confused when stuck | encoder stall vs. motor command mismatch |
| Proud after scoop-and-dump | completion of manipulation routine |
| Lonely if ignored | idle timer with no touch/voice/motion |
| Excited on voice command | parsed command (Tier 4) |

---

## Deferred / explicitly cut for v1
- Camera vision, face recognition, person-following (needs a Pi — v2)
- Charging dock (skipped by choice; everything else comes first)
- On-device wake-word speech (too heavy for the timeline; use phone-app path)
