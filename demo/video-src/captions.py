"""Silent video + burned-in captions on the current (8:43) timeline."""
import importlib.util, os, re, subprocess
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, BG = 1920, 1080, 30, "0x0f1d20"
OUT = "careslot-presentation-captioned.mp4"
os.makedirs("cap", exist_ok=True)

spec = importlib.util.spec_from_file_location("segs", "/Users/navjeetsingh/projects/devsecops-python/demo/video-src/segments.py")
segs = importlib.util.module_from_spec(spec); spec.loader.exec_module(segs)
NARR = {i: t for i, (_, _, t) in enumerate(segs.SEGMENTS, 1)}


def run(c): subprocess.run(c, check=True)
def dur(p): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]))


# ── 1. slides re-rendered with a caption band underneath ──
SLIDE_T = {1: 4, 4: 7, 5: 7, 6: 7, 12: 7, 13: 3}
SW, SH = 1664, 936                      # slide area; leaves a 144 px band at the bottom
enc = ["-c:v", "libx264", "-preset", "medium", "-crf", "22", "-r", str(FPS), "-pix_fmt", "yuv420p", "-an"]
for n in range(1, 14):
    T = SLIDE_T.get(n, 6)
    run(["ffmpeg", "-loglevel", "error", "-y", "-loop", "1", "-framerate", str(FPS), "-t", str(T), "-i", f"slides/s-{n:02d}.png",
         "-vf", f"scale={SW}:{SH}:flags=lanczos,pad={W}:{H}:{(W - SW) // 2}:0:color={BG},setsar=1,"
                f"fade=t=in:st=0:d=0.2,fade=t=out:st={T - 0.25}:d=0.25", *enc, "-t", str(T), f"silent/slide{n:02d}.mp4"])

parts = [l.split("'")[1] for l in open("silent/list.txt")]
starts, t = [], 0.0
for p in parts:
    starts.append(t); t += dur(p)
TOTAL = t

# ── 2. caption text ──
SLIDE_CAPS = {
    1: ["CareSlot: a clinic appointment scheduler, shipped from a laptop to a monitored Kubernetes cluster."],
    2: ["Clinics still book on paper and spreadsheets, so doctors get double-booked.", "CareSlot's core rule: a doctor can never be double-booked."],
    3: ["React front desk, FastAPI backend, PostgreSQL.", "Overlapping bookings are rejected with a 409 conflict."],
    4: ["The stack, layer by layer: application, quality, containers, CI/CD,", "security, infrastructure, Kubernetes and observability."],
    5: ["Push → GitHub Actions tests, scans and builds → images in GHCR tagged with the commit SHA",
         "→ CI writes the SHA into Git → Argo CD syncs the cluster → Prometheus and Grafana watch it."],
    6: ["Four quality gates in parallel, then build, Trivy gate and push to GHCR.",
         "A throwaway kind cluster books a real appointment before anything is promoted."],
    7: ["Trivy blocked the first backend image: 7 HIGH CVEs, including CVE-2025-62727 in Starlette.",
         "Fixed by upgrading and stripping pip. Both images now scan clean."],
    8: ["Terraform modules: a VPC with public and private subnets across two AZs,", "and EKS with a managed node group. Plan, apply, destroy: 28 resources."],
    9: ["Helm chart: 2 replicas each, ClusterIP services, an Ingress for / and /api,", "non-root pods and Pod Security. Argo CD does the deploying."],
    10: ["Under load, the HPA scaled the backend from 2 to 6 pods, then back down."],
    11: ["Prometheus scrapes /metrics through a ServiceMonitor.", "Grafana shows traffic, latency, errors, CPU per pod and booking metrics."],
    12: ["Learnings: scanners find real problems, and start-up order is a deployment concern.", "GitOps keeps the cluster boring, and troubleshooting is the job."],
    13: ["Now the live walkthrough."],
}
CODEBASE_CAPS = [  # (start, end, text) relative to the codebase clip
    (0.4, 10.5, "The repository: backend, frontend, Helm chart, Terraform, Argo CD, monitoring and CI, each in its own folder."),
    (10.5, 15.5, "appointments.py: ALLOWED_TRANSITIONS defines the appointment status workflow."),
    (15.5, 20.5, "_ensure_slot_free is the double-booking rule: any overlap for the same doctor raises a 409."),
    (20.5, 25.5, "conftest.py swaps the database for in-memory SQLite, so tests never touch Postgres."),
    (25.5, 29.5, "Multi-stage Dockerfile. The runtime image runs as non-root user 10001."),
    (29.5, 33.5, "Helm templates: deployments, services, Ingress, HPA, ServiceMonitor and Grafana dashboard."),
    (33.5, 38.5, "Terraform EKS module: IAM roles, KMS key, the cluster and its managed node group."),
    (38.5, 42.5, "Argo CD application: tracks the chart on main with auto-sync, prune and self-heal."),
    (42.5, 48.3, "The CI/CD workflow that runs everything shown next."),
]
FIX = {"H P A": "HPA", "marked skip C I": "marked [skip ci]", "careslot dot local": "careslot.local",
       "the five hundred error ratio": "the 5xx error ratio"}


