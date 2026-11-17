"""Geometria de las 'mancuernas' del logo: dos circulos unidos por filetes tangentes."""
import math


def _fillet(c1, r1, c2, r2, R, s):
    dx, dy = c2[0] - c1[0], c2[1] - c1[1]
    d = math.hypot(dx, dy)
    ux, uy = dx / d, dy / d
    nx, ny = -uy, ux
    a, b = r1 + R, r2 + R
    x = (a * a - b * b + d * d) / (2 * d)
    y = s * math.sqrt(max(a * a - x * x, 0.0))
    P = (c1[0] + ux * x + nx * y, c1[1] + uy * x + ny * y)
    T1 = (c1[0] + r1 * (P[0] - c1[0]) / a, c1[1] + r1 * (P[1] - c1[1]) / a)
    T2 = (c2[0] + r2 * (P[0] - c2[0]) / b, c2[1] + r2 * (P[1] - c2[1]) / b)
    return P, T1, T2


def neck_half(c1, r1, c2, r2, R):
    P, _, _ = _fillet(c1, r1, c2, r2, R, 1)
    dx, dy = c2[0] - c1[0], c2[1] - c1[1]
    d = math.hypot(dx, dy)
    dist = abs((P[0] - c1[0]) * (-dy / d) + (P[1] - c1[1]) * (dx / d))
    return dist - R


def R_for_neck(c1, r1, c2, r2, w):
    lo, hi = 0.5, 2000.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if neck_half(c1, r1, c2, r2, mid) > w:   # el cuello crece con R
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def _ang(c, p):
    return math.atan2(p[1] - c[1], p[0] - c[0])


def _arc_samples(c, r, a0, a1, n):
    return [(c[0] + r * math.cos(a0 + (a1 - a0) * i / n), c[1] + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def _norm(a):
    while a <= -math.pi:
        a += 2 * math.pi
    while a > math.pi:
        a -= 2 * math.pi
    return a


def outline(c1, r1, c2, r2, w, n=90):
    """Devuelve (puntos_poligono, path_svg)."""
    R = R_for_neck(c1, r1, c2, r2, w)
    Pp, T1p, T2p = _fillet(c1, r1, c2, r2, R, 1)
    Pm, T1m, T2m = _fillet(c1, r1, c2, r2, R, -1)
    far1 = _ang(c1, (2 * c1[0] - c2[0], 2 * c1[1] - c2[1]))
    far2 = _ang(c2, (2 * c2[0] - c1[0], 2 * c2[1] - c1[1]))

    segs = []  # (center, radius, a_start, a_end)

    def big_arc(c, r, pa, pb, far):
        a0, a1 = _ang(c, pa), _ang(c, pb)
        # elegir direccion que pase por 'far'
        d = _norm(a1 - a0)
        long_d = d - 2 * math.pi if d > 0 else d + 2 * math.pi
        for cand in (d, long_d):
            mid = a0 + cand / 2
            if abs(_norm(mid - far)) < math.pi / 2:
                return (c, r, a0, a0 + cand)
        return (c, r, a0, a0 + long_d)

    def small_arc(P, R, pa, pb):
        a0, a1 = _ang(P, pa), _ang(P, pb)
        return (P, R, a0, a0 + _norm(a1 - a0))

    segs.append(big_arc(c1, r1, T1p, T1m, far1))
    segs.append(small_arc(Pm, R, T1m, T2m))
    segs.append(big_arc(c2, r2, T2m, T2p, far2))
    segs.append(small_arc(Pp, R, T2p, T1p))

    pts = []
    for c, r, a0, a1 in segs:
        pts += _arc_samples(c, r, a0, a1, n)[:-1]

    def f(v):
        return f"{v:.2f}".rstrip("0").rstrip(".")

    d = f"M{f(T1p[0])} {f(T1p[1])}"
    for c, r, a0, a1 in segs:
        end = (c[0] + r * math.cos(a1), c[1] + r * math.sin(a1))
        large = 1 if abs(a1 - a0) > math.pi else 0
        sweep = 1 if a1 > a0 else 0
        d += f"A{f(r)} {f(r)} 0 {large} {sweep} {f(end[0])} {f(end[1])}"
    d += "Z"
    return pts, d
