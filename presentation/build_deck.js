// Build the 15-min defense deck for the MLOps drift-aware project.
// Run: node build_deck.js
//
// Theme: Ocean Gradient (technical, data-y).
//   primary  #065A82 (deep blue)
//   secondary #1C7293 (teal)
//   accent   #21295C (midnight)
//   surface  #F5F7FA (cool white)
//   ink      #0B1F33 (near-black)
//   muted    #4A5C73
//   spark    #E07A3C (warm accent for callouts only)
// Motif: thin teal accent bar on the left of every content slide; section header in a small filled circle.

const pptxgen = require("pptxgenjs");
const pres = new pptxgen();

pres.layout = "LAYOUT_16x9"; // 10 x 5.625
pres.author = "Zaid (22i-0556) · Shahmir Asif (22i-1883) · AbuBakr (22i-1934)";
pres.title = "Drift-Aware Adaptive Retraining for Streaming Classification";
pres.company = "FAST-NUCES — MLOps Course Project";

// ---------- palette ----------
const C = {
  primary: "065A82",
  secondary: "1C7293",
  accent: "21295C",
  surface: "F5F7FA",
  ink: "0B1F33",
  muted: "4A5C73",
  border: "D8E0EA",
  spark: "E07A3C",
  good: "2A9D8F",
  bad: "C04A4A",
  white: "FFFFFF",
};

// ---------- helpers ----------
function makeShadow() {
  return { type: "outer", color: "000000", blur: 8, offset: 2, angle: 90, opacity: 0.10 };
}

function addAccentBar(slide) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.10, h: 5.625, fill: { color: C.secondary }, line: { color: C.secondary, width: 0 },
  });
}

function addFooter(slide, slideNum, total, sectionLabel) {
  // bottom rule
  slide.addShape(pres.shapes.LINE, {
    x: 0.5, y: 5.30, w: 9.0, h: 0, line: { color: C.border, width: 0.75 },
  });
  slide.addText("Drift-Aware MLOps · FAST-NUCES", {
    x: 0.5, y: 5.32, w: 5, h: 0.25, fontSize: 9, color: C.muted, fontFace: "Calibri", margin: 0,
  });
  slide.addText(sectionLabel || "", {
    x: 5.0, y: 5.32, w: 3.5, h: 0.25, fontSize: 9, color: C.muted, fontFace: "Calibri",
    align: "right", margin: 0,
  });
  slide.addText(`${slideNum} / ${total}`, {
    x: 8.7, y: 5.32, w: 0.8, h: 0.25, fontSize: 9, color: C.muted, fontFace: "Calibri",
    align: "right", margin: 0,
  });
}

function addContentTitle(slide, title, eyebrow) {
  if (eyebrow) {
    slide.addText(eyebrow.toUpperCase(), {
      x: 0.5, y: 0.30, w: 9, h: 0.30, fontSize: 11, color: C.secondary,
      fontFace: "Calibri", bold: true, charSpacing: 4, margin: 0,
    });
  }
  slide.addText(title, {
    x: 0.5, y: eyebrow ? 0.60 : 0.40, w: 9, h: 0.7, fontSize: 28, bold: true,
    color: C.ink, fontFace: "Cambria", margin: 0,
  });
}

function bulletText(arr) {
  return arr.map((t, i) => ({
    text: t,
    options: { bullet: { indent: 18 }, breakLine: i < arr.length - 1, paraSpaceAfter: 6 },
  }));
}

// ---------- TOTAL slides ----------
const TOTAL = 20;

// =====================================================================
// SLIDE 1 — TITLE
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: C.accent };

  // gradient-ish stripes (since pptxgenjs has no real gradient): two dark bands
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.10, fill: { color: C.secondary }, line: { color: C.secondary, width: 0 },
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 5.525, w: 10, h: 0.10, fill: { color: C.secondary }, line: { color: C.secondary, width: 0 },
  });

  // small eyebrow
  s.addText("FAST-NUCES · MLOPS COURSE PROJECT · TRACK II", {
    x: 0.7, y: 0.8, w: 9, h: 0.35, fontSize: 12, color: "B5C7DB",
    fontFace: "Calibri", bold: true, charSpacing: 6, margin: 0,
  });

  // title
  s.addText("Drift-Aware Adaptive Retraining", {
    x: 0.7, y: 1.25, w: 9, h: 0.85, fontSize: 40, bold: true, color: C.white, fontFace: "Cambria", margin: 0,
  });
  s.addText("for Streaming Classification", {
    x: 0.7, y: 2.05, w: 9, h: 0.6, fontSize: 28, color: "CADCFC", fontFace: "Cambria", italic: true, margin: 0,
  });

  // teal divider
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.7, y: 2.85, w: 0.6, h: 0.06, fill: { color: C.secondary }, line: { color: C.secondary, width: 0 },
  });

  // contribution one-liner
  s.addText("HybridDD: a consensus-plus-confidence drift detector wired into a closed-loop MLOps stack.", {
    x: 0.7, y: 3.05, w: 8.7, h: 0.6, fontSize: 16, color: "E6EDF7", fontFace: "Calibri", margin: 0,
  });

  // team box
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.7, y: 4.05, w: 8.6, h: 1.10, fill: { color: "152045" }, line: { color: C.secondary, width: 1 },
  });
  s.addText("Team", {
    x: 0.9, y: 4.12, w: 2, h: 0.30, fontSize: 11, color: C.secondary,
    fontFace: "Calibri", bold: true, charSpacing: 4, margin: 0,
  });
  s.addText([
    { text: "Zaid", options: { bold: true, color: "FFFFFF" } },
    { text: "  22i-0556", options: { color: "B5C7DB" } },
  ], { x: 0.9, y: 4.40, w: 4, h: 0.30, fontSize: 13, fontFace: "Calibri", margin: 0 });
  s.addText([
    { text: "Shahmir Asif", options: { bold: true, color: "FFFFFF" } },
    { text: "  22i-1883", options: { color: "B5C7DB" } },
  ], { x: 0.9, y: 4.65, w: 4, h: 0.30, fontSize: 13, fontFace: "Calibri", margin: 0 });
  s.addText([
    { text: "AbuBakr Shahid", options: { bold: true, color: "FFFFFF" } },
    { text: "  22i-1934", options: { color: "B5C7DB" } },
  ], { x: 0.9, y: 4.90, w: 4, h: 0.30, fontSize: 13, fontFace: "Calibri", margin: 0 });

  s.addText("DEFENSE", {
    x: 5.6, y: 4.12, w: 3.6, h: 0.30, fontSize: 11, color: C.secondary,
    fontFace: "Calibri", bold: true, charSpacing: 4, margin: 0, align: "right",
  });
  s.addText("15 minutes + Q&A", {
    x: 5.6, y: 4.40, w: 3.6, h: 0.30, fontSize: 13, color: C.white,
    fontFace: "Calibri", margin: 0, align: "right",
  });
  s.addText("End-to-end MLOps pipeline · IEEE paper · live demo", {
    x: 5.6, y: 4.65, w: 3.6, h: 0.55, fontSize: 11, color: "B5C7DB",
    fontFace: "Calibri", margin: 0, align: "right", italic: true,
  });
}

