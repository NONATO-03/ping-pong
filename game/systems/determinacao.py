import time
import pygame
import os

# TUDO RELACIONADO AO EFETIO "DETERMINAÇÃO

DETERMINACAO_DURACAO = 90  # 1min30s
DETERMINACAO_IMG_PATH = os.path.join("assets", "determinacao", "determinacao.png")
DETERMINACAO_MUSIC_PATH = os.path.join("assets", "determinacao", "determinacao.wav")

# Cores do arco-íris para a raquete
ARCOIRIS_CORES = [
    (255, 0, 0),      # vermelho
    (255, 255, 0),    # amarelo
    (0, 255, 0),      # verde
    (0, 0, 255),      # azul
    (148, 0, 211),    # roxo
]

def arcoiris_color(t, fator_velocidade=10.0):
    # Aumentar o denominador para desacelerar a transição
    t_ajustado = t / fator_velocidade
    n = len(ARCOIRIS_CORES)
    idx = int(t_ajustado) % n
    next_idx = (idx + 1) % n
    frac = t_ajustado - int(t_ajustado)
    c1 = ARCOIRIS_CORES[idx]
    c2 = ARCOIRIS_CORES[next_idx]
    return tuple(int(c1[i] * (1 - frac) + c2[i] * frac) for i in range(3))

class DeterminacaoManager:
    def __init__(self, l_paddle, r_paddle, placar, som):
        self.l_paddle = l_paddle
        self.r_paddle = r_paddle
        self.placar = placar
        self.som = som
        self.ativo = False
        self.start_time = None
        self.paddle_side = None  # "left" ou "right"
        self.l_seq = 0
        self.r_seq = 0
        self.last_l_score = placar.l_score
        self.last_r_score = placar.r_score
        self.music_playing = False

    def update(self):
    # sequência de pontos
        if not self.ativo:
            if self.placar.l_score != self.last_l_score:
                if self.placar.l_score > self.last_l_score:
                    self.l_seq += 1
                    self.r_seq = 0
                else:
                    self.l_seq = 0
                self.last_l_score = self.placar.l_score
            if self.placar.r_score != self.last_r_score:
                if self.placar.r_score > self.last_r_score:
                    self.r_seq += 1
                    self.l_seq = 0
                else:
                    self.r_seq = 0
                self.last_r_score = self.placar.r_score
        else:
            # Atualiza cor arco-íris e mantém efeito
            t = (time.time() - self.start_time) * 1.5
            cor = arcoiris_color(t)
            if self.paddle_side == "left":
                self.l_paddle.color = cor
                self.l_paddle.height = 190
                self.l_paddle.power_ups = {k: False for k in self.l_paddle.power_ups}
            elif self.paddle_side == "right":
                self.r_paddle.color = cor
                self.r_paddle.height = 190
                self.r_paddle.power_ups = {k: False for k in self.r_paddle.power_ups}

        # Desativa
        if self.start_time is not None and time.time() - self.start_time > DETERMINACAO_DURACAO:
            self.desativar()

    def desativar(self):
        self.ativo = False
        self.start_time = None
        self.paddle_side = None
        self.l_paddle.height = self.l_paddle.base_height
        self.r_paddle.height = self.r_paddle.base_height
        self.l_paddle.color = (255,255,255)
        self.r_paddle.color = (255,255,255)
        self.stop_music()

    def play_music(self):
        
        if not self.music_playing:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(DETERMINACAO_MUSIC_PATH)
            pygame.mixer.music.set_volume(0.1)
            pygame.mixer.music.play(-1)
            self.music_playing = True

    def stop_music(self):
        
        if self.music_playing:
            pygame.mixer.music.stop()
            self.music_playing = False

    def is_active(self):
        return self.ativo

    def get_side(self):
        return self.paddle_side

    def get_time_left(self):
        if not self.ativo or not self.start_time:
            return 0
        return max(0, DETERMINACAO_DURACAO - (time.time() - self.start_time))
    
    def ativar(self, side):
        self.ativo = True
        self.start_time = time.time()
        self.paddle_side = side
        if side == "left":
            self.l_paddle.height = 190
            self.l_paddle.color = arcoiris_color(0)
            self.l_paddle.power_ups = {k: False for k in self.l_paddle.power_ups}
        elif side == "right":
            self.r_paddle.height = 190
            self.r_paddle.color = arcoiris_color(0)
            self.r_paddle.power_ups = {k: False for k in self.r_paddle.power_ups}

def aplicar_determinacao_na_bola(bola, l_paddle, r_paddle, determinacao_manager):
    if determinacao_manager is None:
        return
    if determinacao_manager.is_active():
        side = determinacao_manager.get_side()
        if side == "left":
            if bola.last_hit_by == "left":
                bola.x_move *= 2
                bola.y_move *= 2
        elif side == "right":
            if bola.last_hit_by == "right":
                bola.x_move *= 2
                bola.y_move *= 2

def pode_coletar_fruta(paddle, determinacao_manager):
    # Se está sob efeito de determinação, não pode coletar fruta
    if determinacao_manager.is_active():
        side = determinacao_manager.get_side()
        if (side == "left" and paddle.is_left_paddle) or (side == "right" and not paddle.is_left_paddle):
            return False
    return True

