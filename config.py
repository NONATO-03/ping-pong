import pygame
import os

#ARMAZENA ALGUMAS VARIAVEIS QUE SÃO UTILIZADAS NO CÓDIGO TODO

# Inicialização do pygame 
pygame.init()
info = pygame.display.Info()
WIDTH = info.current_w
HEIGHT = info.current_h

# Arena
ARENA_W = 700
ARENA_H = 500
ARENA_X = (WIDTH - ARENA_W) // 2
ARENA_Y = (HEIGHT - ARENA_H) // 2
ARENA_LEFT = ARENA_X
ARENA_RIGHT = ARENA_X + ARENA_W
ARENA_TOP = ARENA_Y
ARENA_BOTTOM = ARENA_Y + ARENA_H
ARENA_CENTER_X = ARENA_X + ARENA_W // 2
ARENA_CENTER_Y = ARENA_Y + ARENA_H // 2

# Fonte padrão
FONT_PATH = "assets/fonts/PressStart2P-Regular.ttf"

# Poderes/frutas
POWER_TOTAL_TIMER = {
    "morango": 20,
    "banana": 20,
    "melancia": 20,
    "uva": 20,
    "blueberry": 20
}

POWER_COLORS = {
    "uva": ((180,0,255), (180,0,255,120)),
    "melancia": ((0,255,120), (0,255,120,120)),
    "banana": ((255,255,0), (255,255,0,120)),
    "morango": ((255,0,0), (255,0,0,120)),
    "blueberry": ((80,180,255), (80,180,255,120)),
}

POWER_TEXTS = {
    "morango": "3X PONTOS",
    "banana": "SUPER RAQUETE",
    "melancia": "RAQUETE DUPLA",
    "uva": "RAQUETE MAIOR",
    "blueberry": "BOLAS FALSAS",
    "determinacao": "DETERMINAÇÃO"
}

# Imagens das frutas 
def carregar_fruta_images():
    import pygame
    import os
    imagens = {}
    for tipo in POWER_TOTAL_TIMER.keys():
        path = os.path.join("assets", "images", f"{tipo}.png")
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            imagens[tipo] = pygame.transform.smoothscale(img, (32, 32))
        else:
            imagens[tipo] = None
    return imagens

WIDTH, HEIGHT = info.current_w, info.current_h

def carregar_map_images():
    nomes = ["alpha", "beta", "gamma", "delta", "epsilon", "alpha"]
    imagens = []
    for nome in nomes:
        path = os.path.join("assets", "images", "arenas", f"{nome}.png")
        if os.path.exists(path):
            img = pygame.image.load(path)  
            imagens.append(img)
        else:
            imagens.append(None)
    return imagens

MAP_IMAGES = carregar_map_images()