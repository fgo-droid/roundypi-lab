import time, math, supervisor, sys
from _roundypi import *

FOCUS=25*60; BREAK=5*60; LONG=15*60; BEFORE_LONG=4
mode="FOCUS"; running=True; session=1; duration=FOCUS; remaining=FOCUS; last_tick=int(time.monotonic()); buf=""

def set_mode(m):
    global mode,duration,remaining
    mode=m; duration = FOCUS if m=="FOCUS" else LONG if m=="LONG" else BREAK; remaining=duration
def next_phase():
    global session
    if mode=="FOCUS": set_mode("LONG" if session % BEFORE_LONG == 0 else "BREAK")
    else:
        session = 1 if mode=="LONG" else session + 1
        set_mode("FOCUS")
def command(cmd):
    global running, remaining
    cmd=cmd.strip().upper()
    if cmd in ("START","RESUME"): running=True
    elif cmd=="PAUSE": running=False
    elif cmd=="RESET": remaining=duration; running=True
    elif cmd=="SKIP": next_phase()
    elif cmd in ("FOCUS","BREAK","LONG"): set_mode(cmd); running=True
    if cmd: print("POMODORO",cmd)
def read_usb():
    global buf
    while supervisor.runtime.serial_bytes_available:
        ch=sys.stdin.read(1)
        if ch in "\r\n": command(buf); buf=""
        else:
            buf += ch
            if len(buf)>40: buf=""
def color(): return 8 if mode=="FOCUS" else 9 if mode=="LONG" else 4
def draw(frame):
    c=color(); done=1-(remaining/duration); phase=frame*.08
    bitmap.fill(0); disk(CX,CY,116,1); disk(CX,CY,98,11); ring(110,3,phase,dash=6); ring(91,12,-phase,dash=9)
    arc(103, done, c, 4); disk(CX,39,25,12); disk(CX,39,20,1); draw_centered(mode,32,c,1)
    draw_centered(pad2(remaining//60)+":"+pad2(remaining%60),90,6,3)
    draw_centered("RUNNING" if running else "PAUSED",130,10 if running else 7,1)
    draw_centered("SESSION "+str(session)+"/"+str(BEFORE_LONG),154,5,1)
    draw_centered("USB START PAUSE SKIP",181,4,1); draw_centered("RESET FOCUS BREAK",197,5,1)
    disk(int(CX+math.cos(phase*2)*61), int(CY+math.sin(phase*2)*61), 3, c)
    refresh()
print("ROUNDYPI_POMODORO_READY")
frame=0; last_draw=-1
while True:
    read_usb(); now=int(time.monotonic())
    if now != last_tick:
        elapsed=now-last_tick; last_tick=now
        if running:
            remaining -= elapsed
            if remaining <= 0: next_phase()
    slot=int(time.monotonic()*2)
    if slot != last_draw:
        draw(frame); frame += 1; last_draw=slot
    time.sleep(0.02)
