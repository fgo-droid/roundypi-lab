import time, math
from _roundypi import *

def comet(a, r, color, tail, size):
    for j in range(7, 0, -1):
        aa = a - j * 0.055
        pixel(int(CX + math.cos(aa) * (r-j)), int(CY + math.sin(aa) * (r-j)), tail)
    disk(int(CX + math.cos(a) * r), int(CY + math.sin(a) * r), size, color)

frame = 0
while True:
    phase = frame * 0.035
    pulse = int((math.sin(frame * 0.08) + 1) * 4)
    bitmap.fill(0)
    disk(CX, CY, 112, 1); disk(CX, CY, 92+pulse, 11); disk(CX, CY, 63, 12)
    for i in range(44):
        a = i * 2.39996 + phase * (0.06 + (i % 5) * 0.01)
        r = 18 + ((i * 37) % 96)
        pixel(int(CX+math.cos(a)*r), int(CY+math.sin(a)*r), 5 if i % 3 else 7)
    ring(108, 3, phase); ring(86+pulse, 9, -phase*1.3); ring(59, 4, phase*1.8); ring(35+pulse//2, 8, -phase*2.2)
    comet(phase*2.1, 82, 5, 3, 3); comet(-phase*1.7+2.1, 67, 8, 9, 2)
    comet(phase*1.25+4.2, 7, 9, 8, 2); comet(-phase*2.6+5.4, 45, 10, 4, 2)
    disk(CX, CY, 18+pulse//2, 9); disk(CX, CY, 12, 8); disk(CX, CY, 6, 6)
    refresh()
    frame += 1
    time.sleep(0.035)
