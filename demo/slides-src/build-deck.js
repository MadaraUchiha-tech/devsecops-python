const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const { applyTheme } = require("/Users/navjeetsingh/.claude/skills/synced/6788ccea-a993-430d-981f-7bc6b0508ff6_e5bc85c5-6a5f-4195-b2f9-9ce7f3359d3f/pptx/scripts/apply_theme.js");
const lu = require("react-icons/lu");

const SHOTS = "/Users/navjeetsingh/projects/devsecops-python/demo/screenshots/";
const OUT = process.argv[2];

// CareSlot brand: deep clinic teal, teal accent, amber highlight (same tokens as the UI)
const THEME = {
  name: "CareSlot",
  headFontFace: "Arial",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1D2A2E", lt1: "FFFFFF", dk2: "0F3D47", lt2: "EEF4F4",
    accent1: "0F6B74", accent2: "E08A1E", accent3: "2E6B3F", accent4: "A63A2B",
    accent5: "2F5D8A", accent6: "5F6B6E", hlink: "0F6B74", folHlink: "2F5D8A",
  },
};
const HEX = THEME.colors;

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "CareSlot - DevSecOps Capstone";
pres.author = "MadaraUchiha-tech";
const C = pres.SchemeColor;

async function icon(Comp, color, size = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Comp, { color: "#" + color, size: String(size) }));
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

pres.defineSlideMaster({
  title: "DARK",
  background: { color: HEX.dk2 },
  objects: [],
  slideNumber: { x: 12.4, y: 6.95, w: 0.6, h: 0.3, color: "9FC3C7", fontSize: 10, align: "right" },
  placeholders: [],
});
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: HEX.lt1 },
  margin: [0.5, 0.6, 0.6, 0.6],
  objects: [
    { text: { text: "CareSlot · DevSecOps capstone", options: { x: 0.6, y: 6.95, w: 6, h: 0.3, fontSize: 10, color: "5F6B6E", margin: 0 } } },
  ],
  slideNumber: { x: 12.4, y: 6.95, w: 0.6, h: 0.3, color: "5F6B6E", fontSize: 10, align: "right" },
  placeholders: [
    { placeholder: { name: "title", type: "title", options: { x: 0.6, y: 0.4, w: 12.1, h: 0.8, fontSize: 32, bold: true, color: C.text2, valign: "middle", margin: 0 } } },
  ],
});

const shadow = () => ({ type: "outer", blur: 8, offset: 3, angle: 90, color: "1D2A2E", opacity: 0.18 });
function shot(slide, file, x, y, w, h, name) {
  slide.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: HEX.lt1 }, line: { color: "D5DEDF", width: 0.75 }, shadow: shadow(), objectName: name + " frame" });
  slide.addImage({ path: SHOTS + file, x: x + 0.04, y: y + 0.04, w: w - 0.08, h: h - 0.08, objectName: name });
}
function sized(file, maxW, maxH, px) {
  const r = px[1] / px[0];
  let w = maxW, h = maxW * r;
  if (h > maxH) { h = maxH; w = maxH / r; }
  return { w, h };
}
function title(slide, text) {
  slide.addText(text, { x: 0.6, y: 0.4, w: 12.1, h: 0.8, fontSize: 30, bold: true, color: HEX.dk2, fontFace: "Arial", valign: "middle", margin: 0, isTextBox: true });
}
function sub(slide, text, y = 1.2) {
  slide.addText(text, { x: 0.6, y, w: 12.1, h: 0.45, fontSize: 16, color: "4B585C", margin: 0, isTextBox: true });
}
function iconRow(slide, img, x, y, head, body, w = 5.6) {
  slide.addShape(pres.shapes.OVAL, { x, y, w: 0.6, h: 0.6, fill: { color: HEX.lt2 }, line: { type: "none" } });
  slide.addImage({ data: img, x: x + 0.14, y: y + 0.14, w: 0.32, h: 0.32 });
  slide.addText([
    { text: head, options: { bold: true, color: HEX.dk1, fontSize: 16, breakLine: true } },
    { text: body, options: { color: "4B585C", fontSize: 14 } },
  ], { x: x + 0.8, y: y - 0.05, w, h: 0.95, valign: "top", margin: 0, isTextBox: true });
}

