import time
import math
from _roundypi import *

# Creature eyes with irregular blinks and pseudo-random emotions.

EMOTIONS = ("CALM", "HAPPY", "CURIOUS", "SLEEPY", "SUSPICIOUS", "SURPRISED")

seed = 12345
emotion = "CALM"
next_emotion_at = 4.0
next_blink_at = 1.0
blink_start = -10
wink_start = -10
blink_duration = 0.14
wink_duration = 0.32
look_x = 0
look_y = 0
target_x = 0
target_y = 0
next_look_at = 1.0


def rnd(max_value):
    global seed
    seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
    return seed % max_value


def rnd_range(low, high):
    return low + rnd(high - low + 1)


def oval(cx, cy, rx, ry, color):
    ry = max(1, ry)
    for y in range(-ry, ry + 1):
        span = int(rx * math.sqrt(max(0, 1 - (y * y) / (ry * ry))))
        hline(cx - span, cx + span, cy + y, color)


def blink_value(t, start, duration):
    if t < start or t > start + duration:
        return 0
    p = (t - start) / duration
    return math.sin(p * math.pi)


def choose_emotion(t):
    global emotion, next_emotion_at
    emotion = EMOTIONS[rnd(len(EMOTIONS))]
    next_emotion_at = t + 3 + rnd(7)
    print("EMOTION", emotion)


def schedule_blink(t):
    global next_blink_at, blink_start, blink_duration, wink_start
    if rnd(8) == 0:
        wink_start = t
    else:
        blink_start = t
    blink_duration = 0.10 + rnd(9) / 100
    # Frequent but still organic. Sometimes a very quick double blink.
    if rnd(5) == 0:
        next_blink_at = t + 0.28 + rnd(18) / 100
    else:
        next_blink_at = t + 0.85 + rnd(260) / 100


def schedule_look(t):
    global target_x, target_y, next_look_at
    if emotion == "SUSPICIOUS":
        target_x = rnd_range(-22, 22)
        target_y = rnd_range(-4, 4)
    elif emotion == "SLEEPY":
        target_x = rnd_range(-8, 8)
        target_y = rnd_range(2, 9)
    elif emotion == "SURPRISED":
        target_x = rnd_range(-5, 5)
        target_y = rnd_range(-8, -2)
    else:
        target_x = rnd_range(-18, 18)
        target_y = rnd_range(-7, 7)
    next_look_at = t + 0.6 + rnd(22) / 10


def ease_eye_motion():
    global look_x, look_y
    look_x = int(look_x * 0.72 + target_x * 0.28)
    look_y = int(look_y * 0.72 + target_y * 0.28)


def eye_shape():
    # Returns base openness and brow tilt.
    if emotion == "HAPPY":
        return 24, -7
    if emotion == "CURIOUS":
        return 31, 9
    if emotion == "SLEEPY":
        return 15, -2
    if emotion == "SUSPICIOUS":
        return 18, 12
    if emotion == "SURPRISED":
        return 36, -12
    return 29, 0


def draw_eye(cx, cy, open_h, dx, dy, emotion_offset):
    eye_rx = 49
    open_h = max(2, open_h)
    oval(cx, cy, eye_rx + 5, open_h + 5, 11)
    oval(cx, cy, eye_rx, open_h, 6)
    if open_h > 8:
        oval(cx - 5, cy - 4, eye_rx - 8, max(3, open_h - 6), 14)
        ix = cx + dx
        iy = cy + dy
        disk(ix, iy, 19, 3)
        disk(ix, iy, 15, 4)
        disk(ix, iy, 11, 13)
        for i in range(8):
            a = math.pi * 2 * i / 8 + emotion_offset
            line(ix, iy, int(ix + math.cos(a) * 16), int(iy + math.sin(a) * 16), 5 if i % 2 else 2)
        pupil = 7 if emotion == "SURPRISED" else 10 if emotion == "SLEEPY" else 9
        disk(ix, iy, pupil, 0)
        disk(ix - 6, iy - 7, 4, 14)
        disk(ix - 2, iy - 3, 2, 6)

    # Strong lids when nearly closed.
    if open_h < 12:
        line(cx - eye_rx, cy, cx + eye_rx, cy, 5, 2)


def mouth(y, color):
    if emotion == "HAPPY":
        pixel(CX-8,y, color); pixel(CX-5,y+2,color); pixel(CX,y+3,color); pixel(CX+5,y+2,color); pixel(CX+8,y,color)
    elif emotion == "SURPRISED":
        disk(CX, y+1, 5, color); disk(CX, y+1, 3, 0)
    elif emotion == "SLEEPY":
        hline(CX-7, CX+7, y+2, color)
    elif emotion == "SUSPICIOUS":
        line(CX-9, y+3, CX+9, y-1, color, 1)
    else:
        hline(CX-6, CX+6, y, color)


def draw(frame):
    global next_emotion_at, next_blink_at, next_look_at
    t = time.monotonic()

    if t >= next_emotion_at:
        choose_emotion(t)
    if t >= next_blink_at:
        schedule_blink(t)
    if t >= next_look_at:
        schedule_look(t)
    ease_eye_motion()

    base_open, brow_tilt = eye_shape()
    blink = blink_value(t, blink_start, blink_duration)
    wink = blink_value(t, wink_start, wink_duration)

    right_open = int(base_open * (1 - blink))
    left_open = int(base_open * (1 - max(blink, wink)))

    # Micro expressions.
    breathe = int(math.sin(t * 2.2) * 2)
    right_open += breathe
    left_open += breathe

    bitmap.fill(0)
    disk(CX, CY, 116, 1)
    ring(111, 3, phase=t * 0.08, dash=8)
    ring(97, 12, phase=-t * 0.06, dash=9)

    lx, ly = 73, 111
    rx, ry = 167, 111

    # Brows encode emotion clearly.
    if emotion == "HAPPY":
        line(28, 62, 112, 58, 13, 3)
        line(128, 58, 212, 62, 13, 3)
    elif emotion == "SUSPICIOUS":
        line(30, 58, 112, 68, 13, 4)
        line(128, 68, 210, 58, 13, 4)
    else:
        line(28, 62 + brow_tilt, 112, 58 - brow_tilt, 13, 4)
        line(128, 58 - brow_tilt, 212, 62 + brow_tilt, 13, 4)

    offset = frame * 0.03
    draw_eye(lx, ly, left_open, look_x, look_y, offset)
    draw_eye(rx, ry, right_open, look_x, look_y, offset)

    mouth(173, 5)

    if wink > 0.35:
        label = "WINK"
    elif blink > 0.65:
        label = "BLINK"
    else:
        label = emotion
    draw_centered(label, 204, 5, 1)

    # Heartbeat dot.
    a = frame * 0.17
    disk(int(CX + math.cos(a) * 103), int(CY + math.sin(a) * 103), 3, 10)

    refresh()


choose_emotion(0)
frame = 0
while True:
    draw(frame)
    frame += 1
    time.sleep(0.055)
