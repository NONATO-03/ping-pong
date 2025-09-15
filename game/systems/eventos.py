import random
import time
import pygame

#EVENTOS

EVENTO_NOMES = ["Festival das Frutas", "gato???", "Bola extra"]

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

class FestivalDasFrutas:
    def __init__(self, power_colors):
        self.ativo = False
        self.inicio = 0
        self.duracao = 20  # segundos
        self.ultimo_spawn = 0
        self.ultimo_check = time.time()
        self.power_colors = power_colors

    def tentar_iniciar(self):
        agora = time.time()
        if not self.ativo and (agora - self.ultimo_check > 20):
            self.ultimo_check = agora
            if random.random() < 1:
                self.ativo = True
                self.inicio = agora
                self.ultimo_spawn = agora

    def atualizar(self, habilidades, Habilidade):
        agora = time.time()
        if self.ativo:
            if agora - self.ultimo_spawn > 1:
                tipo = random.choice(list(self.power_colors.keys()))
                cor = self.power_colors[tipo][0]
                habilidades.append(Habilidade(cor, tipo))
                self.ultimo_spawn = agora
            if agora - self.inicio > self.duracao:
                self.ativo = False

def draw_festival_text(screen, WIDTH, ARENA_TOP, FONT_PATH):
    font = pygame.font.Font(FONT_PATH, 16)
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
    y = ARENA_TOP - 28
    for letra_surf in letras_surfs:
        screen.blit(letra_surf, (x, y))
        x += letra_surf.get_width()

class EventoIntroAnim:
    def __init__(self, WIDTH, ARENA_TOP, FONT_PATH, evento_final, sistema_som=None):
        self.WIDTH = WIDTH
        self.ARENA_TOP = ARENA_TOP
        self.FONT_PATH = FONT_PATH
        self.evento_final = evento_final
        self.start_time = time.time()
        self.state = "descendo"
        self.y_offset = -60  # começa fora da tela
        self.frame1_h = 18
        self.frame2_h = 32
        self.frame1_w = 110
        self.frame2_w = 370
        self.frame1_target_y = ARENA_TOP - 110
        self.frame2_target_y = ARENA_TOP - 110 + self.frame1_h + 4
        self.evento_nome_atual = random.choice(EVENTO_NOMES)
        self.sorteando = True
        self.sorteio_time = self.start_time
        self.sorteio_dur = 6.2
        self.stay_time = 8.0
        self.state_time = 0
        self.sistema_som = sistema_som

    def update(self):
        now = time.time()
        if self.state == "descendo":
            speed = 1
            self.y_offset += speed
            if self.y_offset >= 0:
                self.y_offset = 0
                self.state = "sorteando"
                self.sorteio_time = now
        elif self.state == "sorteando":
            if now - self.sorteio_time < self.sorteio_dur:
                idx = int((now - self.sorteio_time)*12)
                novo_nome = EVENTO_NOMES[idx % 2]
                if novo_nome != self.evento_nome_atual:
                    self.evento_nome_atual = novo_nome
                    if self.sistema_som:
                        self.sistema_som.play_som_click() 
            else:
                self.evento_nome_atual = self.evento_final
                self.state = "parado"
                self.state_time = now
        elif self.state == "parado":
            if now - self.state_time > self.stay_time:
                self.state = "subindo"
        elif self.state == "subindo":
            speed = 1
            self.y_offset -= speed
            if self.y_offset <= -60:
                self.y_offset = -60
                self.state = "fim"

    def draw(self, screen):
        t = time.time()
        # Frame 1: EVENTO
        font1 = pygame.font.Font(self.FONT_PATH, 14)
        frame1_rect = pygame.Rect(
            self.WIDTH//2 - self.frame1_w//2,
            self.frame1_target_y + self.y_offset,
            self.frame1_w, self.frame1_h
        )
        pygame.draw.rect(screen, (40,40,60,220), frame1_rect, border_radius=8)
        evento_text = font1.render("EVENTO", True, (255,255,255))
        evento_rect = evento_text.get_rect(center=frame1_rect.center)
        screen.blit(evento_text, evento_rect)

        # Frame 2: nome do evento colorido 
        font2 = pygame.font.Font(self.FONT_PATH, 18)
        frame2_rect = pygame.Rect(
            self.WIDTH//2 - self.frame2_w//2,
            self.frame2_target_y + self.y_offset,
            self.frame2_w, self.frame2_h
        )
        pygame.draw.rect(screen, (40,40,60,220), frame2_rect, border_radius=10)
        nome = self.evento_nome_atual

        letras = arcoiris_text(nome, font2, t, 0, 0)
        total_w = sum([surf.get_width() for surf, _ in letras])
        base_x = frame2_rect.x + (self.frame2_w - total_w)//2
        base_y = frame2_rect.y + (self.frame2_h - font2.get_height())//2
        for surf, _ in letras:
            screen.blit(surf, (base_x, base_y))
            base_x += surf.get_width()

    def acabou(self):
        return self.state == "fim"

