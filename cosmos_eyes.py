#!/usr/bin/env python3
"""Cosmos — idle eyes renderer.

A RoboEyes-inspired (https://github.com/FluxGarage/RoboEyes) animated-eye
renderer for the 2.0" ST7789 IPS LCD. This is the very first, sensor-free
stage of the emotion system: two glowing cyan eyes that blink on their own and
occasionally look around, so Cosmos already feels alive before any input
sensors are wired up.

What it does (no sensors required):
  * draws two rounded-rectangle cyan eyes on black
  * auto-blinks at randomised intervals
  * idle mode: every few seconds the eyes drift to a new spot ("looking around")
  * occasional happy squint for a bit of charm
  * subtle breathing bob so it's never perfectly still

All animation uses RoboEyes' tweening trick: each frame every value eases
toward its target via `current = (current + target) / 2`, which gives smooth,
springy motion for free.

Run on the Pi:
    python3 cosmos_eyes.py

Preview the geometry on a dev machine (Pillow only, no Pi hardware needed):
    python3 cosmos_eyes.py --still eyes.png

Wiring is per the project's CLAUDE.md (SPI, rotation=90, CE0/D24/D25).
"""

import argparse
import math
import random
import time

from PIL import Image, ImageDraw

# --------------------------------------------------------------------------
# Configuration — tweak these to taste.
# --------------------------------------------------------------------------

# Canvas is landscape because the panel is initialised with rotation=90.
# A 320x240 image is rotated to the panel's native 240x320 by the driver.
WIDTH = 320
HEIGHT = 240

BG_COLOR = (0, 0, 0)            # black background
EYE_COLOR = (0, 255, 255)       # cyan eyes
SWAP_RED_BLUE = False           # set True if colors look wrong (BGR panels)

# Eye geometry (scaled up from RoboEyes' 128x64 defaults for this display).
EYE_W = 95                      # eye width
EYE_H = 95                      # eye height (open)
EYE_RADIUS = 28                 # corner roundness
SPACE_BETWEEN = 40              # gap between the two eyes
BLINK_H = 4                     # eye height when fully closed

# Idle "look around": how far from center the eyes may drift, in pixels.
IDLE_RANGE_X = 38
IDLE_RANGE_Y = 26

# Timing (seconds): base interval + a random extra up to *_VAR.
BLINK_INTERVAL = 2.4
BLINK_VAR = 3.0
IDLE_INTERVAL = 2.2
IDLE_VAR = 3.0
HAPPY_CHANCE = 0.22             # chance an idle move also does a happy squint
HAPPY_HOLD = 1.1                # seconds to hold the happy squint

BREATH_AMPLITUDE = 2.5          # px of gentle vertical bob
BREATH_PERIOD = 4.0            # seconds per breath cycle

FPS = 30                        # target frame rate


# --------------------------------------------------------------------------
# RoboEyes-style animation engine (pure logic, no hardware).
# --------------------------------------------------------------------------

