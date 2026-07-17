import pygame
from config import POWER_TEXTS, POWER_COLORS
from game.ui.neon import lighten, get_font, NEON_PINK

# LOGICA DO FRAME QUE MOSTRA QUAL PODER ESTA SENDO UTILIZADO NO MOMENTO


DETERMINACAO_IMG_CACHE = None


def draw_power_frame(screen, font_path, x, y, tipo, tempo_left, tempo_total, get_fruit_image):
    """
    Desenha um cartão neon mostrando a fruta equipada, seu efeito e uma
    barra de tempo com a cor do poder.
    """
    global DETERMINACAO_IMG_CACHE
    # Imagem da fruta ou determinação
    if tipo == "determinacao":
        if DETERMINACAO_IMG_CACHE is None:
            DETERMINACAO_IMG_CACHE = pygame.image.load("assets/determinacao/determinacao.png").convert_alpha()
            DETERMINACAO_IMG_CACHE = pygame.transform.smoothscale(DETERMINACAO_IMG_CACHE, (28, 28))
        img = DETERMINACAO_IMG_CACHE
        texto = "Determinação"
        accent = (255, 80, 180)
    else:
        img = get_fruit_image(tipo)
        if img is None:
            img = pygame.Surface((28, 28), pygame.SRCALPHA)
            pygame.draw.circle(img, (120, 120, 120), (14, 14), 14)
        else:
            img = pygame.transform.smoothscale(img, (28, 28))
        texto = POWER_TEXTS.get(tipo, "")
        accent = POWER_COLORS.get(tipo, (NEON_PINK, None))[0]

    font = get_font(18)
    txt_surf = font.render(texto, True, lighten(accent, 0.6))
    # Frame base (imagem + espaço + texto)
    frame_w = img.get_width() + 8 + txt_surf.get_width() + 16
    frame_h = max(img.get_height(), txt_surf.get_height()) + 22
    frame_rect = pygame.Rect(x, y, frame_w, frame_h)
    # Fundo do frame (cartão escuro com halo da cor do poder)
    pad = 12
    frame_surf = pygame.Surface((frame_w + pad * 2, frame_h + pad * 2), pygame.SRCALPHA)
    inner = pygame.Rect(pad, pad, frame_w, frame_h)
    pygame.draw.rect(frame_surf, accent[:3] + (30,), inner.inflate(10, 10), border_radius=16)
    pygame.draw.rect(frame_surf, (16, 12, 38, 225), inner, border_radius=12)
    pygame.draw.rect(frame_surf, lighten(accent, 0.25) + (220,), inner, width=2, border_radius=12)
    # Barra de tempo (trilho)
    barra_w = frame_w - 16
    barra_h = 7
    barra_x = pad + 8
    barra_y = pad + frame_h - barra_h - 6
    pygame.draw.rect(frame_surf, (60, 50, 100, 140), (barra_x, barra_y, barra_w, barra_h), border_radius=4)
    # Barra de tempo (preenchimento na cor do poder)
    if tempo_left is None:
        tempo_left = 0
    if tempo_total is None or tempo_total == 0:
        tempo_total = 1
    pct = max(0.0, min(1.0, tempo_left / tempo_total))
    minhoca_w = int(barra_w * pct)
    if minhoca_w > 0:
        pygame.draw.rect(frame_surf, lighten(accent, 0.2),
                         (barra_x, barra_y, minhoca_w, barra_h), border_radius=4)
    # Fruta e texto lado a lado
    frame_surf.blit(img, (pad + 8, pad + (frame_h - barra_h - 8 - img.get_height()) // 2 + 2))
    frame_surf.blit(txt_surf, (pad + img.get_width() + 16,
                               pad + (frame_h - barra_h - 8 - txt_surf.get_height()) // 2 + 2))
    # Desenha na tela
    screen.blit(frame_surf, (frame_rect.x - pad, frame_rect.y - pad))
