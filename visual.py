import pygame
import time
import os
import math

from game.systems.arenas import (
    # Funções para desenhar diferentes arenas
    draw_arena_alpha, draw_arena_beta, draw_arena_gamma,
    draw_arena_delta, draw_arena_epsilon, draw_arena_aleatoria
)
from game.systems.f_fruta_equipada import draw_power_frame
from config import FONT_PATH, POWER_COLORS
from game.systems.determinacao import arcoiris_color
from game.ui.neon import (
    NEON_CYAN, NEON_PINK, NEON_PURPLE, NEON_GOLD, NEON_GREEN, NEON_RED,
    TEXT_MAIN, TEXT_DIM,
    lighten, darken, lerp_color,
    get_font, neon_text, draw_neon_text, blit_glow, radial_glow,
    draw_panel, glow_rect_outline, draw_background,
)

# CAMADA VISUAL DO JOGO — TEMA "NEON ARCADE"
# Todas as telas compartilham o mesmo cenário synthwave (gradiente, estrelas e
# grade em perspectiva) desenhado por game/ui/neon.py.

# OBJETO GLOBAL DO ARQUIVO:
# Essas variáveis globais controlam o estado visual do jogo
fan_angle = 0  # Usado para a animação de rotação da arena beta

paddle_trail_left = []   # Rastro da raquete esquerda
paddle_trail_right = []  # Rastro da raquete direita
paddle_shake_left = 0    # "Efeito gelatina" da raquete esquerda
paddle_shake_right = 0   # "Efeito gelatina" da raquete direita
paddle_shake_time_left = 0
paddle_shake_time_right = 0
fade_borda_fogo = 0.0    # Fade da borda de fogo
fade_borda_azul = 0.0    # Fade da borda azul/gelo

# Inicializa o Pygame
pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Ping Pong Neon")
clock = pygame.time.Clock()

mapa_escolhido = 0  # Índice do mapa atual, 0 é o padrão (Alpha)

# Define as dimensões e a posição da arena de jogo
ARENA_W, ARENA_H = 700, 500
ARENA_X = (WIDTH - ARENA_W) // 2
ARENA_Y = (HEIGHT - ARENA_H) // 2
ARENA_LEFT = ARENA_X
ARENA_RIGHT = ARENA_X + ARENA_W
ARENA_TOP = ARENA_Y
ARENA_BOTTOM = ARENA_Y + ARENA_H
ARENA_CENTER_X = ARENA_X + ARENA_W // 2
ARENA_CENTER_Y = ARENA_Y + ARENA_H // 2

# Identidade visual dos jogadores
PLAYER_LEFT_COLOR = NEON_CYAN
PLAYER_RIGHT_COLOR = NEON_PINK

# Cache de imagens de frutas para evitar recarregar a cada frame
FRUIT_IMAGES = {}


def get_fruit_image(tipo):
    # Carrega e armazena a imagem da fruta se ela ainda não estiver em cache
    if tipo not in FRUIT_IMAGES:
        path = os.path.join("assets", "images", "frutas", f"{tipo}.png")
        img = pygame.image.load(path).convert_alpha()
        FRUIT_IMAGES[tipo] = pygame.transform.smoothscale(img, (32, 32))
    return FRUIT_IMAGES[tipo]


def draw_habilidade_fruta(x, y, tipo):
    # Desenha uma fruta de poder flutuando com um halo colorido pulsante
    img = get_fruit_image(tipo)
    t = time.time()
    bob = math.sin(t * 3 + x * 0.05) * 4  # flutuação vertical suave
    cor = POWER_COLORS.get(tipo, ((255, 255, 255), None))[0]
    pulse = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(t * 4 + y * 0.03))
    blit_glow(screen, (int(x), int(y + bob)), 34, cor, int(90 * pulse))
    rect = img.get_rect(center=(int(x), int(y + bob)))
    screen.blit(img, rect)


# Cache do halo das raquetes (por cor e altura)
_PADDLE_GLOWS = {}