class EventoGatoSimples:
    def __init__(self, arena_top, arena_bottom, arena_left, arena_right, get_ball):
        self.arena_top = arena_top
        self.arena_bottom = arena_bottom
        self.arena_left = arena_left
        self.arena_right = arena_right
        self.get_ball = get_ball

        self.miaus = [
            pygame.mixer.Sound("assets/cat/gato_miau_1.wav"),
            pygame.mixer.Sound("assets/cat/gato_miau_2.wav"),
            pygame.mixer.Sound("assets/cat/gato_miau_3.wav"),
            pygame.mixer.Sound("assets/cat/gato_miau_4.wav"),
        ]
        for miau in self.miaus:
            miau.set_volume(0.1)
        self.ultimo_miau = time.time()
        gato_size = (64, 64)
        self.img_parado = [
            pygame.transform.smoothscale(
                pygame.image.load("assets/cat/gato_1.png").convert_alpha(), gato_size
            ),
            pygame.transform.smoothscale(
                pygame.image.load("assets/cat/gato_2.png").convert_alpha(), gato_size
            )
        ]
        self.img_correndo = [
            pygame.transform.smoothscale(
                pygame.image.load(f"assets/cat/gato_correndo_{i}.png").convert_alpha(), gato_size
            ) for i in range(1, 7)
        ]
        self.estado = "parado"
        self.frame = 0
        self.frame_timer = 0
        self.x = (arena_left + arena_right) // 2
        self.y = arena_bottom - 32
        self.vx = 0
        self.vy = 0
        self.tempo_total = 0
        self.tempo_correndo = 0

    def update(self):
        self.tempo_total += 1/60
        agora = time.time()
        if agora - self.ultimo_miau > 5:
            random.choice(self.miaus).play()
            self.ultimo_miau = agora
        if self.estado == "parado":
            self.frame_timer += 1
            if self.frame_timer >= 20:
                self.frame = 1 - self.frame
                self.frame_timer = 0
            if self.tempo_total > 2.5:
                self.estado = "correndo"
                self.tempo_correndo = 0
        elif self.estado == "correndo":
            self.tempo_correndo += 1/60
            self.frame_timer += 1
            if self.frame_timer >= 8:
                self.frame = (self.frame + 1) % len(self.img_correndo)
                self.frame_timer = 0
            ball = self.get_ball()
            dx = ball.x - self.x
            dy = ball.y - self.y
            dist = max(1, (dx**2 + dy**2)**0.5)
            acel = 0.9
            max_vel = 11
            self.vx += acel * dx/dist
            self.vy += acel * dy/dist
            self.vx *= 0.93
            self.vy *= 0.93
            speed = (self.vx**2 + self.vy**2)**0.5
            if speed > max_vel:
                self.vx *= max_vel/speed
                self.vy *= max_vel/speed
            self.x += self.vx
            self.y += self.vy
            if abs(self.x - ball.x) < 48 and abs(self.y - ball.y) < 48:
                ball.x_move += self.vx * 0.25
                ball.y_move += self.vy * 0.25
            self.x = min(max(self.x, self.arena_left+24), self.arena_right-24)
            self.y = min(max(self.y, self.arena_top+24), self.arena_bottom-24)
            if self.tempo_correndo > 20:
                self.estado = "parado_final"
                self.frame = 0
                self.frame_timer = 0
        elif self.estado == "parado_final":
            self.frame_timer += 1
            if self.frame_timer >= 20:
                self.frame = 1 - self.frame
                self.frame_timer = 0
            if self.tempo_total > 40:
                self.estado = "fim"

    def draw(self, screen):
        ball = self.get_ball()
        flip = False
        if hasattr(ball, "x_move"):
            flip = ball.x_move > 0
        if self.estado in ["parado", "parado_final"]:
            img = self.img_parado[self.frame]
        elif self.estado == "correndo":
            img = self.img_correndo[self.frame]
        else:
            return
        if flip:
            img = pygame.transform.flip(img, True, False)
        rect = img.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(img, rect)