def draw_determinacao_frame(screen, font_path, x, y, tempo_left, tempo_total):
    # Desenha o frame de habilidade "determinação"
    img = pygame.image.load(DETERMINACAO_IMG_PATH).convert_alpha()
    img = pygame.transform.smoothscale(img, (28, 28))
    texto = "Determinação"
    font = pygame.font.Font(font_path, 18)
    txt_surf = font.render(texto, True, (255,255,255))
    frame_w = img.get_width() + 8 + txt_surf.get_width() + 16
    frame_h = max(img.get_height(), txt_surf.get_height()) + 16
    frame_rect = pygame.Rect(x, y, frame_w, frame_h)
    frame_surf = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
    pygame.draw.rect(frame_surf, (40,40,60,180), frame_surf.get_rect(), border_radius=12)
    barra_w = frame_w - 16
    barra_h = 8
    barra_x = 8
    barra_y = frame_h - barra_h - 6
    pygame.draw.rect(frame_surf, (80,80,120,90), (barra_x, barra_y, barra_w, barra_h), border_radius=4)
    pct = max(0.0, min(1.0, tempo_left / tempo_total))
    minhoca_w = int(barra_w * pct)
    minhoca_color = (255, 80, 180)
    pygame.draw.rect(frame_surf, minhoca_color, (barra_x, barra_y, minhoca_w, barra_h), border_radius=4)
    frame_surf.blit(img, (8, (frame_h - img.get_height()) // 2))
    frame_surf.blit(txt_surf, (img.get_width() + 16, (frame_h - txt_surf.get_height()) // 2))
    screen.blit(frame_surf, (frame_rect.x, frame_rect.y))

class DeterminacaoCutscene:
    def __init__(self, screen, side, nome_lado, callback_ativar):
        self.screen = screen
        self.side = side  # "left" ou "right"
        self.nome_lado = nome_lado  # "ESQUERDA" ou "DIREITA"
        self.callback_ativar = callback_ativar
        self.start_time = time.time()
        self.fase = 0  # 0: msg1, 1: msg2, 2: onda azul, 3: fim
        self.ativo = True

    def update(self):
        agora = time.time()
        elapsed = agora - self.start_time

        # Fase 0: Mensagem de diferença absurda (6s)
        if self.fase == 0:
            if elapsed > 6:
                self.fase = 1
                self.start_time = agora
        # Fase 1: Mensagem "Não desista." (5s)
        elif self.fase == 1:
            if elapsed > 5:
                self.fase = 2
                self.start_time = agora
        # Fase 2: só ativa o efeito 
        elif self.fase == 2:
            if elapsed > 1:
                self.fase = 3
                self.ativo = False
                self.callback_ativar(self.side)
        # Fase 3: Fim da cutscene

    def draw(self):
        # Fade-in da tela escurecendo 
        tempo_fade = min(1.5, time.time() - self.start_time)
        alpha = int(200 * (tempo_fade / 1.5))
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0,0,0,alpha))
        self.screen.blit(overlay, (0,0))

        font = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 24)
        if self.fase == 0:
            # Espera um pouco após fade-in antes de começar a digitar
            tempo = time.time() - self.start_time
            delay_texto = 0.7
            msg_linhas = [
                '"A força não provém da capacidade física.',
                'Provém de uma vontade indomável."'
            ]
            msg_total = "\n".join(msg_linhas)
            if tempo < delay_texto:
                texto_mostrado = ""
                letras = 0
            else:
                tempo_texto = tempo - delay_texto
                letras = int(tempo_texto * 32)
                texto_mostrado = ""
                count = 0
                for linha in msg_linhas:
                    if letras > count:
                        texto_mostrado += linha[:max(0, letras - count)] + "\n"
                    count += len(linha)
            # Renderiza cada linha centralizada
            linhas = texto_mostrado.strip().split("\n")
            for i, linha in enumerate(linhas):
                text = font.render(linha, True, (255,255,255))
                rect = text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2 - 20 + i*32))
                self.screen.blit(text, rect)

            # Autor com fade-in no canto inferior direito
            autor = "Mahatma Gandhi"
            tempo_autor = max(0, tempo - delay_texto - (sum(len(l) for l in msg_linhas)/32) + 0.5)
            alpha_autor = int(255 * min(1, tempo_autor / 1.5))
            if alpha_autor > 0:
                font_autor = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 20)
                autor_surf = font_autor.render(autor, True, (200,200,200))
                autor_surf.set_alpha(alpha_autor)
                autor_rect = autor_surf.get_rect(bottomright=(self.screen.get_width()-32, self.screen.get_height()-32))
                self.screen.blit(autor_surf, autor_rect)

        elif self.fase == 1:
            font2 = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 38)
            msg = "[EFEITO DETERMINAÇÃO]"
            text = font2.render(msg, True, (80,180,255))
            rect = text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2))
            self.screen.blit(text, rect)

    def ativar(self, side):
        self.ativo = True
        self.start_time = time.time()
        self.paddle_side = side
        self.onda_start_time = time.time()  
        if side == "left":
            self.l_paddle.height = 190
            self.l_paddle.color = arcoiris_color(0)
            self.l_paddle.power_ups = {k: False for k in self.l_paddle.power_ups}
        elif side == "right":
            self.r_paddle.height = 190
            self.r_paddle.color = arcoiris_color(0)
            self.r_paddle.power_ups = {k: False for k in self.r_paddle.power_ups}
        self.play_music()

    def is_active(self):
        return self.ativo