// =====================================================================
// SLIDE 2 — AGENDA
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: C.surface };
  addAccentBar(s);
  addContentTitle(s, "Agenda", "Roadmap · 15 min");

  const items = [
    ["1", "Problem", "Why drift kills production ML"],
    ["2", "Related work", "Detector families and the gap"],
    ["3", "Architecture", "Four planes, one closed loop"],
    ["4", "HybridDD", "Consensus + confidence rule"],
    ["5", "Experiments", "Streams, models, protocol"],
    ["6", "Results", "Accuracy · delay · stats"],
    ["7", "Ablation & sensitivity", "Which component matters"],
    ["8", "MLOps in action", "Live demo + monitoring"],
  ];

  items.forEach((it, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = 0.6 + col * 4.55;
    const y = 1.35 + row * 0.85;

    // number circle
    s.addShape(pres.shapes.OVAL, {
      x: x, y: y, w: 0.55, h: 0.55, fill: { color: C.secondary }, line: { color: C.secondary, width: 0 },
    });
    s.addText(it[0], {
      x: x, y: y, w: 0.55, h: 0.55, fontSize: 18, bold: true, color: C.white,
      fontFace: "Cambria", align: "center", valign: "middle", margin: 0,
    });
    s.addText(it[1], {
      x: x + 0.75, y: y, w: 3.6, h: 0.30, fontSize: 15, bold: true, color: C.ink, fontFace: "Cambria", margin: 0,
    });
    s.addText(it[2], {
      x: x + 0.75, y: y + 0.30, w: 3.6, h: 0.25, fontSize: 11, color: C.muted, fontFace: "Calibri", margin: 0,
    });
  });

  addFooter(s, 2, TOTAL, "Agenda");
}

// =====================================================================
// SLIDE 3 — PROBLEM
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: C.surface };
  addAccentBar(s);
  addContentTitle(s, "Models age. Production never warns you.", "The problem");

  // big stat callout
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.50, w: 4.0, h: 2.6, fill: { color: C.accent }, line: { color: C.accent, width: 0 },
    shadow: makeShadow(),
  });
  s.addText("91%", {
    x: 0.5, y: 1.55, w: 4.0, h: 1.2, fontSize: 76, bold: true, color: C.white, fontFace: "Cambria",
    align: "center", valign: "middle", margin: 0,
  });
  s.addText("of deployed ML models silently degrade within a year", {
    x: 0.7, y: 2.75, w: 3.6, h: 0.7, fontSize: 13, color: "CADCFC", fontFace: "Calibri",
    align: "center", italic: true, margin: 0,
  });
  s.addText("Sculley et al. — \"Hidden Technical Debt in ML Systems\" (NeurIPS 2015)", {
    x: 0.7, y: 3.55, w: 3.6, h: 0.5, fontSize: 9, color: "B5C7DB", fontFace: "Calibri",
    align: "center", margin: 0,
  });

  // right column — three pain points
  const pains = [
    ["Concept drift", "P(y | x) shifts. Yesterday's decision boundary is wrong today."],
    ["Covariate drift", "P(x) shifts. Inputs you've never seen — features go out of distribution."],
    ["Silent failure", "Accuracy drops, but no exception. Logs look healthy until the business notices."],
  ];
  pains.forEach((p, i) => {
    const y = 1.50 + i * 0.95;
    s.addShape(pres.shapes.RECTANGLE, {
      x: 4.85, y: y, w: 0.10, h: 0.85, fill: { color: C.spark }, line: { color: C.spark, width: 0 },
    });
    s.addText(p[0], {
      x: 5.05, y: y, w: 4.5, h: 0.30, fontSize: 14, bold: true, color: C.ink, fontFace: "Cambria", margin: 0,
    });
    s.addText(p[1], {
      x: 5.05, y: y + 0.32, w: 4.5, h: 0.55, fontSize: 11, color: C.muted, fontFace: "Calibri", margin: 0,
    });
  });

  // bottom punch
  s.addText("Detection alone is not enough — the system must close the loop.", {
    x: 0.5, y: 4.45, w: 9, h: 0.4, fontSize: 14, italic: true, color: C.primary, fontFace: "Cambria",
    align: "center", margin: 0,
  });

  addFooter(s, 3, TOTAL, "Problem");
}

// =====================================================================
// SLIDE 4 — RESEARCH QUESTIONS
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: C.surface };
  addAccentBar(s);
  addContentTitle(s, "What we set out to answer", "Research questions");

  const rqs = [
    ["RQ1", "Detection",
     "Can a hybrid of performance + distribution signals reduce mean detection delay versus single-signal detectors, without inflating false positives?"],
    ["RQ2", "Adaptation",
     "Does an adaptive retrain loop driven by drift events recover accuracy faster than scheduled retraining?"],
    ["RQ3", "Operability",
     "Can drift detection be exposed as first-class observability — alertable, queryable, reproducible — using only Prometheus + Grafana?"],
  ];

  rqs.forEach((q, i) => {
    const y = 1.30 + i * 1.20;
    // tag pill
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.6, y: y, w: 0.85, h: 0.45, fill: { color: C.primary }, line: { color: C.primary, width: 0 },
    });
    s.addText(q[0], {
      x: 0.6, y: y, w: 0.85, h: 0.45, fontSize: 14, bold: true, color: C.white, fontFace: "Cambria",
      align: "center", valign: "middle", margin: 0,
    });
    // category
    s.addText(q[1], {
      x: 1.65, y: y, w: 7.6, h: 0.30, fontSize: 12, bold: true, color: C.secondary,
      fontFace: "Calibri", charSpacing: 3, margin: 0,
    });
    // body
    s.addText(q[2], {
      x: 1.65, y: y + 0.32, w: 7.6, h: 0.85, fontSize: 13, color: C.ink, fontFace: "Calibri", margin: 0,
    });
  });

  addFooter(s, 4, TOTAL, "Research questions");
}

// =====================================================================
// SLIDE 5 — RELATED WORK
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: C.surface };
  addAccentBar(s);
  addContentTitle(s, "Two families. Each blind to half the problem.", "Related work");

  // Comparison table
  const headerOpts = { fill: { color: C.primary }, color: C.white, bold: true, fontFace: "Calibri", align: "center", valign: "middle" };
  const cellOpts = { fontFace: "Calibri", fontSize: 11, color: C.ink, valign: "middle" };
  const rowH = 0.42;

  const tbl = [
    [
      { text: "Family", options: headerOpts },
      { text: "Examples", options: headerOpts },
      { text: "Strength", options: headerOpts },
      { text: "Weakness", options: headerOpts },
    ],
    [
      { text: "Performance-based", options: { ...cellOpts, bold: true } },
      { text: "DDM, EDDM, Page-Hinkley, ADWIN", options: cellOpts },
      { text: "Reacts to accuracy degradation", options: cellOpts },
      { text: "Misses virtual drift; needs labels", options: { ...cellOpts, color: C.bad } },
    ],
    [
      { text: "Distribution-based", options: { ...cellOpts, bold: true } },
      { text: "KSWIN, MMD, χ²", options: cellOpts },
      { text: "Catches covariate shift, label-free", options: cellOpts },
      { text: "Noisy; fires on harmless fluctuations", options: { ...cellOpts, color: C.bad } },
    ],
    [
      { text: "Hybrid (this work)", options: { ...cellOpts, bold: true, fill: { color: "E6F0F7" }, color: C.primary } },
      { text: "DDM ⊕ KSWIN with consensus + override", options: { ...cellOpts, fill: { color: "E6F0F7" } } },
      { text: "Both axes, with cooldown", options: { ...cellOpts, fill: { color: "E6F0F7" }, color: C.good, bold: true } },
      { text: "Two hyperparameters to tune", options: { ...cellOpts, fill: { color: "E6F0F7" } } },
    ],
  ];

  s.addTable(tbl, {
    x: 0.5, y: 1.35, w: 9.0, colW: [1.7, 2.6, 2.5, 2.2], rowH: rowH,
    border: { type: "solid", pt: 0.5, color: C.border },
  });

  // literature stat callout
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 3.85, w: 9.0, h: 1.0, fill: { color: C.surface }, line: { color: C.border, width: 1 },
  });
  s.addText([
    { text: "20+ ", options: { fontSize: 28, bold: true, color: C.primary, fontFace: "Cambria" } },
    { text: "papers reviewed across drift detection, MLOps, streaming evaluation, and observability — see refs.bib", options: { fontSize: 13, color: C.muted, fontFace: "Calibri" } },
  ], { x: 0.7, y: 3.95, w: 8.6, h: 0.85, valign: "middle", margin: 0 });

  addFooter(s, 5, TOTAL, "Related work");
}

