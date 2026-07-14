import time, gc
from _roundypi import *
try:
    import microcontroller
except ImportError:
    microcontroller = None

def temp():
    try: return str(int(microcontroller.cpu.temperature)) + "C"
    except Exception: return "--C"

start = int(time.monotonic()); loops = 0; frames = 0; fps_count = 0; fps = 0
last = -1; mem_min = gc.mem_free(); gc_runs = 0; last_gc = 0
print("ROUNDYPI_DIAG_START")

while True:
    loops += 1; fps_count += 1
    up = int(time.monotonic()) - start
    if up != last:
        fps = fps_count; fps_count = 0
        if up - last_gc >= 60:
            gc.collect(); gc_runs += 1; last_gc = up
        mem = gc.mem_free(); mem_min = min(mem_min, mem)
        bitmap.fill(0); disk(CX,CY,116,1); disk(CX,CY,101,11)
        ring(110,3,frames*.03,dash=5); ring(88,12,-frames*.02,dash=7)
        a=frames*.25; disk(int(CX+math.cos(a)*93), int(CY+math.sin(a)*93), 4, 10)
        draw_centered("DIAG",25,5,1)
        draw_centered("ROUNDYPI STABILITY",61,6,1)
        draw_text("UP "+pad2(up//3600)+":"+pad2((up//60)%60)+":"+pad2(up%60),39,92,6,2)
        draw_text("FPS "+str(fps),39,120,5,1); draw_text("LOOP "+str(loops%1000000),39,136,5,1)
        draw_text("MEM "+str(mem),39,152,4,1); draw_text("MIN "+str(mem_min),39,168,4,1)
        draw_text("CPU "+temp(),39,184,7,1); draw_text("GC "+str(gc_runs),39,200,9,1)
        refresh()
        print("DIAG UP",up,"FPS",fps,"MEM",mem,"MIN",mem_min,"LOOP",loops)
        frames += 1; last = up
    time.sleep(0.02)
