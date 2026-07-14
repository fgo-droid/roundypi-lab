import board
import busio
import digitalio
import displayio
import fourwire
import busdisplay
import math

WIDTH = 240
HEIGHT = 240
CX = WIDTH // 2
CY = HEIGHT // 2

LCD_SCK = board.GP10
LCD_MOSI = board.GP11
LCD_CS = board.GP9
LCD_DC = board.GP8
LCD_RST = board.GP12
LCD_BL = board.GP13

INIT_SEQUENCE = bytes((
    0xEF, 0, 0xEB, 1, 0x14, 0xFE, 0, 0xEF, 0, 0xEB, 1, 0x14,
    0x84, 1, 0x40, 0x85, 1, 0xFF, 0x86, 1, 0xFF, 0x87, 1, 0xFF,
    0x88, 1, 0x0A, 0x89, 1, 0x21, 0x8A, 1, 0x00, 0x8B, 1, 0x80,
    0x8C, 1, 0x01, 0x8D, 1, 0x01, 0x8E, 1, 0xFF, 0x8F, 1, 0xFF,
    0xB6, 2, 0x00, 0x20, 0x36, 1, 0x08, 0x3A, 1, 0x05,
    0x90, 4, 0x08, 0x08, 0x08, 0x08, 0xBD, 1, 0x06, 0xBC, 1, 0x00,
    0xFF, 3, 0x60, 0x01, 0x04, 0xC3, 1, 0x13, 0xC4, 1, 0x13, 0xC9, 1, 0x22,
    0xBE, 1, 0x11, 0xE1, 2, 0x10, 0x0E, 0xDF, 3, 0x21, 0x0C, 0x02,
    0xF0, 6, 0x45, 0x09, 0x08, 0x08, 0x26, 0x2A,
    0xF1, 6, 0x43, 0x70, 0x72, 0x36, 0x37, 0x6F,
    0xF2, 6, 0x45, 0x09, 0x08, 0x08, 0x26, 0x2A,
    0xF3, 6, 0x43, 0x70, 0x72, 0x36, 0x37, 0x6F,
    0xED, 2, 0x1B, 0x0B, 0xAE, 1, 0x77, 0xCD, 1, 0x63,
    0x70, 9, 0x07, 0x07, 0x04, 0x0E, 0x0F, 0x09, 0x07, 0x08, 0x03,
    0xE8, 1, 0x34,
    0x62, 12, 0x18, 0x0D, 0x71, 0xED, 0x70, 0x70, 0x18, 0x0F, 0x71, 0xEF, 0x70, 0x70,
    0x63, 12, 0x18, 0x11, 0x71, 0xF1, 0x70, 0x70, 0x18, 0x13, 0x71, 0xF3, 0x70, 0x70,
    0x64, 7, 0x28, 0x29, 0xF1, 0x01, 0xF1, 0x00, 0x07,
    0x66, 10, 0x3C, 0x00, 0xCD, 0x67, 0x45, 0x45, 0x10, 0x00, 0x00, 0x00,
    0x67, 10, 0x00, 0x3C, 0x00, 0x00, 0x00, 0x01, 0x54, 0x10, 0x32, 0x98,
    0x74, 7, 0x10, 0x85, 0x80, 0x00, 0x00, 0x4E, 0x00,
    0x98, 2, 0x3E, 0x07, 0x35, 0, 0x21, 0, 0x11, 0x80, 120, 0x29, 0x80, 20,
))

