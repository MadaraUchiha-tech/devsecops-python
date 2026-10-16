import subprocess, os, sys
sys.argv = [sys.argv[0], "unused.mp4"]
src = open("build_video.py").read()
exec(src[:src.index("srt, t_cursor, parts")])  # imports, chip(), constants
fit = f"scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color={BG},setsar=1"
enc = ["-c:v", "libx264", "-preset", "medium", "-crf", "22", "-r", str(FPS), "-pix_fmt", "yuv420p", "-an"]
SLIDE_T = {1: 4, 4: 7, 5: 7, 6: 7, 12: 7, 13: 3}
parts = []
def still(n, T):
    out = f"silent/slide{n:02d}.mp4"
    run(["ffmpeg", "-loglevel", "error", "-y", "-loop", "1", "-framerate", str(FPS), "-t", str(T), "-i", f"slides/s-{n:02d}.png",
         "-vf", f"{fit},fade=t=in:st=0:d=0.2,fade=t=out:st={T-0.25}:d=0.25", *enc, "-t", str(T), out])
    return out
def clip(path, label, name):
    out = f"silent/{name}.mp4"; png = f"silent/{name}-chip.png"; chip(label, png)
    T = dur(path)
    run(["ffmpeg", "-loglevel", "error", "-y", "-i", path, "-loop", "1", "-i", png, "-filter_complex",
         f"[0:v]fps={FPS},{fit}[v0];[v0][1:v]overlay=0:0:shortest=1,fade=t=in:st=0:d=0.25,fade=t=out:st={T-0.3}:d=0.3,format=yuv420p[v]",
         "-map", "[v]", *enc, out])
    return out
def strip(i):
    out = f"silent/seg{i:02d}.mp4"
    run(["ffmpeg", "-loglevel", "error", "-y", "-i", f"build/seg{i:02d}.mp4", "-map", "0:v", "-c", "copy", out]); return out
for n in range(1, 14): parts.append(still(n, SLIDE_T.get(n, 6)))
parts.append(clip("clips/codebase.mp4", "Codebase", "codebase"))
for i in range(15, 29):
    parts.append(clip("clips/ci-done.mp4", "CI/CD · result", "cidone") if i == 19 else strip(i))
with open("silent/list.txt", "w") as f: f.writelines(f"file '{os.path.abspath(p)}'\n" for p in parts)
run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", "silent/list.txt", "-c", "copy", "-movflags", "+faststart", "careslot-presentation-v3.mp4"])
t = 0
for p in parts:
    print(f"{int(t)//60}:{int(t)%60:02d} {os.path.basename(p)}"); t += dur(p)
print("total", round(t, 1), "MB", round(os.path.getsize("careslot-presentation-v3.mp4")/1e6, 1))
