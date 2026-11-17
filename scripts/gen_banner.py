"""Genera assets/banner.svg: banner animado (SMIL) para el README del perfil.

Uso: python scripts/gen_banner.py assets/banner.svg
Para cambiar las frases que se escriben solas, edita LINES.
"""
import math
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dumbbell import outline  # noqa: E402

OUT = Path(sys.argv[1])

W, H = 1000, 280
GREEN = "#3fb950"
MONO = "Consolas, 'SF Mono', Menlo, 'DejaVu Sans Mono', 'Liberation Mono', monospace"
SANS = "'Segoe UI', Ubuntu, 'Helvetica Neue', Arial, sans-serif"
EASE = 'calcMode="spline" keyTimes="0;0.5;1" keySplines="0.45 0 0.55 1;0.45 0 0.55 1"'

# ---------- texto que se escribe solo ----------
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

times = sorted({t for ev in all_ev for t, _ in ev})
cur = [(t, X0 + 2 + max(value_at(ev, t) for ev in all_ev)) for t in times]
ckt, cvals = smil_lists(cur)
cursor_base = X0 + 2 + len(LINES[0]) * CW

# ---------- logo: 4 "mancuernas" calcadas del logo de Gradient AI ----------
# (centro1, radio1, centro2, radio2, medio-ancho del cuello, gris?) en coordenadas del calco
PIECES = [
    ((146.5, 294.8), 85.5, (325.2, 485.5), 66.7, 10.5, True),
    ((341.8, 293.8), 82.8, (513.5, 121.2), 60.9, 9.0, False),
    ((530.0, 294.5), 72.1, (677.2, 440.8), 50.9, 8.8, False),
    ((519.0, 486.5), 63.1, (391.5, 610.0), 44.3, 8.8, False),
]
LCX, LCY = 394.3, 357.3     # centro del logo en el calco
CX, CY = 205, 140           # centro del logo en el banner
S = 0.36                    # escala calco -> banner
RIM = (7, 9)                # grosor visible de la placa (en coords del calco)

piece_defs, piece_svg = [], []
for k, (c1, r1, c2, r2, w, gray) in enumerate(PIECES):
    _, d = outline(c1, r1, c2, r2, w)
    piece_defs.append(f'<path id="p{k}" d="{d}"/><clipPath id="pc{k}"><use href="#p{k}"/></clipPath>')
    # direccion hacia afuera para la entrada animada
    mx, my = (c1[0] + c2[0]) / 2 - LCX, (c1[1] + c2[1]) / 2 - LCY
    n = math.hypot(mx, my) or 1
    ox, oy = mx / n * 120, my / n * 120
    delay = 0.12 * k
    intro_dur = 1.3
    kt = f"0;{delay / intro_dur:.3f};1"
    face = "url(#faceGray)" if gray else "url(#faceWhite)"
    rim = "#2a2a2a" if gray else "#8d8d8a"
    bob = 2.2 / S
    piece_svg.append(f'''
    <g>
      <animateTransform attributeName="transform" type="translate" dur="{intro_dur}s" fill="freeze"
        values="{ox:.1f} {oy:.1f};{ox:.1f} {oy:.1f};0 0" keyTimes="{kt}" calcMode="spline" keySplines="0 0 1 1;0.16 1 0.3 1"/>
      <animate attributeName="opacity" dur="{intro_dur}s" fill="freeze" values="0;0;1" keyTimes="{kt}"/>
      <g>
        <animateTransform attributeName="transform" type="translate" dur="{5.2 + k * 0.7:.1f}s" repeatCount="indefinite"
          values="0 0;0 {-bob:.1f};0 0" {EASE}/>
        <use href="#p{k}" x="{RIM[0]}" y="{RIM[1]}" fill="{rim}"/>
        <use href="#p{k}" fill="{face}"/>
        <rect x="0" y="0" width="800" height="720" fill="url(#sheen)" clip-path="url(#pc{k})"/>
      </g>
    </g>''')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Samuel Gómez Dávila — Ingeniero Industrial · Python · Automatización · Datos">