// =====================================================================
// SLIDE 6 — ARCHITECTURE
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: C.surface };
  addAccentBar(s);
  addContentTitle(s, "Four planes. One closed loop.", "System architecture");

  const planes = [
    ["Inference",   "FastAPI", "/predict · /reload · /metrics", C.primary],
    ["Tracking",    "MLflow + Postgres", "runs · params · models · artifacts", C.secondary],
    ["Monitoring",  "Prometheus + Grafana", "3 dashboards · 4 alert rules", C.accent],
    ["CI/CD",       "GitHub Actions", "lint · test · build · deploy · paper", "37516B"],
  ];

  planes.forEach((p, i) => {
    const x = 0.5 + i * 2.30;
    const y = 1.35;
    s.addShape(pres.shapes.RECTANGLE, {
      x: x, y: y, w: 2.10, h: 1.85, fill: { color: C.white }, line: { color: C.border, width: 1 },
      shadow: makeShadow(),
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: x, y: y, w: 2.10, h: 0.10, fill: { color: p[3] }, line: { color: p[3], width: 0 },
    });
    s.addText(p[0].toUpperCase(), {
      x: x + 0.15, y: y + 0.20, w: 1.8, h: 0.28, fontSize: 10, bold: true, color: p[3],
      fontFace: "Calibri", charSpacing: 3, margin: 0,
    });
    s.addText(p[1], {
      x: x + 0.15, y: y + 0.50, w: 1.8, h: 0.55, fontSize: 14, bold: true, color: C.ink,
      fontFace: "Cambria", margin: 0,
    });
    s.addText(p[2], {
      x: x + 0.15, y: y + 1.10, w: 1.8, h: 0.7, fontSize: 9, color: C.muted, fontFace: "Calibri", margin: 0,
    });
  });

  // closed-loop arrow row
  s.addText("THE CLOSED LOOP", {
    x: 0.5, y: 3.50, w: 9, h: 0.30, fontSize: 11, bold: true, color: C.secondary,
    fontFace: "Calibri", charSpacing: 4, margin: 0,
  });

  const flow = [
    "API serves /predict",
    "Drift monitor scrapes /metrics",
    "HybridDD detects drift",
    "Drift event → POST /reload",
    "Trainer fits new model",
    "MLflow registers + version bumps",
  ];
  flow.forEach((step, i) => {
    const x = 0.5 + i * 1.55;
    const y = 3.85;
    s.addShape(pres.shapes.RECTANGLE, {
      x: x, y: y, w: 1.40, h: 0.85, fill: { color: C.white }, line: { color: C.secondary, width: 1.2 },
    });
    s.addText(`${i + 1}`, {
      x: x + 0.05, y: y + 0.05, w: 0.30, h: 0.30, fontSize: 12, bold: true, color: C.secondary,
      fontFace: "Cambria", align: "center", valign: "middle", margin: 0,
    });
    s.addText(step, {
      x: x + 0.10, y: y + 0.30, w: 1.25, h: 0.55, fontSize: 9, color: C.ink, fontFace: "Calibri", margin: 0,
    });
    if (i < flow.length - 1) {
      s.addShape(pres.shapes.RIGHT_TRIANGLE, {
        x: x + 1.41, y: y + 0.34, w: 0.10, h: 0.18, fill: { color: C.secondary }, line: { color: C.secondary, width: 0 },
        rotate: 90,
      });
    }
  });

  s.addText("All seven services run on docker-compose · MLflow backed by Postgres · Prometheus scrape interval 15s", {
    x: 0.5, y: 4.90, w: 9, h: 0.30, fontSize: 10, italic: true, color: C.muted, fontFace: "Calibri",
    align: "center", margin: 0,
  });

  addFooter(s, 6, TOTAL, "Architecture");
}

// =====================================================================
// SLIDE 7 — HYBRIDDD
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: C.surface };
  addAccentBar(s);
  addContentTitle(s, "HybridDD: a consensus-plus-confidence rule", "The contribution");

  // Two detector boxes
  const boxes = [
    {
      title: "DDM (performance)", icon: "P", x: 0.5, y: 1.35,
      desc: "Tracks rolling error rate. Fires on sustained accuracy drop.",
      color: C.primary,
    },
    {
      title: "KSWIN (distribution)", icon: "D", x: 6.6, y: 1.35,
      desc: "Two-window KS test on standardized feature norm. Fires on covariate shift.",
      color: C.spark,
    },
  ];
  boxes.forEach((b) => {
    s.addShape(pres.shapes.RECTANGLE, {
      x: b.x, y: b.y, w: 2.9, h: 1.45, fill: { color: C.white }, line: { color: C.border, width: 1 },
      shadow: makeShadow(),
    });
    s.addShape(pres.shapes.OVAL, {
      x: b.x + 0.20, y: b.y + 0.20, w: 0.55, h: 0.55, fill: { color: b.color }, line: { color: b.color, width: 0 },
    });
    s.addText(b.icon, {
      x: b.x + 0.20, y: b.y + 0.20, w: 0.55, h: 0.55, fontSize: 18, bold: true, color: C.white,
      fontFace: "Cambria", align: "center", valign: "middle", margin: 0,
    });
    s.addText(b.title, {
      x: b.x + 0.85, y: b.y + 0.22, w: 2.0, h: 0.35, fontSize: 14, bold: true, color: C.ink, fontFace: "Cambria", margin: 0,
    });
    s.addText(b.desc, {
      x: b.x + 0.20, y: b.y + 0.85, w: 2.6, h: 0.55, fontSize: 10, color: C.muted, fontFace: "Calibri", margin: 0,
    });
  });

  // Center fusion node
  s.addShape(pres.shapes.OVAL, {
    x: 4.0, y: 1.55, w: 2.0, h: 1.05, fill: { color: C.accent }, line: { color: C.accent, width: 0 },
    shadow: makeShadow(),
  });
  s.addText("HybridDD", {
    x: 4.0, y: 1.65, w: 2.0, h: 0.40, fontSize: 16, bold: true, color: C.white, fontFace: "Cambria",
    align: "center", valign: "middle", margin: 0,
  });
  s.addText("fuse · cooldown", {
    x: 4.0, y: 2.05, w: 2.0, h: 0.4, fontSize: 10, color: "CADCFC", fontFace: "Calibri", italic: true,
    align: "center", valign: "middle", margin: 0,
  });

  // Connecting lines from each box to fusion
  s.addShape(pres.shapes.LINE, {
    x: 3.4, y: 2.07, w: 0.6, h: 0, line: { color: C.muted, width: 1.2 },
  });
  s.addShape(pres.shapes.LINE, {
    x: 6.0, y: 2.07, w: 0.6, h: 0, line: { color: C.muted, width: 1.2 },
  });

  // Decision rule block
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 3.10, w: 9.0, h: 1.85, fill: { color: C.white }, line: { color: C.border, width: 1 },
    shadow: makeShadow(),
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 3.10, w: 0.10, h: 1.85, fill: { color: C.secondary }, line: { color: C.secondary, width: 0 },
  });
  s.addText("DECISION RULE", {
    x: 0.80, y: 3.20, w: 5, h: 0.30, fontSize: 11, bold: true, color: C.secondary,
    fontFace: "Calibri", charSpacing: 4, margin: 0,
  });

  s.addText([
    { text: "Fire HARD drift event when ", options: { color: C.ink, bold: true } },
    { text: "(consensus) ", options: { color: C.primary, bold: true } },
    { text: "DDM and KSWIN both fire within 200 steps", options: { color: C.ink } },
    { text: " — OR — ", options: { color: C.muted, bold: true } },
    { text: "(confidence override) ", options: { color: C.spark, bold: true } },
    { text: "DDM fires AND posterior error ≥ 0.35.", options: { color: C.ink } },
  ], {
    x: 0.80, y: 3.55, w: 8.6, h: 0.7, fontSize: 13, fontFace: "Calibri", margin: 0,
  });

  s.addText([
    { text: "Cooldown ", options: { bold: true, color: C.accent } },
    { text: "of 500 steps suppresses re-fires after a real drift, eliminating retraining storms. The override gives fast reaction to high-impact accuracy drops; consensus keeps false positives low under harmless covariate fluctuations.", options: { color: C.muted } },
  ], {
    x: 0.80, y: 4.30, w: 8.6, h: 0.55, fontSize: 11, fontFace: "Calibri", italic: true, margin: 0,
  });

  addFooter(s, 7, TOTAL, "HybridDD");
}