FONT = {
    " ":(0,0,0,0,0), ".":(0,96,96,0,0), ":":(0,54,54,0,0), "/":(96,16,8,4,3), "-":(8,8,8,8,8),
    "A":(126,9,9,9,126), "B":(127,73,73,73,54), "C":(62,65,65,65,34), "D":(127,65,65,34,28),
    "E":(127,73,73,73,65), "F":(127,9,9,9,1), "G":(62,65,73,73,122), "H":(127,8,8,8,127),
    "I":(0,65,127,65,0), "J":(32,64,65,63,1), "K":(127,8,20,34,65), "L":(127,64,64,64,64),
    "M":(127,2,12,2,127), "N":(127,4,8,16,127), "O":(62,65,65,65,62), "P":(127,9,9,9,6),
    "Q":(62,65,81,33,94), "R":(127,9,25,41,70), "S":(38,73,73,73,50), "T":(1,1,127,1,1),
    "U":(63,64,64,64,63), "V":(31,32,64,32,31), "W":(127,32,24,32,127), "X":(99,20,8,20,99),
    "Y":(7,8,112,8,7), "Z":(97,81,73,69,67),
    "0":(62,81,73,69,62), "1":(0,66,127,64,0), "2":(98,81,73,73,70), "3":(34,65,73,73,54),
    "4":(24,20,18,127,16), "5":(39,69,69,69,57), "6":(60,74,73,73,48), "7":(1,113,9,5,3),
    "8":(54,73,73,73,54), "9":(6,73,73,41,30),
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
for i, c in enumerate((0x02030A,0x07122A,0x102B5C,0x173E76,0x29E6C5,0xA8FFF1,0xF7FBFF,0xFFB000,0xFF3045,0x8B5CFF,0x35FF7A,0x17234A,0x24386E,0x35519B,0xFFFFFF,0x000000)):
    palette[i] = c
group = displayio.Group()
group.append(displayio.TileGrid(bitmap, pixel_shader=palette))
display.root_group = group

def pad2(n): return ("0" + str(n))[-2:]
def pixel(x,y,c):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT: bitmap[x,y] = c
def hline(x0,x1,y,c):
    if y < 0 or y >= HEIGHT: return
    if x0 > x1: x0,x1 = x1,x0
    for x in range(max(0,x0), min(WIDTH-1,x1)+1): bitmap[x,y] = c
def line(x0,y0,x1,y1,c,w=1):
    dx=abs(x1-x0); sx=1 if x0<x1 else -1; dy=-abs(y1-y0); sy=1 if y0<y1 else -1; err=dx+dy
    while True:
        r=w//2
        for oy in range(-r,r+1):
            for ox in range(-r,r+1): pixel(x0+ox,y0+oy,c)
        if x0==x1 and y0==y1: return
        e2=err*2
        if e2>=dy: err+=dy; x0+=sx
        if e2<=dx: err+=dx; y0+=sy
def disk(cx,cy,r,c):
    r2=r*r
    for y in range(-r,r+1):
        s2=r2-y*y
        if s2>=0:
            s=int(math.sqrt(s2)); hline(cx-s,cx+s,cy+y,c)
def ring(r,c,phase=0,dash=0):
    last=None
    for i in range(137):
        if dash and (i//dash)%2: last=None; continue
        a=math.pi*2*i/136+phase; x=int(CX+math.cos(a)*r); y=int(CY+math.sin(a)*r)
        if last: line(last[0],last[1],x,y,c)
        last=(x,y)
def arc(r,f,c,w=3):
    f=max(0,min(1,f)); last=None
    for i in range(int(144*f)+1):
        a=-math.pi/2+math.pi*2*i/144; x=int(CX+math.cos(a)*r); y=int(CY+math.sin(a)*r)
        if last: line(last[0],last[1],x,y,c,w)
        last=(x,y)
def char_width(ch,scale): return (4 if ch==" " else 6)*scale
def text_width(text,scale):
    n=0
    for ch in text.upper(): n += char_width(ch,scale)
    return n
def draw_char(ch,x,y,c,scale=1):
    glyph=FONT.get(ch.upper(),FONT[" "])
    for col in range(5):
        bits=glyph[col]
        for row in range(7):
            if bits & (1<<row):
                for yy in range(scale):
                    for xx in range(scale): pixel(x+col*scale+xx,y+row*scale+yy,c)
def draw_text(text,x,y,c,scale=1):
    for ch in text.upper():
        draw_char(ch,x,y,c,scale); x += char_width(ch,scale)
def draw_centered(text,y,c,scale=1):
    draw_text(text,(WIDTH-text_width(text,scale))//2,y,c,scale)
def refresh():
    display.refresh()
