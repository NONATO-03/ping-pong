import pygame
import time
import os
from game.systems.eventos import FestivalDasFrutas, draw_festival_text, draw_festival_columns
from game.systems.arenas import (
    draw_arena_alpha, draw_arena_beta, draw_arena_gamma,
    draw_arena_delta, draw_arena_epsilon, draw_arena_zeta
)
import math

fan_angle = 0

paddle_trail_left = []
paddle_trail_right = []
paddle_shake_left = 0
paddle_shake_right = 0
paddle_shake_time_left = 0
paddle_shake_time_right = 0

pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Ping Pong Neon")
clock = pygame.time.Clock()

FONT_PATH = "assets/fonts/PressStart2P-Regular.ttf"

mapa_escolhido = 0  # padrão: alpha

# Arena
ARENA_W, ARENA_H = 700, 500
ARENA_X = (WIDTH - ARENA_W) // 2
ARENA_Y = (HEIGHT - ARENA_H) // 2
ARENA_LEFT = ARENA_X
ARENA_RIGHT = ARENA_X + ARENA_W
ARENA_TOP = ARENA_Y
ARENA_BOTTOM = ARENA_Y + ARENA_H
ARENA_CENTER_X = ARENA_X + ARENA_W // 2
ARENA_CENTER_Y = ARENA_Y + ARENA_H // 2

# Carregue as imagens das frutas só uma vez
FRUIT_IMAGES = {}
def get_fruit_image(tipo):
    if tipo not in FRUIT_IMAGES:
        path = os.path.join("assets", "images", f"{tipo}.png")
        img = pygame.image.load(path).convert_alpha()
        FRUIT_IMAGES[tipo] = pygame.transform.smoothscale(img, (32, 32))  # menor
    return FRUIT_IMAGES[tipo]

def draw_habilidade_fruta(x, y, tipo):
    img = get_fruit_image(tipo)
    rect = img.get_rect(center=(int(x), int(y)))
    # Glow mais transparente e centralizado
    glow = pygame.Surface((44,44), pygame.SRCALPHA)
    pygame.draw.circle(glow, (255,255,255,35), (22,22), 20)
    screen.blit(glow, (rect.centerx-22, rect.centery-22))
    # Fruta real
    screen.blit(img, rect)