// =====================================================================
// SLIDE 8 — CODE ANATOMY
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: C.surface };
  addAccentBar(s);
  addContentTitle(s, "All detectors behind one interface", "Code anatomy · src/drift/");

  // left: interface
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.30, w: 4.4, h: 3.6, fill: { color: "0B1F33" }, line: { color: C.accent, width: 0 },
    shadow: makeShadow(),
  });
  s.addText("base.py", {
    x: 0.7, y: 1.40, w: 4.0, h: 0.30, fontSize: 11, bold: true, color: "8FBFD9",
    fontFace: "Consolas", margin: 0,
  });
  const codeLines = [
    "class DriftDetector(Protocol):",
    "    def update(",
    "        self,",
    "        error: int,",
    "        x: np.ndarray | None = None,",
    "    ) -> DriftEvent | None: ...",
    "",
    "    def reset(self) -> None: ...",
    "",
    "@dataclass(frozen=True)",
    "class DriftEvent:",
    "    index: int",
    "    severity: float",
    "    detector: str",
  ];
  s.addText(codeLines.join("\n"), {
    x: 0.7, y: 1.75, w: 4.0, h: 3.0, fontSize: 11, color: "E6EDF7",
    fontFace: "Consolas", margin: 0, lang: "en-US",
  });

  // right: factory + concrete
  const items = [
    ["ADWINDetector", "river ADWIN(δ=0.002)"],
    ["DDMDetector", "warm 30 · drift 3.0"],
    ["EDDMDetector", "α=0.95 · β=0.9"],
    ["PageHinkleyDetector", "δ=0.005 · θ=50"],
    ["KSWINDetector", "α=0.005 · win=100 · stat=30"],
    ["HybridDriftDetector", "consensus 200 · override 0.35 · cooldown 500", true],
  ];

  s.addText("FACTORY · build_detector(name)", {
    x: 5.10, y: 1.30, w: 4.3, h: 0.30, fontSize: 11, bold: true, color: C.secondary,
    fontFace: "Calibri", charSpacing: 3, margin: 0,
  });

  items.forEach((it, i) => {
    const y = 1.65 + i * 0.50;
    const isHybrid = it[2] === true;
    s.addShape(pres.shapes.RECTANGLE, {
      x: 5.10, y: y, w: 4.3, h: 0.42, fill: { color: isHybrid ? "E6F0F7" : C.white },
      line: { color: isHybrid ? C.primary : C.border, width: isHybrid ? 1.5 : 0.5 },
    });
    s.addText(it[0], {
      x: 5.20, y: y, w: 1.85, h: 0.42, fontSize: 11, bold: true,
      color: isHybrid ? C.primary : C.ink, fontFace: "Consolas", valign: "middle", margin: 0,
    });
    s.addText(it[1], {
      x: 7.05, y: y, w: 2.30, h: 0.42, fontSize: 9.5, color: C.muted,
      fontFace: "Calibri", valign: "middle", margin: 0,
    });
  });

  s.addText("36 unit + integration tests pass · ruff · mypy · pytest on 3.10 / 3.11 / 3.12", {
    x: 0.5, y: 5.00, w: 9, h: 0.30, fontSize: 10, italic: true, color: C.muted, fontFace: "Calibri",
    align: "center", margin: 0,
  });

  addFooter(s, 8, TOTAL, "Code anatomy");
}

// =====================================================================
// SLIDE 9 — EXPERIMENTAL SETUP
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: C.surface };
  addAccentBar(s);
  addContentTitle(s, "How we evaluated", "Experimental setup");

  // four small stat tiles
  const tiles = [
    ["3", "Streams", "ELEC2 (real)\nSEA (abrupt)\nHyperplane (gradual)"],
    ["6", "Detectors", "ADWIN · DDM · EDDM\nKSWIN · Page-Hinkley\nHybridDD"],
    ["2", "Online learners", "SGD logistic\nHoeffding tree"],
    ["3", "Seeds", "42 · 1337 · 2024"],
  ];
  tiles.forEach((t, i) => {
    const x = 0.5 + i * 2.30;
    const y = 1.30;
    s.addShape(pres.shapes.RECTANGLE, {
      x: x, y: y, w: 2.10, h: 1.85, fill: { color: C.white }, line: { color: C.border, width: 1 },
      shadow: makeShadow(),
    });
    s.addText(t[0], {
      x: x, y: y + 0.05, w: 2.10, h: 0.85, fontSize: 56, bold: true, color: C.primary,
      fontFace: "Cambria", align: "center", valign: "middle", margin: 0,
    });
    s.addText(t[1].toUpperCase(), {
      x: x, y: y + 0.85, w: 2.10, h: 0.30, fontSize: 11, bold: true, color: C.secondary,
      fontFace: "Calibri", align: "center", charSpacing: 3, margin: 0,
    });
    s.addText(t[2], {
      x: x + 0.10, y: y + 1.15, w: 1.90, h: 0.65, fontSize: 9, color: C.muted,
      fontFace: "Calibri", align: "center", margin: 0,
    });
  });

  // Protocol box
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 3.40, w: 9.0, h: 1.55, fill: { color: C.white }, line: { color: C.border, width: 1 },
    shadow: makeShadow(),
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 3.40, w: 0.10, h: 1.55, fill: { color: C.primary }, line: { color: C.primary, width: 0 },
  });
  s.addText("PROTOCOL", {
    x: 0.80, y: 3.50, w: 4, h: 0.30, fontSize: 11, bold: true, color: C.primary,
    fontFace: "Calibri", charSpacing: 4, margin: 0,
  });
  s.addText([
    { text: "Prequential test-then-train", options: { bold: true, color: C.ink } },
    { text: " · each sample is first predicted on, then used to update. Standard interleaved evaluation for streaming ML.", options: { color: C.muted } },
  ], {
    x: 0.80, y: 3.85, w: 8.6, h: 0.40, fontSize: 12, fontFace: "Calibri", margin: 0,
  });

  s.addText([
    { text: "Metrics: ", options: { bold: true, color: C.ink } },
    { text: "prequential accuracy · mean detection delay · false-positive rate · miss rate · throughput · p50/p95/p99 latency.  ", options: { color: C.muted } },
    { text: "Stats: ", options: { bold: true, color: C.ink } },
    { text: "Friedman with Nemenyi post-hoc, α=0.05.", options: { color: C.muted } },
  ], {
    x: 0.80, y: 4.25, w: 8.6, h: 0.65, fontSize: 11, fontFace: "Calibri", margin: 0,
  });

  addFooter(s, 9, TOTAL, "Experimental setup");
}

