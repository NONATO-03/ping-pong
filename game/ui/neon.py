import math
import random
import time

import pygame

from config import FONT_PATH

# SISTEMA DE DESIGN "NEON ARCADE"
# Paleta, fontes e primitivas de desenho com brilho usadas por todas as telas
# do jogo. Tudo aqui é somente visual: nenhuma função altera estado da partida.

# Paleta principal
BG_DEEP = (7, 5, 20)          # topo do céu
BG_HORIZON = (70, 22, 90)     # brilho do horizonte
GRID_COLOR = (56, 32, 96)     # linhas da grade em perspectiva
GRID_BRIGHT = (140, 62, 150)  # linhas da grade que "correm"
STAR_COLOR = (200, 210, 255)

NEON_CYAN = (0, 229, 255)     # jogador da esquerda
NEON_PINK = (255, 64, 180)    # jogador da direita
NEON_PURPLE = (150, 110, 255) # estrutura/arena
NEON_GOLD = (255, 200, 60)
NEON_GREEN = (60, 255, 170)
NEON_ORANGE = (255, 140, 50)
NEON_RED = (255, 70, 90)

TEXT_MAIN = (235, 240, 255)
TEXT_DIM = (150, 150, 195)
PANEL_FILL = (16, 12, 38, 215)


def lighten(color, f):
    """Aproxima a cor do branco por um fator f entre 0 e 1."""
    return tuple(int(c + (255 - c) * f) for c in color[:3])


def darken(color, f):
    """Aproxima a cor do preto por um fator f entre 0 e 1."""
    return tuple(int(c * (1 - f)) for c in color[:3])


def lerp_color(c1, c2, t):
    """Interpola linearmente entre duas cores."""
    t = max(0.0, min(1.0, t))
    return tuple(int(a + (b - a) * t) for a, b in zip(c1[:3], c2[:3]))


# Fontes (cache para não recriar a cada frame)
_FONTS = {}


def get_font(size):
    if size not in _FONTS:
        _FONTS[size] = pygame.font.Font(FONT_PATH, size)
    return _FONTS[size]


# Halos radiais (cache)
_GLOWS = {}


def radial_glow(radius, color, max_alpha=90):
    """Retorna uma superfície com um brilho radial suave (cacheada)."""
    key = (radius, color, max_alpha)
    if key not in _GLOWS:
        surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        steps = 12
        for i in range(steps, 0, -1):
            r = int(radius * i / steps)
            alpha = int(max_alpha * ((steps - i) / steps) ** 2)
            if alpha > 0 and r > 0:
                pygame.draw.circle(surf, color[:3] + (alpha,), (radius, radius), r)
        _GLOWS[key] = surf
    return _GLOWS[key]


def blit_glow(target, center, radius, color, max_alpha=90):
    surf = radial_glow(radius, color, max_alpha)
    target.blit(surf, (center[0] - radius, center[1] - radius))


# Texto neon (núcleo claro + halo colorido), com cache
_TEXT_CACHE = {}