(async () => {
  const I = {};
  for (const [k, comp] of Object.entries({
    cal: lu.LuCalendarCheck, users: lu.LuUsers, steth: lu.LuStethoscope, ban: lu.LuCalendarX, shield: lu.LuShieldCheck,
    git: lu.LuGitBranch, box: lu.LuContainer, cloud: lu.LuCloud, chart: lu.LuChartLine, test: lu.LuFlaskConical,
    layers: lu.LuLayers, ship: lu.LuShip, bug: lu.LuBug, lock: lu.LuLock, refresh: lu.LuRefreshCw, gauge: lu.LuGauge,
    eye: lu.LuEye, lightbulb: lu.LuLightbulb, server: lu.LuServer, code: lu.LuCode,
  })) I[k] = await icon(comp, HEX.accent1);
  const W = {};
  for (const [k, comp] of Object.entries({ cal: lu.LuCalendarCheck, git: lu.LuGitBranch })) W[k] = await icon(comp, "FFFFFF");

  // 1. Title
  pres.addSection({ title: "Overview" });
  let s = pres.addSlide({ masterName: "DARK", sectionTitle: "Overview" });
  s.addImage({ data: W.cal, x: 0.8, y: 1.2, w: 0.7, h: 0.7 });
  s.addText("CareSlot", { x: 0.8, y: 2.1, w: 6.2, h: 1.1, fontSize: 54, bold: true, color: "FFFFFF", fontFace: "Arial", margin: 0, isTextBox: true });
  s.addText("Clinic appointment scheduling, shipped from laptop to a monitored Kubernetes cluster", { x: 0.8, y: 3.2, w: 5.8, h: 1.0, fontSize: 20, color: "CFE3E3", margin: 0, isTextBox: true });
  s.addText([
    { text: "DevOps Final Capstone · Session 21", options: { breakLine: true } },
    { text: "github.com/MadaraUchiha-tech/devsecops-python" },
  ], { x: 0.8, y: 5.3, w: 6, h: 0.8, fontSize: 14, color: "9FC3C7", margin: 0, isTextBox: true });
  s.addImage({ path: SHOTS + "01-app-schedule-ingress.png", x: 6.9, y: 1.9, w: 5.8, h: 3.63, shadow: shadow() });
  s.addNotes("Hi, I'm <your name>. This is CareSlot, a clinic appointment scheduler, and the DevSecOps pipeline that takes it from my laptop to a monitored Kubernetes cluster.");

  // 2. Problem
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Overview" });
  title(s, "Front desks double-book doctors");
  sub(s, "Small clinics still schedule on paper or shared spreadsheets. CareSlot replaces that with one source of truth.");
  iconRow(s, I.ban, 0.6, 2.1, "Double booking", "Two receptionists book the same doctor at the same time. The API refuses overlapping slots with a 409.");
  iconRow(s, I.users, 0.6, 3.3, "No view of the waiting room", "Check-in, completion, cancellations and no-shows are tracked as a status workflow.");
  iconRow(s, I.steth, 0.6, 4.5, "Uneven doctor workload", "A live workload panel shows upcoming visits per doctor; doctors can go off duty.");
  shot(s, "02-app-double-booking-409.png", 7.2, 2.0, 5.5, 3.44, "Double-booking conflict screenshot");
  s.addText("The booking form rejects a slot that overlaps an existing visit", { x: 7.2, y: 5.55, w: 5.5, h: 0.35, fontSize: 12, italic: true, color: "5F6B6E", margin: 0, isTextBox: true });
  s.addNotes("Small clinics still book on paper or in spreadsheets. Two receptionists can book the same doctor at the same time, and nobody knows who is in the waiting room. CareSlot fixes that; its main rule is that a doctor can never be double-booked.");

  // 3. Application
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Overview" });
  title(s, "The application: React, FastAPI, PostgreSQL");
  const stats = [["16", "REST endpoints across doctors, patients, appointments"], ["21", "pytest cases, 94% line coverage"], ["5", "appointment states with enforced transitions"]];
  stats.forEach(([n, l], i) => {
    const x = 0.6 + i * 2.15;
    s.addText(n, { x, y: 1.5, w: 2.0, h: 0.9, fontSize: 48, bold: true, color: C.accent1, margin: 0, isTextBox: true, fontFace: "Arial" });
    s.addText(l, { x, y: 2.4, w: 1.95, h: 0.9, fontSize: 13, color: "4B585C", margin: 0, valign: "top", isTextBox: true });
  });
  s.addText([
    { text: "SCHEDULED → CHECKED_IN → COMPLETED; cancel or mark no-show along the way", options: { bullet: true, breakLine: true } },
    { text: "Overlapping bookings for a doctor return 409 with the clashing visit", options: { bullet: true, breakLine: true } },
    { text: "Alembic owns the schema; demo data seeded behind a Postgres advisory lock", options: { bullet: true, breakLine: true } },
    { text: "/health (liveness), /ready (DB check), /metrics (Prometheus) for Kubernetes", options: { bullet: true } },
  ], { x: 0.6, y: 3.6, w: 6.2, h: 2.6, fontSize: 15, color: HEX.dk1, paraSpaceAfter: 8, margin: 0, valign: "top", isTextBox: true });
  shot(s, "01-app-schedule-ingress.png", 7.2, 1.45, 5.5, 3.44, "Schedule view");
  shot(s, "06-swagger-docs.png", 9.0, 4.1, 3.7, 2.31, "Swagger docs");
  s.addNotes("React front desk, FastAPI backend, Postgres. Appointments follow a workflow, and a booking that overlaps one the doctor already has comes back as a 409 conflict.");

  // 4. Tech stack
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Overview" });
  title(s, "Tech stack");
  const stack = [
    [I.code, "Application", "React 19 · Vite · FastAPI · SQLAlchemy · Alembic · Postgres 16"],
    [I.test, "Quality", "pytest · pytest-cov · Ruff lint + format"],
    [I.box, "Containers", "Multi-stage Docker · Compose · nginx-unprivileged · non-root"],
    [I.git, "CI/CD", "GitHub Actions · GHCR · SHA-tagged images · kind smoke test"],
    [I.shield, "Security", "Trivy image, secret and IaC scans · SARIF · Pod Security"],
    [I.cloud, "Infrastructure", "Terraform modules · AWS VPC · EKS · IAM · KMS"],
    [I.ship, "Kubernetes", "Helm 3 · ingress-nginx · HPA · Argo CD (GitOps)"],
    [I.chart, "Observability", "kube-prometheus-stack · ServiceMonitor · Grafana"],
  ];
  stack.forEach(([img, h, b], i) => {
    const col = i % 2, row = Math.floor(i / 2);
    iconRow(s, img, 0.6 + col * 6.3, 1.5 + row * 1.3, h, b, 5.0);
  });
  s.addNotes("Read across the layers quickly: app, quality, containers, CI, security, infra, Kubernetes, observability.");

  // 5. Architecture
  pres.addSection({ title: "Pipeline" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Pipeline" });
  title(s, "Architecture: Git is the only way into the cluster");
  const box = (x, y, w, h, t, sub2, fill, txt = HEX.dk1) => {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: fill }, line: { color: fill === "FFFFFF" ? "C9D6D8" : fill, width: 1 } });
    s.addText([{ text: t, options: { bold: true, fontSize: 14, color: txt, breakLine: !!sub2 } }].concat(sub2 ? [{ text: sub2, options: { fontSize: 11, color: txt === HEX.dk1 ? "4B585C" : "CFE3E3" } }] : []),
      { x, y, w, h, align: "center", valign: "middle", margin: 4, isTextBox: true });
  };
  const arrow = (x1, y1, x2, y2) => s.addShape(pres.shapes.LINE, { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1) || 0.001, h: Math.abs(y2 - y1) || 0.001, flipV: y2 < y1, line: { color: "5F6B6E", width: 1.5, endArrowType: "triangle" } });
  box(0.6, 1.6, 1.7, 0.9, "Developer", "git push", HEX.lt2);
  box(2.8, 1.6, 2.2, 0.9, "GitHub Actions", "test · build · scan", HEX.dk2, "FFFFFF");
  box(5.5, 1.6, 1.9, 0.9, "GHCR", "image:<git-sha>", HEX.lt2);
  box(7.9, 1.6, 2.2, 0.9, "Git: values.yaml", "tag ← <git-sha>", HEX.lt2);
  box(10.6, 1.6, 2.1, 0.9, "Argo CD", "auto-sync, self-heal", HEX.accent1, "FFFFFF");
  arrow(2.3, 2.05, 2.8, 2.05); arrow(5.0, 2.05, 5.5, 2.05); arrow(7.4, 2.05, 7.9, 2.05); arrow(10.1, 2.05, 10.6, 2.05);
  // cluster
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 3.6, y: 3.05, w: 9.1, h: 3.45, rectRadius: 0.1, fill: { color: "F7FAFA" }, line: { color: "9FC3C7", width: 1, dashType: "dash" } });
  s.addText("Kubernetes · namespace careslot", { x: 3.8, y: 3.12, w: 5, h: 0.35, fontSize: 12, bold: true, color: C.accent1, margin: 0, isTextBox: true });
  arrow(11.65, 2.5, 11.65, 3.05);
  box(3.9, 3.7, 1.9, 0.8, "Ingress", "/ and /api", "FFFFFF");
  box(6.3, 3.55, 2.4, 0.75, "Frontend ×2", "Nginx, uid 101", "FFFFFF");
  box(6.3, 4.6, 2.4, 0.75, "Backend 2–6", "FastAPI + HPA", "FFFFFF");
  box(9.2, 4.6, 1.9, 0.75, "PostgreSQL", "StatefulSet + PVC", "FFFFFF");
  box(9.2, 5.6, 1.6, 0.7, "Prometheus", null, HEX.lt2);
  box(11.1, 5.6, 1.4, 0.7, "Grafana", null, HEX.lt2);
  arrow(5.8, 3.95, 6.3, 3.9); arrow(5.8, 4.25, 6.3, 4.95); arrow(8.7, 4.97, 9.2, 4.97); arrow(8.7, 5.2, 9.2, 5.85); arrow(10.8, 5.95, 11.1, 5.95);
  box(0.6, 3.7, 2.4, 1.1, "Terraform", "AWS VPC + EKS", HEX.lt2);
  arrow(3.0, 4.25, 3.6, 4.25);
  s.addText("Browser → Ingress. Every change arrives as a Git commit; nobody runs kubectl apply by hand.", { x: 0.6, y: 5.25, w: 2.8, h: 1.2, fontSize: 12, color: "4B585C", margin: 0, valign: "top", isTextBox: true });
  s.addNotes("Push, Actions tests and scans, images go to GHCR tagged with the commit SHA, CI writes that SHA into Git, Argo CD syncs the cluster, Prometheus scrapes, Grafana shows it.");

  // 6. CI/CD
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Pipeline" });
  title(s, "CI/CD: nothing reaches the registry untested or unscanned");
  const stages = [
    ["1  Quality gates", "Ruff + pytest · npm build · terraform validate · helm lint · Trivy secrets"],
    ["2  Build", "Backend and frontend images, tagged with the commit SHA (never latest)"],
    ["3  Trivy gate", "Fail on any fixable HIGH/CRITICAL CVE; SARIF to GitHub Security"],
    ["4  Push", "Only scanned images go to ghcr.io/madarauchiha-tech/careslot-*"],
    ["5  Smoke test", "kind cluster + helm upgrade --install + book a real appointment"],
    ["6  GitOps promote", "CI commits the SHA into values.yaml; Argo CD rolls it out"],
  ];
  stages.forEach(([h, b], i) => {
    const y = 1.45 + i * 0.86;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y, w: 5.6, h: 0.74, rectRadius: 0.06, fill: { color: i === 2 ? "FBEED6" : HEX.lt2 }, line: { type: "none" } });
    s.addText([{ text: h, options: { bold: true, fontSize: 14, color: HEX.dk1, breakLine: true } }, { text: b, options: { fontSize: 12, color: "4B585C" } }],
      { x: 0.75, y, w: 5.35, h: 0.74, valign: "middle", margin: 0, isTextBox: true });
  });
  shot(s, "10-github-actions-run.png", 6.6, 1.45, 6.1, 3.81, "GitHub Actions run");
  s.addText("Run #3: all 8 jobs green in 2m 55s · images in GHCR tagged a4a589b…", { x: 6.6, y: 5.4, w: 6.1, h: 0.35, fontSize: 12, italic: true, color: "5F6B6E", margin: 0, isTextBox: true });
  s.addNotes("Four quality gates run in parallel. The images are built once, Trivy scans them, and only clean images are pushed. Then a throwaway kind cluster installs the chart and books a real appointment before anything is promoted.");

  // 7. DevSecOps
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Pipeline" });
  title(s, "DevSecOps: Trivy blocked a real vulnerability");
  s.addText("7", { x: 0.6, y: 1.4, w: 1.6, h: 1.0, fontSize: 60, bold: true, color: C.accent4, margin: 0, isTextBox: true, fontFace: "Arial" });
  s.addText("HIGH CVEs in the first backend image", { x: 0.6, y: 2.4, w: 2.6, h: 0.6, fontSize: 13, color: "4B585C", margin: 0, isTextBox: true });
  s.addImage({ data: I.shield, x: 3.35, y: 1.75, w: 0.5, h: 0.5 });
  s.addText("0", { x: 4.2, y: 1.4, w: 1.6, h: 1.0, fontSize: 60, bold: true, color: C.accent3, margin: 0, isTextBox: true, fontFace: "Arial" });
  s.addText("fixable HIGH/CRITICAL in both images now", { x: 4.2, y: 2.4, w: 2.6, h: 0.6, fontSize: 13, color: "4B585C", margin: 0, isTextBox: true });
  s.addText([
    { text: "CVE-2025-62727 · Starlette 0.48.0", options: { bold: true, breakLine: true, color: HEX.dk1 } },
    { text: "A request with many overlapping Range headers made Starlette do quadratic work merging them: a few requests could pin a CPU (denial of service). Fixed in 0.49.1.", options: { breakLine: true, color: "4B585C" } },
    { text: "Fix: upgrade FastAPI/Starlette, and strip pip and setuptools (and their vendored urllib3) from the runtime image.", options: { color: "4B585C" } },
  ], { x: 0.6, y: 3.2, w: 6.2, h: 2.2, fontSize: 14, paraSpaceAfter: 6, margin: 0, valign: "top", isTextBox: true });
  s.addText("Also: Trivy secret scan (blocking) · IaC scan led to KMS-encrypted EKS secrets and a read-only Postgres rootfs · non-root pods, all capabilities dropped", { x: 0.6, y: 5.5, w: 6.2, h: 0.9, fontSize: 12, color: "4B585C", margin: 0, valign: "top", isTextBox: true });
  const t1 = sized("43", 5.6, 2.2, [2870, 742]);
  shot(s, "43-trivy-cve-found.png", 7.1, 1.45, t1.w + 0.08, t1.h + 0.08, "Trivy findings before fix");
  const t2 = sized("45", 5.6, 2.6, [2668, 910]);
  shot(s, "45-trivy-ci-backend-clean.png", 7.1, 3.35, t2.w + 0.08, t2.h + 0.08, "Trivy clean after fix");
  s.addNotes("Trivy caught a real one: CVE-2025-62727 in Starlette 0.48, a Range-header denial of service. I upgraded the stack and stripped pip out of the runtime image; both images now scan with zero fixable HIGH or CRITICAL issues.");

  // 8. Infrastructure
  pres.addSection({ title: "Platform" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Platform" });
  title(s, "Infrastructure as Code: VPC + EKS in Terraform");
  // VPC diagram
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 1.45, w: 6.4, h: 4.3, rectRadius: 0.08, fill: { color: "F7FAFA" }, line: { color: HEX.accent1, width: 1.25 } });
  s.addText("VPC 10.20.0.0/16 · ap-south-1", { x: 0.8, y: 1.55, w: 5, h: 0.35, fontSize: 13, bold: true, color: C.accent1, margin: 0, isTextBox: true });
  ["ap-south-1a", "ap-south-1b"].forEach((az, i) => {
    const x = 0.85 + i * 3.1;
    s.addText(az, { x, y: 1.95, w: 2.8, h: 0.3, fontSize: 11, color: "5F6B6E", margin: 0, isTextBox: true });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 2.3, w: 2.8, h: 1.0, rectRadius: 0.05, fill: { color: "E3ECF6" }, line: { type: "none" } });
    s.addText([{ text: "Public subnet", options: { bold: true, breakLine: true } }, { text: `10.20.10${i + 1}.0/24 · ${i === 0 ? "NAT gateway" : "ELB-tagged"}` }], { x, y: 2.3, w: 2.8, h: 1.0, fontSize: 12, color: HEX.dk1, align: "center", valign: "middle", margin: 2, isTextBox: true });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 3.5, w: 2.8, h: 1.0, rectRadius: 0.05, fill: { color: "E2F0E5" }, line: { type: "none" } });
    s.addText([{ text: "Private subnet", options: { bold: true, breakLine: true } }, { text: `10.20.${i + 1}.0/24 · worker nodes` }], { x, y: 3.5, w: 2.8, h: 1.0, fontSize: 12, color: HEX.dk1, align: "center", valign: "middle", margin: 2, isTextBox: true });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.85, y: 4.7, w: 5.9, h: 0.85, rectRadius: 0.05, fill: { color: HEX.dk2 }, line: { type: "none" } });
  s.addText([{ text: "EKS careslot-dev · Kubernetes 1.33", options: { bold: true, breakLine: true } }, { text: "managed node group t3.medium ×2 (max 4) · KMS-encrypted secrets · audit logs" }], { x: 0.85, y: 4.7, w: 5.9, h: 0.85, fontSize: 12, color: "FFFFFF", align: "center", valign: "middle", margin: 2, isTextBox: true });
  s.addText("28", { x: 7.4, y: 1.4, w: 1.6, h: 0.9, fontSize: 54, bold: true, color: C.accent1, margin: 0, isTextBox: true, fontFace: "Arial" });
  s.addText("resources: plan → apply → destroy, all clean", { x: 9.0, y: 1.6, w: 3.7, h: 0.6, fontSize: 14, color: "4B585C", margin: 0, valign: "middle", isTextBox: true });
  s.addText([
    { text: "Two modules (vpc, eks), variables with validation, tfvars.example; no credentials in Git", options: { bullet: true, breakLine: true } },
    { text: "Full lifecycle verified: init, plan, apply, destroy (28 resources)", options: { bullet: true, breakLine: true } },
    { text: "Remote state ready: S3 backend + DynamoDB lock (commented in versions.tf)", options: { bullet: true } },
  ], { x: 7.4, y: 2.45, w: 5.3, h: 1.9, fontSize: 14, color: HEX.dk1, paraSpaceAfter: 6, margin: 0, valign: "top", isTextBox: true });
  const t3 = sized("51", 5.3, 1.75, [2200, 1750]);
  shot(s, "51-aws-vpc-eks-resources.png", 7.4, 4.35, t3.w + 0.08, t3.h + 0.08, "AWS CLI resources");
  s.addNotes("Terraform modules for the VPC and EKS: two public and two private subnets, NAT, a managed node group, KMS-encrypted secrets. I ran plan, apply and destroy, 28 resources each way.");

  // 9. Kubernetes + GitOps
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Platform" });
  title(s, "Kubernetes, Helm and GitOps with Argo CD");
  iconRow(s, I.layers, 0.6, 1.5, "Helm chart", "Deployments ×2, ClusterIP Services, Postgres StatefulSet, Secret, Ingress, HPA, ServiceMonitor, dashboard", 4.8);
  iconRow(s, I.lock, 0.6, 2.75, "Hardened pods", "runAsNonRoot, read-only rootfs, caps dropped, Pod Security baseline, quotas", 4.8);
  iconRow(s, I.refresh, 0.6, 4.0, "Argo CD", "Auto-sync from main, prune, self-heal: a manual scale-down was reverted in seconds", 4.8);
  iconRow(s, I.server, 0.6, 5.25, "Ingress", "careslot.local: / → frontend, /api → FastAPI (ingress-nginx on minikube)", 4.8);
  shot(s, "31-argocd-careslot-tree.png", 6.6, 1.45, 6.1, 3.81, "Argo CD tree");
  const t4 = sized("60", 6.1, 1.0, [2280, 448]);
  shot(s, "60-kubectl-get-pods.png", 6.6, 5.45, t4.w + 0.08, t4.h + 0.08, "kubectl get pods");
  s.addNotes("Helm chart: two replicas each, ClusterIP services, an Ingress that splits / and /api, an HPA from 2 to 6, non-root pods, Pod Security on the namespace. Argo CD does the deploying.");

  // 10. HPA
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Platform" });
  title(s, "Autoscaling under load: 2 → 6 backend pods");
  s.addChart(pres.charts.LINE, [{ name: "Backend pods UP", labels: ["15:12", "15:13", "15:14", "15:15", "15:16", "15:17", "15:18", "15:19", "15:20", "15:21", "15:22", "15:23"], values: [2, 2, 2, 3, 6, 6, 6, 6, 6, 5, 2, 2] }], {
    x: 0.6, y: 1.45, w: 6.0, h: 4.0, chartColors: [HEX.accent1], lineSize: 3, lineDataSymbolSize: 7,
    showTitle: true, title: "Backend pods UP (Prometheus, 1-min steps)", titleFontSize: 13, titleColor: HEX.dk1, titleFontFace: "+mn-lt",
    showValue: true, dataLabelPosition: "t", dataLabelColor: HEX.dk1, dataLabelFontSize: 11, dataLabelFontFace: "+mn-lt",
    valAxisMinVal: 0, valAxisMaxVal: 7, valAxisLabelColor: "5F6B6E", catAxisLabelColor: "5F6B6E", valAxisLabelFontFace: "+mn-lt", catAxisLabelFontFace: "+mn-lt",
    valGridLine: { color: "E1E8E9", size: 0.5 }, catGridLine: { style: "none" }, showLegend: false,
  });
  s.addText("Load test 15:14–15:18 at ~200 req/s (60 workers). CPU peaked at 462% of request vs a 60% target; HPA hit its max of 6, then scaled back to 2 after the 2-minute stabilisation window.", { x: 0.6, y: 5.5, w: 6.0, h: 0.8, fontSize: 12, color: "4B585C", margin: 0, valign: "top", isTextBox: true });
  const t5 = sized("64", 5.9, 4.4, [2786, 1624]);
  shot(s, "64-hpa-scaling.png", 6.8, 1.45, t5.w + 0.08, t5.h + 0.08, "HPA scaling terminal");
  s.addNotes("metrics-server feeds CPU to the HPA. Under 60 concurrent workers the backend went from 2 to 6 pods, the configured maximum; it scales back down after a 2-minute stabilisation window.");

  // 11. Observability
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Platform" });
  title(s, "Observability: Prometheus scrapes, Grafana explains");
  const t6 = sized("22", 7.0, 4.9, [1600, 1120]);
  shot(s, "22-grafana-dashboard.png", 0.6, 1.45, t6.w + 0.08, t6.h + 0.08, "Grafana dashboard");
  const gx = 0.6 + t6.w + 0.4;
  shot(s, "20-prometheus-targets-up.png", gx, 1.45, 12.7 - gx, (12.7 - gx) * 0.625, "Prometheus targets");
  s.addText([
    { text: "ServiceMonitor → 6/6 backend targets UP", options: { bullet: true, breakLine: true } },
    { text: "HTTP rate, p50/p95/p99 latency, 5xx ratio, CPU per pod", options: { bullet: true, breakLine: true } },
    { text: "Business metrics: bookings by specialty, status changes, rejected double-bookings", options: { bullet: true, breakLine: true } },
    { text: "Dashboard ships in the Helm chart (ConfigMap + Grafana sidecar)", options: { bullet: true } },
  ], { x: gx, y: 1.45 + (12.7 - gx) * 0.625 + 0.3, w: 12.7 - gx, h: 2.6, fontSize: 13, color: HEX.dk1, paraSpaceAfter: 6, margin: 0, valign: "top", isTextBox: true });
  s.addNotes("A ServiceMonitor gets Prometheus scraping /metrics. Grafana shows traffic, latency, errors, CPU per pod, and business metrics like bookings by specialty and rejected double-bookings.");

  // 12. Learnings
  pres.addSection({ title: "Wrap-up" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Wrap-up" });
  title(s, "Key learnings");
  const L = [
    [I.bug, "Scanners find real problems", "Trivy failed the very first image on a DoS CVE. The fix was a dependency bump plus a smaller runtime image."],
    [I.refresh, "Starting order is a deployment concern", "Two replicas racing Alembic crash-looped. An advisory lock and a wait-for-db init container fixed it."],
    [I.git, "GitOps makes the cluster boring", "CI writes the SHA to Git; Argo CD does the rest, and kubectl drift is reverted automatically."],
    [I.eye, "Starter code had real bugs", "Ingress pointed at the wrong port, service names didn't match, the HCL didn't parse. Troubleshooting is the job."],
  ];
  L.forEach(([img, h, b], i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = 0.6 + col * 6.2, y = 1.5 + row * 2.45;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 5.9, h: 2.15, rectRadius: 0.08, fill: { color: HEX.lt2 }, line: { type: "none" } });
    s.addImage({ data: img, x: x + 0.3, y: y + 0.3, w: 0.45, h: 0.45 });
    s.addText(h, { x: x + 0.95, y: y + 0.25, w: 4.7, h: 0.55, fontSize: 17, bold: true, color: HEX.dk1, margin: 0, valign: "middle", isTextBox: true });
    s.addText(b, { x: x + 0.3, y: y + 0.95, w: 5.3, h: 1.05, fontSize: 14, color: "4B585C", margin: 0, valign: "top", isTextBox: true });
  });
  s.addNotes("Pick two or three in your own words.");

  // 13. Close
  s = pres.addSlide({ masterName: "DARK", sectionTitle: "Wrap-up" });
  s.addText("Thank you", { x: 0.8, y: 1.6, w: 11, h: 1.0, fontSize: 48, bold: true, color: "FFFFFF", margin: 0, isTextBox: true, fontFace: "Arial" });
  s.addText("Live walkthrough next: code → CI run → Terraform → Argo CD → kubectl → Prometheus → Grafana", { x: 0.8, y: 2.7, w: 11, h: 0.6, fontSize: 20, color: "CFE3E3", margin: 0, isTextBox: true });
  s.addImage({ data: W.git, x: 0.8, y: 4.15, w: 0.45, h: 0.45 });
  s.addText("github.com/MadaraUchiha-tech/devsecops-python", { x: 1.45, y: 4.1, w: 9, h: 0.55, fontSize: 18, color: "FFFFFF", margin: 0, valign: "middle", isTextBox: true });
  s.addText("ghcr.io/madarauchiha-tech/careslot-backend · careslot-frontend", { x: 1.45, y: 4.7, w: 9, h: 0.45, fontSize: 14, color: "9FC3C7", margin: 0, isTextBox: true });
  s.addNotes("Now the live walkthrough.");

  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT);
})();
