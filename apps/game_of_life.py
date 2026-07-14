import time
from _roundypi import *

# Conway's Game of Life for the RoundyPi.
# Runs on a 48x48 grid, drawn as 5x5 cells on the 240x240 round display.
# When the world dies, stabilizes, or enters a repeated loop, it reseeds itself.

GRID = 48
CELL = 5
MAX_HISTORY = 32
MIN_RESET_GEN = 24

seed = 0xC0D3CAFE
world = [[0 for _ in range(GRID)] for _ in range(GRID)]
next_world = [[0 for _ in range(GRID)] for _ in range(GRID)]
history = []
generation = 0
reset_count = 0
last_hash = -1
same_hash_count = 0


def rnd():
    global seed
    seed = (seed * 1664525 + 1013904223) & 0xFFFFFFFF
    return seed


def inside_round(x, y):
    px = x * CELL + CELL // 2 - CX
    py = y * CELL + CELL // 2 - CY
    return px * px + py * py < 113 * 113


def clear_world():
    for y in range(GRID):
        row = world[y]
        nxt = next_world[y]
        for x in range(GRID):
            row[x] = 0
            nxt[x] = 0


def add_glider(x, y):
    pts = ((1, 0), (2, 1), (0, 2), (1, 2), (2, 2))
    for dx, dy in pts:
        xx = x + dx
        yy = y + dy
        if 0 <= xx < GRID and 0 <= yy < GRID and inside_round(xx, yy):
            world[yy][xx] = 1


def add_blinker(x, y):
    for dx in range(3):
        xx = x + dx
        if 0 <= xx < GRID and 0 <= y < GRID and inside_round(xx, y):
            world[y][xx] = 1


def seed_world():
    global generation, history, reset_count, last_hash, same_hash_count, seed
    clear_world()
    reset_count += 1
    generation = 0
    history = []
    last_hash = -1
    same_hash_count = 0
    seed = (seed + reset_count * 0x9E3779B9 + int(time.monotonic() * 1000)) & 0xFFFFFFFF

    # Random soup, slightly sparse so it stays readable.
    for y in range(GRID):
        for x in range(GRID):
            if inside_round(x, y):
                edge_bias = 1 if 7 < x < GRID - 8 and 7 < y < GRID - 8 else 0
                world[y][x] = 1 if (rnd() % 100) < (23 + edge_bias * 5) else 0

    # Inject a few recognizable movers/oscillators.
    for _ in range(4):
        add_glider(7 + rnd() % 30, 7 + rnd() % 30)
    for _ in range(3):
        add_blinker(5 + rnd() % 36, 5 + rnd() % 36)


def neighbors(x, y):
    n = 0
    for yy in (y - 1, y, y + 1):
        if yy < 0 or yy >= GRID:
            continue
        row = world[yy]
        for xx in (x - 1, x, x + 1):
            if xx < 0 or xx >= GRID or (xx == x and yy == y):
                continue
            n += row[xx]
    return n


def step():
    global generation
    alive = 0
    changed = 0
    h = 2166136261

    for y in range(GRID):
        for x in range(GRID):
            if not inside_round(x, y):
                next_world[y][x] = 0
                continue
            cell = world[y][x]
            n = neighbors(x, y)
            new_cell = 1 if (n == 3 or (cell and n == 2)) else 0
            next_world[y][x] = new_cell
            alive += new_cell
            if new_cell != cell:
                changed += 1
            if new_cell:
                h = ((h ^ (x + y * GRID + generation * 17)) * 16777619) & 0xFFFFFFFF

    for y in range(GRID):
        wr = world[y]
        nr = next_world[y]
        for x in range(GRID):
            wr[x] = nr[x]

    generation += 1
    return alive, changed, h


def draw_cell(x, y, color):
    px = x * CELL
    py = y * CELL
    # Slightly inset cells: readable grid without drawing grid lines.
    for yy in range(py + 1, py + CELL - 1):
        hline(px + 1, px + CELL - 2, yy, color)


def draw_world(alive, changed):
    bitmap.fill(0)
    disk(CX, CY, 116, 1)
    disk(CX, CY, 112, 0)
    ring(114, 3, phase=generation * 0.015, dash=8)

    # Draw live cells.
    for y in range(GRID):
        for x in range(GRID):
            if world[y][x]:
                # Color by quadrant / generation: gives a little biological shimmer.
                color = 4 if (x + y + generation) % 5 else 5
                draw_cell(x, y, color)

    # Center title when reseeding; tiny status otherwise.
    draw_centered("LIFE", 9, 5, 1)
    draw_text("G" + str(generation % 10000), 13, 222, 7, 1)
    draw_text("A" + str(alive), 91, 222, 10, 1)
    draw_text("D" + str(changed), 165, 222, 5, 1)
    refresh()


def should_reset(alive, changed, h):
    global last_hash, same_hash_count, history
    if generation < MIN_RESET_GEN:
        last_hash = h
        return False
    if alive == 0:
        return True
    if changed == 0:
        return True
    if h == last_hash:
        same_hash_count += 1
    else:
        same_hash_count = 0
    last_hash = h
    if same_hash_count >= 3:
        return True
    if h in history:
        return True
    history.append(h)
    if len(history) > MAX_HISTORY:
        history.pop(0)
    return False


seed_world()
alive = 0
changed = 0

while True:
    alive, changed, h = step()
    draw_world(alive, changed)
    if should_reset(alive, changed, h):
        draw_centered("RESEED", 108, 8, 2)
        refresh()
        time.sleep(0.35)
        seed_world()
    time.sleep(0.08)