def draw_menu_principal(selected_idx=0, mostrar_opcoes=False, letras_bolas=None, letras_voltando=False):
    screen = pygame.display.get_surface()
    font_title = pygame.font.Font(FONT_PATH, 72)
    font_opt = pygame.font.Font(FONT_PATH, 32)
    font_hint = pygame.font.Font(FONT_PATH, 24)
    font_exit = pygame.font.Font(FONT_PATH, 18)

    screen.fill((10, 10, 20))

    title = "PING-PONG"
    base_x = WIDTH // 2
    base_y = HEIGHT // 2 - 160
    spacing = 92
    total_w = len(title) * spacing
    start_x = base_x - total_w // 2 + spacing // 2

    letras_rects = []

    # Se estiver no modo quicando, desenha as letras como bolas
    if letras_bolas is not None:
        for letra in letras_bolas:
            letra_surf = font_title.render(letra['letra'], True, (255,255,255))
            letra_surf = pygame.transform.rotate(letra_surf, 0)
            letra_rect = letra_surf.get_rect(center=(letra['x'], letra['y']))
            screen.blit(letra_surf, letra_rect)
            letras_rects.append((letra['letra'], letra_rect))
    else:
        # Título animado letra por letra (normal)
        t = time.time()
        for i, letra in enumerate(title):
            phase = t * 2 + i * 0.5
            dy = math.sin(phase) * 18
            angle = math.sin(phase) * 12
            letra_surf = font_title.render(letra, True, (255,255,255))
            letra_surf = pygame.transform.rotate(letra_surf, angle)
            letra_rect = letra_surf.get_rect(center=(start_x + i * spacing, base_y + dy))
            screen.blit(letra_surf, letra_rect)
            letras_rects.append((letra, letra_rect))

    # Mensagem piscando mais para baixo
    if not mostrar_opcoes and letras_bolas is None:
        t = time.time()
        if int(t*2) % 2 == 0:
            hint_text = font_hint.render("APERTE [ESPAÇO] PARA CONTINUAR", True, (255,255,255))
            hint_surf = pygame.Surface(hint_text.get_size(), pygame.SRCALPHA)
            hint_surf.blit(hint_text, (0,0))
            hint_surf.set_alpha(180)
            hint_rect = hint_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 80))
            screen.blit(hint_surf, hint_rect)
    elif mostrar_opcoes and letras_bolas is None:
        # Opções
        options = ["JOGAR", "AJUDA", "CRÉDITOS"]
        frames = []
        opt_y_start = HEIGHT//2 + 10
        frame_w, frame_h = 340, 60
        padding_y = 24
        t = time.time()
        for i, opt in enumerate(options):
            opt_text = font_opt.render(opt, True, (255,255,255))
            opt_rect = opt_text.get_rect(center=(WIDTH//2, opt_y_start + i*(frame_h + padding_y)))
            screen.blit(opt_text, opt_rect)
            frame_rect = pygame.Rect(
                opt_rect.centerx - frame_w//2, opt_rect.centery - frame_h//2,
                frame_w, frame_h
            )
            frames.append(frame_rect)
            # Frame de seleção piscando
            if i == selected_idx:
                blink = 180 + int(60 * (0.5 + 0.5 * math.sin(t * 2)))
                sel_surf = pygame.Surface((frame_rect.width, frame_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(sel_surf, (255,255,255,blink), sel_surf.get_rect(), width=6, border_radius=18)
                screen.blit(sel_surf, (frame_rect.x, frame_rect.y))
        # [X] SAIR no canto inferior esquerdo
        exit_text = font_exit.render("[X] SAIR", True, (200,200,200))
        exit_surf = pygame.Surface(exit_text.get_size(), pygame.SRCALPHA)
        exit_surf.blit(exit_text, (0,0))
        exit_surf.set_alpha(100)
        screen.blit(exit_surf, (24, HEIGHT - 40))

    # RETORNA OS RETÂNGULOS DAS LETRAS PARA CLIQUE
    return letras_rects

def draw_modo_menu():
    screen = pygame.display.get_surface()
    font_title = pygame.font.Font(FONT_PATH, 48)
    font_opt = pygame.font.Font(FONT_PATH, 32)

    screen.fill((10, 10, 20))

    # Título centralizado
    title_text = font_title.render("ESCOLHA O MODO DE JOGO", True, (255,255,255))
    title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 120))
    screen.blit(title_text, title_rect)

    # Opções centralizadas, uma embaixo da outra, cada uma em um frame do mesmo tamanho
    opt1_text = font_opt.render("[1] VS LOCAL", True, (255,255,255))
    opt2_text = font_opt.render("[2] VS BOT", True, (255,255,255))

    # Descubra o maior tamanho
    max_width = max(opt1_text.get_width(), opt2_text.get_width())
    max_height = max(opt1_text.get_height(), opt2_text.get_height())

    # Centralize as opções
    opt1_rect = opt1_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 20))
    opt2_rect = opt2_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 60))

    # Frame para cada opção (mesmo tamanho)
    padding_x, padding_y = 32, 16
    frame_w = max_width + 2*padding_x
    frame_h = max_height + 2*padding_y

    frame1 = pygame.Rect(
        opt1_rect.centerx - frame_w//2, opt1_rect.centery - frame_h//2,
        frame_w, frame_h
    )
    frame2 = pygame.Rect(
        opt2_rect.centerx - frame_w//2, opt2_rect.centery - frame_h//2,
        frame_w, frame_h
    )
    pygame.draw.rect(screen, (255,255,255), frame1, width=3, border_radius=10)
    pygame.draw.rect(screen, (255,255,255), frame2, width=3, border_radius=10)

    screen.blit(opt1_text, opt1_rect)
    screen.blit(opt2_text, opt2_rect)