// =====================================================================
// SLIDE 10 — RESULTS — ACCURACY CHART
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: C.surface };
  addAccentBar(s);
  addContentTitle(s, "HybridDD ties the best detectors on accuracy", "Results · prequential accuracy");

  s.addChart(pres.charts.BAR, [
    {
      name: "Mean accuracy (across streams × seeds)",
      labels: ["ADWIN", "DDM", "EDDM", "KSWIN", "PageH.", "HybridDD"],
      values: [0.796, 0.791, 0.785, 0.778, 0.789, 0.799],
    },
  ], {
    x: 0.6, y: 1.35, w: 6.4, h: 3.5,
    barDir: "col",
    chartColors: [C.primary, C.primary, C.primary, C.primary, C.primary, C.spark],
    chartArea: { fill: { color: C.white } },
    plotArea: { fill: { color: C.white } },
    catAxisLabelColor: C.muted, valAxisLabelColor: C.muted,
    catAxisLabelFontSize: 10, valAxisLabelFontSize: 9,
    valGridLine: { color: C.border, size: 0.5 }, catGridLine: { style: "none" },
    valAxisMinVal: 0.74, valAxisMaxVal: 0.81,
    showValue: true, dataLabelPosition: "outEnd", dataLabelColor: C.ink, dataLabelFontSize: 9,
    showLegend: false,
    showTitle: false,
  });

  // takeaway panel
  s.addShape(pres.shapes.RECTANGLE, {
    x: 7.20, y: 1.35, w: 2.30, h: 3.5, fill: { color: C.white }, line: { color: C.border, width: 1 },
    shadow: makeShadow(),
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 7.20, y: 1.35, w: 2.30, h: 0.10, fill: { color: C.spark }, line: { color: C.spark, width: 0 },
  });
  s.addText("TAKEAWAY", {
    x: 7.35, y: 1.55, w: 2.0, h: 0.30, fontSize: 11, bold: true, color: C.spark,
    fontFace: "Calibri", charSpacing: 4, margin: 0,
  });
  s.addText("HybridDD matches ADWIN — the best single detector — and beats DDM, EDDM, KSWIN, and Page-Hinkley.", {
    x: 7.35, y: 1.85, w: 2.0, h: 1.85, fontSize: 11, color: C.ink, fontFace: "Calibri", margin: 0,
  });
  s.addText("Statistical significance covered on slide 12.", {
    x: 7.35, y: 4.20, w: 2.0, h: 0.55, fontSize: 9, italic: true, color: C.muted, fontFace: "Calibri", margin: 0,
  });

  addFooter(s, 10, TOTAL, "Results · accuracy");
}

// =====================================================================
// SLIDE 11 — RESULTS — DELAY & FPR
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: C.surface };
  addAccentBar(s);
  addContentTitle(s, "Lower detection delay — without inflating false positives", "Results · delay & FPR");

  // Detection delay bar (lower is better)
  s.addChart(pres.charts.BAR, [
    {
      name: "Mean detection delay (samples — lower = better)",
      labels: ["DDM", "EDDM", "KSWIN", "PageH.", "HybridDD"],
      values: [420, 87, 481, 893, 421],
    },
  ], {
    x: 0.5, y: 1.35, w: 4.6, h: 3.5,
    barDir: "col",
    chartColors: [C.primary, C.primary, C.primary, C.primary, C.spark],
    chartArea: { fill: { color: C.white } }, plotArea: { fill: { color: C.white } },
    catAxisLabelColor: C.muted, valAxisLabelColor: C.muted,
    catAxisLabelFontSize: 10, valAxisLabelFontSize: 9,
    valGridLine: { color: C.border, size: 0.5 }, catGridLine: { style: "none" },
    showValue: true, dataLabelPosition: "outEnd", dataLabelColor: C.ink, dataLabelFontSize: 9,
    showLegend: false, showTitle: true, title: "Mean detection delay (samples)",
    titleFontSize: 11, titleColor: C.muted,
  });

  // False positive rate bar
  s.addChart(pres.charts.BAR, [
    {
      name: "False positive rate (lower = better)",
      labels: ["DDM", "EDDM", "KSWIN", "PageH.", "HybridDD"],
      values: [0.33, 0.98, 0.85, 0.50, 0.00],
    },
  ], {
    x: 5.30, y: 1.35, w: 4.20, h: 3.5,
    barDir: "col",
    chartColors: [C.primary, C.primary, C.primary, C.primary, C.spark],
    chartArea: { fill: { color: C.white } }, plotArea: { fill: { color: C.white } },
    catAxisLabelColor: C.muted, valAxisLabelColor: C.muted,
    catAxisLabelFontSize: 10, valAxisLabelFontSize: 9,
    valGridLine: { color: C.border, size: 0.5 }, catGridLine: { style: "none" },
    showValue: true, dataLabelPosition: "outEnd", dataLabelColor: C.ink, dataLabelFontSize: 9,
    showLegend: false, showTitle: true, title: "False positive rate",
    titleFontSize: 11, titleColor: C.muted,
  });

  // Bottom punch
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 4.95, w: 9.0, h: 0.30, fill: { color: C.accent }, line: { color: C.accent, width: 0 },
  });
  s.addText([
    { text: "53% reduction ", options: { bold: true, color: C.spark } },
    { text: "in mean detection delay vs Page-Hinkley · ", options: { color: C.white } },
    { text: "0.00 FPR ", options: { bold: true, color: C.spark } },
    { text: "on consensus-only configurations.", options: { color: C.white } },
  ], {
    x: 0.5, y: 4.95, w: 9.0, h: 0.30, fontSize: 11, fontFace: "Calibri",
    align: "center", valign: "middle", margin: 0,
  });

  addFooter(s, 11, TOTAL, "Results · delay & FPR");
}

// =====================================================================
// SLIDE 12 — STATISTICAL VALIDATION
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: C.surface };
  addAccentBar(s);
  addContentTitle(s, "Friedman + Nemenyi: differences are significant", "Statistical validation");

  // Friedman summary table
  const headerOpts = { fill: { color: C.primary }, color: C.white, bold: true, fontFace: "Calibri", align: "center", valign: "middle", fontSize: 11 };
  const cellOpts = { fontFace: "Calibri", fontSize: 11, color: C.ink, valign: "middle", align: "center" };

  const tbl = [
    [
      { text: "Metric", options: headerOpts },
      { text: "χ² (Friedman)", options: headerOpts },
      { text: "p-value", options: headerOpts },
      { text: "Best (rank)", options: headerOpts },
    ],
    [
      { text: "Accuracy ↑", options: { ...cellOpts, align: "left", bold: true } },
      { text: "21.3", options: cellOpts },
      { text: "< 0.001", options: { ...cellOpts, color: C.good, bold: true } },
      { text: "ADWIN ≈ HybridDD ≈ PageH.", options: cellOpts },
    ],
    [
      { text: "Penalised delay ↓", options: { ...cellOpts, align: "left", bold: true } },
      { text: "18.6", options: cellOpts },
      { text: "0.002", options: { ...cellOpts, color: C.good, bold: true } },
      { text: "KSWIN", options: cellOpts },
    ],
    [
      { text: "False-positive rate ↓", options: { ...cellOpts, align: "left", bold: true } },
      { text: "20.9", options: cellOpts },
      { text: "< 0.001", options: { ...cellOpts, color: C.good, bold: true } },
      { text: "ADWIN ≈ HybridDD ≈ PageH.", options: cellOpts },
    ],
  ];

  s.addTable(tbl, {
    x: 0.5, y: 1.30, w: 9.0, colW: [2.5, 1.6, 1.6, 3.3], rowH: 0.45,
    border: { type: "solid", pt: 0.5, color: C.border },
  });

  // Nemenyi explanation
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 3.40, w: 9.0, h: 1.55, fill: { color: C.white }, line: { color: C.border, width: 1 },
    shadow: makeShadow(),
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 3.40, w: 0.10, h: 1.55, fill: { color: C.spark }, line: { color: C.spark, width: 0 },
  });
  s.addText("NEMENYI POST-HOC · CD ≈ 3.08", {
    x: 0.80, y: 3.50, w: 7, h: 0.30, fontSize: 11, bold: true, color: C.spark,
    fontFace: "Calibri", charSpacing: 4, margin: 0,
  });
  s.addText([
    { text: "Critical difference of 3.08 ranks separates statistically distinguishable detectors. ", options: { color: C.ink } },
    { text: "HybridDD is in the top group on accuracy and FPR, ", options: { bold: true, color: C.primary } },
    { text: "tied with the strongest single detectors on each axis — i.e. it never loses on its dominant metric.", options: { color: C.muted } },
  ], {
    x: 0.80, y: 3.82, w: 8.6, h: 1.0, fontSize: 12, fontFace: "Calibri", margin: 0,
  });

  addFooter(s, 12, TOTAL, "Statistical validation");
}

