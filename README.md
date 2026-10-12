# wallflow

Live wallpaper that reacts to your music in real time.

Combines PaperRuner (xwinwrap + mpv) with cava's FFT OUTput. Bass hits shift hue + saturation, mids push brightness, video pulses with the beat.

## Install

```bash
git clone https://github.com/Apersonwithtoenail/wallflow.git
cd wallflow
./install.sh
```

## Use

```bash
wallflow                  # auto-picks ~,Videos/LiveWallpapers (prefers *.lite.mp4)
wallflow /path/to/vid.mp4 # custom video
```

Ctrl+C to stop.

## Requires

- xwinwrap
- mpv
- cava
-  xrandr
- PipeWire/PulseAudio with monitor source

## License

MIT
