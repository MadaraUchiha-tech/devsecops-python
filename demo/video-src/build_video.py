"""Assemble the CareSlot presentation video: TTS narration + slides + screen recordings."""
import json, os, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
from segments import SEGMENTS, PRON

VOICE, RATE, FPS, W, H = "Samantha", "178", 30, 1920, 1080
BG = "0x0f1d20"
OUT = sys.argv[1]
MAXSPEED = {"hpa.mp4": 99, "ci-watch.mp4": 99, "06-terraform": 2.0, "obs-live": 3.5, "07-tests": 1.5, "heal.mp4": 1.5, "k8s.mp4": 1.3}
os.makedirs("build", exist_ok=True)
only = set(int(x) for x in sys.argv[2:])  # rebuild selected segments only


def run(cmd):
    subprocess.run(cmd, check=True, shell=isinstance(cmd, str))


def dur(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]))


def tts_text(t):
    for k in sorted(PRON, key=len, reverse=True):
        t = re.sub(rf"(?<![\w-]){re.escape(k)}(?![\w-])", PRON[k], t)
    return t


def chip(label, path):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 30, index=1)
    text = f"LIVE  ·  {label}"
    x0, y0, x1, y1 = d.textbbox((0, 0), text, font=f)
    pad_x, pad_y, mx, my = 22, 12, 28, 26
    bw, bh = x1 - x0 + 40 + pad_x, y1 - y0 + 2 * pad_y
    bx, by = mx, H - my - bh
    d.rounded_rectangle((bx, by, bx + bw, by + bh), radius=12, fill=(10, 60, 62, 230))
    d.ellipse((bx + 14, by + bh / 2 - 6, bx + 26, by + bh / 2 + 6), fill=(232, 76, 61, 255))
    d.text((bx + 40 - x0, by + pad_y - y0), text, font=f, fill=(255, 255, 255, 255))
    img.save(path)


srt, t_cursor, parts = [], 0.0, []
for i, (label, vis, text) in enumerate(SEGMENTS, 1):
    seg = f"build/seg{i:02d}.mp4"
    aiff = f"build/seg{i:02d}.aiff"
    if not only or i in only or not os.path.exists(seg):
        run(["say", "-v", VOICE, "-r", RATE, "-o", aiff, tts_text(text)])
    a = dur(aiff)
    T = round(a + 0.9, 3)  # 0.3 s lead-in + 0.6 s tail
    if not only or i in only or not os.path.exists(seg):
        fit = f"scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color={BG},setsar=1"
        if vis[0] == "img":
            vin = ["-loop", "1", "-framerate", str(FPS), "-t", str(T), "-i", vis[1]]
            vf = f"[0:v]{fit}"
        else:
            _, path, ss, to = vis
            c = to - ss
            cap = next((v for k, v in MAXSPEED.items() if k in path), 1.05)
            T = max(T, round(c / cap, 3))
            vin = ["-ss", str(ss), "-t", str(c), "-i", path]
            if c > T:
                vf = f"[0:v]setpts=(PTS-STARTPTS)*{T / c:.5f},fps={FPS},{fit}"
            else:
                vf = f"[0:v]setpts=PTS-STARTPTS,fps={FPS},{fit},tpad=stop_mode=clone:stop_duration={T - c + 0.1:.3f}"
        inputs = vin + ["-i", aiff]
        fc = vf
        if label:
            png = f"build/chip{i:02d}.png"
            chip(label, png)
            inputs += ["-loop", "1", "-i", png]
            fc += "[v0];[v0][2:v]overlay=0:0:shortest=1"
        fc += f",trim=duration={T},fade=t=in:st=0:d=0.25,fade=t=out:st={T - 0.3}:d=0.3,format=yuv420p[v];"
        fc += f"[1:a]aresample=48000,adelay=300|300,apad,atrim=duration={T},afade=t=out:st={T - 0.25}:d=0.25[a]"
        run(["ffmpeg", "-loglevel", "error", "-y", *inputs, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
             "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-r", str(FPS), "-c:a", "aac", "-b:a", "160k", "-ac", "2",
             "-t", str(T), seg])
        print(f"seg{i:02d} {T:6.1f}s  {label or 'slide'}", flush=True)
    real = dur(seg)
    # subtitles: split narration into sentence chunks spread over the audio time
    sents = [s for s in re.split(r"(?<=[.!?])\s+", text) if s]
    total_chars = sum(len(s) for s in sents)
    st = t_cursor + 0.3
    for s in sents:
        d_ = a * len(s) / total_chars
        srt.append((st, st + d_, s))
        st += d_
    t_cursor += real
    parts.append(seg)

with open("build/list.txt", "w") as f:
    f.writelines(f"file '{os.path.abspath(p)}'\n" for p in parts)


def ts(x):
    h, m = divmod(int(x), 3600)
    m, s = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d},{int((x - int(x)) * 1000):03d}"


with open("build/captions.srt", "w") as f:
    for n, (a_, b_, s) in enumerate(srt, 1):
        f.write(f"{n}\n{ts(a_)} --> {ts(b_)}\n{s}\n\n")

run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", "build/list.txt", "-i", "build/captions.srt",
     "-map", "0:v", "-map", "0:a", "-map", "1:s", "-c:v", "copy", "-c:a", "copy", "-c:s", "mov_text",
     "-metadata:s:s:0", "language=eng", "-movflags", "+faststart", OUT])
print(json.dumps({"out": OUT, "seconds": round(dur(OUT), 1), "MB": round(os.path.getsize(OUT) / 1e6, 1)}))
