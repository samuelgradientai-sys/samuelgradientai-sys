"""Genera assets/banner.svg: banner animado (SMIL) para el README del perfil."""
import sys
from html import escape
from pathlib import Path

OUT = Path(sys.argv[1])

W, H = 1000, 280
GREEN = "#3fb950"
MONO = "Consolas, 'SF Mono', Menlo, 'DejaVu Sans Mono', 'Liberation Mono', monospace"
SANS = "'Segoe UI', Ubuntu, 'Helvetica Neue', Arial, sans-serif"

# ---------- typing ----------
LINES = [
    "Ingeniero Industrial @ 3PL",
    "Python · Automatización · Datos",
    "Homelab con LLMs locales",
    "Tecnología aplicada a la logística",
    "Construyendo Gradient AI",
]
FS = 22
CW = FS * 0.6          # ancho fijo por caracter (textLength lo fuerza)
X0 = 440               # inicio del texto tipeado
TY = 182               # baseline de la linea tipeada
SLOT, TYPE, HOLD, ERASE = 4.0, 1.6, 1.75, 0.45
CYCLE = SLOT * len(LINES)


def width_events(i):
    n = len(LINES[i])
    s = i * SLOT
    ev = [(0.0, 0.0)]
    for k in range(1, n + 1):
        ev.append((s + TYPE * k / n, k * CW))
    e0 = s + TYPE + HOLD
    for j in range(1, n + 1):
        ev.append((e0 + ERASE * j / n, (n - j) * CW))
    return ev


def value_at(ev, t):
    v = 0.0
    for tt, vv in ev:
        if tt <= t + 1e-9:
            v = vv
        else:
            break
    return v


def smil_lists(ev):
    # dedupe consecutive equal values
    out = []
    for t, v in ev:
        if out and abs(out[-1][1] - v) < 1e-9:
            continue
        out.append((t, v))
    kt = ";".join(f"{t / CYCLE:.5f}" for t, _ in out)
    vals = ";".join(f"{v:.1f}" for _, v in out)
    return kt, vals


all_ev = [width_events(i) for i in range(len(LINES))]
typing_defs, typing_text = [], []
for i, line in enumerate(LINES):
    kt, vals = smil_lists(all_ev[i])
    full = len(line) * CW
    base_w = f"{full:.1f}" if i == 0 else "0"   # render estatico: muestra la 1a linea
    typing_defs.append(
        f'<clipPath id="tc{i}"><rect x="{X0}" y="{TY - 24}" height="34" width="{base_w}">'
        f'<animate attributeName="width" dur="{CYCLE}s" repeatCount="indefinite" calcMode="discrete" '
        f'keyTimes="{kt}" values="{vals}"/></rect></clipPath>'
    )
    typing_text.append(
        f'<text x="{X0}" y="{TY}" clip-path="url(#tc{i})" textLength="{full:.1f}" '
        f'lengthAdjust="spacingAndGlyphs">{escape(line)}</text>'
    )

# cursor: x = X0 + ancho de la linea activa
times = sorted({t for ev in all_ev for t, _ in ev})
cur = [(t, X0 + 2 + max(value_at(ev, t) for ev in all_ev)) for t in times]
ckt, cvals = smil_lists(cur)
cursor_base = X0 + 2 + len(LINES[0]) * CW

# ---------- molecula (inspirada en el logo) ----------
CX, CY = 205, 140
NODES = {  # nombre: (x, y, r, gris?)
    "top": (12, -70, 21, False),
    "mid": (-12, -8, 31, False),
    "right": (58, -14, 24, False),
    "left": (-78, 8, 24, True),
    "low": (34, 50, 23, False),
    "tail": (2, 98, 16, False),
}
BONDS = [("top", "mid"), ("mid", "right"), ("mid", "left"), ("right", "low"), ("low", "tail")]

bond_svg, pulse_svg = [], []
for k, (a, b) in enumerate(BONDS):
    xa, ya, _, ga = NODES[a]
    xb, yb, _, gb = NODES[b]
    color = "url(#bondGray)" if (ga or gb) else "url(#bond)"
    bond_svg.append(
        f'<line x1="{xa}" y1="{ya}" x2="{xb}" y2="{yb}" stroke="{color}" stroke-width="17" stroke-linecap="round"/>'
    )
    begin = f"{k * 0.55:.2f}s"
    pulse_svg.append(
        f'<circle r="4" fill="{GREEN}" filter="url(#glow)" opacity="0">'
        f'<animateMotion dur="2.2s" begin="{begin}" repeatCount="indefinite" path="M{xa} {ya} L{xb} {yb}"/>'
        f'<animate attributeName="opacity" dur="2.2s" begin="{begin}" repeatCount="indefinite" '
        f'values="0;1;1;0" keyTimes="0;0.2;0.8;1"/></circle>'
    )

node_svg = []
for k, (name, (x, y, r, gray)) in enumerate(NODES.items()):
    fill = "url(#nodeGray)" if gray else "url(#node)"
    d = 3.2 + k * 0.45
    node_svg.append(
        f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}">'
        f'<animate attributeName="r" dur="{d:.2f}s" repeatCount="indefinite" '
        f'values="{r};{r + 1.6};{r}" calcMode="spline" keySplines="0.45 0 0.55 1;0.45 0 0.55 1"/></circle>'
    )

