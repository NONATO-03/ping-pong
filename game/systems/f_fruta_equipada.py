import pygame
from config import POWER_TEXTS

#LOGICA DO FRAME QUE MOSTRAL QUAL PODER ESTA SENDO UTILIZADO NO MOMENTO


DETERMINACAO_IMG_CACHE = None

def draw_power_frame(screen, font_path, x, y, tipo, tempo_left, tempo_total, get_fruit_image):
    """
    Desenha um frame na tela mostrando a fruta equipada, seu efeito e uma barra de tempo.
    """
    global DETERMINACAO_IMG_CACHE
    # Imagem da fruta ou determinação
    if tipo == "determinacao":
        if DETERMINACAO_IMG_CACHE is None:
            DETERMINACAO_IMG_CACHE = pygame.image.load("assets/determinacao/determinacao.png").convert_alpha()
            DETERMINACAO_IMG_CACHE = pygame.transform.smoothscale(DETERMINACAO_IMG_CACHE, (28, 28))
        img = DETERMINACAO_IMG_CACHE
        texto = "Determinação"
    else:
        img = get_fruit_image(tipo)
        if img is None:
            img = pygame.Surface((28, 28), pygame.SRCALPHA)
            pygame.draw.circle(img, (120,120,120), (14,14), 14)  
        else:
            img = pygame.transform.smoothscale(img, (28, 28))
        texto = POWER_TEXTS.get(tipo, "")
    font = pygame.font.Font(font_path, 18)
    txt_surf = font.render(texto, True, (255,255,255))
    # Frame base (imagem + espaço + texto)
    frame_w = img.get_width() + 8 + txt_surf.get_width() + 16
    frame_h = max(img.get_height(), txt_surf.get_height()) + 16
    frame_rect = pygame.Rect(x, y, frame_w, frame_h)
    # Fundo do frame
    frame_surf = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
    pygame.draw.rect(frame_surf, (40,40,60,180), frame_surf.get_rect(), border_radius=12)
    # Barra de tempo 
    barra_w = frame_w - 16
    barra_h = 8
    barra_x = 8
    barra_y = frame_h - barra_h - 6
    pygame.draw.rect(frame_surf, (80,80,120,90), (barra_x, barra_y, barra_w, barra_h), border_radius=4)
    # Barra de tempo 
    if tempo_left is None:
        tempo_left = 0
    if tempo_total is None or tempo_total == 0:
        tempo_total = 1
    pct = max(0.0, min(1.0, tempo_left / tempo_total))
    minhoca_w = int(barra_w * pct)
    if tipo == "determinacao":
        minhoca_color = (255, 80, 180)
    else:
        minhoca_color = (180,180,255) if tipo == "blueberry" else (255,120,0) if tipo in ["morango","banana","melancia"] else (180,0,255) if tipo=="uva" else (0,255,120)
    pygame.draw.rect(frame_surf, minhoca_color, (barra_x, barra_y, minhoca_w, barra_h), border_radius=4)
    # Fruta e texto lado a lado
    frame_surf.blit(img, (8, (frame_h - img.get_height()) // 2))
    frame_surf.blit(txt_surf, (img.get_width() + 16, (frame_h - txt_surf.get_height()) // 2))
    # Desenha na tela
    screen.blit(frame_surf, (frame_rect.x, frame_rect.y))