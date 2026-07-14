import board
import busio
import digitalio
import displayio
import fourwire
import busdisplay
import time
import math
import supervisor
import sys


WIDTH = 240
HEIGHT = 240
CX = WIDTH // 2
CY = HEIGHT // 2

# RoundyPi / SB Components (RP2040)
LCD_SCK = board.GP10
LCD_MOSI = board.GP11
LCD_CS = board.GP9
LCD_DC = board.GP8
LCD_RST = board.GP12
LCD_BL = board.GP13

# GC9A01A initialization sequence.
INIT_SEQUENCE = bytes((
    0xEF, 0,
    0xEB, 1, 0x14,
    0xFE, 0, 0xEF, 0,
    0xEB, 1, 0x14,
    0x84, 1, 0x40, 0x85, 1, 0xFF, 0x86, 1, 0xFF, 0x87, 1, 0xFF,
    0x88, 1, 0x0A, 0x89, 1, 0x21, 0x8A, 1, 0x00, 0x8B, 1, 0x80,
    0x8C, 1, 0x01, 0x8D, 1, 0x01, 0x8E, 1, 0xFF, 0x8F, 1, 0xFF,
    0xB6, 2, 0x00, 0x20,
    0x36, 1, 0x08,
    0x3A, 1, 0x05,
    0x90, 4, 0x08, 0x08, 0x08, 0x08,
    0xBD, 1, 0x06, 0xBC, 1, 0x00,
    0xFF, 3, 0x60, 0x01, 0x04,
    0xC3, 1, 0x13, 0xC4, 1, 0x13, 0xC9, 1, 0x22,
    0xBE, 1, 0x11,
    0xE1, 2, 0x10, 0x0E,
    0xDF, 3, 0x21, 0x0C, 0x02,
    0xF0, 6, 0x45, 0x09, 0x08, 0x08, 0x26, 0x2A,
    0xF1, 6, 0x43, 0x70, 0x72, 0x36, 0x37, 0x6F,
    0xF2, 6, 0x45, 0x09, 0x08, 0x08, 0x26, 0x2A,
    0xF3, 6, 0x43, 0x70, 0x72, 0x36, 0x37, 0x6F,
    0xED, 2, 0x1B, 0x0B,
    0xAE, 1, 0x77,
    0xCD, 1, 0x63,
    0x70, 9, 0x07, 0x07, 0x04, 0x0E, 0x0F, 0x09, 0x07, 0x08, 0x03,
    0xE8, 1, 0x34,
    0x62, 12, 0x18, 0x0D, 0x71, 0xED, 0x70, 0x70, 0x18, 0x0F, 0x71, 0xEF, 0x70, 0x70,
    0x63, 12, 0x18, 0x11, 0x71, 0xF1, 0x70, 0x70, 0x18, 0x13, 0x71, 0xF3, 0x70, 0x70,
    0x64, 7, 0x28, 0x29, 0xF1, 0x01, 0xF1, 0x00, 0x07,
    0x66, 10, 0x3C, 0x00, 0xCD, 0x67, 0x45, 0x45, 0x10, 0x00, 0x00, 0x00,
    0x67, 10, 0x00, 0x3C, 0x00, 0x00, 0x00, 0x01, 0x54, 0x10, 0x32, 0x98,
    0x74, 7, 0x10, 0x85, 0x80, 0x00, 0x00, 0x4E, 0x00,
    0x98, 2, 0x3E, 0x07,
    0x35, 0,
    0x21, 0,
    0x11, 0x80, 120,
    0x29, 0x80, 20,
))