class CosmosEyes:
    """Holds eye state and renders one frame at a time onto a PIL image."""

    def __init__(self):
        # Resting position: both eyes centered as a pair.
        total_w = EYE_W + SPACE_BETWEEN + EYE_W
        self.base_x = (WIDTH - total_w) // 2       # left edge of the left eye
        self.base_y = (HEIGHT - EYE_H) // 2

        # Animated values: *_cur eases toward *_next every frame.
        self.x_cur = self.x_next = 0.0             # horizontal look offset
        self.y_cur = self.y_next = 0.0             # vertical look offset
        self.h_cur = self.h_next = float(EYE_H)    # eye height (for blinking)
        self.happy_cur = self.happy_next = 0.0     # bottom-eyelid offset (0..1)

        self.closing = False                       # mid-blink, eyes shutting

        now = time.monotonic()
        self.next_blink = now + self._rand(BLINK_INTERVAL, BLINK_VAR)
        self.next_idle = now + self._rand(IDLE_INTERVAL, IDLE_VAR)
        self.happy_until = 0.0
        self.start = now

    @staticmethod
    def _rand(base, var):
        return base + random.random() * var

    # -- scheduled autonomous behaviours -----------------------------------

    def _update_schedule(self, now):
        # Auto-blinker.
        if not self.closing and now >= self.next_blink:
            self.closing = True
            self.h_next = BLINK_H

        # Idle "look around": pick a new gentle target offset.
        if now >= self.next_idle:
            self.x_next = random.uniform(-IDLE_RANGE_X, IDLE_RANGE_X)
            self.y_next = random.uniform(-IDLE_RANGE_Y, IDLE_RANGE_Y)
            self.next_idle = now + self._rand(IDLE_INTERVAL, IDLE_VAR)
            if random.random() < HAPPY_CHANCE:
                self.happy_next = 1.0
                self.happy_until = now + HAPPY_HOLD

        # End the happy squint when its hold time is up.
        if self.happy_next > 0 and now >= self.happy_until:
            self.happy_next = 0.0

        # Blink state machine: once shut, reopen.
        if self.closing and self.h_cur <= BLINK_H + 1:
            self.closing = False
            self.h_next = float(EYE_H)
            self.next_blink = now + self._rand(BLINK_INTERVAL, BLINK_VAR)

    # -- per-frame tween + draw --------------------------------------------

    def render(self, now):
        self._update_schedule(now)

        # Ease every animated value toward its target (RoboEyes averaging).
        self.x_cur = (self.x_cur + self.x_next) / 2
        self.y_cur = (self.y_cur + self.y_next) / 2
        self.h_cur = (self.h_cur + self.h_next) / 2
        self.happy_cur = (self.happy_cur + self.happy_next) / 2

        breath = BREATH_AMPLITUDE * math.sin(
            2 * math.pi * (now - self.start) / BREATH_PERIOD
        )

        img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
        draw = ImageDraw.Draw(img)

        # Eye height shrinks for blinks; keep it centered vertically.
        h = max(BLINK_H, self.h_cur)
        y = self.base_y + self.y_cur + breath + (EYE_H - h) / 2

        left_x = self.base_x + self.x_cur
        right_x = left_x + EYE_W + SPACE_BETWEEN

        for ex in (left_x, right_x):
            self._draw_eye(draw, ex, y, h)

        return img

    def _draw_eye(self, draw, x, y, h):
        radius = min(EYE_RADIUS, h / 2)
        draw.rounded_rectangle(
            (x, y, x + EYE_W, y + h),
            radius=radius,
            fill=EYE_COLOR,
        )

        # Happy mood: a black rounded rect rises over the bottom of the eye,
        # carving a smiling lower curve. Offset grows to 50% of eye height.
        if self.happy_cur > 0.01:
            lid = self.happy_cur * 0.5 * h
            ly = y + h - lid
            draw.rounded_rectangle(
                (x - 2, ly, x + EYE_W + 2, y + h + radius),
                radius=radius,
                fill=BG_COLOR,
            )


# --------------------------------------------------------------------------
# Hardware display setup.
# --------------------------------------------------------------------------

def make_display():
    """Initialise the ST7789 per the project's tested wiring (CLAUDE.md)."""
    import board
    import digitalio
    from adafruit_rgb_display import st7789

    cs = digitalio.DigitalInOut(board.CE0)
    dc = digitalio.DigitalInOut(board.D24)
    rst = digitalio.DigitalInOut(board.D25)

    return st7789.ST7789(
        board.SPI(),
        width=240,
        height=320,
        rotation=90,
        cs=cs,
        dc=dc,
        rst=rst,
        baudrate=24000000,
    )


def show(disp, img):
    if SWAP_RED_BLUE:
        r, g, b = img.split()
        img = Image.merge("RGB", (b, g, r))
    disp.image(img)


# --------------------------------------------------------------------------
# Entry points.
# --------------------------------------------------------------------------

def run_still(path):
    """Render a single frame to a PNG (no hardware needed) for previewing."""
    eyes = CosmosEyes()
    # Advance a few frames so tweens settle to the resting pose.
    for _ in range(8):
        img = eyes.render(time.monotonic())
    img.save(path)
    print(f"Saved a preview frame to {path}  ({WIDTH}x{HEIGHT})")


def run_live():
    eyes = CosmosEyes()
    disp = make_display()
    print("Cosmos eyes running. Ctrl-C to stop.")
    frame_time = 1.0 / FPS
    try:
        while True:
            t0 = time.monotonic()
            show(disp, eyes.render(t0))
            dt = time.monotonic() - t0
            if dt < frame_time:
                time.sleep(frame_time - dt)
    except KeyboardInterrupt:
        print("\nStopping. Bye!")


def main():
    parser = argparse.ArgumentParser(description="Cosmos idle eyes")
    parser.add_argument(
        "--still",
        metavar="FILE.png",
        help="render one frame to a PNG and exit (no Pi hardware required)",
    )
    args = parser.parse_args()

    if args.still:
        run_still(args.still)
        return

    try:
        run_live()
    except ImportError as exc:
        raise SystemExit(
            f"Missing hardware library ({exc}).\n"
            "On the Pi install:\n"
            "  sudo pip3 install --break-system-packages \\\n"
            "    adafruit-blinka adafruit-circuitpython-rgb-display pillow\n"
            "Or preview without hardware:  python3 cosmos_eyes.py --still eyes.png"
        )


if __name__ == "__main__":
    main()
