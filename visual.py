import pygame 
import time 
import os 
from game.systems.arenas import (
    # Funções para desenhar diferentes arenas
    draw_arena_alpha, draw_arena_beta, draw_arena_gamma,
    draw_arena_delta, draw_arena_epsilon, draw_arena_aleatoria
)
import math 
from game.systems.f_fruta_equipada import draw_power_frame
from config import FONT_PATH
from game.systems.determinacao import arcoiris_color


# OBJETO GLOBAL DO ARQUIVO:
# Essas variáveis globais controlam o estado visual do jogo
fan_angle = 0 # Usado para a animação de rotação da arena beta

paddle_trail_left = [] # Armazena a posição e tempo para criar o rastro da raquete esquerda
paddle_trail_right = [] # Armazena a posição e tempo para criar o rastro da raquete direita
paddle_shake_left = 0 # Valor para o "efeito gelatina" da raquete esquerda
paddle_shake_right = 0 # Valor para o "efeito gelatina" da raquete direita
paddle_shake_time_left = 0 # O momento em que a raquete esquerda se moveu
paddle_shake_time_right = 0 # O momento em que a raquete direita se moveu
fade_borda_fogo = 0.0 # Controla o "fade in/out" da borda de fogo
fade_borda_azul = 0.0 # Controla o "fade in/out" da borda azul/gelo

# Inicializa o Pygame
pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h # Obtém a largura e altura da tela do usuário para tela cheia
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN) # Cria a janela do jogo em tela cheia
pygame.display.set_caption("Ping Pong Neon") # Define o título da janela
clock = pygame.time.Clock() # Cria um objeto para controlar o FPS (Frames por segundo)

mapa_escolhido = 0 # Índice do mapa atual, 0 é o padrão (Alpha)

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

# Cache de imagens de frutas para evitar recarregar a cada frame
FRUIT_IMAGES = {}
def get_fruit_image(tipo):
    # Carrega e armazena a imagem da fruta se ela ainda não estiver em cache
    if tipo not in FRUIT_IMAGES:
        path = os.path.join("assets", "images", "frutas", f"{tipo}.png")
        img = pygame.image.load(path).convert_alpha() # Carrega a imagem com transparência.
        FRUIT_IMAGES[tipo] = pygame.transform.smoothscale(img, (32, 32)) # Redimensiona suavemente
    return FRUIT_IMAGES[tipo]

def draw_habilidade_fruta(x, y, tipo):
    # Desenha uma fruta de poder com um brilho suave
    img = get_fruit_image(tipo)
    rect = img.get_rect(center=(int(x), int(y)))
    glow = pygame.Surface((44,44), pygame.SRCALPHA) # Cria uma superfície transparente para o brilho
    pygame.draw.circle(glow, (255,255,255,35), (22,22), 20) # Desenha um círculo semi-transparente para o brilho
    screen.blit(glow, (rect.centerx-22, rect.centery-22)) # Desenha o brilho
    screen.blit(img, rect) # Desenha a imagem da fruta

def draw_paddle(x, y, color=(255,255,255), power=None, power_time_left=None, determinacao_ativa=False):
    # Desenha a raquete com base na sua posição e poder
    paddle_w, paddle_h = 28, 120 # Dimensões padrão da raquete
    cor = color
    # Altera a cor e a altura da raquete se houver um poder ativo
    if determinacao_ativa:
        paddle_h = 160
        cor = arcoiris_color(int(time.time()*100)%255)  # Ou qualquer função de cor dinâmica
    else:
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