EASE = 'calcMode="spline" keyTimes="0;0.5;1" keySplines="0.45 0 0.55 1;0.45 0 0.55 1"'

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Samuel Gómez Dávila — Ingeniero Industrial · Python · Automatización · Datos">
<title>Samuel Gómez Dávila</title>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#0b0f14"/><stop offset="1" stop-color="#161b22"/>
  </linearGradient>
  <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">
    <circle cx="2" cy="2" r="1" fill="#ffffff" opacity="0.07"/>
  </pattern>
  <radialGradient id="halo"><stop offset="0" stop-color="#ffffff" stop-opacity="0.13"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/></radialGradient>
  <radialGradient id="node" cx="0.5" cy="0.5" fx="0.34" fy="0.3" r="0.65">
    <stop offset="0" stop-color="#ffffff"/><stop offset="0.6" stop-color="#e6eaee"/><stop offset="1" stop-color="#9aa4ae"/>
  </radialGradient>
  <radialGradient id="nodeGray" cx="0.5" cy="0.5" fx="0.34" fy="0.3" r="0.65">
    <stop offset="0" stop-color="#b4bcc4"/><stop offset="1" stop-color="#4f575f"/>
  </radialGradient>
  <linearGradient id="bond" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f0f3f6"/><stop offset="1" stop-color="#aab3bc"/></linearGradient>
  <linearGradient id="bondGray" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#d0d7de"/><stop offset="1" stop-color="#5c646c"/></linearGradient>
  <linearGradient id="nameFill" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#9aa4ae"/></linearGradient>
  <linearGradient id="sweep" gradientUnits="userSpaceOnUse" x1="250" y1="0" x2="410" y2="0">
    <stop offset="0" stop-color="{GREEN}" stop-opacity="0"/><stop offset="0.5" stop-color="{GREEN}"/><stop offset="1" stop-color="{GREEN}" stop-opacity="0"/>
    <animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="720 0" dur="4s" repeatCount="indefinite"/>
  </linearGradient>
  <filter id="glow" x="-200%" y="-200%" width="500%" height="500%">
    <feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="shadow" x="-30%" y="-30%" width="160%" height="160%">
    <feDropShadow dx="0" dy="8" stdDeviation="9" flood-color="#000000" flood-opacity="0.7"/>
  </filter>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath>
  {"".join(typing_defs)}
</defs>

<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" fill="url(#dots)"/>

  <!-- halo + orbitas -->
  <circle cx="{CX}" cy="{CY}" r="120" fill="url(#halo)">
    <animate attributeName="r" dur="6s" repeatCount="indefinite" values="112;132;112" {EASE}/>
  </circle>
  <g transform="translate({CX} {CY})">
    <g>
      <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="28s" repeatCount="indefinite"/>
      <circle r="128" fill="none" stroke="{GREEN}" stroke-opacity="0.35" stroke-width="1.2" stroke-dasharray="2 10"/>
      <circle cx="128" cy="0" r="4" fill="{GREEN}" filter="url(#glow)"/>
    </g>
    <g>
      <animateTransform attributeName="transform" type="rotate" from="360" to="0" dur="46s" repeatCount="indefinite"/>
      <circle r="150" fill="none" stroke="#8b949e" stroke-opacity="0.25" stroke-width="1" stroke-dasharray="1 7"/>
      <circle cx="-150" cy="0" r="2.5" fill="#c9d1d9"/>
    </g>
  </g>

  <!-- molecula -->
  <g transform="translate({CX} {CY})">
    <g>
      <animateTransform attributeName="transform" type="translate" dur="6s" repeatCount="indefinite" values="0 0;0 -9;0 0" {EASE}/>
      <g>
        <animateTransform attributeName="transform" type="rotate" dur="12s" repeatCount="indefinite" values="-4;4;-4" {EASE}/>
        <g filter="url(#shadow)">
          {"".join(bond_svg)}
          {"".join(node_svg)}
        </g>
        {"".join(pulse_svg)}
      </g>
    </g>
  </g>

  <!-- texto -->
  <g font-family="{MONO}">
    <text x="412" y="80" font-size="14" letter-spacing="4" fill="{GREEN}">HOLA, SOY</text>
  </g>
  <text x="410" y="132" font-family="{SANS}" font-size="46" font-weight="700" fill="url(#nameFill)">Samuel Gómez Dávila
    <animate attributeName="opacity" values="0;1" dur="0.9s" begin="0s" fill="freeze"/>
  </text>

  <g font-family="{MONO}" font-size="{FS}">
    <text x="412" y="{TY}" fill="{GREEN}" font-weight="700">&gt;</text>
    <g fill="#e6edf3">{"".join(typing_text)}</g>
    <rect x="{cursor_base:.1f}" y="{TY - 19}" width="11" height="23" fill="{GREEN}">
      <animate attributeName="x" dur="{CYCLE}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{ckt}" values="{cvals}"/>
      <animate attributeName="opacity" dur="1s" repeatCount="indefinite" calcMode="discrete" keyTimes="0;0.5" values="1;0"/>
    </rect>
  </g>

  <line x1="412" y1="208" x2="955" y2="208" stroke="#30363d" stroke-width="1.5"/>
  <line x1="412" y1="208" x2="955" y2="208" stroke="url(#sweep)" stroke-width="2"/>

  <text x="412" y="240" font-family="{MONO}" font-size="14" fill="#8b949e">Bogotá, Colombia  ·  Gradient AI / 3PL  ·  gradientai.lat</text>

  <rect x="0.75" y="0.75" width="{W - 1.5}" height="{H - 1.5}" rx="17.5" fill="none" stroke="#30363d" stroke-width="1.5"/>
</g>
</svg>
'''

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(svg, encoding="utf-8")
print(f"OK {OUT} ({len(svg)} bytes)")
