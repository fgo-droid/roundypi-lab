import time
import math
from _roundypi import *

# Lightweight robot eyes.
# Inspired by simple OLED robot expressions: very fast, readable, expressive.

EMOTIONS = ("IDLE", "HAPPY", "CURIOUS", "SLEEPY", "FOCUS", "SURPRISED", "GRUMPY")

seed = 4242
emotion = "IDLE"
next_emotion = 2.0
next_blink = 1.0
blink_start = -10
blink_dur = 0.12
wink_start = -10
look_x = 0
look_y = 0
target_x = 0
target_y = 0
next_look = 0.7


def rnd(n):
    global seed
    seed = (seed * 1664525 + 1013904223) & 0xFFFFFFFF
    return seed % n


def choose_emotion(t):
    global emotion, next_emotion
    emotion = EMOTIONS[rnd(len(EMOTIONS))]
    next_emotion = t + 2.0 + rnd(50) / 10
    print("ROBOT_EYES", emotion)


def schedule_blink(t):
    global next_blink, blink_start, blink_dur, wink_start
    if rnd(9) == 0:
        wink_start = t
    else:
        blink_start = t
    blink_dur = 0.08 + rnd(7) / 100
    # Sometimes double-blink.
    next_blink = t + (0.22 + rnd(15) / 100 if rnd(5) == 0 else 0.9 + rnd(30) / 10)


def schedule_look(t):
    global target_x, target_y, next_look
    if emotion == "FOCUS":
        target_x, target_y = 0, 0
    elif emotion == "SLEEPY":
        target_x, target_y = rnd(9) - 4, rnd(5) + 2
    elif emotion == "SURPRISED":
        target_x, target_y = rnd(7) - 3, -4
    else:
        target_x, target_y = rnd(31) - 15, rnd(13) - 6
    next_look = t + 0.45 + rnd(22) / 10


def blink_value(t, start, dur):
    if t < start or t > start + dur:
        return 0
    return math.sin(((t - start) / dur) * math.pi)


def rounded_rect(x, y, w, h, r, color):
    hline(x + r, x + w - r, y, color)
    hline(x + r, x + w - r, y + h, color)
    for yy in range(y + 1, y + h):
        if yy < y + r:
            d = y + r - yy
            inset = int(math.sqrt(max(0, r * r - d * d)))
            hline(x + r - inset, x + w - r + inset, yy, color)
        elif yy > y + h - r:
            d = yy - (y + h - r)
            inset = int(math.sqrt(max(0, r * r - d * d)))
            hline(x + r - inset, x + w - r + inset, yy, color)
        else:
            hline(x, x + w, yy, color)


def eye_box(cx, cy, w, h, color):
    rounded_rect(cx - w // 2, cy - h // 2, w, h, min(10, h // 3), color)


def draw_eye(cx, cy, dx, dy, open_factor, side):
    color = 4
    if emotion == "GRUMPY":
        color = 8
    elif emotion == "HAPPY":
        color = 10
    elif emotion == "SURPRISED":
        color = 5
    elif emotion == "FOCUS":
        color = 7

    w = 44
    h = 42
    if emotion == "SURPRISED":
        w, h = 42, 52
    elif emotion == "SLEEPY":
        h = 22
    elif emotion == "FOCUS":
        h = 28
    elif emotion == "HAPPY":
        h = 32

    h = max(3, int(h * open_factor))
    x = cx + dx
    y = cy + dy

    if emotion == "HAPPY":
        # Smiling crescent eye.
        line(x - 23, y + 5, x - 10, y + 16, color, 4)
        line(x - 10, y + 16, x + 10, y + 16, color, 4)
        line(x + 10, y + 16, x + 23, y + 5, color, 4)
    elif emotion == "GRUMPY":
        eye_box(x, y, w, h, color)
        tilt = -12 if side == "L" else 12
        line(x - 26, y - 22 + tilt, x + 26, y - 16 - tilt, 1, 8)
    elif emotion == "CURIOUS":
        eye_box(x, y + (4 if side == "L" else -2), w, h + (8 if side == "L" else -4), color)
    else:
        eye_box(x, y, w, h, color)

    # Inner glow / pupil hint.
    if h > 12 and emotion not in ("HAPPY",):
        eye_box(x, y, max(12, w // 2), max(5, h // 3), 5)


def draw_face(frame):
    global look_x, look_y
    t = time.monotonic()
    bitmap.fill(0)

    # Minimal fast background.
    disk(CX, CY, 116, 0)
    ring(112, 3, phase=frame * 0.015, dash=10)
    ring(101, 12, phase=-frame * 0.011, dash=14)

    # Smooth saccades.
    look_x = int(look_x * 0.65 + target_x * 0.35)
    look_y = int(look_y * 0.65 + target_y * 0.35)

    blink = blink_value(t, blink_start, blink_dur)
    wink = blink_value(t, wink_start, 0.28)
    left_open = max(0.04, 1 - max(blink, wink))
    right_open = max(0.04, 1 - blink)

    # Eye positions breathe a little.
    breathe = int(math.sin(t * 2.4) * 2)
    left_y = 107 + breathe
    right_y = 107 + breathe

    draw_eye(74, left_y, look_x, look_y, left_open, "L")
    draw_eye(166, right_y, look_x, look_y, right_open, "R")

    # Brows / forehead accents.
    if emotion == "GRUMPY":
        line(35, 60, 108, 73, 8, 3)
        line(132, 73, 205, 60, 8, 3)
    elif emotion == "SURPRISED":
        line(45, 58, 103, 50, 5, 2)
        line(137, 50, 195, 58, 5, 2)
    elif emotion == "SLEEPY":
        line(42, 72, 105, 71, 13, 2)
        line(135, 71, 198, 72, 13, 2)
    else:
        line(42, 61, 105, 56, 13, 2)
        line(135, 56, 198, 61, 13, 2)

    # Small mouth / status.
    if emotion == "SURPRISED":
        disk(CX, 172, 5, 5)
        disk(CX, 172, 3, 0)
    elif emotion == "HAPPY":
        line(CX - 12, 168, CX - 5, 174, 10, 2)
        line(CX - 5, 174, CX + 5, 174, 10, 2)
        line(CX + 5, 174, CX + 12, 168, 10, 2)
    elif emotion == "GRUMPY":
        line(CX - 12, 174, CX + 12, 168, 8, 2)
    else:
        hline(CX - 10, CX + 10, 171, 5)

    if wink > 0.35:
        label = "WINK"
    elif blink > 0.65:
        label = "BLINK"
    else:
        label = emotion
    draw_centered(label, 204, 5, 1)

    # Heartbeat pixel: confirms liveness even on subtle expressions.
    a = frame * 0.18
    disk(int(CX + math.cos(a) * 103), int(CY + math.sin(a) * 103), 3, 10)
    refresh()


choose_emotion(0)
frame = 0
while True:
    now = time.monotonic()
    if now >= next_emotion:
        choose_emotion(now)
    if now >= next_blink:
        schedule_blink(now)
    if now >= next_look:
        schedule_look(now)
    draw_face(frame)
    frame += 1
    time.sleep(0.045)