FONT = {
    " ": (0, 0, 0, 0, 0), ".": (0, 96, 96, 0, 0), ":": (0, 54, 54, 0, 0), "/": (96, 16, 8, 4, 3), "-": (8, 8, 8, 8, 8),
    "A": (126, 9, 9, 9, 126), "B": (127, 73, 73, 73, 54), "C": (62, 65, 65, 65, 34), "D": (127, 65, 65, 34, 28),
    "E": (127, 73, 73, 73, 65), "F": (127, 9, 9, 9, 1), "G": (62, 65, 73, 73, 122), "H": (127, 8, 8, 8, 127),
    "I": (0, 65, 127, 65, 0), "J": (32, 64, 65, 63, 1), "K": (127, 8, 20, 34, 65), "L": (127, 64, 64, 64, 64),
    "M": (127, 2, 12, 2, 127), "N": (127, 4, 8, 16, 127), "O": (62, 65, 65, 65, 62), "P": (127, 9, 9, 9, 6),
    "Q": (62, 65, 81, 33, 94), "R": (127, 9, 25, 41, 70), "S": (38, 73, 73, 73, 50), "T": (1, 1, 127, 1, 1),
    "U": (63, 64, 64, 64, 63), "V": (31, 32, 64, 32, 31), "W": (127, 32, 24, 32, 127), "X": (99, 20, 8, 20, 99),
    "Y": (7, 8, 112, 8, 7), "Z": (97, 81, 73, 69, 67),
    "0": (62, 81, 73, 69, 62), "1": (0, 66, 127, 64, 0), "2": (98, 81, 73, 73, 70), "3": (34, 65, 73, 73, 54),
    "4": (24, 20, 18, 127, 16), "5": (39, 69, 69, 69, 57), "6": (60, 74, 73, 73, 48), "7": (1, 113, 9, 5, 3),
    "8": (54, 73, 73, 73, 54), "9": (6, 73, 73, 41, 30),
}

STATES = {
    "FREE":  {"color": 10, "title": "FREE", "line": "OK TO TALK", "hint": "AVAILABLE"},
    "BUSY":  {"color": 7, "title": "BUSY", "line": "WORKING", "hint": "PING FIRST"},
    "DND":   {"color": 8, "title": "DND", "line": "DO NOT DISTURB", "hint": "DEEP WORK"},
    "AWAY":  {"color": 9, "title": "AWAY", "line": "BACK SOON", "hint": "NOT AT DESK"},
}

displayio.release_displays()
backlight = digitalio.DigitalInOut(LCD_BL)
backlight.direction = digitalio.Direction.OUTPUT
backlight.value = True

spi = busio.SPI(LCD_SCK, MOSI=LCD_MOSI)
bus = fourwire.FourWire(spi, command=LCD_DC, chip_select=LCD_CS, reset=LCD_RST)
display = busdisplay.BusDisplay(bus, INIT_SEQUENCE, width=WIDTH, height=HEIGHT, auto_refresh=False)

bitmap = displayio.Bitmap(WIDTH, HEIGHT, 16)
palette = displayio.Palette(16)
palette[0] = 0x02030A
palette[1] = 0x07122A
palette[2] = 0x102B5C
palette[3] = 0x173E76
palette[4] = 0x29E6C5
palette[5] = 0xA8FFF1
palette[6] = 0xF7FBFF
palette[7] = 0xFFB000
palette[8] = 0xFF3045
palette[9] = 0x8B5CFF
palette[10] = 0x35FF7A
palette[11] = 0x17234A
palette[12] = 0x24386E
palette[13] = 0x35519B
palette[14] = 0xFFFFFF
palette[15] = 0x000000

group = displayio.Group()
group.append(displayio.TileGrid(bitmap, pixel_shader=palette))
display.root_group = group


def pixel(x, y, color):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        bitmap[x, y] = color


def hline(x0, x1, y, color):
    if y < 0 or y >= HEIGHT:
        return
    if x0 > x1:
        x0, x1 = x1, x0
    x0 = max(0, x0)
    x1 = min(WIDTH - 1, x1)
    for x in range(x0, x1 + 1):
        bitmap[x, y] = color


def line(x0, y0, x1, y1, color, width=1):
    dx = abs(x1 - x0)
    sx = 1 if x0 < x1 else -1
    dy = -abs(y1 - y0)
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        radius = width // 2
        for oy in range(-radius, radius + 1):
            for ox in range(-radius, radius + 1):
                pixel(x0 + ox, y0 + oy, color)
        if x0 == x1 and y0 == y1:
            return
        e2 = err * 2
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def disk(cx, cy, radius, color):
    r2 = radius * radius
    for y in range(-radius, radius + 1):
        span2 = r2 - y * y
        if span2 >= 0:
            span = int(math.sqrt(span2))
            hline(cx - span, cx + span, cy + y, color)


