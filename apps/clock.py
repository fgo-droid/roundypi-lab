import time, math, rtc, supervisor, sys
from _roundypi import *

buf = ""

def sync():
    global buf
    while supervisor.runtime.serial_bytes_available:
        ch = sys.stdin.read(1)
        if ch in "\r\n":
            cmd = buf.strip(); buf = ""
            if cmd.startswith("TIME,"):
                try:
                    p = [int(v) for v in cmd.split(",")[1:]]
                    rtc.RTC().datetime = time.struct_time((p[0],p[1],p[2],p[3],p[4],p[5],p[6],-1,-1))
                    print("TIME_OK")
                except Exception:
                    print("TIME_ERROR")
        else:
            buf += ch
            if len(buf) > 80: buf = ""

def hand(a, length, color, width):
    a -= math.pi / 2
    line(CX, CY, int(CX + math.cos(a) * length), int(CY + math.sin(a) * length), color, width)

def face():
    bitmap.fill(0)
    disk(CX, CY, 116, 1)
    disk(CX, CY, 105, 0)
    ring(110, 3)
    for m in range(60):
        a = math.pi * 2 * m / 60 - math.pi / 2
        inner = 94 if m % 5 == 0 else 101
        outer = 107
        line(int(CX+math.cos(a)*inner), int(CY+math.sin(a)*inner),
             int(CX+math.cos(a)*outer), int(CY+math.sin(a)*outer), 6 if m%5==0 else 13, 2 if m%5==0 else 1)

last = -1
while True:
    sync()
    now = time.localtime()
    if now.tm_sec != last:
        face()
        hand((now.tm_hour % 12 + now.tm_min / 60) * math.pi * 2 / 12, 55, 6, 6)
        hand((now.tm_min + now.tm_sec / 60) * math.pi * 2 / 60, 82, 4, 4)
        hand(now.tm_sec * math.pi * 2 / 60, 92, 8, 2)
        disk(CX, CY, 7, 6); disk(CX, CY, 3, 8)
        refresh()
        last = now.tm_sec
    time.sleep(0.02)