def _paddle_glow(cor, w, h):
    key = (cor, w, h)
    if key not in _PADDLE_GLOWS:
        pad = 26
        surf = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
        for grow, alpha in ((pad, 22), (pad // 2, 45)):
            pygame.draw.rect(
                surf, cor[:3] + (alpha,),
                pygame.Rect(pad - grow, pad - grow, w + grow * 2, h + grow * 2),
                border_radius=14 + grow)
        _PADDLE_GLOWS[key] = surf
    return _PADDLE_GLOWS[key]


def _draw_paddle_body(x, y, w, h, cor, alpha=255):
    """Desenha o corpo de uma raquete neon (halo + corpo + borda clara)."""
    rect = pygame.Rect(int(x - w // 2), int(y - h // 2), w, h)
    glow = _paddle_glow(cor, w, h)
    screen.blit(glow, (rect.x - 26, rect.y - 26))
    body = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(body, darken(cor, 0.45) + (alpha,), body.get_rect(), border_radius=10)
    inner = body.get_rect().inflate(-8, -12)
    pygame.draw.rect(body, cor + (alpha,), inner, border_radius=8)
    # Reflexo "glossy" no topo (tom claro da própria cor)
    gloss = pygame.Rect(9, 10, w - 18, h // 7)
    pygame.draw.rect(body, lighten(cor, 0.55) + (int(140 * alpha / 255),), gloss, border_radius=5)
    pygame.draw.rect(body, lighten(cor, 0.6) + (alpha,), body.get_rect(), width=2, border_radius=10)
    screen.blit(body, rect)


def draw_paddle(x, y, color=(255, 255, 255), power=None, power_time_left=None,
                determinacao_ativa=False):
    # Desenha a raquete com base na sua posição e poder
    paddle_w, paddle_h = 28, 120
    cor = color if color != (255, 255, 255) else (200, 210, 255)
    # Altera a cor e a altura da raquete se houver um poder ativo
    if determinacao_ativa:
        paddle_h = 160
        cor = arcoiris_color(int(time.time() * 100) % 255)
    else:
        if power == "uva":
            cor = (190, 90, 255)
            paddle_h = 160
        elif power == "banana":
            cor = (255, 220, 50)
        elif power == "morango":
            cor = (255, 80, 90)
        elif power == "melancia":
            cor = (120, 255, 190)
            paddle_h = 140
        elif power == "blueberry":
            cor = (120, 200, 255)

    _draw_paddle_body(x, y, paddle_w, paddle_h, cor)


def draw_ball_trail(rastro, fogo=False, fogo_azul=False):
    # Desenha o rastro da bola: círculos que encolhem e perdem opacidade
    for r in rastro:
        surf = pygame.Surface((r['radius'] * 2, r['radius'] * 2), pygame.SRCALPHA)
        cor = r.get('color', (255, 255, 255))
        pygame.draw.circle(surf, cor + (int(r['alpha']),),
                           (int(r['radius']), int(r['radius'])), int(r['radius']))
        screen.blit(surf, (r['x'] - r['radius'], r['y'] - r['radius']))
        # Adiciona brilho de fogo ou gelo se as condições forem verdadeiras
        if fogo_azul:
            blit_glow(screen, (int(r['x']), int(r['y'])),
                      int(r['radius'] * 2), (80, 120, 255), 70)
        elif fogo:
            blit_glow(screen, (int(r['x']), int(r['y'])),
                      int(r['radius'] * 2), (255, 120, 0), 70)


def draw_ball(x, y, radius=14, color=(255, 255, 255), fogo=False, fogo_azul=False,
              fogo_start_time=None, angle=0):
    # Desenha a bola principal com halo neon
    if fogo_azul:
        halo, corpo = (80, 140, 255), (170, 210, 255)
    elif fogo:
        halo, corpo = (255, 120, 20), (255, 200, 120)
    elif color != (255, 255, 255):
        halo, corpo = color, lighten(color, 0.35)
    else:
        halo, corpo = (170, 190, 255), (245, 248, 255)
    blit_glow(screen, (int(x), int(y)), radius * 3, halo, 110)
    pygame.draw.circle(screen, corpo, (int(x), int(y)), radius)
    pygame.draw.circle(screen, lighten(corpo, 0.7),
                       (int(x - radius * 0.3), int(y - radius * 0.3)),
                       max(2, radius // 3))


def draw_score(left, right):
    # Placar neon: ciano para a esquerda, rosa para a direita
    left_center = (ARENA_LEFT + ARENA_W // 4, ARENA_TOP + 58)
    right_center = (ARENA_LEFT + 3 * ARENA_W // 4, ARENA_TOP + 58)
    draw_neon_text(screen, str(left), 48, PLAYER_LEFT_COLOR, center=left_center)
    draw_neon_text(screen, str(right), 48, PLAYER_RIGHT_COLOR, center=right_center)
    draw_neon_text(screen, "P1", 12, TEXT_DIM,
                   center=(left_center[0], left_center[1] + 44), glow=0.3)
    draw_neon_text(screen, "P2", 12, TEXT_DIM,
                   center=(right_center[0], right_center[1] + 44), glow=0.3)


def draw_mode_label(tempo_str, tempo_acabando=False, tempo_acabando_start=None):
    # Cápsula do cronômetro abaixo da arena
    t = time.time()
    if tempo_acabando:
        pulse = 0.5 + 0.5 * math.sin(t * 6)
        accent = lerp_color(NEON_RED, (120, 20, 40), 1 - pulse)
        text_color = NEON_RED
    else:
        accent = NEON_PURPLE
        text_color = TEXT_MAIN
    text_surf = neon_text(tempo_str, 28, text_color)
    rect_w, rect_h = text_surf.get_width() + 24, 54
    rect = pygame.Rect(ARENA_CENTER_X - rect_w // 2, ARENA_BOTTOM + 10, rect_w, rect_h)
    draw_panel(screen, rect, accent=accent, radius=16)
    screen.blit(text_surf, text_surf.get_rect(center=rect.center))
    if tempo_acabando and int(t * 2) % 2 == 0:
        draw_neon_text(screen, "1 MINUTO RESTANTE!", 22, NEON_RED,
                       center=(rect.centerx, rect.bottom + 30))


def draw_melancia_espelhada(x, y, power_time_left):
    # Desenha a raquete espelhada do poder melancia (levemente translúcida)
    _draw_paddle_body(x, y, 28, 140, (60, 230, 150), alpha=210)


# BOTÃO DE CANTO ("[Z] VOLTAR" / "[X] SAIR")

def _corner_button(text):
    rect = draw_neon_text(screen, text, 18, TEXT_DIM,
                          topleft=(24, HEIGHT - 56), glow=0.35)
    mx, my = pygame.mouse.get_pos()
    if rect.collidepoint(mx, my):
        blink = 120 + int(80 * (0.5 + 0.5 * math.sin(time.time() * 4)))
        sel = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(sel, NEON_PURPLE[:3] + (blink,), sel.get_rect(),
                         width=2, border_radius=10)
        screen.blit(sel, rect)
    return rect


# Cores do título: degradê ciano -> roxo -> rosa por letra
_TITLE = "PING-PONG"


def _title_letter_color(i):
    f = i / (len(_TITLE) - 1)
    if f < 0.5:
        return lerp_color(NEON_CYAN, NEON_PURPLE, f * 2)
    return lerp_color(NEON_PURPLE, NEON_PINK, (f - 0.5) * 2)


def draw_menu_principal(selected_idx=0, mostrar_opcoes=False, letras_bolas=None,
                        letras_voltando=False):
    # Desenha a tela do menu principal
    screen = pygame.display.get_surface()
    draw_background(screen)

    base_x = WIDTH // 2
    base_y = HEIGHT // 2 - 160
    spacing = 92
    total_w = len(_TITLE) * spacing
    start_x = base_x - total_w // 2 + spacing // 2
    letras_rects = []

    # Animação secreta das letras quicando como bolas
    if letras_bolas is not None:
        for i, letra in enumerate(letras_bolas):
            cor = _title_letter_color(i % len(_TITLE))
            letra_surf = neon_text(letra['letra'], 72, cor)
            letra_rect = letra_surf.get_rect(center=(letra['x'], letra['y']))
            screen.blit(letra_surf, letra_rect)
            letras_rects.append((letra['letra'], letra_rect))
        exit_rect = _corner_button("[X] SAIR")
        return letras_rects, None, exit_rect

    # Título com movimento de onda
    t = time.time()
    for i, letra in enumerate(_TITLE):
        phase = t * 2 + i * 0.5
        dy = math.sin(phase) * 18
        angle = math.sin(phase) * 12
        letra_surf = neon_text(letra, 72, _title_letter_color(i))
        letra_surf = pygame.transform.rotate(letra_surf, angle)
        letra_rect = letra_surf.get_rect(center=(start_x + i * spacing, base_y + dy))
        screen.blit(letra_surf, letra_rect)
        letras_rects.append((letra, letra_rect))

    # Subtítulo
    draw_neon_text(screen, "NEON ARCADE", 16, TEXT_DIM,
                   center=(WIDTH // 2, base_y + 84), glow=0.4)

    if not mostrar_opcoes:
        if int(t * 2) % 2 == 0:
            draw_neon_text(screen, "APERTE [ESPAÇO] PARA CONTINUAR", 24, TEXT_MAIN,
                           center=(WIDTH // 2, HEIGHT // 2 + 80), glow=0.6)
        exit_rect = _corner_button("[X] SAIR")
        return letras_rects, None, exit_rect

    # Opções do menu como cartões neon
    options = ["JOGAR", "AJUDA", "CRÉDITOS"]
    frames = []
    opt_y_start = HEIGHT // 2 + 10
    frame_w, frame_h = 360, 60
    padding_y = 24
    mx, my = pygame.mouse.get_pos()
    mouse_idx = None
    for i, opt in enumerate(options):
        center = (WIDTH // 2, opt_y_start + i * (frame_h + padding_y))
        frame_rect = pygame.Rect(center[0] - frame_w // 2, center[1] - frame_h // 2,
                                 frame_w, frame_h)
        frames.append(frame_rect)
        if frame_rect.collidepoint(mx, my):
            mouse_idx = i

    idx_to_draw = mouse_idx if mouse_idx is not None else selected_idx
    for i, opt in enumerate(options):
        frame_rect = frames[i]
        selecionado = (i == idx_to_draw)
        accent = NEON_CYAN if selecionado else NEON_PURPLE
        draw_panel(screen, frame_rect, accent=accent, radius=14,
                   border=3 if selecionado else 2)
        cor_txt = TEXT_MAIN if selecionado else TEXT_DIM
        draw_neon_text(screen, opt, 28, cor_txt, center=frame_rect.center,
                       glow=0.9 if selecionado else 0.3)
        if selecionado:
            # Setas indicadoras pulsantes ao lado da opção
            pulse = int(4 * math.sin(time.time() * 5))
            draw_neon_text(screen, ">", 24, NEON_CYAN,
                           center=(frame_rect.left - 28 + pulse, frame_rect.centery))
            draw_neon_text(screen, "<", 24, NEON_CYAN,
                           center=(frame_rect.right + 28 - pulse, frame_rect.centery))

    exit_rect = _corner_button("[X] SAIR")
    return frames, mouse_idx, exit_rect


def _draw_mini_paddle(x, y, cor, h=46):
    """Ícone de raquete usado nos cartões de modo de jogo."""
    rect = pygame.Rect(x - 6, y - h // 2, 12, h)
    pygame.draw.rect(screen, darken(cor, 0.4), rect, border_radius=5)
    pygame.draw.rect(screen, cor, rect.inflate(-4, -6), border_radius=4)
    pygame.draw.rect(screen, lighten(cor, 0.6), rect, width=1, border_radius=5)


def draw_modo_menu(selected_idx=0):
    # Desenha o menu para selecionar o modo de jogo
    screen = pygame.display.get_surface()
    draw_background(screen)

    draw_neon_text(screen, "ESCOLHA O MODO DE JOGO", 40, NEON_GOLD,
                   center=(WIDTH // 2, HEIGHT // 2 - 160))

    options = ["[1] VS LOCAL", "[2] VS BOT"]
    frames = []
    opt_y_start = HEIGHT // 2 - 20
    frame_w, frame_h = 460, 92
    padding_y = 110
    t = time.time()
    mx, my = pygame.mouse.get_pos()
    mouse_idx = None
    for i, opt in enumerate(options):
        center = (WIDTH // 2, opt_y_start + i * padding_y)
        frame_rect = pygame.Rect(center[0] - frame_w // 2, center[1] - frame_h // 2,
                                 frame_w, frame_h)
        frames.append(frame_rect)
        if frame_rect.collidepoint(mx, my):
            mouse_idx = i

    idx_to_draw = mouse_idx if mouse_idx is not None else selected_idx
    for i, opt in enumerate(options):
        frame_rect = frames[i]
        selecionado = (i == idx_to_draw)
        accent = (NEON_CYAN if i == 0 else NEON_PINK) if selecionado else NEON_PURPLE
        draw_panel(screen, frame_rect, accent=accent, radius=16,
                   border=3 if selecionado else 2)
        # Ícones do modo
        icon_x = frame_rect.left + 56
        if i == 0:
            _draw_mini_paddle(icon_x - 14, frame_rect.centery, NEON_CYAN)
            _draw_mini_paddle(icon_x + 14, frame_rect.centery, NEON_PINK)
        else:
            _draw_mini_paddle(icon_x - 16, frame_rect.centery, NEON_CYAN)
            # Cabeça de robô
            head = pygame.Rect(icon_x + 2, frame_rect.centery - 14, 28, 28)
            pygame.draw.rect(screen, darken(NEON_PINK, 0.4), head, border_radius=6)
            pygame.draw.rect(screen, lighten(NEON_PINK, 0.4), head, width=2, border_radius=6)
            olho_y = head.centery - 2
            brilho = 0.5 + 0.5 * math.sin(t * 3)
            cor_olho = lerp_color((120, 30, 80), NEON_PINK, brilho)
            pygame.draw.circle(screen, cor_olho, (head.centerx - 6, olho_y), 3)
            pygame.draw.circle(screen, cor_olho, (head.centerx + 6, olho_y), 3)
        cor_txt = TEXT_MAIN if selecionado else TEXT_DIM
        draw_neon_text(screen, opt, 28, cor_txt,
                       center=(frame_rect.centerx + 40, frame_rect.centery),
                       glow=0.9 if selecionado else 0.3)

    exit_rect = _corner_button("[Z] VOLTAR")
    return frames, mouse_idx, exit_rect


def draw_gameover(winner):
    # Tela de fim de jogo
    screen = pygame.display.get_surface()
    draw_background(screen)
    t = time.time()

    cor_vencedor = PLAYER_LEFT_COLOR if winner.upper() == "ESQUERDA" else PLAYER_RIGHT_COLOR

    # Raios giratórios atrás do troféu
    cx, cy = WIDTH // 2, HEIGHT // 2 - 210
    rays = pygame.Surface((300, 300), pygame.SRCALPHA)
    for k in range(10):
        ang = t * 0.6 + k * math.tau / 10
        x2 = 150 + math.cos(ang) * 145
        y2 = 150 + math.sin(ang) * 145
        pygame.draw.line(rays, NEON_GOLD[:3] + (22,), (150, 150), (x2, y2), 6)
    screen.blit(rays, (cx - 150, cy - 150))

    # Troféu dourado
    blit_glow(screen, (cx, cy), 90, NEON_GOLD, 80)
    pygame.draw.circle(screen, NEON_GOLD, (cx, cy - 10), 34, width=8)
    pygame.draw.rect(screen, NEON_GOLD, (cx - 8, cy + 20, 16, 22))
    pygame.draw.rect(screen, NEON_GOLD, (cx - 26, cy + 42, 52, 10), border_radius=3)
    pygame.draw.arc(screen, NEON_GOLD, (cx - 56, cy - 34, 36, 40), 1.2, 4.6, 6)
    pygame.draw.arc(screen, NEON_GOLD, (cx + 20, cy - 34, 36, 40), -1.5, 2.0, 6)

    draw_neon_text(screen, "FIM DE JOGO!", 56, NEON_GOLD,
                   center=(WIDTH // 2, HEIGHT // 2 - 80))
    pulse = 0.7 + 0.3 * math.sin(t * 3)
    draw_neon_text(screen, f"VENCEDOR: {winner.upper()}", 36, cor_vencedor,
                   center=(WIDTH // 2, HEIGHT // 2 + 20), glow=pulse)
    if int(t * 2) % 2 == 0:
        draw_neon_text(screen, "[ESPAÇO] VOLTAR AO MENU", 24, TEXT_DIM,
                       center=(WIDTH // 2, HEIGHT // 2 + 120), glow=0.4)


# -------------------A FUNÇÃO MAIS IMPORTANTE, RENDERIZA TUDO----------------------------------------------------------

def render_visual(
    l_paddle_x, l_paddle_y, l_paddle_power, l_paddle_power_time,
    r_paddle_x, r_paddle_y, r_paddle_power, r_paddle_power_time,
    ball_x, ball_y, ball_rastro,
    habilidades,
    left_score, right_score,
    tempo_str,
    ball_color=(255, 255, 255),
    impact_left=False, impact_right=False,
    fake_balls=None,
    festival=None,
    mapa_escolhido=0,
    ball=None,
    tempo_acabando=False,
    tempo_acabando_start=None,
    get_fruit_image=None,
    determinacao_manager=None,
    arena_aleatoria_idx=None,
    indice_arena_aleatoria=None
):

    # Função principal para desenhar o estado completo do jogo em um frame
    global paddle_trail_left, paddle_trail_right
    global paddle_shake_left, paddle_shake_right, paddle_shake_time_left, paddle_shake_time_right
    global fan_angle
    fan_angle += 0.04

    draw_background(screen)
    arena_draw_functions = [
        draw_arena_alpha,
        draw_arena_beta,
        draw_arena_gamma,
        draw_arena_delta,
        draw_arena_epsilon,
        draw_arena_aleatoria
    ]

    if mapa_escolhido == indice_arena_aleatoria and arena_aleatoria_idx is not None:
        if arena_aleatoria_idx == 1:
            draw_arena_beta(screen, ARENA_X, ARENA_Y, ARENA_W, ARENA_H, angle=fan_angle)
        else:
            arena_draw_functions[arena_aleatoria_idx](screen, ARENA_X, ARENA_Y, ARENA_W, ARENA_H)
    elif mapa_escolhido == 1:
        draw_arena_beta(screen, ARENA_X, ARENA_Y, ARENA_W, ARENA_H, angle=fan_angle)
    else:
        arena_func = arena_draw_functions[mapa_escolhido]
        arena_func(screen, ARENA_X, ARENA_Y, ARENA_W, ARENA_H)

    # DETERMINAÇÃO
    if determinacao_manager and determinacao_manager.is_active() and hasattr(determinacao_manager, "onda_start_time"):
        tempo_onda = time.time() - determinacao_manager.onda_start_time
        if tempo_onda < 1.2:
            draw_onda_determinacao(screen, tempo_onda, determinacao_manager.get_side())
        else:
            delattr(determinacao_manager, "onda_start_time")

    for h in habilidades:
        if h["tipo"] in ["uva", "banana", "morango", "melancia", "blueberry"]:
            draw_habilidade_fruta(h["x"], h["y"], h["tipo"])

    if l_paddle_power == "melancia":
        espelhada_y = ARENA_BOTTOM - (l_paddle_y - ARENA_TOP)
        draw_melancia_espelhada(l_paddle_x, espelhada_y, l_paddle_power_time)
    if r_paddle_power == "melancia":
        espelhada_y = ARENA_BOTTOM - (r_paddle_y - ARENA_TOP)
        draw_melancia_espelhada(r_paddle_x, espelhada_y, r_paddle_power_time)

    # Animação de rastro e "gelatina" das raquetes
    last_left = getattr(render_visual, "last_left", None)
    last_right = getattr(render_visual, "last_right", None)
    if last_left is not None:
        if l_paddle_y != last_left:
            paddle_shake_time_left = time.time()
            paddle_trail_left.append({"x": l_paddle_x, "y": l_paddle_y, "time": time.time(), "dir": 1 if l_paddle_y > last_left else -1})
    if last_right is not None:
        if r_paddle_y != last_right:
            paddle_shake_time_right = time.time()
            paddle_trail_right.append({"x": r_paddle_x, "y": r_paddle_y, "time": time.time(), "dir": 1 if r_paddle_y > last_right else -1})
    render_visual.last_left = l_paddle_y
    render_visual.last_right = r_paddle_y

    shake_left = 0
    shake_right = 0
    if time.time() - paddle_shake_time_left < 0.18:
        shake_left = math.sin((time.time() - paddle_shake_time_left) * 18) * 7
    if time.time() - paddle_shake_time_right < 0.18:
        shake_right = math.sin((time.time() - paddle_shake_time_right) * 18) * 7

    paddle_trail_left = [t for t in paddle_trail_left if time.time() - t["time"] < 0.25]
    paddle_trail_right = [t for t in paddle_trail_right if time.time() - t["time"] < 0.25]

    for t in paddle_trail_left:
        alpha = int(90 * (1 - (time.time() - t["time"]) / 0.25))
        alpha = max(0, min(255, alpha))
        trail_surf = pygame.Surface((28, 24), pygame.SRCALPHA)
        cor = PLAYER_LEFT_COLOR[:3] + (alpha,)
        pygame.draw.rect(trail_surf, cor, trail_surf.get_rect(), border_radius=8)
        trail_x = l_paddle_x - 14
        trail_y = t["y"] - 12 + (8 * t["dir"])
        screen.blit(trail_surf, (trail_x, trail_y))

    for t in paddle_trail_right:
        alpha = int(90 * (1 - (time.time() - t["time"]) / 0.25))
        alpha = max(0, min(255, alpha))
        trail_surf = pygame.Surface((28, 24), pygame.SRCALPHA)
        cor = PLAYER_RIGHT_COLOR[:3] + (alpha,)
        pygame.draw.rect(trail_surf, cor, trail_surf.get_rect(), border_radius=8)
        trail_x = r_paddle_x - 14
        trail_y = t["y"] - 12 + (8 * t["dir"])
        screen.blit(trail_surf, (trail_x, trail_y))

    # Para a raquete esquerda
    draw_paddle(
        l_paddle_x, l_paddle_y + shake_left,
        PLAYER_LEFT_COLOR, l_paddle_power, l_paddle_power_time,
        determinacao_ativa=determinacao_manager.is_active() and determinacao_manager.get_side() == "left"
    )

    # Para a raquete direita
    draw_paddle(
        r_paddle_x, r_paddle_y + shake_right,
        PLAYER_RIGHT_COLOR, r_paddle_power, r_paddle_power_time,
        determinacao_ativa=determinacao_manager.is_active() and determinacao_manager.get_side() == "right"
    )

    # Desenha as bolas "fake" da blueberry
    if fake_balls:
        for fake in fake_balls:
            draw_ball_trail(fake.rastro)
            draw_ball(fake.x, fake.y, color=fake.color)

    fogo_ativo = getattr(ball, "fogo_ativo", False)
    fogo_azul = getattr(ball, "fogo_azul", False)
    global fade_borda_fogo, fade_borda_azul
    dt = min(clock.tick() / 1000.0, 0.05)
    fade_speed = 2.5
    if fogo_azul:
        fade_borda_azul = min(1.0, fade_borda_azul + dt * fade_speed)
        fade_borda_fogo = max(0.0, fade_borda_fogo - dt * fade_speed)
    elif fogo_ativo:
        fade_borda_fogo = min(1.0, fade_borda_fogo + dt * fade_speed)
        fade_borda_azul = max(0.0, fade_borda_azul - dt * fade_speed)
    else:
        fade_borda_fogo = max(0.0, fade_borda_fogo - dt * fade_speed)
        fade_borda_azul = max(0.0, fade_borda_azul - dt * fade_speed)

    if not fogo_ativo and not fogo_azul:
        draw_ball_trail(ball_rastro)
    else:
        draw_ball_trail(ball_rastro, fogo=fogo_ativo, fogo_azul=fogo_azul)
    draw_ball(
        ball_x, ball_y,
        color=ball_color,
        fogo=fogo_ativo,
        fogo_azul=fogo_azul,
        fogo_start_time=getattr(ball, "spawn_time", None),
        angle=getattr(ball, "angle", 0)
    )

    # Efeito de borda luminosa para o "fogo" ou "gelo"
    if fade_borda_fogo > 0.01 or fade_borda_azul > 0.01:
        t = time.time()
        fade = fade_borda_fogo * (1 - fade_borda_azul) + fade_borda_azul
        if fade_borda_azul > 0.01:
            cor1 = (
                int(255 * (1 - fade_borda_azul) + 80 * fade_borda_azul),
                int(120 * (1 - fade_borda_azul) + 120 * fade_borda_azul),
                int(0 * (1 - fade_borda_azul) + 255 * fade_borda_azul)
            )
            cor2 = (
                int(255 * (1 - fade_borda_azul) + 120 * fade_borda_azul),
                int(40 * (1 - fade_borda_azul) + 40 * fade_borda_azul),
                int(0 * (1 - fade_borda_azul) + 255 * fade_borda_azul)
            )
            intensidade = int(120 * fade_borda_azul + 80 * (1 - fade_borda_azul))
            camadas = 4
        else:
            cor1 = (255, 120, 0)
            cor2 = (255, 40, 0)
            intensidade = int(80 * fade_borda_fogo)
            camadas = 3
        for i in range(camadas):
            alpha = int(intensidade * (1 - i / camadas) * fade * (0.7 + 0.3 * math.sin(t * 2 + i)))
            thickness = 18 - i * 4
            surf = pygame.Surface((WIDTH, thickness), pygame.SRCALPHA)
            surf.fill(cor1 + (alpha,))
            screen.blit(surf, (0, 0))
            screen.blit(surf, (0, HEIGHT - thickness))
            surf_v = pygame.Surface((thickness, HEIGHT), pygame.SRCALPHA)
            surf_v.fill(cor1 + (alpha,))
            screen.blit(surf_v, (0, 0))
            screen.blit(surf_v, (WIDTH - thickness, 0))
            if fade_borda_azul > 0.01:
                alpha2 = int(alpha * 0.7)
                surf2 = pygame.Surface((WIDTH, thickness // 2), pygame.SRCALPHA)
                surf2.fill(cor2 + (alpha2,))
                screen.blit(surf2, (0, 0))
                screen.blit(surf2, (0, HEIGHT - thickness // 2))
                surf2_v = pygame.Surface((thickness // 2, HEIGHT), pygame.SRCALPHA)
                surf2_v.fill(cor2 + (alpha2,))
                screen.blit(surf2_v, (0, 0))
                screen.blit(surf2_v, (WIDTH - thickness // 2, 0))

    draw_score(left_score, right_score)
    draw_mode_label(tempo_str, tempo_acabando=tempo_acabando, tempo_acabando_start=tempo_acabando_start)

    # FRAME DE FRUTA EQUIPADA
    from config import POWER_TOTAL_TIMER

    # Frame do jogador da esquerda
    if l_paddle_power:
        tempo_total = POWER_TOTAL_TIMER.get(l_paddle_power, 20)
        draw_power_frame(
            screen,
            FONT_PATH,
            ARENA_CENTER_X - 350,
            ARENA_BOTTOM + 80,
            l_paddle_power,
            l_paddle_power_time,
            tempo_total,
            get_fruit_image
        )

    # Frame do jogador da direita
    if r_paddle_power:
        tempo_total = POWER_TOTAL_TIMER.get(r_paddle_power, 20)
        draw_power_frame(
            screen,
            FONT_PATH,
            ARENA_CENTER_X + 110,
            ARENA_BOTTOM + 80,
            r_paddle_power,
            r_paddle_power_time,
            tempo_total,
            get_fruit_image
        )

    # Frame de Determinação
    if determinacao_manager and determinacao_manager.is_active():
        tempo_left = determinacao_manager.get_time_left()
        draw_power_frame(
            screen,
            FONT_PATH,
            ARENA_CENTER_X - 350 if determinacao_manager.get_side() == "left" else ARENA_CENTER_X + 110,
            ARENA_BOTTOM + 80,
            "determinacao",
            tempo_left,
            90,
            get_fruit_image
        )


from config import MAP_IMAGES

# Cache das miniaturas das arenas já redimensionadas
_MAP_THUMBS = {}

# Cor de destaque de cada arena no menu de seleção
_MAP_ACCENTS = [NEON_PURPLE, NEON_GOLD, NEON_GREEN, (255, 140, 50), NEON_PINK, NEON_CYAN]


def draw_map_select_menu(selected_idx=0, last_selected_idx=None, som=None):
    # Desenha o menu de seleção de arena, com imagens e nomes dos mapas
    screen = pygame.display.get_surface()
    draw_background(screen)
    map_names = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Aleatória"]

    draw_neon_text(screen, "ESCOLHA UMA ARENA", 32, NEON_GOLD,
                   center=(WIDTH // 2, HEIGHT // 2 - 295))

    # Layout adaptável: encolhe os cartões se a tela for estreita
    frame_w, frame_h = 340, 200
    padding_x, padding_y = 110, 110
    total_w = 3 * frame_w + 2 * padding_x
    if total_w > WIDTH - 60:
        escala = (WIDTH - 60) / total_w
        frame_w = int(frame_w * escala)
        frame_h = int(frame_h * escala)
        padding_x = int(padding_x * escala)
    start_x = WIDTH // 2 - (3 * frame_w + 2 * padding_x) // 2
    start_y = HEIGHT // 2 - 260

    t = time.time()
    mx, my = pygame.mouse.get_pos()
    frame_rects = []
    mouse_idx = None
    for i in range(6):
        row = i // 3
        col = i % 3
        x = start_x + col * (frame_w + padding_x)
        y = start_y + row * (frame_h + padding_y)
        frame_rect = pygame.Rect(x, y, frame_w, frame_h)
        frame_rects.append(frame_rect)
        if frame_rect.collidepoint(mx, my):
            mouse_idx = i

        accent = _MAP_ACCENTS[i]
        draw_panel(screen, frame_rect, accent=accent, radius=18)

        if i == 5:  # Arena Aleatória
            # Animação do "?"
            float_y = math.sin(t * 2.5) * 14
            spin_phase = (t % 4)
            if spin_phase < 0.7:
                angle = (spin_phase / 0.7) * 360
            else:
                angle = math.sin(t * 0.7) * 8

            q_surf = neon_text("?", 110, NEON_CYAN)
            q_surf = pygame.transform.rotozoom(q_surf, angle, 1)
            q_rect = q_surf.get_rect(center=(frame_rect.centerx, frame_rect.centery + float_y))
            screen.blit(q_surf, q_rect)
        else:
            if i not in _MAP_THUMBS:
                img = MAP_IMAGES[i]
                if img is not None:
                    if img.get_alpha() is None:
                        img = img.convert_alpha()
                    _MAP_THUMBS[i] = pygame.transform.smoothscale(
                        img, (frame_w - 24, frame_h - 24))
                else:
                    _MAP_THUMBS[i] = None
            thumb = _MAP_THUMBS[i]
            if thumb is not None:
                img_rect = thumb.get_rect(center=frame_rect.center)
                screen.blit(thumb, img_rect)

        idx_atual = mouse_idx if mouse_idx is not None else selected_idx
        cor_nome = lighten(accent, 0.4) if i == idx_atual else TEXT_DIM
        draw_neon_text(screen, map_names[i], 22, cor_nome,
                       center=(frame_rect.centerx, frame_rect.bottom + 30),
                       glow=0.8 if i == idx_atual else 0.25)

    # Moldura de seleção pulsante
    idx_to_draw = mouse_idx if mouse_idx is not None else selected_idx
    frame_rect = frame_rects[idx_to_draw]
    pulse = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(t * 4))
    sel_surf = pygame.Surface((frame_rect.width + 56, frame_rect.height + 56), pygame.SRCALPHA)
    sel_rect = pygame.Rect(28, 28, frame_rect.width, frame_rect.height)
    accent = _MAP_ACCENTS[idx_to_draw]
    glow_rect_outline(sel_surf, lerp_color(accent, lighten(accent, 0.5), pulse),
                      sel_rect.inflate(16, 16), width=4, radius=24)
    screen.blit(sel_surf, (frame_rect.x - 28, frame_rect.y - 28))
    return frame_rects, mouse_idx


def _draw_keycap(x, y, label, accent, size=34):
    """Desenha uma tecla estilizada (keycap) com o rótulo centralizado."""
    rect = pygame.Rect(x, y, size, size)
    pygame.draw.rect(screen, (26, 20, 52), rect, border_radius=7)
    pygame.draw.rect(screen, lighten(accent, 0.25), rect, width=2, border_radius=7)
    txt = get_font(14).render(label, True, lighten(accent, 0.55))
    screen.blit(txt, txt.get_rect(center=rect.center))
    return rect


def draw_ajuda():
    # Tela de ajuda
    screen = pygame.display.get_surface()
    draw_background(screen)

    # Título principal
    draw_neon_text(screen, "COMO JOGAR", 44, NEON_GOLD,
                   center=(WIDTH // 2, HEIGHT // 2 - 320))

    # Painéis de controles
    section_top_y = HEIGHT // 2 - 250
    section_h = 170
    section_w = 440
    left_panel = pygame.Rect(WIDTH // 2 - section_w - 32, section_top_y, section_w, section_h)
    right_panel = pygame.Rect(WIDTH // 2 + 32, section_top_y, section_w, section_h)

    draw_panel(screen, left_panel, accent=NEON_CYAN)
    draw_panel(screen, right_panel, accent=NEON_PINK)

    draw_neon_text(screen, "MULTIJOGADOR", 24, NEON_CYAN,
                   center=(left_panel.centerx, left_panel.y + 34))
    _draw_keycap(left_panel.x + 40, left_panel.y + 70, "W", NEON_CYAN)
    _draw_keycap(left_panel.x + 80, left_panel.y + 70, "S", NEON_CYAN)
    txt = get_font(14).render("Jogador Esquerda", True, TEXT_MAIN)
    screen.blit(txt, (left_panel.x + 130, left_panel.y + 80))
    _draw_keycap(left_panel.x + 40, left_panel.y + 116, "^", NEON_PINK)
    _draw_keycap(left_panel.x + 80, left_panel.y + 116, "v", NEON_PINK)
    txt = get_font(14).render("Jogador Direita", True, TEXT_MAIN)
    screen.blit(txt, (left_panel.x + 130, left_panel.y + 126))

    draw_neon_text(screen, "VS BOT", 24, NEON_PINK,
                   center=(right_panel.centerx, right_panel.y + 34))
    _draw_keycap(right_panel.x + 40, right_panel.y + 70, "W", NEON_CYAN)
    _draw_keycap(right_panel.x + 80, right_panel.y + 70, "S", NEON_CYAN)
    txt = get_font(14).render("Você", True, TEXT_MAIN)
    screen.blit(txt, (right_panel.x + 130, right_panel.y + 80))
    txt = get_font(14).render("BOT: automático", True, TEXT_DIM)
    screen.blit(txt, (right_panel.x + 40, right_panel.y + 126))

    # Título "Durante o jogo"
    section2_top_y = section_top_y + section_h + 64
    draw_neon_text(screen, "DURANTE O JOGO", 28, TEXT_MAIN,
                   center=(WIDTH // 2, section2_top_y))

    # Painéis FRUTAS e EVENTOS
    section2_h = 280
    section2_w = 480
    section2_y = section2_top_y + 40
    frutas_panel = pygame.Rect(WIDTH // 2 - section2_w - 32, section2_y, section2_w, section2_h)
    eventos_panel = pygame.Rect(WIDTH // 2 + 32, section2_y, section2_w, section2_h)

    draw_panel(screen, frutas_panel, accent=NEON_GREEN)
    draw_panel(screen, eventos_panel, accent=NEON_GOLD)

    # FRUTAS (título arco-íris)
    t = time.time()
    fruta_title = arcoiris_text("FRUTAS", get_font(26), t,
                                frutas_panel.centerx - 84, frutas_panel.y + 18)
    for surf, (x, y) in fruta_title:
        screen.blit(surf, (x, y))
    fruta_y = frutas_panel.y + 64

    # Mostra cada fruta e efeito
    from config import POWER_TEXTS
    fruta_types = ["uva", "banana", "morango", "melancia", "blueberry"]
    for i, tipo in enumerate(fruta_types):
        img = pygame.transform.smoothscale(get_fruit_image(tipo), (36, 36))
        cor = POWER_COLORS.get(tipo, ((255, 255, 255), None))[0]
        blit_glow(screen, (frutas_panel.x + 54, fruta_y + i * 42 + 18), 24, cor, 60)
        screen.blit(img, (frutas_panel.x + 36, fruta_y + i * 42))
        txt = get_font(15).render(POWER_TEXTS.get(tipo, ""), True, lighten(cor, 0.45))
        screen.blit(txt, (frutas_panel.x + 90, fruta_y + i * 42 + 10))

    # EVENTOS
    draw_neon_text(screen, "EVENTOS", 26, NEON_GOLD,
                   center=(eventos_panel.centerx, eventos_panel.y + 32))
    eventos_y = eventos_panel.y + 70
    eventos_info = [
        ("Festival das Frutas", "Várias frutas aparecem na arena!"),
        ("Gato???", "Um gato aparece e persegue a bola!"),
        ("Bola extra", "Uma bola extra aparece na partida!"),
    ]
    for i, (nome, desc) in enumerate(eventos_info):
        nome_surf = get_font(16).render(nome, True, lighten(NEON_GOLD, 0.35))
        desc_surf = get_font(13).render(desc, True, TEXT_DIM)
        screen.blit(nome_surf, (eventos_panel.x + 36, eventos_y + i * 62))
        screen.blit(desc_surf, (eventos_panel.x + 36, eventos_y + i * 62 + 26))

    return _corner_button("[Z] VOLTAR")


def arcoiris_text(text, font, t, base_x, base_y):
    colors = [
        (255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0),
        (0, 0, 255), (75, 0, 130), (148, 0, 211)
    ]
    letras_surfs = []
    arcoiris_offset = int(t * 2)
    x = base_x
    for i, letra in enumerate(text):
        cor = colors[(i + arcoiris_offset) % len(colors)]
        letra_surf = font.render(letra, True, cor)
        letras_surfs.append((letra_surf, (x, base_y)))
        x += letra_surf.get_width()
    return letras_surfs


def draw_onda_determinacao(screen, tempo_onda, lado):
    largura = screen.get_width()
    altura = screen.get_height()
    # Onda percorre da esquerda para direita ou vice-versa
    if lado == "left":
        x = int(largura * min(1, tempo_onda / 1.2))
    else:
        x = int(largura * (1 - min(1, tempo_onda / 1.2)))
    surf = pygame.Surface((240, altura), pygame.SRCALPHA)
    for i, (w, a) in enumerate([(240, 30), (160, 55), (80, 90), (26, 160)]):
        pygame.draw.rect(surf, (120, 200, 255, a), (120 - w // 2, 0, w, altura))
    pygame.draw.line(surf, (220, 245, 255, 220), (120, 0), (120, altura), 4)
    screen.blit(surf, (x - 120, 0))


_LINKEDIN_IMG = None


def draw_creditos():
    # Tela de créditos com informações e fontes de som
    screen = pygame.display.get_surface()
    draw_background(screen)

    title_rect = draw_neon_text(screen, "Vitor Nonato Nascimento", 40, NEON_CYAN,
                                center=(WIDTH // 2, HEIGHT // 2 - 220))

    global _LINKEDIN_IMG
    if _LINKEDIN_IMG is None:
        _LINKEDIN_IMG = pygame.transform.smoothscale(
            pygame.image.load("assets/images/Linkedin.png").convert_alpha(), (40, 40))
    linkedin_img = _LINKEDIN_IMG
    link_text = get_font(20).render("https://www.linkedin.com/in/vitor-n-9441932b1/", True, (120, 200, 255))
    link_rect = link_text.get_rect()
    total_w = linkedin_img.get_width() + 16 + link_rect.width
    base_x = WIDTH // 2 - total_w // 2
    base_y = title_rect.bottom + 8
    screen.blit(linkedin_img, (base_x, base_y))
    link_pos = (base_x + linkedin_img.get_width() + 16,
                base_y + (linkedin_img.get_height() - link_rect.height) // 2)
    screen.blit(link_text, link_pos)

    mouse_pos = pygame.mouse.get_pos()
    link_area = pygame.Rect(base_x, base_y, total_w, linkedin_img.get_height())
    blink = 120 + int(80 * (0.5 + 0.5 * math.sin(time.time() * 4)))
    if link_area.collidepoint(mouse_pos):
        sel_surf = pygame.Surface(link_area.size, pygame.SRCALPHA)
        pygame.draw.rect(sel_surf, NEON_CYAN[:3] + (blink,), sel_surf.get_rect(),
                         width=2, border_radius=8)
        screen.blit(sel_surf, link_area)

    # Painel com créditos de música e efeitos sonoros
    painel_w = min(1180, WIDTH - 80)
    painel = pygame.Rect(WIDTH // 2 - painel_w // 2, base_y + 78, painel_w, 220)
    draw_panel(screen, painel, accent=NEON_PURPLE)

    sfx_rect = draw_neon_text(screen, "MUSICA/SFX", 26, NEON_GOLD,
                              center=(painel.centerx, painel.y + 36))
    fs_text = get_font(16).render("FREESOUND.ORG / FREEMUSICARCHIVE.ORG", True, TEXT_DIM)
    screen.blit(fs_text, fs_text.get_rect(center=(painel.centerx, sfx_rect.bottom + 6)))

    sfx_names = [
        ("cat.wav by HamFace", "retro crime movie loop 4.wav by zagi2", "time continues.wav by lomowo"),
        ("Revenge from behind the grave by Gigakoops", "The furcula curse by Gigakoops", "Condemned by Eggy Toast"),
        ("Break In by Eggy Toast", "place holder", "place holder"),
    ]
    num_cols = len(sfx_names[0])
    num_rows = len(sfx_names)
    spacing_x = 24
    spacing_y = 22

    # Escolhe o maior tamanho de fonte cujas colunas caibam no painel
    for tamanho in (10, 9, 8, 7):
        font_small = get_font(tamanho)
        col_widths = []
        for col in range(num_cols):
            max_w = 0
            for row in range(num_rows):
                surf = font_small.render(sfx_names[row][col], True, TEXT_MAIN)
                max_w = max(max_w, surf.get_width())
            col_widths.append(max_w)
        total_w = sum(col_widths) + spacing_x * (num_cols - 1)
        if total_w <= painel.w - 48:
            break
    start_x = WIDTH // 2 - total_w // 2
    start_y = painel.y + 130

    # Centraliza cada coluna
    for col in range(num_cols):
        x = start_x + sum(col_widths[:col]) + spacing_x * col + col_widths[col] // 2
        for row in range(num_rows):
            color = TEXT_MAIN if row == 0 else TEXT_DIM
            surf = font_small.render(sfx_names[row][col], True, color)
            rect = surf.get_rect(center=(x, start_y + row * spacing_y))
            screen.blit(surf, rect)

    exit_rect = _corner_button("[Z] VOLTAR")
    return link_area, exit_rect
