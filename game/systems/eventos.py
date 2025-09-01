import random
import time
import pygame

class FestivalDasFrutas:
    def __init__(self, power_colors):
        self.ativo = False
        self.inicio = 0
        self.duracao = 20  # segundos
        self.ultimo_spawn = 0
        self.ultimo_check = time.time()
        self.power_colors = power_colors
        self.colunas_entrada = False
        self.colunas_y = -9999  # posição Y inicial das colunas (fora da tela)
        self.colunas_entrada_inicio = 0

    def tentar_iniciar(self):
        agora = time.time()
        if not self.ativo and (agora - self.ultimo_check > 20):
            self.ultimo_check = agora
            if random.random() < 0.02:  # 2% de chance
                self.ativo = True
                self.inicio = agora
                self.ultimo_spawn = agora
                self.colunas_entrada = True
                self.colunas_y = -200  # começa bem acima da tela
                self.colunas_entrada_inicio = agora

    def atualizar(self, habilidades, Habilidade):
        agora = time.time()
        if self.ativo:
            # Spawna fruta a cada 1s
            if agora - self.ultimo_spawn > 1:
                tipo = random.choice(list(self.power_colors.keys()))
                cor = self.power_colors[tipo][0]
                habilidades.append(Habilidade(cor, tipo))
                self.ultimo_spawn = agora
            # Termina o festival após a duração
            if agora - self.inicio > self.duracao:
                self.ativo = False
                self.colunas_entrada = False

def draw_festival_text(screen, WIDTH, ARENA_TOP, FONT_PATH):
        font = pygame.font.Font(FONT_PATH, 25)  # <-- tamanho menor
        text = "Festival das Frutas"
        colors = [
            (255,0,0), (255,127,0), (255,255,0), (0,255,0),
            (0,0,255), (75,0,130), (148,0,211)
        ]
        letras_surfs = []
        total_width = 0
        arcoiris_offset = int(time.time()*2)
        for i, letra in enumerate(text):
            cor = colors[(i + arcoiris_offset) % len(colors)]
            letra_surf = font.render(letra, True, cor)
            letras_surfs.append(letra_surf)
            total_width += letra_surf.get_width()
        x = WIDTH // 2 - total_width // 2
        y = ARENA_TOP - 40  # ajuste para subir/descer o texto
        for letra_surf in letras_surfs:
            screen.blit(letra_surf, (x, y))
            x += letra_surf.get_width()            

# --- FUNÇÃO FORA DA CLASSE ---
def draw_festival_columns(screen, WIDTH, HEIGHT, ARENA_LEFT, ARENA_RIGHT, festival):
    col_width = 32  # largura da coluna
    afastamento = 64  # distância extra da arena
    speed = 120  # pixels por segundo para animação arco-íris
    entrada_speed = 600  # velocidade de entrada (pixels/segundo)
    t = time.time()
    colors = [
        (255,0,0), (255,127,0), (255,255,0), (0,255,0),
        (0,0,255), (75,0,130), (148,0,211)
    ]
    stripe_height = 40
    n_stripes = HEIGHT // stripe_height + 2

    # ANIMAÇÃO DE ENTRADA
    if getattr(festival, "colunas_entrada", False):
        # Move as colunas para baixo até y=0
        delta = t - festival.colunas_entrada_inicio
        y_offset = min(int(delta * entrada_speed), 0)
        festival.colunas_y = y_offset
        if y_offset >= 0:
            festival.colunas_entrada = False
            festival.colunas_y = 0
    else:
        festival.colunas_y = 0

    # Esquerda (fora da arena)
    x_left = ARENA_LEFT - col_width - afastamento
    for i in range(n_stripes):
        color = colors[(i + int(t*2)) % len(colors)]
        y = (i * stripe_height + int((t * speed) % HEIGHT) + festival.colunas_y) % HEIGHT
        rect = pygame.Rect(x_left, y, col_width, stripe_height)
        pygame.draw.rect(screen, color, rect, border_radius=8)

    # Direita (fora da arena)
    x_right = ARENA_RIGHT + afastamento
    for i in range(n_stripes):
        color = colors[(i + int(t*2)) % len(colors)]
        y = (i * stripe_height + int((t * speed) % HEIGHT) + festival.colunas_y) % HEIGHT
        rect = pygame.Rect(x_right, y, col_width, stripe_height)
        pygame.draw.rect(screen, color, rect, border_radius=8)