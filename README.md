# Judge Dredd P-ROC / VPX Bridge

Runs the **JD2 pyprocgame** game engine inside **Visual Pinball X** via a COM bridge, replacing the VPinMAME ROM with full P-ROC game code. Audio, lamps, GI, solenoids, and the DMD all route through the bridge.


## What This Project Changes

### Audio — subprocess sound server

**Problem:** `pythonw.exe` (the COM server host) has no audible audio session in Windows — pygame initialises successfully but the output is silenced by the OS.

**Fix:** `subprocess_sound.py` spawns a hidden `python.exe` child process running `tools/audio_server.py`. All sound commands (play, stop, volume, music) are sent to it via stdin pipe. `python.exe` has a normal audio session and plays audio correctly.

Key files:
- `game/subprocess_sound.py` — drop-in `SoundController` replacement
- `tools/audio_server.py` — standalone pygame audio server

### DMD

**Problem:** The standard pyprocgame `Desktop` renders the DMD in grayscale.

**Fix:** `jd_desktop.py` subclasses `Desktop` and overrides `draw()` to render dots in blue (`R=0, G=brightness/4, B=brightness`) with an ambient floor so unlit dots show as faint blue rather than pure black. The window is titled "Judge Dredd" and set always-on-top.

Key file: `game/jd_desktop.py`

### GI lighting — correct brightness

**Problem:** The VPX table's GI system (`DynamicLamps`) expects WPC GI levels 0–7. The P-ROC reports GI driver state as boolean (`True`/`False`). `True` → integer `1` through COM → `1/7 ≈ 14%` brightness → table plastics appear dim.

**Fix:** `tools/register_vpcom.py` `getGIStates()` now returns `7` (full WPC GI level) when a GI driver is on, and `0` when off.

Key file: `tools/register_vpcom.py` (`getGIStates` method)

### VPX table script — P-ROC mode

The included `.vbs` file has `Const UsePROC = 1` which switches the table from VPinMAME to the VPROC COM controller. Solenoid, lamp, GI, and switch callbacks are all mapped for P-ROC.

---

## File Structure

```
JD2-Proc-VPX/
  README.md
  register_com.bat          — COM server registration (run as Admin)
  game/                     — JD2 pyprocgame source and assets
    jd2.py                  — main game (modified: subprocess sound + blue DMD)
    subprocess_sound.py     — audio via python.exe subprocess
    jd_desktop.py           — blue DMD window subclass
    asset_loader.py
    layers.py
    config/                 — JD.yaml machine config, settings, game data
    my_modes/               — all game mode Python files
    assets/
      dmd/                  — DMD animations
      fonts/                — DMD fonts
      lamps/                — lamp show files
      sound/                — music, sfx, voice callouts
  tools/
    audio_server.py         — pygame audio subprocess server
    register_vpcom.py       — VPROC COM bridge (modified: GI level fix)
  table/
    Judge Dredd Continued (Bally 1993) VPW v1.1.vbs  — VPX table script
```

---

## Known Limitations

- **Attract mode GI:** The game intentionally disables most GI strings during attract mode (real machine behaviour). In VPX this means some playfield plastics are unlit during attract. They illuminate correctly once a game starts.
- **Python 2.7 only:** pyprocgame and the P-ROC pinproc bindings require Python 2.7 32-bit. No Python 3 support.
- **Fake P-ROC driver:** This runs in simulation mode with no physical P-ROC board. Switch inputs come from the VPX keyboard map.
- **Audio latency:** Sound routes through a stdin pipe to a subprocess. There may be slight latency on very rapid sound triggers.

---

## Credits

- **JD2 game code:** Original pyprocgame Judge Dredd implementation
- **VPX table:** Judge Dredd (Bally 1993) VPW v1.1 by V-Pin Workshop
- **VPROC COM bridge:** based on work by destruk, Gerry Stellenberg, and Adam Preble
- **VPX P-ROC integration:** subprocess audio, blue DMD, and GI fix additions
