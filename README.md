# Cosmos

A compact, cute, tracked robot companion — think *baby robot + tiny dump truck + emotional pet*. A desk companion designed to feel like a little living presence rather than a tool.

It has a big animated face (glowing cyan eyes on black), two glowing teal antennae, a front scoop that picks up tiny objects, and a rear dump bed they get tipped into.

## Status

Tier 1 focus: animated eyes + the local affect (emotion) engine.

## Repo contents

- [`CLAUDE.md`](CLAUDE.md) — full project context, locked decisions, and roadmap.
- [`cosmos-build-roadmap.md`](cosmos-build-roadmap.md) — build plan.
- `cosmos-bom.xlsx` — costed bill of materials.

> Large 3D assets (`.stl`, `.blend`) are intentionally **not** tracked in git (see `.gitignore`). Use Git LFS if they ever need to live here.

## Hardware (summary)

- **Brain:** Raspberry Pi Zero 2 W (headless Pi OS Lite 64-bit)
- **Drive:** 2× N20 motors, DRV8833 H-bridge, skid-steer tracks
- **Face:** 2.0" ST7789 IPS LCD (cyan eyes, no mouth)
- **Actuators:** MG90S servos via PCA9685 (scoop, wrist, dump bed)
- **Sensors:** MPU-6050 IMU, MPR121 capacitive touch

See [`CLAUDE.md`](CLAUDE.md) for the complete bill of materials and rationale.
