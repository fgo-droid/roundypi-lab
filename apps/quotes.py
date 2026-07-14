import time, math, rtc, supervisor, sys
from _roundypi import *

QUOTES = (
    ("OSE COMMENCER", "LE MOUVEMENT CREE LA CLARTE"),
    ("FAIS SIMPLE", "PUIS RENDS LE VIVANT"),
    ("AUJOURD HUI SUFFIT", "UNE BONNE HEURE A LA FOIS"),
    ("LA CURIOSITE", "EST UNE FORME DE COURAGE"),
    ("PETIT PAS", "GRANDE TRAJECTOIRE"),
    ("RESPIRE", "TU AVANCES DEJA"),
    ("RESTE JOUEUR", "C EST SOUVENT LA BONNE PORTE"),
    ("CHOISIS L ELAN", "PAS LA PERFECTION"),
)
buf = ""

def sync():
    global buf
    while supervisor.runtime.serial_bytes_available:
        ch = sys.stdin.read(1)
        if ch in "\r\n":
            cmd = buf.strip(); buf = ""
            if cmd.startswith("TIME,"):
                try:
                    p=[int(v) for v in cmd.split(",")[1:]]
                    rtc.RTC().datetime=time.struct_time((p[0],p[1],p[2],p[3],p[4],p[5],p[6],-1,-1)); print("TIME_OK")
                except Exception: print("TIME_ERROR")
        else:
            buf += ch
            if len(buf) > 80: buf = ""

def scene(hour, frame):
    q = QUOTES[hour % len(QUOTES)]
    phase = frame * 0.035
    bitmap.fill(0); disk(CX,CY,116,1); disk(CX,CY,100,11); disk(CX,CY,74,2)
    ring(112,3,phase,dash=8); ring(93,13,-phase,dash=7); ring(38,9,phase*2)
    disk(CX,43,18,12); disk(CX,43,14,1); draw_centered(pad2(hour)+"H",36,5,1)
    hline(35,205,85,13); hline(35,205,158,3)
    draw_centered(q[0], 103, 6, 2 if text_width(q[0],2) < 198 else 1)
    draw_centered(q[1], 136, 5, 1)
    draw_centered("ROUNDYPI", 185, 4, 1)
    refresh()

last_second = -1; frame = 0
while True:
    sync()
    now = time.localtime()
    if now.tm_sec != last_second:
        scene(now.tm_hour, frame); frame += 1; last_second = now.tm_sec
    time.sleep(0.05)