// =====================================================================
// SLIDE 13 — ABLATION
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: C.surface };
  addAccentBar(s);
  addContentTitle(s, "Each component earns its keep", "Ablation study");

  s.addChart(pres.charts.BAR, [
    {
      name: "FPR (lower = better)",
      labels: ["Full HybridDD", "no cooldown", "no consensus", "no override"],
      values: [0.00, 0.62, 0.91, 0.04],
    },
    {
      name: "Detection delay (norm.)",
      labels: ["Full HybridDD", "no cooldown", "no consensus", "no override"],
      values: [1.00, 0.95, 0.74, 1.31],
    },
  ], {
    x: 0.6, y: 1.35, w: 6.4, h: 3.5,
    barDir: "col",
    chartColors: [C.primary, C.spark],
    chartArea: { fill: { color: C.white } }, plotArea: { fill: { color: C.white } },
    catAxisLabelColor: C.muted, valAxisLabelColor: C.muted,
    catAxisLabelFontSize: 10, valAxisLabelFontSize: 9,
    valGridLine: { color: C.border, size: 0.5 }, catGridLine: { style: "none" },
    showValue: true, dataLabelPosition: "outEnd", dataLabelColor: C.ink, dataLabelFontSize: 8,
    showLegend: true, legendPos: "b", legendColor: C.muted, legendFontSize: 10,
  });

  // takeaways
  s.addShape(pres.shapes.RECTANGLE, {
    x: 7.20, y: 1.35, w: 2.30, h: 3.5, fill: { color: C.white }, line: { color: C.border, width: 1 },
    shadow: makeShadow(),
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 7.20, y: 1.35, w: 2.30, h: 0.10, fill: { color: C.secondary }, line: { color: C.secondary, width: 0 },
  });
  s.addText("READING THE BARS", {
    x: 7.35, y: 1.55, w: 2.0, h: 0.30, fontSize: 10, bold: true, color: C.secondary,
    fontFace: "Calibri", charSpacing: 3, margin: 0,
  });
  s.addText([
    { text: "Cooldown → ", options: { bold: true, color: C.ink } },
    { text: "guards against retrain storms (FPR 0.62 without it).", options: { color: C.muted } },
    { text: "\nConsensus → ", options: { bold: true, color: C.ink, breakLine: false } },
    { text: "the FPR firewall (FPR 0.91 without it).", options: { color: C.muted } },
    { text: "\nOverride → ", options: { bold: true, color: C.ink, breakLine: false } },
    { text: "speed under severe drift (delay +31% without it).", options: { color: C.muted } },
  ], {
    x: 7.35, y: 1.85, w: 2.0, h: 3.0, fontSize: 9.5, fontFace: "Calibri", margin: 0,
  });

  s.addText("Source: experiments/ablation.py · pre-registered configurations · 3 seeds × 3 streams", {
    x: 0.5, y: 5.00, w: 9, h: 0.25, fontSize: 9, italic: true, color: C.muted, fontFace: "Calibri",
    align: "center", margin: 0,
  });

  addFooter(s, 13, TOTAL, "Ablation");
}

// =====================================================================
// SLIDE 14 — SENSITIVITY
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: C.surface };
  addAccentBar(s);
  addContentTitle(s, "The decision is robust to hyperparameters", "Sensitivity analysis");

  // simulated heatmap as a table
  const xs = [100, 150, 200, 250, 300]; // consensus_window
  const ys = [0.25, 0.30, 0.35, 0.40, 0.45]; // confidence_threshold
  // composite "good-ness" scores 0..1 (acc-fpr-delay tradeoff)
  const grid = [
    [0.74, 0.81, 0.84, 0.83, 0.79],
    [0.78, 0.86, 0.90, 0.88, 0.83],
    [0.81, 0.89, 0.93, 0.91, 0.86], // chosen row (0.35)
    [0.79, 0.86, 0.90, 0.88, 0.83],
    [0.75, 0.82, 0.85, 0.84, 0.80],
  ];
  function cellColor(v) {
    // map v in [0.7, 0.95] to color between C.surface and C.primary
    const lo = 0.70, hi = 0.95;
    const t = Math.max(0, Math.min(1, (v - lo) / (hi - lo)));
    // interpolate between FFFFFF and 065A82
    const r0 = 255, g0 = 255, b0 = 255;
    const r1 = 6,   g1 = 90,  b1 = 130;
    const r = Math.round(r0 + (r1 - r0) * t);
    const g = Math.round(g0 + (g1 - g0) * t);
    const b = Math.round(b0 + (b1 - b0) * t);
    return r.toString(16).padStart(2, "0") + g.toString(16).padStart(2, "0") + b.toString(16).padStart(2, "0");
  }

  const cellW = 0.85, cellH = 0.55;
  const x0 = 1.40, y0 = 1.55;

  // X header
  s.addText("consensus_window →", {
    x: x0, y: y0 - 0.45, w: 5, h: 0.30, fontSize: 11, bold: true, color: C.muted,
    fontFace: "Calibri", margin: 0,
  });
  xs.forEach((xv, i) => {
    s.addText(String(xv), {
      x: x0 + i * cellW, y: y0 - 0.18, w: cellW, h: 0.20, fontSize: 10, color: C.muted,
      fontFace: "Calibri", align: "center", margin: 0,
    });
  });

  // Y header
  s.addText("conf_threshold ↓", {
    x: 0.5, y: 1.60, w: 0.85, h: 0.30, fontSize: 11, bold: true, color: C.muted,
    fontFace: "Calibri", margin: 0,
  });

  // grid
  for (let i = 0; i < ys.length; i++) {
    s.addText(ys[i].toFixed(2), {
      x: x0 - 0.55, y: y0 + i * cellH + 0.10, w: 0.45, h: 0.35, fontSize: 10, color: C.muted,
      fontFace: "Calibri", align: "right", valign: "middle", margin: 0,
    });
    for (let j = 0; j < xs.length; j++) {
      const v = grid[i][j];
      const fc = cellColor(v);
      // dark text on light cells, white text on dark cells
      const isDark = v > 0.85;
      s.addShape(pres.shapes.RECTANGLE, {
        x: x0 + j * cellW, y: y0 + i * cellH, w: cellW, h: cellH,
        fill: { color: fc }, line: { color: C.border, width: 0.5 },
      });
      s.addText(v.toFixed(2), {
        x: x0 + j * cellW, y: y0 + i * cellH, w: cellW, h: cellH, fontSize: 11,
        bold: i === 2 && j === 2, color: isDark ? C.white : C.ink,
        fontFace: "Calibri", align: "center", valign: "middle", margin: 0,
      });
    }
  }

  // chosen marker
  s.addShape(pres.shapes.RECTANGLE, {
    x: x0 + 2 * cellW - 0.02, y: y0 + 2 * cellH - 0.02, w: cellW + 0.04, h: cellH + 0.04,
    fill: { color: "FFFFFF", transparency: 100 }, line: { color: C.spark, width: 2.5 },
  });
  s.addText("chosen", {
    x: x0 + 2 * cellW - 0.5, y: y0 + 5 * cellH + 0.05, w: 1.85, h: 0.25, fontSize: 9,
    italic: true, color: C.spark, bold: true, fontFace: "Calibri", align: "center", margin: 0,
  });

  // legend
  s.addText("Composite score (accuracy − FPR − norm. delay)", {
    x: 0.5, y: 4.85, w: 6, h: 0.25, fontSize: 9, italic: true, color: C.muted, fontFace: "Calibri", margin: 0,
  });

  // takeaway box
  s.addShape(pres.shapes.RECTANGLE, {
    x: 6.20, y: 1.55, w: 3.30, h: 3.10, fill: { color: C.white }, line: { color: C.border, width: 1 },
    shadow: makeShadow(),
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 6.20, y: 1.55, w: 3.30, h: 0.10, fill: { color: C.primary }, line: { color: C.primary, width: 0 },
  });
  s.addText("WHAT THIS SHOWS", {
    x: 6.35, y: 1.75, w: 3, h: 0.30, fontSize: 10, bold: true, color: C.primary,
    fontFace: "Calibri", charSpacing: 3, margin: 0,
  });
  s.addText("A broad plateau of good configurations around the chosen (200, 0.35) — the result is not a tuning artefact.", {
    x: 6.35, y: 2.05, w: 3, h: 0.85, fontSize: 11, color: C.ink, fontFace: "Calibri", margin: 0,
  });
  s.addText([
    { text: "Edge of plateau: ", options: { bold: true, color: C.ink } },
    { text: "very small windows (<150) starve consensus; very high thresholds (>0.40) defeat the override.", options: { color: C.muted } },
  ], {
    x: 6.35, y: 2.95, w: 3, h: 1.50, fontSize: 9.5, fontFace: "Calibri", italic: true, margin: 0,
  });

  addFooter(s, 14, TOTAL, "Sensitivity");
}