def draw_comandos_menu():
    screen = pygame.display.get_surface()
    font_menu = pygame.font.Font(FONT_PATH, 32)
    screen.fill((10, 10, 20))
    title = font_menu.render("COMANDOS", True, (255,255,255))
    title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//2 - 180))
    screen.blit(title, title_rect)
    msg1 = font_menu.render("JOGADOR ESQUERDA: W/S", True, (200,200,200))
    msg2 = font_menu.render("JOGADOR DIREITA: ↑/↓", True, (200,200,200))
    msg3 = font_menu.render("[Z] VOLTAR AO MENU", True, (180,180,180))
    msg4 = font_menu.render("[ESPAÇO] COMEÇAR", True, (180,180,180))
    screen.blit(msg1, msg1.get_rect(center=(WIDTH//2, HEIGHT//2 - 60)))
    screen.blit(msg2, msg2.get_rect(center=(WIDTH//2, HEIGHT//2)))
    screen.blit(msg3, msg3.get_rect(center=(WIDTH//2, HEIGHT//2 + 80)))
    screen.blit(msg4, msg4.get_rect(center=(WIDTH//2, HEIGHT//2 + 130)))

def draw_gameover(winner):
    screen = pygame.display.get_surface()
    font_menu = pygame.font.Font(FONT_PATH, 36)
    screen.fill((10, 10, 20))
    title = font_menu.render("FIM DE JOGO!", True, (255,255,255))
    screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//2 - 120)))
    msg = font_menu.render(f"VENCEDOR: {winner.upper()}", True, (255,255,0))
    screen.blit(msg, msg.get_rect(center=(WIDTH//2, HEIGHT//2)))
    msg2 = font_menu.render("[ESPAÇO] VOLTAR AO MENU", True, (200,200,200))
    screen.blit(msg2, msg2.get_rect(center=(WIDTH//2, HEIGHT//2 + 100)))

def draw_neon_arena():
    # Borda branca sólida e simples
    pygame.draw.rect(screen, (255,255,255), (ARENA_X, ARENA_Y, ARENA_W, ARENA_H), width=8)
    # Linha central levemente transparente
    center_line = pygame.Surface((8, ARENA_H), pygame.SRCALPHA)
    pygame.draw.rect(center_line, (255,255,255,80), (0,0,8,ARENA_H))
    screen.blit(center_line, (ARENA_CENTER_X-4, ARENA_Y))

def draw_paddle(x, y, color=(255,255,255), power=None, power_time_left=None):
    paddle_w, paddle_h = 28, 120
    cor = color
    if power == "uva":
        cor = (180,0,255)
        paddle_h = 160
    elif power == "banana":
        cor = (255,255,0)
    elif power == "morango":
        cor = (255,0,0)
    elif power == "melancia":
        cor = (255,255,255)
        paddle_h = 140
    elif power == "blueberry":
        cor = (120,200,255)
    rect = pygame.Rect(x - paddle_w//2, y - paddle_h//2, paddle_w, paddle_h)
    pygame.draw.rect(screen, cor, rect, border_radius=8)

def draw_ball_trail(rastro, fogo=False):
    for r in rastro:
        surf = pygame.Surface((r['radius']*2, r['radius']*2), pygame.SRCALPHA)
        cor = r.get('color', (255,255,255))
        pygame.draw.circle(surf, cor + (int(r['alpha']),), (int(r['radius']), int(r['radius'])), int(r['radius']))
        screen.blit(surf, (r['x']-r['radius'], r['y']-r['radius']))
        if fogo:
            # Efeito fogo: glow laranja/vermelho
            fogo_surf = pygame.Surface((r['radius']*3, r['radius']*3), pygame.SRCALPHA)
            pygame.draw.circle(fogo_surf, (255,120,0,80), (int(r['radius']*1.5), int(r['radius']*1.5)), int(r['radius']*1.5))
            pygame.draw.circle(fogo_surf, (255,40,0,60), (int(r['radius']*1.5), int(r['radius']*1.5)), int(r['radius']))
            screen.blit(fogo_surf, (r['x']-r['radius']*1.5, r['y']-r['radius']*1.5))

def draw_ball(x, y, radius=14, color=(255,255,255)):
    pygame.draw.circle(screen, color, (int(x), int(y)), radius)

def draw_score(left, right):
    font = pygame.font.Font(FONT_PATH, 48)
    # Centralizado no campo esquerdo
    left_text = font.render(str(left), True, (180,180,180))
    left_x = ARENA_LEFT + (ARENA_W // 4) - (left_text.get_width() // 2)
    left_y = ARENA_TOP + 30
    screen.blit(left_text, (left_x, left_y))
    # Centralizado no campo direito
    right_text = font.render(str(right), True, (180,180,180))
    right_x = ARENA_LEFT + (3 * ARENA_W // 4) - (right_text.get_width() // 2)
    right_y = ARENA_TOP + 30
    screen.blit(right_text, (right_x, right_y))

def draw_mode_label(tempo_str, tempo_acabando=False, tempo_acabando_start=None):
    font = pygame.font.Font(FONT_PATH, 28)
    color = (255,0,0) if tempo_acabando else (0,0,0)
    text = font.render(tempo_str, True, color)
    w, h = text.get_size()
    rect_w = w + 40
    rect_h = h + 16
    rect_x = ARENA_CENTER_X - rect_w // 2
    rect_y = ARENA_BOTTOM - 2
    pygame.draw.rect(screen, (255,255,255), (rect_x, rect_y, rect_w, rect_h), border_radius=8)
    screen.blit(text, (rect_x + (rect_w - w)//2, rect_y + (rect_h - h)//2))
    # Mensagem de tempo acabando (1 minuto)
    if tempo_acabando:
        aviso_font = pygame.font.Font(FONT_PATH, 24)
        aviso_text = aviso_font.render("1 MINUTO RESTANTE!", True, (255,0,0))
        aviso_rect = aviso_text.get_rect(center=(rect_x + rect_w//2, rect_y + rect_h + 28))
        screen.blit(aviso_text, aviso_rect)

def draw_melancia_espelhada(x, y, power_time_left):
    paddle_w, paddle_h = 28, 140  # altura maior
    cor = (0,255,120)
    rect = pygame.Rect(x - paddle_w//2, y - paddle_h//2, paddle_w, paddle_h)
    pygame.draw.rect(screen, cor, rect, border_radius=8)

def render_visual(
    l_paddle_x, l_paddle_y, l_paddle_power, l_paddle_power_time,
    r_paddle_x, r_paddle_y, r_paddle_power, r_paddle_power_time,
    ball_x, ball_y, ball_rastro,
    habilidades,
    left_score, right_score,
    tempo_str,
    ball_color=(255,255,255),
    impact_left=False, impact_right=False,
    fake_balls=None,
    festival=None,
    mapa_escolhido=0,
    ball=None,
    tempo_acabando=False,
    tempo_acabando_start=None
):
    global paddle_trail_left, paddle_trail_right
    global paddle_shake_left, paddle_shake_right, paddle_shake_time_left, paddle_shake_time_right
    global fan_angle
    fan_angle += 0.04  # velocidade de rotação

    screen.fill((10, 10, 20))
    arena_draw_functions = [
        draw_arena_alpha,
        draw_arena_beta,
        draw_arena_gamma,
        draw_arena_delta,
        draw_arena_epsilon,
        draw_arena_zeta
    ]
    if mapa_escolhido == 1:
        draw_arena_beta(screen, ARENA_X, ARENA_Y, ARENA_W, ARENA_H, angle=fan_angle)
    else:
        arena_func = arena_draw_functions[mapa_escolhido]
        arena_func(screen, ARENA_X, ARENA_Y, ARENA_W, ARENA_H)

    if hasattr(pygame, "festival_ativo") and pygame.festival_ativo:
        draw_festival_columns(screen, WIDTH, HEIGHT, ARENA_LEFT, ARENA_RIGHT, festival)
        draw_festival_text(screen, WIDTH, ARENA_TOP, FONT_PATH)
    
    # Desenha as frutas de habilidade
    for h in habilidades:
        if h["tipo"] in ["uva", "banana", "morango", "melancia", "blueberry"]:
            draw_habilidade_fruta(h["x"], h["y"], h["tipo"])

    # --- RAQUETE ESPELHADA MELANCIA ---
    if l_paddle_power == "melancia":
        espelhada_y = ARENA_BOTTOM - (l_paddle_y - ARENA_TOP)
        draw_melancia_espelhada(l_paddle_x, espelhada_y, l_paddle_power_time)
    if r_paddle_power == "melancia":
        espelhada_y = ARENA_BOTTOM - (r_paddle_y - ARENA_TOP)
        draw_melancia_espelhada(r_paddle_x, espelhada_y, r_paddle_power_time)

    # --- ANIMAÇÃO GELATINA E RASTRO ---
    # Detecta movimento e parada para shake
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

    # Shake gelatina
    shake_left = 0
    shake_right = 0
    if time.time() - paddle_shake_time_left < 0.18:
        shake_left = math.sin((time.time() - paddle_shake_time_left)*18) * 7
    if time.time() - paddle_shake_time_right < 0.18:
        shake_right = math.sin((time.time() - paddle_shake_time_right)*18) * 7

    # Rastro: só mantém os últimos 0.25s
    paddle_trail_left = [t for t in paddle_trail_left if time.time() - t["time"] < 0.25]
    paddle_trail_right = [t for t in paddle_trail_right if time.time() - t["time"] < 0.25]

    # Desenha rastro esquerda
    for t in paddle_trail_left:
        alpha = int(110 * (1 - (time.time() - t["time"])/0.25))
        alpha = max(0, min(255, alpha))
        trail_surf = pygame.Surface((28, 24), pygame.SRCALPHA)
        cor = (180,180,255, alpha)
        pygame.draw.rect(trail_surf, cor, trail_surf.get_rect(), border_radius=8)
        trail_x = l_paddle_x - 14
        trail_y = t["y"] - 12 + (8 * t["dir"])
        screen.blit(trail_surf, (trail_x, trail_y))

    # Desenha rastro direita
    for t in paddle_trail_right:
        alpha = int(110 * (1 - (time.time() - t["time"])/0.25))
        alpha = max(0, min(255, alpha))
        trail_surf = pygame.Surface((28, 24), pygame.SRCALPHA)
        cor = (255,180,180, alpha)
        pygame.draw.rect(trail_surf, cor, trail_surf.get_rect(), border_radius=8)
        trail_x = r_paddle_x - 14
        trail_y = t["y"] - 12 + (8 * t["dir"])
        screen.blit(trail_surf, (trail_x, trail_y))

    # Raquetes com poderes + shake
    draw_paddle(l_paddle_x, l_paddle_y + shake_left, (255,255,255), l_paddle_power, l_paddle_power_time)
    draw_paddle(r_paddle_x, r_paddle_y + shake_right, (255,255,255), r_paddle_power, r_paddle_power_time)

    # Raquetes com poderes
    draw_paddle(l_paddle_x, l_paddle_y, (255,255,255), l_paddle_power, l_paddle_power_time)
    draw_paddle(r_paddle_x, r_paddle_y, (255,255,255), r_paddle_power, r_paddle_power_time)

    # --- DESENHA AS BOLAS FAKE ---
    if fake_balls:
        for fake in fake_balls:
            draw_ball_trail(fake.rastro)
            draw_ball(fake.x, fake.y, color=fake.color)

    # Bola e rastro principal
    draw_ball_trail(ball_rastro, fogo=getattr(ball, "fogo_ativo", False))
    draw_ball(ball_x, ball_y, color=ball_color)
    # Placar
    draw_score(left_score, right_score)
    # tempo de jogo
    draw_mode_label(tempo_str, tempo_acabando=tempo_acabando, tempo_acabando_start=tempo_acabando_start)
    pygame.display.flip()
    clock.tick(60)

def draw_map_select_menu(selected_idx=0, last_selected_idx=None, som=None):
    screen = pygame.display.get_surface()
    font_title = pygame.font.Font(FONT_PATH, 21)
    font_map = pygame.font.Font(FONT_PATH, 24)
    map_names = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta"]

    # Carregue uma imagem diferente para cada arena
    map_images = [
        pygame.image.load(os.path.join("assets", "images", "alpha.png")).convert_alpha(),
        pygame.image.load(os.path.join("assets", "images", "beta.png")).convert_alpha(),
        pygame.image.load(os.path.join("assets", "images", "alpha.png")).convert_alpha(),
        pygame.image.load(os.path.join("assets", "images", "alpha.png")).convert_alpha(),
        pygame.image.load(os.path.join("assets", "images", "alpha.png")).convert_alpha(),
        pygame.image.load(os.path.join("assets", "images", "alpha.png")).convert_alpha()
    ]

    # Título mais para baixo
    title_text = font_title.render("ESCOLHA UMA ARENA", True, (255,255,255))
    title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 295))
    screen.fill((10, 10, 20))
    screen.blit(title_text, title_rect)

    # Frames dos mapas (mais largos e afastados)
    frame_w, frame_h = 340, 200  # <-- MAIS LARGO!
    padding_x, padding_y = 110, 110
    start_x = WIDTH//2 - (3*frame_w + 2*padding_x)//2
    start_y = HEIGHT//2 - 260

    # Piscar frame de seleção
    t = time.time()
    blink = 180 + int(60 * (0.5 + 0.5 * math.sin(t * 2)))  # alpha entre 120~240, suave

    for i in range(6):
        row = i // 3
        col = i % 3
        x = start_x + col * (frame_w + padding_x)
        y = start_y + row * (frame_h + padding_y)
        frame_rect = pygame.Rect(x, y, frame_w, frame_h)
        # Frame cinza
        pygame.draw.rect(screen, (180,180,180), frame_rect, border_radius=20)
        # Imagem do mapa
        img = pygame.transform.smoothscale(map_images[i], (frame_w-32, frame_h-32))
        img_rect = img.get_rect(center=frame_rect.center)
        screen.blit(img, img_rect)
        # Nome do mapa
        name_text = font_map.render(map_names[i], True, (255,255,255))
        name_rect = name_text.get_rect(center=(frame_rect.centerx, frame_rect.bottom + 28))
        screen.blit(name_text, name_rect)
        # Seleção piscando
        if i == selected_idx:
            sel_surf = pygame.Surface((frame_rect.width+24, frame_rect.height+24), pygame.SRCALPHA)
            sel_surf.fill((0,0,0,0))  # Garante fundo transparente
            blink_alpha = max(80, min(255, int(blink)))  # Garante alpha válido
            pygame.draw.rect(
                sel_surf,
                (255,255,255,blink_alpha),
                sel_surf.get_rect(),
                width=6,
                border_radius=28
            )
            screen.blit(sel_surf, (frame_rect.x-12, frame_rect.y-12))
            if last_selected_idx is not None and last_selected_idx != selected_idx and som is not None:
                som.play_som_menu_selecao()

def draw_ajuda():
    screen = pygame.display.get_surface()
    font_title = pygame.font.Font(FONT_PATH, 48)
    font_body = pygame.font.Font(FONT_PATH, 28)
    font_exit = pygame.font.Font(FONT_PATH, 18)
    screen.fill((10, 10, 20))
    title = font_title.render("COMO JOGAR", True, (255,255,255))
    screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//2 - 180)))
    msg1 = font_body.render("JOGADOR ESQUERDA: W/S", True, (200,200,200))
    msg2 = font_body.render("JOGADOR DIREITA: ↑/↓", True, (200,200,200))
    msg3 = font_body.render("Pegue frutas para poderes!", True, (180,180,180))
    screen.blit(msg1, msg1.get_rect(center=(WIDTH//2, HEIGHT//2 - 60)))
    screen.blit(msg2, msg2.get_rect(center=(WIDTH//2, HEIGHT//2)))
    screen.blit(msg3, msg3.get_rect(center=(WIDTH//2, HEIGHT//2 + 60)))
    exit_text = font_exit.render("[Z] VOLTAR", True, (200,200,200))
    exit_surf = pygame.Surface(exit_text.get_size(), pygame.SRCALPHA)
    exit_surf.blit(exit_text, (0,0))
    exit_surf.set_alpha(100)
    screen.blit(exit_surf, (24, HEIGHT - 40))

def draw_creditos():
    screen = pygame.display.get_surface()
    font_body = pygame.font.Font(FONT_PATH, 32)
    font_exit = pygame.font.Font(FONT_PATH, 18)
    screen.fill((10, 10, 20))
    msg = font_body.render("vitor (página em construção)", True, (255,255,255))
    screen.blit(msg, msg.get_rect(center=(WIDTH//2, HEIGHT//2)))
    exit_text = font_exit.render("[Z] VOLTAR", True, (200,200,200))
    exit_surf = pygame.Surface(exit_text.get_size(), pygame.SRCALPHA)
    exit_surf.blit(exit_text, (0,0))
    exit_surf.set_alpha(100)
    screen.blit(exit_surf, (24, HEIGHT - 40))