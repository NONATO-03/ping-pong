import pygame
import math
import random

from game.ui.neon import (
    NEON_PURPLE, NEON_GOLD, NEON_GREEN, NEON_ORANGE, NEON_PINK,
    glow_lines, glow_line, glow_arc, lighten,
)

# FUNÇOES DE DESENHO DAS ARENAS
# A geometria das paredes é idêntica à original (a física em bola.py depende
# dela); apenas o acabamento visual mudou para o estilo neon.

_CACHE = {}


def _cached_layer(key, size, builder):
    """Constrói (uma única vez) uma camada SRCALPHA do tamanho da tela."""
    if _CACHE.get(key) is None or _CACHE[key].get_size() != size:
        surf = pygame.Surface(size, pygame.SRCALPHA)
        builder(surf)
        _CACHE[key] = surf
    return _CACHE[key]


def _draw_floor(surf, x, y, w, h):
    """Preenchimento sutil do 'chão' da arena para destacar a área de jogo."""
    pygame.draw.rect(surf, (14, 10, 36, 150), (x, y, w, h))
    # Reflexo suave no centro
    pygame.draw.rect(surf, (30, 20, 70, 60), (x, y + h // 3, w, h // 3))


def _draw_center_line(surf, center_x, y_top, y_bottom):
    """Linha divisória tracejada com brilho e círculo central."""
    dash_h, gap = 22, 16
    y = y_top + 8
    while y < y_bottom - 8:
        y_end = min(y + dash_h, y_bottom - 8)
        pygame.draw.line(surf, NEON_PURPLE[:3] + (34,), (center_x, y), (center_x, y_end), 12)
        pygame.draw.line(surf, lighten(NEON_PURPLE, 0.3) + (170,), (center_x, y), (center_x, y_end), 4)
        y += dash_h + gap
    # Círculo central
    center_y = (y_top + y_bottom) // 2
    pygame.draw.circle(surf, NEON_PURPLE[:3] + (30,), (center_x, center_y), 56, 10)
    pygame.draw.circle(surf, lighten(NEON_PURPLE, 0.35) + (180,), (center_x, center_y), 52, 3)
    pygame.draw.circle(surf, lighten(NEON_PURPLE, 0.5) + (200,), (center_x, center_y), 5)


def _draw_corner_ticks(surf, x, y, w, h, accent):
    """Pequenos detalhes nos cantos da arena."""
    L = 26
    for cx, cy, dx, dy in [(x, y, 1, 1), (x + w, y, -1, 1),
                           (x, y + h, 1, -1), (x + w, y + h, -1, -1)]:
        pygame.draw.line(surf, lighten(accent, 0.6) + (230,),
                         (cx + dx * 10, cy + dy * 10), (cx + dx * (10 + L), cy + dy * 10), 3)
        pygame.draw.line(surf, lighten(accent, 0.6) + (230,),
                         (cx + dx * 10, cy + dy * 10), (cx + dx * 10, cy + dy * (10 + L)), 3)


def draw_arena_alpha(screen, ARENA_X, ARENA_Y, ARENA_W, ARENA_H):
    """Arena padrão: retângulo fechado com moldura neon."""
    def build(surf):
        _draw_floor(surf, ARENA_X, ARENA_Y, ARENA_W, ARENA_H)
        _draw_center_line(surf, ARENA_X + ARENA_W // 2, ARENA_Y, ARENA_Y + ARENA_H)
        rect = pygame.Rect(ARENA_X, ARENA_Y, ARENA_W, ARENA_H)
        glow_lines(surf, NEON_PURPLE,
                   [rect.topleft, rect.topright, rect.bottomright, rect.bottomleft],
                   width=6, closed=True)
        _draw_corner_ticks(surf, ARENA_X, ARENA_Y, ARENA_W, ARENA_H, NEON_PURPLE)

    layer = _cached_layer(("alpha", ARENA_X, ARENA_Y, ARENA_W, ARENA_H),
                          screen.get_size(), build)
    screen.blit(layer, (0, 0))


def draw_arena_beta(screen, ARENA_X, ARENA_Y, ARENA_W, ARENA_H, angle=0):
    """Arena padrão com uma barra giratória dourada no centro."""
    # Parte estática (igual à alpha, mas com detalhes dourados)
    def build(surf):
        _draw_floor(surf, ARENA_X, ARENA_Y, ARENA_W, ARENA_H)
        _draw_center_line(surf, ARENA_X + ARENA_W // 2, ARENA_Y, ARENA_Y + ARENA_H)
        rect = pygame.Rect(ARENA_X, ARENA_Y, ARENA_W, ARENA_H)
        glow_lines(surf, NEON_PURPLE,
                   [rect.topleft, rect.topright, rect.bottomright, rect.bottomleft],
                   width=6, closed=True)
        _draw_corner_ticks(surf, ARENA_X, ARENA_Y, ARENA_W, ARENA_H, NEON_GOLD)

    layer = _cached_layer(("beta", ARENA_X, ARENA_Y, ARENA_W, ARENA_H),
                          screen.get_size(), build)
    screen.blit(layer, (0, 0))

    # Barra giratória (dinâmica, desenhada a cada frame)
    center_x = ARENA_X + ARENA_W // 2
    center_y = ARENA_Y + ARENA_H // 2
    barra_len = 170
    barra_thick = 18
    half = barra_len // 2 + 30
    bar_surf = pygame.Surface((half * 2, half * 2), pygame.SRCALPHA)
    x1 = half - math.cos(angle) * barra_len / 2
    y1 = half - math.sin(angle) * barra_len / 2
    x2 = half + math.cos(angle) * barra_len / 2
    y2 = half + math.sin(angle) * barra_len / 2
    glow_line(bar_surf, NEON_GOLD, (x1, y1), (x2, y2), barra_thick // 2)
    pygame.draw.circle(bar_surf, lighten(NEON_GOLD, 0.6) + (255,), (half, half), 7)
    screen.blit(bar_surf, (center_x - half, center_y - half))


def draw_arena_gamma(screen, ARENA_X, ARENA_Y, ARENA_W, ARENA_H):
    """Arena com as paredes laterais curvadas para dentro ("barrigas")."""
    ARENA_BOTTOM = ARENA_Y + ARENA_H

    def build(surf):
        _draw_floor(surf, ARENA_X, ARENA_Y, ARENA_W, ARENA_H)
        _draw_center_line(surf, ARENA_X + ARENA_W // 2, ARENA_Y, ARENA_BOTTOM)
        # Curvas laterais (mesma geometria dos arcos originais)
        glow_arc(surf, NEON_GREEN,
                 pygame.Rect(ARENA_X - 50, ARENA_Y, 100, ARENA_H), 1.57, 4.71, 6)
        glow_arc(surf, NEON_GREEN,
                 pygame.Rect(ARENA_X + ARENA_W - 50, ARENA_Y, 100, ARENA_H), -1.57, 1.57, 6)
        # Bordas retas superior e inferior
        glow_line(surf, NEON_PURPLE, (ARENA_X, ARENA_Y), (ARENA_X + ARENA_W, ARENA_Y), 6)
        glow_line(surf, NEON_PURPLE, (ARENA_X, ARENA_BOTTOM), (ARENA_X + ARENA_W, ARENA_BOTTOM), 6)

    layer = _cached_layer(("gamma", ARENA_X, ARENA_Y, ARENA_W, ARENA_H),
                          screen.get_size(), build)
    screen.blit(layer, (0, 0))


def draw_arena_delta(screen, ARENA_X, ARENA_Y, ARENA_W, ARENA_H):
    """
    Arena com paredes laterais com uma depressão retangular no centro '[ ]'.
    A arena é totalmente fechada e 20% mais larga (igual à original).
    """
    def build(surf):
        # MODIFICAÇÃO PARA AUMENTAR A LARGURA (mantida da versão original)
        fator_largura = 1.2
        largura_original = ARENA_W
        W = int(ARENA_W * fator_largura)
        X = int(ARENA_X - (W - largura_original) / 2)

        _draw_floor(surf, X, ARENA_Y, W, ARENA_H)
        center_x = X + W // 2
        _draw_center_line(surf, center_x, ARENA_Y, ARENA_Y + ARENA_H)

        glow_line(surf, NEON_PURPLE, (X, ARENA_Y), (X + W, ARENA_Y), 6)
        glow_line(surf, NEON_PURPLE, (X, ARENA_Y + ARENA_H), (X + W, ARENA_Y + ARENA_H), 6)

        indent_height = ARENA_H / 3
        indent_depth = W / 15
        indent_start_y = ARENA_Y + (ARENA_H - indent_height) / 2
        indent_end_y = indent_start_y + indent_height

        left_wall_points = [
            (X, ARENA_Y),
            (X, indent_start_y),
            (X + indent_depth, indent_start_y),
            (X + indent_depth, indent_end_y),
            (X, indent_end_y),
            (X, ARENA_Y + ARENA_H),
        ]
        glow_lines(surf, NEON_ORANGE, left_wall_points, 6)

        right_wall_x = X + W
        right_wall_points = [
            (right_wall_x, ARENA_Y),
            (right_wall_x, indent_start_y),
            (right_wall_x - indent_depth, indent_start_y),
            (right_wall_x - indent_depth, indent_end_y),
            (right_wall_x, indent_end_y),
            (right_wall_x, ARENA_Y + ARENA_H),
        ]
        glow_lines(surf, NEON_ORANGE, right_wall_points, 6)

    layer = _cached_layer(("delta", ARENA_X, ARENA_Y, ARENA_W, ARENA_H),
                          screen.get_size(), build)
    screen.blit(layer, (0, 0))


def draw_arena_epsilon(screen, ARENA_X, ARENA_Y, ARENA_W_original, ARENA_H,
                       fator_largura=1.3,
                       top_line_reduction=0,
                       bottom_line_reduction=0):
    """
    Arena com paredes personalizadas e aberturas diagonais (geometria original):
    - Parede Esquerda: metade inferior com formato '['
    - Parede Direita: metade superior com formato ']'
    """
    def build(surf):
        W = int(ARENA_W_original * fator_largura)
        X = int(ARENA_X - (W - ARENA_W_original) / 2)

        _draw_floor(surf, X, ARENA_Y, W, ARENA_H)
        center_x = X + W // 2
        _draw_center_line(surf, center_x, ARENA_Y, ARENA_Y + ARENA_H)

        indent_height = ARENA_H / 2
        indent_depth = W / 15
        right_wall_x = X + W

        left_wall_points = [
            (X, ARENA_Y),
            (X, ARENA_Y + indent_height),
            (X + indent_depth, ARENA_Y + indent_height),
            (X + indent_depth, ARENA_Y + ARENA_H),
        ]
        glow_lines(surf, NEON_PINK, left_wall_points, 6)

        right_wall_points = [
            (right_wall_x - indent_depth, ARENA_Y),
            (right_wall_x - indent_depth, ARENA_Y + indent_height),
            (right_wall_x, ARENA_Y + indent_height),
            (right_wall_x, ARENA_Y + ARENA_H),
        ]
        glow_lines(surf, NEON_PINK, right_wall_points, 6)

        start_pos_top = (X, ARENA_Y)
        end_pos_top = (right_wall_x - indent_depth - top_line_reduction, ARENA_Y)
        if end_pos_top[0] > start_pos_top[0]:
            glow_line(surf, NEON_PURPLE, start_pos_top, end_pos_top, 6)

        start_pos_bottom = (X + indent_depth + bottom_line_reduction, ARENA_Y + ARENA_H)
        end_pos_bottom = (X + W, ARENA_Y + ARENA_H)
        if start_pos_bottom[0] < end_pos_bottom[0]:
            glow_line(surf, NEON_PURPLE, start_pos_bottom, end_pos_bottom, 6)

    layer = _cached_layer(("epsilon", ARENA_X, ARENA_Y, ARENA_W_original, ARENA_H,
                           fator_largura, top_line_reduction, bottom_line_reduction),
                          screen.get_size(), build)
    screen.blit(layer, (0, 0))


def draw_arena_aleatoria(screen, ARENA_X, ARENA_Y, ARENA_W, ARENA_H):
    """Desenha uma arena aleatória escolhendo uma das outras arenas."""
    arenas = [
        draw_arena_alpha,
        draw_arena_beta,
        draw_arena_gamma,
        draw_arena_delta,
        draw_arena_epsilon,
    ]
    arena_func = random.choice(arenas)
    if arena_func == draw_arena_beta:
        angle = random.uniform(0, 2 * math.pi)
        arena_func(screen, ARENA_X, ARENA_Y, ARENA_W, ARENA_H, angle=angle)
    else:
        arena_func(screen, ARENA_X, ARENA_Y, ARENA_W, ARENA_H)
