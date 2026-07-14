# RoundyPi Lab

Experiments for the SB Components RoundyPi / Round LCD Board based on RP2040.

This repository turns the RoundyPi into a tiny programmable circular display: clocks, animations, status indicators, Pomodoro timers, creature eyes, and other desktop companions.

## Hardware

- Board: RoundyPi / RP2040
- Display: 1.28 inch round LCD, 240x240
- Controller: GC9A01 / GC9A01A
- Firmware used during development: CircuitPython 10.2.1 for Raspberry Pi Pico

Display pins used by the CircuitPython apps:

| Signal | GPIO |
| --- | --- |
| SCK | GP10 |
| MOSI | GP11 |
| CS | GP9 |
| DC | GP8 |
| RST | GP12 |
| BL | GP13 |

## Repository layout

```text
apps/
  _roundypi.py                     Shared display driver/helpers
  clock.py                         Analog clock
  diagnostic.py                    Long-running stability monitor
  galaxy_animation.py              Animated nebula/particle display
  game_of_life.py                  Conway Game of Life with auto-reseed
  pomodoro.py                      Pomodoro focus timer
  quotes.py                        Inspirational quote display
  creature_eyes.py                 Lightweight robot/creature eyes
  creature_eyes_realistic_saved.py Previous organic eyes version
  status_tamagotchi.py             Status display + tiny coach

install_app.ps1                    Copy an app to CIRCUITPY as code.py
sync_clock.ps1                     Send PC time to the board
pomodoro_control.ps1               Control the Pomodoro over USB serial
status_companion.ps1               Windows GUI for FREE/BUSY/DND/AWAY + coach
flash_when_rp2_appears.ps1         Recovery helper for RPI-RP2 bootloader
watch_roundypi_usb.ps1             USB diagnostic helper
upload_via_serial.ps1              Experimental serial uploader
```

## Installing an app

Plug the RoundyPi in CircuitPython mode. It should appear as `CIRCUITPY`, usually `D:`.

Then run:

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\fgobe\Documents\RoundyPi\install_app.ps1 C:\Users\fgobe\Documents\RoundyPi\apps\game_of_life.py
```

The installer copies:

- the selected app to `D:\code.py`
- `apps\_roundypi.py` to `D:\_roundypi.py` when needed

## Useful commands

Synchronize time for clock/quote apps:

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\fgobe\Documents\RoundyPi\sync_clock.ps1
```

Control the Pomodoro:

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\fgobe\Documents\RoundyPi\pomodoro_control.ps1 reset
powershell -ExecutionPolicy Bypass -File C:\Users\fgobe\Documents\RoundyPi\pomodoro_control.ps1 pause
powershell -ExecutionPolicy Bypass -File C:\Users\fgobe\Documents\RoundyPi\pomodoro_control.ps1 start
```

Launch the Windows status companion:

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\fgobe\Documents\RoundyPi\status_companion.ps1
```

## Notes

- The downloaded CircuitPython `.uf2` firmware is intentionally ignored by Git.
- The active app on the board is always named `code.py`.
- The `apps/` folder is the reusable library.
- Some apps can also receive commands from the PC over USB serial.
