import pygame

def draw_arena_alpha(screen, ARENA_X, ARENA_Y, ARENA_W, ARENA_H):
    pygame.draw.rect(screen, (255,255,255), (ARENA_X, ARENA_Y, ARENA_W, ARENA_H), width=8)
    center_x = ARENA_X + ARENA_W//2
    pygame.draw.line(screen, (180,180,180), (center_x, ARENA_Y), (center_x, ARENA_Y+ARENA_H), width=6)

import math

def draw_arena_beta(screen, ARENA_X, ARENA_Y, ARENA_W, ARENA_H, angle=0):
    ARENA_BOTTOM = ARENA_Y + ARENA_H
    ARENA_RIGHT = ARENA_X + ARENA_W

    # Arena padrão
    pygame.draw.rect(screen, (255,255,255), (ARENA_X, ARENA_Y, ARENA_W, ARENA_H), width=8)
    center_x = ARENA_X + ARENA_W//2
    center_y = ARENA_Y + ARENA_H//2
    pygame.draw.line(screen, (180,180,180), (center_x, ARENA_Y), (center_x, ARENA_Y+ARENA_H), width=6)

    # Barra giratória no centro
    barra_len = 170
    barra_thick = 18
    # Calcula os pontos da barra girando
    x1 = center_x - math.cos(angle) * barra_len//2
    y1 = center_y - math.sin(angle) * barra_len//2
    x2 = center_x + math.cos(angle) * barra_len//2
    y2 = center_y + math.sin(angle) * barra_len//2
    pygame.draw.line(screen, (255,255,255), (x1, y1), (x2, y2), barra_thick)

def draw_arena_gamma(screen, ARENA_X, ARENA_Y, ARENA_W, ARENA_H):
    pygame.draw.rect(screen, (255,255,255), (ARENA_X, ARENA_Y, ARENA_W, ARENA_H), width=0)
    for side in [ARENA_Y, ARENA_Y+ARENA_H-8]:
        for i in range(5):
            x = ARENA_X + i*(ARENA_W//5)
            pygame.draw.rect(screen, (255,255,255), (x, side, ARENA_W//10, 8), border_radius=2)
    pygame.draw.rect(screen, (255,255,255), (ARENA_X, ARENA_Y, ARENA_W, ARENA_H), width=8)
    center_x = ARENA_X + ARENA_W//2
    pygame.draw.line(screen, (180,180,180), (center_x, ARENA_Y), (center_x, ARENA_Y+ARENA_H), width=6)

def draw_arena_delta(screen, ARENA_X, ARENA_Y, ARENA_W, ARENA_H):
    bar_w = ARENA_W//6
    bar_h = ARENA_H//3
    pygame.draw.rect(screen, (255,255,255), (ARENA_X, ARENA_Y, bar_w, ARENA_H), width=0)
    pygame.draw.rect(screen, (255,255,255), (ARENA_X+ARENA_W-bar_w, ARENA_Y, bar_w, ARENA_H), width=0)
    pygame.draw.rect(screen, (255,255,255), (ARENA_X, ARENA_Y+bar_h, ARENA_W, bar_h), width=0)
    center_x = ARENA_X + ARENA_W//2
    pygame.draw.line(screen, (180,180,180), (center_x, ARENA_Y), (center_x, ARENA_Y+ARENA_H), width=6)

def draw_arena_epsilon(screen, ARENA_X, ARENA_Y, ARENA_W, ARENA_H):
    draw_arena_alpha(screen, ARENA_X, ARENA_Y, ARENA_W, ARENA_H)
    star_pos = [
        (ARENA_X + ARENA_W//3, ARENA_Y + ARENA_H//2),
        (ARENA_X + 2*ARENA_W//3, ARENA_Y + ARENA_H//2)
    ]
    for x, y in star_pos:
        pygame.draw.polygon(screen, (255,255,0), [
            (x, y-16), (x+6, y-6), (x+16, y-6), (x+8, y+2),
            (x+12, y+12), (x, y+6), (x-12, y+12), (x-8, y+2),
            (x-16, y-6), (x-6, y-6)
        ])

def draw_arena_zeta(screen, ARENA_X, ARENA_Y, ARENA_W, ARENA_H):
    pygame.draw.rect(screen, (255,255,255), (ARENA_X, ARENA_Y, ARENA_W, ARENA_H), width=0)
    for side in [ARENA_X, ARENA_X+ARENA_W-8]:
        pygame.draw.arc(screen, (255,255,255), (side-8, ARENA_Y, 24, ARENA_H), 1.57, 4.71, 8)
    pygame.draw.rect(screen, (255,255,255), (ARENA_X, ARENA_Y, ARENA_W, ARENA_H), width=8)
    center_x = ARENA_X + ARENA_W//2
    pygame.draw.line(screen, (180,180,180), (center_x, ARENA_Y), (center_x, ARENA_Y+ARENA_H), width=6)