class GerenciadorEventos:
    def __init__(self, power_colors, arena_top, arena_bottom, arena_left, arena_right, get_ball):
        self.festival = FestivalDasFrutas(power_colors)
        self.gato_evento = None
        self.ultimo_check = time.time()
        self.ativo = False
        self.evento_atual = None
        self.arena_top = arena_top
        self.arena_bottom = arena_bottom
        self.arena_left = arena_left
        self.arena_right = arena_right
        self.get_ball = get_ball
        self.intro_anim = None
        self.bola_extra_evento = None

    def tentar_iniciar(self, WIDTH, FONT_PATH, sistema_som=None):
        agora = time.time()
        if not self.ativo and (agora - self.ultimo_check > 90):
            self.ultimo_check = agora
            print("Tentando sortear evento!")
            if random.random() < 0.90: #90% de chance
                evento_final = random.choice(EVENTO_NOMES)
                print(f"Evento sorteado: {evento_final}")
                self.intro_anim = EventoIntroAnim(WIDTH, self.arena_top, FONT_PATH, evento_final, sistema_som=sistema_som)
                self.evento_atual = None
                self.ativo = True

    def atualizar(self, habilidades, Habilidade, l_paddle=None, r_paddle=None, placar=None, som=None, fake_balls=None,
              impact_left=None, impact_right=None, ARENA_LEFT=None, ARENA_RIGHT=None, ARENA_TOP=None, ARENA_BOTTOM=None,
              ARENA_CENTER_X=None, ARENA_CENTER_Y=None, tempo_passado=None):
        if self.intro_anim and not self.intro_anim.acabou():
            self.intro_anim.update()
            return
        elif self.intro_anim and self.intro_anim.acabou():
            evento_final = self.intro_anim.evento_final
            self.intro_anim = None
            if evento_final == "Festival das Frutas":
                self.festival.ativo = True
                self.festival.inicio = time.time()
                self.festival.ultimo_spawn = time.time()
                self.evento_atual = "festival"
            elif evento_final == "gato???":
                self.gato_evento = EventoGatoSimples(
                    self.arena_top, self.arena_bottom, self.arena_left, self.arena_right, self.get_ball
                )
                self.evento_atual = "gato"
            elif evento_final == "Bola extra":
                self.bola_extra_evento = EventoBolaExtra(ARENA_CENTER_X, ARENA_CENTER_Y)
                self.evento_atual = "bola_extra"
            return

        if self.evento_atual == "festival":
            self.festival.atualizar(habilidades, Habilidade)
            if not self.festival.ativo:
                self.ativo = False
                self.evento_atual = None
        elif self.evento_atual == "gato":
            if self.gato_evento:
                self.gato_evento.update()
                if self.gato_evento.estado == "fim":
                    self.gato_evento = None
                    self.ativo = False
                    self.evento_atual = None
        elif self.evento_atual == "bola_extra":
            if self.bola_extra_evento and self.bola_extra_evento.ativo:
                self.bola_extra_evento.atualizar(
                    l_paddle, r_paddle, placar, som, fake_balls, impact_left, impact_right,
                    ARENA_LEFT, ARENA_RIGHT, ARENA_TOP, ARENA_BOTTOM, ARENA_CENTER_X, ARENA_CENTER_Y, tempo_passado
                )
            else:
                self.bola_extra_evento = None
                self.ativo = False
                self.evento_atual = None

    def draw(self, screen, WIDTH, HEIGHT, ARENA_LEFT, ARENA_RIGHT, ARENA_TOP, FONT_PATH, ball_draw_func=None):
        if self.intro_anim and not self.intro_anim.acabou():
            self.intro_anim.draw(screen)
            return
        if self.evento_atual == "festival":
            pass
        elif self.evento_atual == "gato" and self.gato_evento:
            self.gato_evento.draw(screen)
        elif self.evento_atual == "bola_extra" and self.bola_extra_evento:
            self.bola_extra_evento.draw(screen, ball_draw_func)

class EventoBolaExtra:
    def __init__(self, ARENA_CENTER_X, ARENA_CENTER_Y):
        from game.entities.bola import Bola
        self.bola_extra = Bola(ARENA_CENTER_X, ARENA_CENTER_Y)
        self.spawn_time = time.time()
        self.ativo = True

    def atualizar(self, l_paddle, r_paddle, placar, som, fake_balls, impact_left, impact_right,
                  ARENA_LEFT, ARENA_RIGHT, ARENA_TOP, ARENA_BOTTOM, ARENA_CENTER_X, ARENA_CENTER_Y, tempo_passado):
        if not self.ativo:
            return
        # Atualiza a bola extra igual à bola principal
        self.bola_extra.update(
            l_paddle, r_paddle, placar, som, fake_balls, impact_left, impact_right,
            ARENA_LEFT, ARENA_RIGHT, ARENA_TOP, ARENA_BOTTOM, ARENA_CENTER_X, ARENA_CENTER_Y, tempo_passado
        )
        # Remove após 40 segundos
        if time.time() - self.spawn_time > 40:
            self.ativo = False

    def draw(self, screen, ball_draw_func):
        if self.ativo:
            from visual import draw_ball_trail
            draw_ball_trail(self.bola_extra.rastro)
            ball_draw_func(self.bola_extra.x, self.bola_extra.y, color=self.bola_extra.color)