<title>Samuel Gómez Dávila</title>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#0b0f14"/><stop offset="1" stop-color="#161b22"/>
  </linearGradient>
  <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">
    <circle cx="2" cy="2" r="1" fill="#ffffff" opacity="0.07"/>
  </pattern>
  <radialGradient id="halo"><stop offset="0" stop-color="#ffffff" stop-opacity="0.12"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/></radialGradient>
  <linearGradient id="faceWhite" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#f4f4f2"/><stop offset="1" stop-color="#dcdcd9"/>
  </linearGradient>
  <linearGradient id="faceGray" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#484848"/><stop offset="1" stop-color="#777776"/>
  </linearGradient>
  <linearGradient id="sheen" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="260" y2="260">
    <stop offset="0" stop-color="#ffffff" stop-opacity="0"/>
    <stop offset="0.5" stop-color="#ffffff" stop-opacity="0.75"/>
    <stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
    <animateTransform attributeName="gradientTransform" type="translate" dur="7s" repeatCount="indefinite"
      values="-420 -420;-420 -420;760 760" keyTimes="0;0.55;1"/>
  </linearGradient>
  <linearGradient id="nameFill" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#9aa4ae"/></linearGradient>
  <linearGradient id="sweep" gradientUnits="userSpaceOnUse" x1="250" y1="0" x2="410" y2="0">
    <stop offset="0" stop-color="{GREEN}" stop-opacity="0"/><stop offset="0.5" stop-color="{GREEN}"/><stop offset="1" stop-color="{GREEN}" stop-opacity="0"/>
    <animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="720 0" dur="4s" repeatCount="indefinite"/>
  </linearGradient>
  <filter id="glow" x="-200%" y="-200%" width="500%" height="500%">
    <feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="shadow" x="-30%" y="-30%" width="160%" height="160%">
    <feDropShadow dx="1" dy="5" stdDeviation="6" flood-color="#000000" flood-opacity="0.75"/>
  </filter>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath>
  {"".join(piece_defs)}
  {"".join(typing_defs)}
</defs>

<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" fill="url(#dots)"/>

  <!-- halo + orbitas -->
  <circle cx="{CX}" cy="{CY}" r="120" fill="url(#halo)">
    <animate attributeName="r" dur="6s" repeatCount="indefinite" values="112;134;112" {EASE}/>
  </circle>
  <g transform="translate({CX} {CY})">
    <g>
      <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="28s" repeatCount="indefinite"/>
      <circle r="134" fill="none" stroke="{GREEN}" stroke-opacity="0.35" stroke-width="1.2" stroke-dasharray="2 10"/>
      <circle cx="134" cy="0" r="4" fill="{GREEN}" filter="url(#glow)"/>
    </g>
    <g>
      <animateTransform attributeName="transform" type="rotate" from="360" to="0" dur="46s" repeatCount="indefinite"/>
      <circle r="154" fill="none" stroke="#8b949e" stroke-opacity="0.25" stroke-width="1" stroke-dasharray="1 7"/>
      <circle cx="-154" cy="0" r="2.5" fill="#c9d1d9"/>
    </g>
  </g>

  <!-- logo -->
  <g transform="translate({CX} {CY})">
    <g>
      <animateTransform attributeName="transform" type="translate" dur="6s" repeatCount="indefinite" values="0 0;0 -7;0 0" {EASE}/>
      <g filter="url(#shadow)">
        <g transform="scale({S}) translate({-LCX} {-LCY})">{"".join(piece_svg)}
        </g>
      </g>
    </g>
  </g>

  <!-- texto -->
  <text x="412" y="80" font-family="{MONO}" font-size="14" letter-spacing="4" fill="{GREEN}">HOLA, SOY</text>
  <text x="410" y="132" font-family="{SANS}" font-size="46" font-weight="700" fill="url(#nameFill)">Samuel Gómez Dávila<animate attributeName="opacity" values="0;1" dur="0.9s" begin="0s" fill="freeze"/></text>

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
