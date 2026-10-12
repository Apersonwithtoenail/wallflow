#!/usr/bin/env python3
"""wallflow - music-reactive live wallpaper."""
import os, sys, time, subprocess, socket, json

SOCK = "/tmp/wallflow.sock"
CAVA_CONF = "/tmp/wallflow-cava.conf"
VIDEO = sys.argv[1] if len(sys.argv) > 1 else None
if not VIDEO:
    d = os.path.expanduser("~/Videos/LiveWallpapers")
    if os.path.isdir(d):
        for f in sorted(os.listdir(d)):
            if f.endswith((".mp4",".mkv",".webm")) and "lite" in f:
                VIDEO = os.path.join(d, f); break
        if not VIDEO:
            for f in sorted(os.listdir(d)):
                if f.endswith((".mp4",".mkv",".webm")):
                    VIDEO = os.path.join(d, f); break
if not VIDEO or not os.path.exists(VIDEO):
    print("usage: wallflow <video>"); sys.exit(1)

open(CAVA_CONF,"w").write("""[general]
framerate = 30
bars = 16
[input]
method = pulse
source = auto
[output]
method = raw
raw_target = /dev/stdout
data_format = ascii
ascii_max_range = 100
bar_delimiter = 59
frame_delimiter = 10
""")

def geom():
    try:
        out = subprocess.check_output(["xrandr"], stderr=subprocess.DEVNULL).decode()
        for ln in out.splitlines():
            if " connected" in ln:
                for p in ln.split():
                    if p and p[0].isdigit() and "x" in p:
                        w = p.split("x")[0]
                        h = p.split("x")[1].split("+")[0]
                        return f"{w}x{h}+0+0"
    except: pass
    return "1366x768+0+0"

def start():
    try: os.unlink(SOCK)
    except: pass
    mpv = ["mpv","-wid","WID",
        "--loop","--no-audio","--no-osc","--no-osd-bar",
        "--no-input-default-bindings","--no-border",
        "--really-quiet","--no-config",
        "--panscan=1.0","--hwdec=auto-safe","--vo=gpu",
        "--profile=fast","--cache=no",
        "--demuxer-max-back-bytes=4M","--demuxer-max-bytes=16M",
        "--demuxer-readahead-secs=1","--vd-queue-enable=no",
        "--ao=null","--vd-lavc-threads=2","--framedrop=decoder",
        "--hwdec-extra-frames=16","--gpu-context=x11egl",
        f"--input-ipc-server={SOCK}",
        "--vf=@eq:eq=hue=0:saturation=1:brightness=0",
        VIDEO]
    cmd = ["xwinwrap","-d","-g",geom(),"-ni","-s","-nf","-b","-un","-argb","-fdt","--"] + mpv
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def cava():
    return subprocess.Popen(["cava","-p",CAVA_CONF],
        stdout=subprocess.PIPE, bufsize=1, universal_newlines=True)

def ipc():
    for i in range(200):  # up to 20s
        if os.path.exists(SOCK):
            try:
                s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                s.connect(SOCK)
                return s
            except: pass
        time.sleep(0.1)
    return None

def main():
    print(f"wallpaper: {VIDEO}")
    start()
    sock = ipc()
    if not sock:
        print("failed to connect to mpv IPC")
        subprocess.run(["pkill","-f","xwinwrap"])
        return 1
    print("connected. play music. ctrl+c to stop")
    cv = cava()
    last = 0
    try:
        for line in cv.stdout:
            vals = [int(x) for x in line.strip().split(";") if x.isdigit()]
            if not vals: continue
            now = time.time()
            if now - last < 0.05: continue
            last = now
            bass = min(1.0, sum(vals[:4])/200)
            mid  = min(1.0, sum(vals[4:10])/300)
            treb = min(1.0, sum(vals[10:])/300)
            hue = (bass - treb) * 180
            sat = 1.0 + bass * 1.2
            bri = mid * 0.7 - 0.1
            cmd = json.dumps({"command":["vf","set","@eq",
                f"hue={hue:.1f}:saturation={sat:.2f}:brightness={bri:.2f}"]})+"\n"
            try: sock.sendall(cmd.encode())
            except: pass
    except KeyboardInterrupt: pass
    finally:
        try: cv.terminate()
        except: pass
        subprocess.run(["pkill","-f","xwinwrap"])
        subprocess.run(["pkill","-f","mpv.*-wid"])
        try: os.unlink(SOCK)
        except: pass
    return 0

if __name__ == "__main__":
    sys.exit(main())