def draw_ball_trail(rastro, fogo=False, fogo_azul=False):
    # Desenha o rastro da bola, que é uma lista de círculos que diminuem a opacidade
    for r in rastro:
        surf = pygame.Surface((r['radius']*2, r['radius']*2), pygame.SRCALPHA)
        cor = r.get('color', (255,255,255))
        pygame.draw.circle(surf, cor + (int(r['alpha']),), (int(r['radius']), int(r['radius'])), int(r['radius']))
        screen.blit(surf, (r['x']-r['radius'], r['y']-r['radius']))
        # Adiciona brilho de fogo ou gelo se as condições forem verdadeiras
        if fogo_azul:
            fogo_surf = pygame.Surface((r['radius']*3, r['radius']*3), pygame.SRCALPHA)
            pygame.draw.circle(fogo_surf, (80,120,255,80), (int(r['radius']*1.5), int(r['radius']*1.5)), int(r['radius']*1.5))
            pygame.draw.circle(fogo_surf, (120,40,255,60), (int(r['radius']*1.5), int(r['radius']*1.5)), int(r['radius']))
            screen.blit(fogo_surf, (r['x']-r['radius']*1.5, r['y']-r['radius']*1.5))
        elif fogo:
            fogo_surf = pygame.Surface((r['radius']*3, r['radius']*3), pygame.SRCALPHA)
            pygame.draw.circle(fogo_surf, (255,120,0,80), (int(r['radius']*1.5), int(r['radius']*1.5)), int(r['radius']*1.5))
            pygame.draw.circle(fogo_surf, (255,40,0,60), (int(r['radius']*1.5), int(r['radius']*1.5)), int(r['radius']))
            screen.blit(fogo_surf, (r['x']-r['radius']*1.5, r['y']-r['radius']*1.5))

def draw_ball(x, y, radius=14, color=(255,255,255), fogo=False, fogo_azul=False, fogo_start_time=None, angle=0):
    # Desenha a bola principal
    if fogo_azul:
        pygame.draw.circle(screen, (80,120,255), (int(x), int(y)), radius)
    elif fogo:
        pygame.draw.circle(screen, (255,120,0), (int(x), int(y)), radius)
    else:
        pygame.draw.circle(screen, color, (int(x), int(y)), radius)