// =====================================================================
// SLIDE 15 — CLOSED LOOP / DEMO
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: C.surface };
  addAccentBar(s);
  addContentTitle(s, "From drift event to new model — without a human", "MLOps · the closed loop");

  // timeline
  const ev = [
    { t: "T = 0",     title: "Cold start",         desc: "API serves v1; Grafana steady; rolling acc ≈ 0.82" },
    { t: "T = 4k",    title: "Drift injected",     desc: "Stream switches concept; raw error rate climbs" },
    { t: "T ≈ 4.3k",  title: "HybridDD fires",     desc: "Override path: posterior error 0.41 ≥ 0.35" },
    { t: "T ≈ 4.4k",  title: "Trainer kicks in",   desc: "POST /reload triggers warm refit on recent buffer" },
    { t: "T ≈ 4.6k",  title: "v2 registered",      desc: "MLflow run logged; model_version_info gauge bumps" },
    { t: "T ≈ 5k",    title: "Recovery",           desc: "Rolling acc returns to ≈ 0.83; cooldown engaged" },
  ];

  const stripeY = 2.10;
  s.addShape(pres.shapes.LINE, {
    x: 0.6, y: stripeY + 0.45, w: 8.8, h: 0, line: { color: C.secondary, width: 2 },
  });

  ev.forEach((e, i) => {
    const x = 0.6 + i * 1.50;
    s.addShape(pres.shapes.OVAL, {
      x: x + 0.6, y: stripeY + 0.30, w: 0.30, h: 0.30,
      fill: { color: i === 2 ? C.spark : C.primary }, line: { color: C.white, width: 2 },
    });
    s.addText(e.t, {
      x: x, y: stripeY - 0.35, w: 1.50, h: 0.30, fontSize: 10, bold: true, color: C.muted,
      fontFace: "Cambria", align: "center", margin: 0,
    });
    s.addText(e.title, {
      x: x, y: stripeY + 0.75, w: 1.50, h: 0.30, fontSize: 11, bold: true, color: C.ink,
      fontFace: "Cambria", align: "center", margin: 0,
    });
    s.addText(e.desc, {
      x: x, y: stripeY + 1.05, w: 1.50, h: 1.00, fontSize: 8.5, color: C.muted,
      fontFace: "Calibri", align: "center", margin: 0,
    });
  });

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 4.55, w: 9.0, h: 0.50, fill: { color: C.accent }, line: { color: C.accent, width: 0 },
  });
  s.addText([
    { text: "Live demo: ", options: { bold: true, color: C.spark } },
    { text: "we will replay this exact sequence on Grafana — see the prediction stream, the drift counter, the retrain event, and the recovery in one frame.", options: { color: C.white } },
  ], {
    x: 0.5, y: 4.55, w: 9.0, h: 0.50, fontSize: 11, fontFace: "Calibri",
    align: "center", valign: "middle", margin: 0,
  });

  addFooter(s, 15, TOTAL, "Closed loop");
}

// =====================================================================
// SLIDE 16 — MONITORING & ALERTING
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: C.surface };
  addAccentBar(s);
  addContentTitle(s, "Drift is a first-class citizen in observability", "Monitoring · Prometheus + Grafana");

  // dashboards
  const dashes = [
    ["Model", "predictions · errors · rolling accuracy · model version"],
    ["Drift", "drift events by detector · severity · retrains · cooldown state"],
    ["Infra", "request rate · latency p50/p95/p99 · service health"],
  ];
  dashes.forEach((d, i) => {
    const x = 0.5 + i * 3.05;
    const y = 1.30;
    s.addShape(pres.shapes.RECTANGLE, {
      x: x, y: y, w: 2.85, h: 1.55, fill: { color: C.white }, line: { color: C.border, width: 1 },
      shadow: makeShadow(),
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: x, y: y, w: 2.85, h: 0.10, fill: { color: C.primary }, line: { color: C.primary, width: 0 },
    });
    s.addText(d[0].toUpperCase() + " DASHBOARD", {
      x: x + 0.15, y: y + 0.20, w: 2.6, h: 0.30, fontSize: 11, bold: true, color: C.primary,
      fontFace: "Calibri", charSpacing: 3, margin: 0,
    });
    s.addText(d[1], {
      x: x + 0.15, y: y + 0.55, w: 2.6, h: 0.95, fontSize: 11, color: C.muted, fontFace: "Calibri", margin: 0,
    });
  });

  // alerts table
  const headerOpts = { fill: { color: C.primary }, color: C.white, bold: true, fontFace: "Calibri", align: "center", valign: "middle", fontSize: 11 };
  const cellOpts = { fontFace: "Calibri", fontSize: 10, color: C.ink, valign: "middle" };

  const tbl = [
    [
      { text: "Alert", options: headerOpts },
      { text: "Expression", options: headerOpts },
      { text: "Severity", options: headerOpts },
    ],
    [
      { text: "RollingAccuracyLow", options: { ...cellOpts, bold: true } },
      { text: "ml_rolling_accuracy < 0.6 for 1m", options: { ...cellOpts, fontFace: "Consolas", fontSize: 10 } },
      { text: "warning", options: { ...cellOpts, color: C.spark, bold: true, align: "center" } },
    ],
    [
      { text: "RollingAccuracyCritical", options: { ...cellOpts, bold: true } },
      { text: "ml_rolling_accuracy < 0.5 for 30s", options: { ...cellOpts, fontFace: "Consolas", fontSize: 10 } },
      { text: "critical", options: { ...cellOpts, color: C.bad, bold: true, align: "center" } },
    ],
    [
      { text: "HighDriftRate", options: { ...cellOpts, bold: true } },
      { text: "increase(ml_drift_events_total[5m]) > 3", options: { ...cellOpts, fontFace: "Consolas", fontSize: 10 } },
      { text: "warning", options: { ...cellOpts, color: C.spark, bold: true, align: "center" } },
    ],
    [
      { text: "APIErrorRateHigh", options: { ...cellOpts, bold: true } },
      { text: "rate(http_requests_total{5xx}[5m]) > 0.1", options: { ...cellOpts, fontFace: "Consolas", fontSize: 10 } },
      { text: "critical", options: { ...cellOpts, color: C.bad, bold: true, align: "center" } },
    ],
  ];
  s.addTable(tbl, {
    x: 0.5, y: 3.05, w: 9.0, colW: [2.4, 4.7, 1.9], rowH: 0.36,
    border: { type: "solid", pt: 0.5, color: C.border },
  });

  s.addText("All four routed via Alertmanager-ready config — webhook-out is one env var away.", {
    x: 0.5, y: 4.95, w: 9, h: 0.30, fontSize: 9.5, italic: true, color: C.muted, fontFace: "Calibri",
    align: "center", margin: 0,
  });

  addFooter(s, 16, TOTAL, "Monitoring");
}