def chunks(sentence, limit=92):
    """Split a long sentence at commas/colons into caption-sized pieces."""
    if len(sentence) <= limit:
        return [sentence]
    out, cur = [], ""
    for piece in re.split(r"(?<=[,:;])\s+", sentence):
        if cur and len(cur) + 1 + len(piece) > limit:
            out.append(cur); cur = piece
        else:
            cur = f"{cur} {piece}".strip()
    if cur:
        out.append(cur)
    return out


cues = []
for idx, p in enumerate(parts):
    name, s0, d = os.path.basename(p), starts[idx], dur(p)
    if name.startswith("slide"):
        lines = SLIDE_CAPS[int(name[5:7])]
        span = (d - 0.4) / len(lines)
        for k, line in enumerate(lines):
            cues.append((s0 + 0.2 + k * span, s0 + 0.2 + (k + 1) * span, line, "slide"))
    elif name == "codebase.mp4":
        cues += [(s0 + a, s0 + b, txt, "live") for a, b, txt in CODEBASE_CAPS]
    else:
        seg = 19 if name == "cidone.mp4" else int(name[3:5])
        text = NARR[seg]
        for k, v in FIX.items():
            text = text.replace(k, v)
        pieces = [c for s in re.split(r"(?<=[.!?])\s+", text) if s for c in chunks(s)]
        aiff = f"build/seg{seg:02d}.aiff"
        speak = dur(aiff) if seg not in (21, 22) and os.path.exists(aiff) else d - 0.8
        speak = min(speak, d - 0.6)
        total = sum(len(c) for c in pieces)
        t0 = s0 + 0.3
        for c in pieces:
            dt = speak * len(c) / total
            cues.append((t0, t0 + dt, c, "live")); t0 += dt

# ── 3. render cue images and a caption overlay track ──
FONT = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 36, index=0)


def wrap(text, maxw, d):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = f"{cur} {w}".strip()
        if d.textlength(test, font=FONT) <= maxw:
            cur = test
        else:
            lines.append(cur); cur = w
    lines.append(cur)
    return lines


def render(text, kind, path):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    lines = wrap(text, 1500, d)
    lh = 48
    tw = max(d.textlength(l, font=FONT) for l in lines)
    bh = lh * len(lines) + 24
    if kind == "slide":                    # centred in the band under the slide
        by = SH + (H - SH - bh) // 2
    else:                                  # above the LIVE chip
        by = H - 112 - bh
    bx = (W - tw) / 2 - 24
    if kind == "live":
        d.rounded_rectangle((bx, by, bx + tw + 48, by + bh), radius=10, fill=(0, 0, 0, 185))
    for i, l in enumerate(lines):
        lw = d.textlength(l, font=FONT)
        d.text(((W - lw) / 2, by + 12 + i * lh), l, font=FONT, fill=(255, 255, 255, 255))
    img.save(path)


blank = "cap/blank.png"
Image.new("RGBA", (W, H), (0, 0, 0, 0)).save(blank)
lst, cur = [], 0.0
for n, (a, b, text, kind) in enumerate(cues):
    if a > cur + 0.01:
        lst.append((blank, a - cur))
    png = f"cap/c{n:03d}.png"; render(text, kind, png)
    lst.append((png, b - max(a, cur))); cur = b
lst.append((blank, max(TOTAL - cur, 0.1)))
with open("cap/list.txt", "w") as f:
    for p, d in lst:
        f.write(f"file '{os.path.abspath(p)}'\nduration {d:.3f}\n")
    f.write(f"file '{os.path.abspath(lst[-1][0])}'\n")

base = "silent/base.mp4"
run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", "silent/list.txt", "-c", "copy", base])
run(["ffmpeg", "-loglevel", "error", "-y", "-i", base, "-f", "concat", "-safe", "0", "-i", "cap/list.txt",
     "-filter_complex", f"[1:v]fps={FPS},format=rgba[c];[0:v][c]overlay=0:0:eof_action=pass:shortest=0,format=yuv420p[v]",
     "-map", "[v]", "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-r", str(FPS), "-an", "-t", f"{TOTAL:.3f}",
     "-movflags", "+faststart", OUT])


def ts(x):
    h, m = divmod(int(x), 3600); m, s = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d},{int(round((x - int(x)) * 1000)) % 1000:03d}"


with open("careslot-presentation.srt", "w") as f:
    for n, (a, b, text, _) in enumerate(cues, 1):
        f.write(f"{n}\n{ts(a)} --> {ts(b)}\n{text}\n\n")
print(f"cues {len(cues)}  total {TOTAL:.1f}s  out {dur(OUT):.1f}s  {os.path.getsize(OUT) / 1e6:.1f} MB")