def ring(radius, color, phase=0, dash=0):
    steps = 136
    last_x = 0
    last_y = 0
    have_last = False
    for i in range(steps + 1):
        if dash and (i // dash) % 2 == 1:
            have_last = False
            continue
        a = math.pi * 2 * i / steps + phase
        wobble = int(math.sin(a * 5 + phase * 2) * 2)
        x = int(CX + math.cos(a) * (radius + wobble))
        y = int(CY + math.sin(a) * (radius + wobble))
        if have_last:
            line(last_x, last_y, x, y, color)
        last_x = x
        last_y = y
        have_last = True


def char_width(ch, scale):
    if ch == " ":
        return 4 * scale
    return 6 * scale


def text_width(text, scale):
    total = 0
    for ch in text.upper():
        total += char_width(ch, scale)
    return total


def draw_char(ch, x, y, color, scale=1):
    glyph = FONT.get(ch.upper(), FONT[" "])
    for col in range(5):
        bits = glyph[col]
        for row in range(7):
            if bits & (1 << row):
                px = x + col * scale
                py = y + row * scale
                for yy in range(scale):
                    for xx in range(scale):
                        pixel(px + xx, py + yy, color)


def draw_text(text, x, y, color, scale=1):
    cursor = x
    for ch in text.upper():
        draw_char(ch, cursor, y, color, scale)
        cursor += char_width(ch, scale)


def draw_centered(text, y, color, scale=1):
    x = (WIDTH - text_width(text, scale)) // 2
    draw_text(text, x, y, color, scale)


state = "FREE"
serial_buffer = ""
last_command_age = 0
pet_energy = 3
daily_checkins = 0
quick_wins = 0
focus_boosts = 0
last_pet_event = "READY"


def set_state(new_state):
    global state, last_command_age
    if new_state in STATES:
        state = new_state
        last_command_age = 0
        print("STATUS_OK", state)
    else:
        print("STATUS_UNKNOWN", new_state)


def clamp_energy():
    global pet_energy
    if pet_energy < 0:
        pet_energy = 0
    if pet_energy > 5:
        pet_energy = 5


def pet_checkin():
    global pet_energy, daily_checkins, last_pet_event
    daily_checkins += 1
    pet_energy += 2
    clamp_energy()
    last_pet_event = "CHECKIN OK"
    print("PET_CHECKIN", daily_checkins, "ENERGY", pet_energy)


def pet_focus():
    global pet_energy, focus_boosts, last_pet_event
    focus_boosts += 1
    pet_energy += 1
    clamp_energy()
    last_pet_event = "FOCUS MODE"
    set_state("DND")
    print("PET_FOCUS", focus_boosts, "ENERGY", pet_energy)


def pet_win():
    global pet_energy, quick_wins, last_pet_event
    quick_wins += 1
    pet_energy += 1
    clamp_energy()
    last_pet_event = "QUICK WIN"
    print("PET_WIN", quick_wins, "ENERGY", pet_energy)


def pet_rest():
    global pet_energy, last_pet_event
    pet_energy += 1
    clamp_energy()
    last_pet_event = "RESTED"
    set_state("FREE")
    print("PET_REST", "ENERGY", pet_energy)


def handle_command(command):
    cmd = command.strip().upper()
    if cmd.startswith("STATUS,"):
        cmd = cmd.split(",", 1)[1].strip()
    if cmd in STATES:
        set_state(cmd)
    elif cmd == "CHECKIN":
        pet_checkin()
    elif cmd == "FOCUS":
        pet_focus()
    elif cmd == "WIN" or cmd == "QUICKWIN":
        pet_win()
    elif cmd == "REST":
        pet_rest()
    elif cmd == "PING":
        print("STATUS", state)
    elif cmd:
        print("STATUS_UNKNOWN", cmd)


def read_usb_commands():
    global serial_buffer
    while supervisor.runtime.serial_bytes_available:
        ch = sys.stdin.read(1)
        if ch == "\n" or ch == "\r":
            command = serial_buffer
            serial_buffer = ""
            handle_command(command)
        else:
            serial_buffer += ch
            if len(serial_buffer) > 60:
                serial_buffer = ""


def draw_pet(cx, cy, color, frame):
    bounce = int(math.sin(frame * 0.18) * 2)
    cy += bounce
    body_color = color if pet_energy > 1 else 7
    eye_color = 6

    disk(cx, cy, 20, body_color)
    disk(cx, cy, 15, 1)
    disk(cx, cy, 12, body_color)

    # Ears / antennae.
    line(cx - 13, cy - 15, cx - 20, cy - 25, body_color, 2)
    line(cx + 13, cy - 15, cx + 20, cy - 25, body_color, 2)
    disk(cx - 21, cy - 26, 3, body_color)
    disk(cx + 21, cy - 26, 3, body_color)

    # Eyes.
    disk(cx - 7, cy - 4, 3, eye_color)
    disk(cx + 7, cy - 4, 3, eye_color)

    # Mood mouth.
    if pet_energy >= 4:
        pixel(cx - 5, cy + 7, eye_color)
        pixel(cx - 3, cy + 9, eye_color)
        pixel(cx, cy + 10, eye_color)
        pixel(cx + 3, cy + 9, eye_color)
        pixel(cx + 5, cy + 7, eye_color)
    elif pet_energy >= 2:
        hline(cx - 5, cx + 5, cy + 8, eye_color)
    else:
        pixel(cx - 5, cy + 10, eye_color)
        pixel(cx - 3, cy + 8, eye_color)
        pixel(cx, cy + 7, eye_color)
        pixel(cx + 3, cy + 8, eye_color)
        pixel(cx + 5, cy + 10, eye_color)


def pet_message():
    if daily_checkins == 0:
        return "DO TODAY CHECKIN"
    if quick_wins == 0:
        return "TACKLE A QUICK WIN"
    if state == "DND":
        return "PROTECT FOCUS"
    if pet_energy <= 1:
        return "REST THEN GO"
    return "GOOD MOMENTUM"


def draw_status(frame):
    info = STATES[state]
    color = info["color"]
    phase = frame * 0.06
    pulse = int((math.sin(frame * 0.12) + 1) * 3)

    bitmap.fill(0)
    disk(CX, CY, 116, 1)
    disk(CX, CY, 100, 11)
    disk(CX, CY, 76 + pulse, 2)
    ring(110, color, phase=phase * 0.9, dash=7)
    ring(92, 13, phase=-phase * 0.5, dash=8)
    ring(62, color, phase=phase * 1.4)

    # Traffic light core.
    disk(CX, 74, 37 + pulse, color)
    disk(CX, 74, 27, 1)
    disk(CX, 74, 18 + (pulse // 2), color)
    disk(CX, 74, 7, 6)

    # Status title.
    scale = 4 if len(info["title"]) <= 4 else 3
    draw_centered(info["title"], 106, 6, scale=scale)
    draw_centered(info["line"], 145, color, scale=1)
    draw_centered(info["hint"], 162, 5, scale=1)

    # Tamagotchi-style companion.
    draw_pet(120, 194, color, frame)
    draw_centered(pet_message(), 219, 5, scale=1)
    draw_text("DAY " + str(daily_checkins), 29, 190, 4, scale=1)
    draw_text("WINS " + str(quick_wins), 161, 190, 7, scale=1)

    # Companion hint and heartbeat.
    a = phase * 2
    hx = int(CX + math.cos(a) * 104)
    hy = int(CY + math.sin(a) * 104)
    disk(hx, hy, 3, color)

    display.refresh()


print("ROUNDYPI_STATUS_READY")
print("COMMANDS: FREE BUSY DND AWAY or STATUS,<STATE>")

frame = 0
last_draw = -1

while True:
    read_usb_commands()
    slot = int(time.monotonic() * 2)
    if slot != last_draw:
        draw_status(frame)
        frame += 1
        last_draw = slot
    time.sleep(0.02)