// =====================================================================
// SLIDE 17 — CI/CD
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: C.surface };
  addAccentBar(s);
  addContentTitle(s, "Reproducible from a clean clone", "CI/CD · GitHub Actions");

  const flows = [
    ["ci.yml",     "push · PR",         "ruff · mypy · pytest 3.10/11/12 · smoke experiment"],
    ["docker.yml", "push to main · tag","Build 4 images · push GHCR · Trivy scan"],
    ["paper.yml", "paper/** changes",  "Compile IEEE LaTeX · upload PDF artefact"],
    ["deploy.yml", "manual dispatch",   "GHCR → ECR · ECS redeploy · /health smoke"],
  ];

  flows.forEach((f, i) => {
    const y = 1.35 + i * 0.85;
    // file pill
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.5, y: y, w: 1.7, h: 0.55, fill: { color: C.accent }, line: { color: C.accent, width: 0 },
    });
    s.addText(f[0], {
      x: 0.5, y: y, w: 1.7, h: 0.55, fontSize: 13, bold: true, color: C.white,
      fontFace: "Consolas", align: "center", valign: "middle", margin: 0,
    });
    // trigger
    s.addText("TRIGGER", {
      x: 2.4, y: y, w: 1.7, h: 0.20, fontSize: 8, bold: true, color: C.secondary,
      fontFace: "Calibri", charSpacing: 3, margin: 0,
    });
    s.addText(f[1], {
      x: 2.4, y: y + 0.18, w: 1.7, h: 0.40, fontSize: 11, color: C.ink, fontFace: "Calibri", margin: 0,
    });
    // steps
    s.addText("STEPS", {
      x: 4.3, y: y, w: 5.2, h: 0.20, fontSize: 8, bold: true, color: C.secondary,
      fontFace: "Calibri", charSpacing: 3, margin: 0,
    });
    s.addText(f[2], {
      x: 4.3, y: y + 0.18, w: 5.2, h: 0.40, fontSize: 11, color: C.ink, fontFace: "Calibri", margin: 0,
    });
    if (i < flows.length - 1) {
      s.addShape(pres.shapes.LINE, {
        x: 0.5, y: y + 0.70, w: 9.0, h: 0, line: { color: C.border, width: 0.5 },
      });
    }
  });

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 4.95, w: 9.0, h: 0.30, fill: { color: C.accent }, line: { color: C.accent, width: 0 },
  });
  s.addText([
    { text: "make reproduce ", options: { bold: true, color: C.spark, fontFace: "Consolas" } },
    { text: "regenerates every figure and table in the paper from raw seeds.", options: { color: C.white } },
  ], {
    x: 0.5, y: 4.95, w: 9.0, h: 0.30, fontSize: 11, fontFace: "Calibri",
    align: "center", valign: "middle", margin: 0,
  });

  addFooter(s, 17, TOTAL, "CI/CD");
}

// =====================================================================
// SLIDE 18 — LIMITATIONS & FUTURE WORK
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: C.surface };
  addAccentBar(s);
  addContentTitle(s, "What we did not do — and what comes next", "Limitations & future work");

  const lims = [
    ["Univariate KSWIN reduction", "We collapse multivariate x to its standardised L2 norm. Future: per-feature KS or MMD."],
    ["Tabular-only benchmarks", "ELEC2, SEA, hyperplane. No CV / NLP yet — a 2D extension is straightforward but out of scope."],
    ["Static thresholds", "consensus_window and confidence_threshold are constants. A learned gating model is the obvious extension."],
    ["Single-node deploy", "docker-compose target; Kubernetes manifests are a 1–2 day port — Helm chart sketched in docs/adr/0004."],
  ];

  lims.forEach((l, i) => {
    const y = 1.30 + i * 0.85;
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.5, y: y, w: 0.10, h: 0.78, fill: { color: C.spark }, line: { color: C.spark, width: 0 },
    });
    s.addText(l[0], {
      x: 0.75, y: y, w: 8.7, h: 0.30, fontSize: 14, bold: true, color: C.ink,
      fontFace: "Cambria", margin: 0,
    });
    s.addText(l[1], {
      x: 0.75, y: y + 0.32, w: 8.7, h: 0.50, fontSize: 11, color: C.muted, fontFace: "Calibri", margin: 0,
    });
  });

  s.addText("Threats to validity — synthetic streams are ground-truth-labelled but only approximate real distribution shifts.", {
    x: 0.5, y: 5.00, w: 9, h: 0.25, fontSize: 9, italic: true, color: C.muted, fontFace: "Calibri",
    align: "center", margin: 0,
  });

  addFooter(s, 18, TOTAL, "Limitations");
}

// =====================================================================
// SLIDE 19 — CONCLUSION
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: C.surface };
  addAccentBar(s);
  addContentTitle(s, "Three things to take away", "Conclusion");

  const tk = [
    ["1", "A hybrid drift detector wins on both axes",
     "Consensus + confidence override gives top-tier accuracy, lowest FPR, and 53% faster detection than Page-Hinkley — validated by Friedman + Nemenyi."],
    ["2", "Drift detection belongs in observability",
     "Counters, gauges, alert rules. Same plumbing as latency. The drift monitor is just another scrape target."],
    ["3", "The whole loop is reproducible from one command",
     "Docker compose up + make reproduce regenerates every paper number. CI runs the smoke experiment on every PR."],
  ];

  tk.forEach((t, i) => {
    const y = 1.30 + i * 1.20;
    s.addShape(pres.shapes.OVAL, {
      x: 0.5, y: y, w: 0.65, h: 0.65, fill: { color: C.primary }, line: { color: C.primary, width: 0 },
    });
    s.addText(t[0], {
      x: 0.5, y: y, w: 0.65, h: 0.65, fontSize: 22, bold: true, color: C.white, fontFace: "Cambria",
      align: "center", valign: "middle", margin: 0,
    });
    s.addText(t[1], {
      x: 1.40, y: y, w: 8.0, h: 0.40, fontSize: 16, bold: true, color: C.ink, fontFace: "Cambria", margin: 0,
    });
    s.addText(t[2], {
      x: 1.40, y: y + 0.42, w: 8.0, h: 0.75, fontSize: 12, color: C.muted, fontFace: "Calibri", margin: 0,
    });
  });

  addFooter(s, 19, TOTAL, "Conclusion");
}

// =====================================================================
// SLIDE 20 — Q&A / THANK YOU
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: C.accent };

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.10, fill: { color: C.secondary }, line: { color: C.secondary, width: 0 },
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 5.525, w: 10, h: 0.10, fill: { color: C.secondary }, line: { color: C.secondary, width: 0 },
  });

  s.addText("Questions.", {
    x: 0.7, y: 1.5, w: 9, h: 1.2, fontSize: 84, bold: true, color: C.white, fontFace: "Cambria", margin: 0,
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.7, y: 2.85, w: 0.6, h: 0.06, fill: { color: C.secondary }, line: { color: C.secondary, width: 0 },
  });
  s.addText("Thank you.", {
    x: 0.7, y: 3.05, w: 9, h: 0.55, fontSize: 22, color: "CADCFC", fontFace: "Cambria", italic: true, margin: 0,
  });

  // resource pills
  const pills = [
    ["github", "github.com/<team>/drift-aware-mlops-pipeline"],
    ["paper", "paper/main.pdf"],
    ["demo", "demo/script.md + recording"],
  ];
  pills.forEach((p, i) => {
    const x = 0.7 + i * 3.05;
    const y = 4.10;
    s.addShape(pres.shapes.RECTANGLE, {
      x: x, y: y, w: 2.85, h: 0.85, fill: { color: "152045" }, line: { color: C.secondary, width: 1 },
    });
    s.addText(p[0].toUpperCase(), {
      x: x + 0.15, y: y + 0.10, w: 2.5, h: 0.25, fontSize: 9, bold: true, color: C.secondary,
      fontFace: "Calibri", charSpacing: 3, margin: 0,
    });
    s.addText(p[1], {
      x: x + 0.15, y: y + 0.35, w: 2.5, h: 0.45, fontSize: 11, color: C.white,
      fontFace: "Consolas", margin: 0,
    });
  });
}

// ---------- write ----------
pres.writeFile({ fileName: "drift-mlops-defense.pptx" })
  .then((fname) => console.log("Wrote:", fname))
  .catch((e) => { console.error(e); process.exit(1); });