def draw_score(left, right):
    # Desenha o placar dos jogadores
    font = pygame.font.Font(FONT_PATH, 48)
    left_text = font.render(str(left), True, (180,180,180))
    left_x = ARENA_LEFT + (ARENA_W // 4) - (left_text.get_width() // 2)
    left_y = ARENA_TOP + 30
    screen.blit(left_text, (left_x, left_y))
    right_text = font.render(str(right), True, (180,180,180))
    right_x = ARENA_LEFT + (3 * ARENA_W // 4) - (right_text.get_width() // 2)
    right_y = ARENA_TOP + 30
    screen.blit(right_text, (right_x, right_y))

def draw_mode_label(tempo_str, tempo_acabando=False, tempo_acabando_start=None):
    # Desenha a caixa de tempo 
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
    if tempo_acabando:
        aviso_font = pygame.font.Font(FONT_PATH, 24)
        aviso_text = aviso_font.render("1 MINUTO RESTANTE!", True, (255,0,0))
        aviso_rect = aviso_text.get_rect(center=(rect_x + rect_w//2, rect_y + rect_h + 28))
        screen.blit(aviso_text, aviso_rect)

def draw_melancia_espelhada(x, y, power_time_left):
    # Desenha a raquete espelhada para o poder melancia
    paddle_w, paddle_h = 28, 140
    cor = (0,255,120)
    rect = pygame.Rect(x - paddle_w//2, y - paddle_h//2, paddle_w, paddle_h)
    pygame.draw.rect(screen, cor, rect, border_radius=8)

def draw_menu_principal(selected_idx=0, mostrar_opcoes=False, letras_bolas=None, letras_voltando=False):
    # Desenha a tela do menu principal
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

    # Animação inicial das letras como bolas
    if letras_bolas is not None:
        for letra in letras_bolas:
            letra_surf = font_title.render(letra['letra'], True, (255,255,255))
            letra_surf = pygame.transform.rotate(letra_surf, 0)
            letra_rect = letra_surf.get_rect(center=(letra['x'], letra['y']))
            screen.blit(letra_surf, letra_rect)
            letras_rects.append((letra['letra'], letra_rect))
        exit_text = font_exit.render("[X] SAIR", True, (200,200,200))
        exit_surf = pygame.Surface(exit_text.get_size(), pygame.SRCALPHA)
        exit_surf.blit(exit_text, (0,0))
        exit_surf.set_alpha(100)
        exit_rect = exit_surf.get_rect(topleft=(24, HEIGHT - 40))
        screen.blit(exit_surf, exit_rect)
        return letras_rects, None, exit_rect

    # Animação do título com movimento de seno
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

    # Desenha as opções do menu 
    if not mostrar_opcoes:
        if int(t*2) % 2 == 0:
            hint_text = font_hint.render("APERTE [ESPAÇO] PARA CONTINUAR", True, (255,255,255))
            hint_surf = pygame.Surface(hint_text.get_size(), pygame.SRCALPHA)
            hint_surf.blit(hint_text, (0,0))
            hint_surf.set_alpha(180)
            hint_rect = hint_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 80))
            screen.blit(hint_surf, hint_rect)
        exit_text = font_exit.render("[X] SAIR", True, (200,200,200))
        exit_surf = pygame.Surface(exit_text.get_size(), pygame.SRCALPHA)
        exit_surf.blit(exit_text, (0,0))
        exit_surf.set_alpha(100)
        exit_rect = exit_surf.get_rect(topleft=(24, HEIGHT - 40))
        screen.blit(exit_surf, exit_rect)
        return letras_rects, None, exit_rect

    options = ["JOGAR", "AJUDA", "CRÉDITOS"]
    frames = []
    opt_y_start = HEIGHT//2 + 10
    frame_w, frame_h = 340, 60
    padding_y = 24
    mx, my = pygame.mouse.get_pos()
    mouse_idx = None
    for i, opt in enumerate(options):
        opt_text = font_opt.render(opt, True, (255,255,255))
        opt_rect = opt_text.get_rect(center=(WIDTH//2, opt_y_start + i*(frame_h + padding_y)))
        screen.blit(opt_text, opt_rect)
        frame_rect = pygame.Rect(
            opt_rect.centerx - frame_w//2, opt_rect.centery - frame_h//2,
            frame_w, frame_h
        )
        frames.append(frame_rect)
        if frame_rect.collidepoint(mx, my):
            mouse_idx = i
    t = time.time()
    blink = 180 + int(60 * (0.5 + 0.5 * math.sin(t * 2)))
    idx_to_draw = mouse_idx if mouse_idx is not None else selected_idx
    frame_rect = frames[idx_to_draw]
    sel_surf = pygame.Surface((frame_rect.width, frame_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(sel_surf, (255,255,255,blink), sel_surf.get_rect(), width=6, border_radius=18)
    screen.blit(sel_surf, (frame_rect.x, frame_rect.y))
    exit_text = font_exit.render("[X] SAIR", True, (200,200,200))
    exit_surf = pygame.Surface(exit_text.get_size(), pygame.SRCALPHA)
    exit_surf.blit(exit_text, (0,0))
    exit_surf.set_alpha(100)
    exit_rect = exit_surf.get_rect(topleft=(24, HEIGHT - 40))
    screen.blit(exit_surf, exit_rect)
    return frames, mouse_idx, exit_rect

def draw_modo_menu(selected_idx=0):
    # Desenha o menu para selecionar o modo de jogo 
    screen = pygame.display.get_surface()
    font_title = pygame.font.Font(FONT_PATH, 48)
    font_opt = pygame.font.Font(FONT_PATH, 32)
    screen.fill((10, 10, 20))

    title_text = font_title.render("ESCOLHA O MODO DE JOGO", True, (255,255,255))
    title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 120))
    screen.blit(title_text, title_rect)

    options = ["[1] VS LOCAL", "[2] VS BOT  "]
    frames = []
    opt_y_start = HEIGHT//2 - 20
    frame_w, frame_h = 440, 80
    padding_y = 110
    t = time.time()
    mx, my = pygame.mouse.get_pos()
    mouse_idx = None
    for i, opt in enumerate(options):
        opt_text = font_opt.render(opt, True, (255,255,255))
        opt_rect = opt_text.get_rect(center=(WIDTH//2, opt_y_start + i*padding_y))
        screen.blit(opt_text, opt_rect)
        frame_rect = pygame.Rect(
            opt_rect.centerx - frame_w//2, opt_rect.centery - frame_h//2,
            frame_w, frame_h
        )
        frames.append(frame_rect)
        blink = 180 + int(60 * (0.5 + 0.5 * math.sin(t * 2)))
        if i == selected_idx or frame_rect.collidepoint(mx, my):
            sel_surf = pygame.Surface((frame_rect.width, frame_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(sel_surf, (255,255,255,blink), sel_surf.get_rect(), width=6, border_radius=18)
            screen.blit(sel_surf, (frame_rect.x, frame_rect.y))
        if frame_rect.collidepoint(mx, my):
            mouse_idx = i
    font_exit = pygame.font.Font(FONT_PATH, 18)
    exit_text = font_exit.render("[Z] VOLTAR", True, (200,200,200))
    exit_surf = pygame.Surface(exit_text.get_size(), pygame.SRCALPHA)
    exit_surf.blit(exit_text, (0,0))
    exit_surf.set_alpha(100)
    exit_rect = exit_surf.get_rect(topleft=(24, HEIGHT - 40))
    screen.blit(exit_surf, exit_rect)
    mx, my = pygame.mouse.get_pos()
    blink = 180 + int(60 * (0.5 + 0.5 * math.sin(time.time() * 2)))
    if exit_rect.collidepoint(mx, my):
        sel_surf = pygame.Surface(exit_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(sel_surf, (255,255,255,blink), sel_surf.get_rect(), width=3, border_radius=8)
        screen.blit(sel_surf, exit_rect)
    return frames, mouse_idx, exit_rect

def draw_gameover(winner):
    # Tela de fim de jogo
    screen = pygame.display.get_surface()
    font_menu = pygame.font.Font(FONT_PATH, 36)
    screen.fill((10, 10, 20))
    title = font_menu.render("FIM DE JOGO!", True, (255,255,255))
    screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//2 - 120)))
    msg = font_menu.render(f"VENCEDOR: {winner.upper()}", True, (255,255,0))
    screen.blit(msg, msg.get_rect(center=(WIDTH//2, HEIGHT//2)))
    msg2 = font_menu.render("[ESPAÇO] VOLTAR AO MENU", True, (200,200,200))
    screen.blit(msg2, msg2.get_rect(center=(WIDTH//2, HEIGHT//2 + 100)))

#-------------------A FUNÇÃO MAIS IMPORTANTE, RENDERIZA TUDO----------------------------------------------------------------------------------------------------------------------------------------------------------
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

    screen.fill((10, 10, 20))
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
        shake_left = math.sin((time.time() - paddle_shake_time_left)*18) * 7
    if time.time() - paddle_shake_time_right < 0.18:
        shake_right = math.sin((time.time() - paddle_shake_time_right)*18) * 7

    paddle_trail_left = [t for t in paddle_trail_left if time.time() - t["time"] < 0.25]
    paddle_trail_right = [t for t in paddle_trail_right if time.time() - t["time"] < 0.25]

    for t in paddle_trail_left:
        alpha = int(110 * (1 - (time.time() - t["time"])/0.25))
        alpha = max(0, min(255, alpha))
        trail_surf = pygame.Surface((28, 24), pygame.SRCALPHA)
        cor = (180,180,255, alpha)
        pygame.draw.rect(trail_surf, cor, trail_surf.get_rect(), border_radius=8)
        trail_x = l_paddle_x - 14
        trail_y = t["y"] - 12 + (8 * t["dir"])
        screen.blit(trail_surf, (trail_x, trail_y))

    for t in paddle_trail_right:
        alpha = int(110 * (1 - (time.time() - t["time"])/0.25))
        alpha = max(0, min(255, alpha))
        trail_surf = pygame.Surface((28, 24), pygame.SRCALPHA)
        cor = (255,180,180, alpha)
        pygame.draw.rect(trail_surf, cor, trail_surf.get_rect(), border_radius=8)
        trail_x = r_paddle_x - 14
        trail_y = t["y"] - 12 + (8 * t["dir"])
        screen.blit(trail_surf, (trail_x, trail_y))

    # Para a raquete esquerda
    draw_paddle(
        l_paddle_x, l_paddle_y + shake_left,
        (255,255,255), l_paddle_power, l_paddle_power_time,
        determinacao_ativa=determinacao_manager.is_active() and determinacao_manager.get_side() == "left"
    )

    # Para a raquete direita
    draw_paddle(
        r_paddle_x, r_paddle_y + shake_right,
        (255,255,255), r_paddle_power, r_paddle_power_time,
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
    dt = clock.tick() / 1000.0
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
    cor1 = (0,0,0)
    cor2 = (0,0,0)
    fade = 0.0

    if fade_borda_fogo > 0.01 or fade_borda_azul > 0.01:
        t = time.time()
        fade = fade_borda_fogo * (1 - fade_borda_azul) + fade_borda_azul
        if fade_borda_azul > 0.01:
            cor1 = (
                int(255 * (1-fade_borda_azul) + 80 * fade_borda_azul),
                int(120 * (1-fade_borda_azul) + 120 * fade_borda_azul),
                int(0 * (1-fade_borda_azul) + 255 * fade_borda_azul)
            )
            cor2 = (
                int(255 * (1-fade_borda_azul) + 120 * fade_borda_azul),
                int(40 * (1-fade_borda_azul) + 40 * fade_borda_azul),
                int(0 * (1-fade_borda_azul) + 255 * fade_borda_azul)
            )
            intensidade = int(120 * fade_borda_azul + 80 * (1-fade_borda_azul))
            camadas = 4
        else:
            cor1 = (255,120,0)
            cor2 = (255,40,0)
            intensidade = int(80 * fade_borda_fogo)
            camadas = 3
        for i in range(camadas):
            alpha = int(intensidade * (1 - i/camadas) * fade * (0.7 + 0.3 * math.sin(t*2+i)))
            thickness = 18 - i*4
            surf = pygame.Surface((WIDTH, thickness), pygame.SRCALPHA)
            surf.fill(cor1 + (alpha,))
            screen.blit(surf, (0,0))
            screen.blit(surf, (0, HEIGHT-thickness))
            surf_v = pygame.Surface((thickness, HEIGHT), pygame.SRCALPHA)
            surf_v.fill(cor1 + (alpha,))
            screen.blit(surf_v, (0,0))
            screen.blit(surf_v, (WIDTH-thickness,0))
            if fade_borda_azul > 0.01:
                alpha2 = int(alpha * 0.7)
                surf2 = pygame.Surface((WIDTH, thickness//2), pygame.SRCALPHA)
                surf2.fill(cor2 + (alpha2,))
                screen.blit(surf2, (0,0))
                screen.blit(surf2, (0, HEIGHT-thickness//2))
                surf2_v = pygame.Surface((thickness//2, HEIGHT), pygame.SRCALPHA)
                surf2_v.fill(cor2 + (alpha2,))
                screen.blit(surf2_v, (0,0))
                screen.blit(surf2_v, (WIDTH-thickness//2,0))

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

def draw_map_select_menu(selected_idx=0, last_selected_idx=None, som=None):
    # Desenha o menu de seleção de arena, com imagens e nomes dos mapas
    screen = pygame.display.get_surface()
    font_title = pygame.font.Font(FONT_PATH, 21)
    font_map = pygame.font.Font(FONT_PATH, 24)
    map_names = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Aleatória"]

    title_text = font_title.render("ESCOLHA UMA ARENA", True, (255,255,255))
    title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 295))
    screen.fill((10, 10, 20))
    screen.blit(title_text, title_rect)

    frame_w, frame_h = 340, 200
    padding_x, padding_y = 110, 110
    start_x = WIDTH//2 - (3*frame_w + 2*padding_x)//2
    start_y = HEIGHT//2 - 260

    t = time.time()
    blink = 180 + int(60 * (0.5 + 0.5 * math.sin(t * 2)))

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

        # Fundo do frame
        if i == 5:  # Arena Aleatória
            pygame.draw.rect(screen, (10,10,20), frame_rect, border_radius=20)  
        else:
            pygame.draw.rect(screen, (180,180,180), frame_rect, border_radius=20)

        if i == 5:  # Arena Aleatória
            # Animação do "?"
            t = time.time()
            float_y = math.sin(t * 2.5) * 16  
            spin_phase = (t % 4) 
            if spin_phase < 0.7:
                angle = (spin_phase / 0.7) * 360  
            else:
                angle = math.sin(t * 0.7) * 8  

            font_q = pygame.font.Font(FONT_PATH, 120)
            q_surf = font_q.render("?", True, (255,255,255))  # Branco
            q_surf = pygame.transform.rotozoom(q_surf, angle, 1)
            q_rect = q_surf.get_rect(center=(frame_rect.centerx, frame_rect.centery + float_y))
            screen.blit(q_surf, q_rect)
        else:
            img = MAP_IMAGES[i]
            if img and img.get_alpha() is None:
                img = img.convert_alpha()
            MAP_IMAGES[i] = img  # Atualiza o cache para não precisar fazer de novo
            img = pygame.transform.smoothscale(img, (frame_w-32, frame_h-32))
            img_rect = img.get_rect(center=frame_rect.center)
            screen.blit(img, img_rect)
        
        name_text = font_map.render(map_names[i], True, (255,255,255))
        name_rect = name_text.get_rect(center=(frame_rect.centerx, frame_rect.bottom + 28))
        screen.blit(name_text, name_rect)

    idx_to_draw = mouse_idx if mouse_idx is not None else selected_idx
    frame_rect = frame_rects[idx_to_draw]
    blink_alpha = max(80, min(255, int(blink)))
    sel_surf = pygame.Surface((frame_rect.width+24, frame_rect.height+24), pygame.SRCALPHA)
    sel_surf.fill((0,0,0,0))
    pygame.draw.rect(
        sel_surf,
        (255,255,255,blink_alpha),
        sel_surf.get_rect(),
        width=6,
        border_radius=28
    )
    screen.blit(sel_surf, (frame_rect.x-12, frame_rect.y-12))
    return frame_rects, mouse_idx

def draw_ajuda():
    # Tela de ajuda
    screen = pygame.display.get_surface()
    font_title = pygame.font.Font(FONT_PATH, 48)
    font_sub = pygame.font.Font(FONT_PATH, 32)
    font_body = pygame.font.Font(FONT_PATH, 20)
    font_small = pygame.font.Font(FONT_PATH, 16)
    font_exit = pygame.font.Font(FONT_PATH, 18)
    screen.fill((10, 10, 20))

    # Título principal 
    title = font_title.render("Como jogar", True, (255,255,255))
    screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//2 - 320)))

    # Seção de controles 
    section_top_y = HEIGHT//2 - 240
    section_h = 160
    section_w = 420
    section_x_left = WIDTH//2 - section_w - 32
    section_x_right = WIDTH//2 + 32

    # Barra vertical divisória
    pygame.draw.line(screen, (80,80,120), (WIDTH//2, section_top_y), (WIDTH//2, section_top_y + section_h), 6)

    # MULTIJOGADOR
    sub1 = font_sub.render("MULTIJOGADOR", True, (255,255,255))
    screen.blit(sub1, sub1.get_rect(center=(section_x_left + section_w//2, section_top_y + 28)))
    # Comandos
    font_cmd = pygame.font.Font(FONT_PATH, 15)
    txt1 = font_cmd.render("Jogador Esquerda: W/S", True, (180,220,255))
    txt2 = font_cmd.render("Jogador Direita: ↑ / ↓", True, (255,180,180))
    screen.blit(txt1, (section_x_left + 36, section_top_y + 70))
    screen.blit(txt2, (section_x_left + 36, section_top_y + 110))

    # BOT
    sub2 = font_sub.render("BOT", True, (255,255,255))
    screen.blit(sub2, sub2.get_rect(center=(section_x_right + section_w//2, section_top_y + 28)))
    txt3 = font_cmd.render("Você: W/S", True, (180,220,255))
    txt4 = font_cmd.render("BOT: automático", True, (255,180,180))
    screen.blit(txt3, (section_x_right + 36, section_top_y + 70))
    screen.blit(txt4, (section_x_right + 36, section_top_y + 110))

    # Título "Durante o jogo" 
    section2_top_y = section_top_y + section_h + 60
    during_title = font_sub.render("Durante o jogo", True, (255,255,255))
    screen.blit(during_title, during_title.get_rect(center=(WIDTH//2, section2_top_y)))

    # Seções FRUTAS e EVENTOS 
    section2_h = 260
    section2_w = 480
    section2_x_left = WIDTH//2 - section2_w - 32
    section2_x_right = WIDTH//2 + 32
    section2_y = section2_top_y + 36

    pygame.draw.line(screen, (80,80,120), (WIDTH//2, section2_y), (WIDTH//2, section2_y + section2_h), 6)

    # FRUTAS 
    t = time.time()
    fruta_title = arcoiris_text("FRUTAS", font_sub, t, section2_x_left + section2_w//2 - 60, section2_y)
    for surf, (x, y) in fruta_title:
        screen.blit(surf, (x, y))
    fruta_y = section2_y + 48

    # Mostra cada fruta e efeito
    from config import POWER_TEXTS
    fruta_types = ["uva", "banana", "morango", "melancia", "blueberry"]
    for i, tipo in enumerate(fruta_types):
        img = get_fruit_image(tipo)
        img = pygame.transform.smoothscale(img, (38,38))
        screen.blit(img, (section2_x_left + 36, fruta_y + i*44))
        txt = font_small.render(POWER_TEXTS.get(tipo, ""), True, (220,220,220))
        screen.blit(txt, (section2_x_left + 90, fruta_y + i*44 + 8))

    # EVENTOS
    eventos_title = font_sub.render("EVENTOS", True, (255,255,255))
    screen.blit(eventos_title, eventos_title.get_rect(center=(section2_x_right + section2_w//2 - 60, section2_y + 8)))
    eventos_y = section2_y + 48
    eventos_info = [
        ("Festival das Frutas", "Várias frutas aparecem na arena!"),
        ("Gato???", "Um gato aparece e persegue a bola!"),
        ("Bola extra", "Uma bola extra aparece na partida!"),
    ]
    for i, (nome, desc) in enumerate(eventos_info):
        nome_surf = font_small.render(nome, True, (255,220,120))
        desc_surf = font_small.render(desc, True, (220,220,220))
        screen.blit(nome_surf, (section2_x_right + 36, eventos_y + i*54))
        screen.blit(desc_surf, (section2_x_right + 36, eventos_y + i*54 + 26))

    # Botão de voltar 
    exit_text = font_exit.render("[Z] VOLTAR", True, (200,200,200))
    exit_surf = pygame.Surface(exit_text.get_size(), pygame.SRCALPHA)
    exit_surf.blit(exit_text, (0,0))
    exit_surf.set_alpha(100)
    exit_rect = exit_surf.get_rect(topleft=(24, HEIGHT - 40))
    screen.blit(exit_surf, exit_rect)
    mx, my = pygame.mouse.get_pos()
    blink = 180 + int(60 * (0.5 + 0.5 * math.sin(time.time() * 2)))
    if exit_rect.collidepoint(mx, my):
        sel_surf = pygame.Surface(exit_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(sel_surf, (255,255,255,blink), sel_surf.get_rect(), width=3, border_radius=8)
        screen.blit(sel_surf, exit_rect)
    return exit_rect

def arcoiris_text(text, font, t, base_x, base_y):
    colors = [
        (255,0,0), (255,127,0), (255,255,0), (0,255,0),
        (0,0,255), (75,0,130), (148,0,211)
    ]
    letras_surfs = []
    arcoiris_offset = int(t*2)
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
    cor_onda = (80,180,255, 120)
    for i in range(-60, 61, 20):
        surf = pygame.Surface((120, altura), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, cor_onda, (0, i, 120, altura))
        screen.blit(surf, (x-60, 0))

def draw_creditos():
    # Tela de créditos com informações minhas e fontes de som
    screen = pygame.display.get_surface()
    font_title = pygame.font.Font(FONT_PATH, 44)
    font_link = pygame.font.Font(FONT_PATH, 22)
    font_sfx = pygame.font.Font(FONT_PATH, 28)
    font_small = pygame.font.Font(FONT_PATH, 18)
    font_exit = pygame.font.Font(FONT_PATH, 18)
    screen.fill((10, 10, 20))
    title = font_title.render("Vitor Nonato Nascimento", True, (255,255,255))
    title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//2 - 220))
    screen.blit(title, title_rect)

    linkedin_img = pygame.image.load("assets/images/linkedin.png").convert_alpha()
    linkedin_img = pygame.transform.smoothscale(linkedin_img, (40, 40))
    link_text = font_link.render("https://www.linkedin.com/in/vitor-n-9441932b1/", True, (80,180,255))
    link_rect = link_text.get_rect()
    total_w = linkedin_img.get_width() + 16 + link_rect.width
    base_x = WIDTH//2 - total_w//2
    base_y = title_rect.bottom + 18
    screen.blit(linkedin_img, (base_x, base_y))
    link_pos = (base_x + linkedin_img.get_width() + 16, base_y + (linkedin_img.get_height() - link_rect.height)//2)
    screen.blit(link_text, link_pos)

    mouse_pos = pygame.mouse.get_pos()
    link_area = pygame.Rect(base_x, base_y, total_w, linkedin_img.get_height())
    blink = 180 + int(60 * (0.5 + 0.5 * math.sin(time.time() * 2)))
    if link_area.collidepoint(mouse_pos):
        sel_surf = pygame.Surface(link_area.size, pygame.SRCALPHA)
        pygame.draw.rect(sel_surf, (255,255,255,blink), sel_surf.get_rect(), width=3, border_radius=8)
        screen.blit(sel_surf, link_area)

    sfx_text = font_sfx.render("MUSICA/SFX:", True, (255,255,255))
    sfx_rect = sfx_text.get_rect(center=(WIDTH//2, base_y + linkedin_img.get_height() + 38))
    screen.blit(sfx_text, sfx_rect)

    fs_text = font_link.render("FREESOUND.ORG/FREEMUSICARCHIVE.ORG", True, (180,180,180))
    fs_rect = fs_text.get_rect(center=(WIDTH//2, sfx_rect.bottom + 22))
    screen.blit(fs_text, fs_rect)

    font_small = pygame.font.Font(FONT_PATH, 10)  # Fonte menor
    sfx_names = [
        ("cat.wav by HamFace", "retro crime movie loop 4.wav by zagi2", "time continues.wav by lomowo"),
        ("Revenge from behind the grave by Gigakoops", "The furcula curse by Gigakoops", "Condemned by Eggy Toast"),
        ("Break In by Eggy Toast", "place holder", "place holder"),
    ]
    num_cols = len(sfx_names[0])
    num_rows = len(sfx_names)
    spacing_x = 24
    spacing_y = 18

    # Calcula largura total do bloco de colunas
    col_widths = []
    for col in range(num_cols):
        max_w = 0
        for row in range(num_rows):
            surf = font_small.render(sfx_names[row][col], True, (255,255,255) if row == 0 else (180,180,180))
            max_w = max(max_w, surf.get_width())
        col_widths.append(max_w)
    total_w = sum(col_widths) + spacing_x * (num_cols - 1)
    start_x = WIDTH // 2 - total_w // 2
    start_y = sfx_rect.bottom + 80  

    # Centraliza cada coluna
    for col in range(num_cols):
        x = start_x + sum(col_widths[:col]) + spacing_x * col + col_widths[col] // 2
        for row in range(num_rows):
            color = (255,255,255) if row == 0 else (180,180,180)
            surf = font_small.render(sfx_names[row][col], True, color)
            rect = surf.get_rect(center=(x, start_y + row * spacing_y))
            screen.blit(surf, rect)

    font_exit = pygame.font.Font(FONT_PATH, 18)
    exit_text = font_exit.render("[Z] VOLTAR", True, (200,200,200))
    exit_surf = pygame.Surface(exit_text.get_size(), pygame.SRCALPHA)
    exit_surf.blit(exit_text, (0,0))
    exit_surf.set_alpha(100)
    exit_rect = exit_surf.get_rect(topleft=(24, HEIGHT - 40))
    screen.blit(exit_surf, exit_rect)
    mx, my = pygame.mouse.get_pos()
    blink = 180 + int(60 * (0.5 + 0.5 * math.sin(time.time() * 2)))
    if exit_rect.collidepoint(mx, my):
        sel_surf = pygame.Surface(exit_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(sel_surf, (255,255,255,blink), sel_surf.get_rect(), width=3, border_radius=8)
        screen.blit(sel_surf, exit_rect)
        return link_area, exit_rect

    return link_area, exit_rect