def neon_text(text, size, color, glow=1.0):
    """Renderiza texto com halo neon. Retorna uma superfície SRCALPHA."""
    key = (text, size, color, round(glow, 2))
    if key not in _TEXT_CACHE:
        if len(_TEXT_CACHE) > 600:
            _TEXT_CACHE.clear()
        font = get_font(size)
        core = font.render(text, True, lighten(color, 0.65))
        w, h = core.get_size()
        pad = max(8, size // 2)
        surf = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
        if glow > 0 and w > 6 and h > 6:
            # Brilho dilatado no formato das letras: o texto colorido é
            # carimbado em anéis de deslocamentos com alpha decrescente
            halo = font.render(text, True, color)
            for radius, alpha in ((6, 14), (3, 30)):
                halo.set_alpha(int(alpha * glow))
                for i in range(8):
                    ang = i * math.tau / 8
                    dx = int(round(math.cos(ang) * radius))
                    dy = int(round(math.sin(ang) * radius))
                    surf.blit(halo, (pad + dx, pad + dy))
        surf.blit(core, (pad, pad))
        _TEXT_CACHE[key] = surf
    return _TEXT_CACHE[key]


def draw_neon_text(target, text, size, color, center=None, topleft=None, glow=1.0):
    """Desenha texto neon e retorna o rect ocupado na tela."""
    surf = neon_text(text, size, color, glow)
    if center is not None:
        rect = surf.get_rect(center=center)
    else:
        rect = surf.get_rect(topleft=topleft or (0, 0))
    target.blit(surf, rect)
    return rect


# Primitivas com brilho (desenham em superfícies SRCALPHA)

def glow_lines(surf, color, points, width=6, closed=False):
    core = lighten(color, 0.55)
    pygame.draw.lines(surf, color[:3] + (26,), closed, points, width * 4)
    pygame.draw.lines(surf, color[:3] + (70,), closed, points, width * 2)
    pygame.draw.lines(surf, core + (255,), closed, points, width)


def glow_line(surf, color, a, b, width=6):
    glow_lines(surf, color, [a, b], width)


def glow_rect_outline(surf, color, rect, width=4, radius=0):
    core = lighten(color, 0.55)
    pygame.draw.rect(surf, color[:3] + (26,), rect.inflate(width * 5, width * 5),
                     width=width * 4, border_radius=radius + width * 2)
    pygame.draw.rect(surf, color[:3] + (70,), rect.inflate(width * 2, width * 2),
                     width=width * 2, border_radius=radius + width)
    pygame.draw.rect(surf, core + (255,), rect, width=width, border_radius=radius)


def glow_arc(surf, color, rect, start, end, width=6):
    core = lighten(color, 0.55)
    pygame.draw.arc(surf, color[:3] + (30,), rect.inflate(width * 3, width * 3),
                    start, end, width * 3)
    pygame.draw.arc(surf, color[:3] + (80,), rect.inflate(width, width),
                    start, end, width * 2)
    pygame.draw.arc(surf, core + (255,), rect, start, end, width)


# Painéis (cartões escuros com borda neon), com cache
_PANELS = {}


def panel_surface(size, accent=NEON_PURPLE, radius=18, border=2,
                  fill=PANEL_FILL, glow=True):
    key = (size, accent, radius, border, fill, glow)
    if key not in _PANELS:
        if len(_PANELS) > 80:
            _PANELS.clear()
        pad = 20
        w, h = size
        surf = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
        r = pygame.Rect(pad, pad, w, h)
        if glow:
            pygame.draw.rect(surf, accent[:3] + (20,), r.inflate(18, 18),
                             border_radius=radius + 9)
            pygame.draw.rect(surf, accent[:3] + (40,), r.inflate(7, 7),
                             border_radius=radius + 4)
        pygame.draw.rect(surf, fill, r, border_radius=radius)
        pygame.draw.rect(surf, lighten(accent, 0.25) + (220,), r,
                         width=border, border_radius=radius)
        _PANELS[key] = surf
    return _PANELS[key]


def draw_panel(target, rect, accent=NEON_PURPLE, radius=18, border=2,
               fill=PANEL_FILL, glow=True):
    surf = panel_surface((rect.w, rect.h), accent, radius, border, fill, glow)
    target.blit(surf, (rect.x - 20, rect.y - 20))


# Fundo animado: gradiente + estrelas + grade em perspectiva + vinheta
_BG = {}


def _build_gradient(W, H):
    stops = [
        (0.00, (5, 4, 18)),
        (0.50, (13, 8, 36)),
        (0.66, (34, 12, 58)),
        (0.685, BG_HORIZON),
        (0.72, (26, 10, 46)),
        (1.00, (10, 6, 26)),
    ]
    strip = pygame.Surface((1, 512))
    for y in range(512):
        t = y / 511
        for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
            if t0 <= t <= t1:
                f = 0 if t1 == t0 else (t - t0) / (t1 - t0)
                strip.set_at((0, y), lerp_color(c0, c1, f))
                break
    return pygame.transform.smoothscale(strip, (W, H))


def _build_stars(W, H, horizon_y):
    rng = random.Random(7)
    static = pygame.Surface((W, H), pygame.SRCALPHA)
    twinkle = []
    for _ in range(150):
        x = rng.randint(0, W - 1)
        y = rng.randint(0, int(horizon_y * 0.96))
        b = rng.randint(40, 150)
        pygame.draw.circle(static, STAR_COLOR + (b,), (x, y),
                           1 if rng.random() < 0.8 else 2)
    for _ in range(45):
        twinkle.append((rng.randint(0, W - 1),
                        rng.randint(0, int(horizon_y * 0.9)),
                        rng.uniform(0, math.tau),
                        rng.uniform(0.6, 2.2)))
    return static, twinkle


def _build_vignette(W, H):
    small_w, small_h = 160, 90
    small = pygame.Surface((small_w, small_h), pygame.SRCALPHA)
    cx, cy = small_w / 2, small_h / 2
    for x in range(small_w):
        for y in range(small_h):
            d = math.hypot((x - cx) / cx, (y - cy) / cy) / math.sqrt(2)
            alpha = int(170 * max(0.0, d - 0.45) ** 2.2)
            if alpha:
                small.set_at((x, y), (0, 0, 0, min(255, alpha)))
    return pygame.transform.smoothscale(small, (W, H))


def _build_scanlines(W, H):
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    for y in range(0, H, 4):
        pygame.draw.line(surf, (0, 0, 0, 28), (0, y), (W, y))
    return surf


def _ensure_bg(W, H):
    if _BG.get('size') != (W, H):
        horizon_y = int(H * 0.685)
        _BG['size'] = (W, H)
        _BG['horizon'] = horizon_y
        _BG['grad'] = _build_gradient(W, H)
        _BG['stars'], _BG['twinkle'] = _build_stars(W, H, horizon_y)
        _BG['vignette'] = _build_vignette(W, H)
        _BG['scan'] = _build_scanlines(W, H)


def draw_background(target, t=None, grid=True, scanlines=True):
    """Desenha o cenário synthwave completo (usado por todas as telas)."""
    W, H = target.get_size()
    _ensure_bg(W, H)
    if t is None:
        t = time.time()
    horizon_y = _BG['horizon']

    target.blit(_BG['grad'], (0, 0))
    target.blit(_BG['stars'], (0, 0))

    # Estrelas piscando (desenhadas direto, o fundo é escuro)
    for (x, y, phase, speed) in _BG['twinkle']:
        b = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(t * speed + phase))
        c = tuple(int(ch * b) for ch in STAR_COLOR)
        pygame.draw.circle(target, c, (x, y), 1)

    if grid:
        # Linhas verticais convergindo para o ponto de fuga
        vp_x = W // 2
        for i in range(-14, 15):
            if i == 0:
                continue
            x_h = vp_x + i * 14
            x_b = vp_x + int(i * (W / 16) * 1.9)
            pygame.draw.line(target, GRID_COLOR, (x_h, horizon_y), (x_b, H), 1)
        # Linhas horizontais que "correm" em direção à câmera
        rows = 10
        scroll = (t * 0.35) % 1.0
        for k in range(rows):
            u = (k + scroll) / rows
            y = horizon_y + int((H - horizon_y) * (u ** 2.1))
            c = lerp_color(GRID_COLOR, GRID_BRIGHT, u)
            pygame.draw.line(target, c, (0, y), (W, y), 1 if u < 0.55 else 2)
        # Brilho do horizonte
        pygame.draw.line(target, (185, 90, 200), (0, horizon_y), (W, horizon_y), 2)
        pygame.draw.line(target, (90, 40, 120), (0, horizon_y + 2), (W, horizon_y + 2), 2)

    target.blit(_BG['vignette'], (0, 0))
    if scanlines:
        target.blit(_BG['scan'], (0, 0))
