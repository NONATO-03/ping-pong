import pygame
import sys
import random
import time

from game.entities.bola import Bola, BolaFake
from game.entities.raquete import Raquete
from game.entities.habilidade import GerenciadorHabilidades
from game.systems.placar import Placar
from game.systems.bot import BotController
from game.systems.som import SistemaDeSom
from game.systems.eventos import FestivalDasFrutas, draw_festival_text
from visual import render_visual
from states.menu import MenuState

tempo_parado = False
tempo_parado_start = None
tempo_voltando_tocado = False
onda_azul_raquete = None
som = SistemaDeSom()
fake_balls = []
modo_escolhido = None
tempo_acabando_avisado = False
tempo_acabando_start = None
musica_tempo_acabando_tocando = False

pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Ping Pong Neon")
clock = pygame.time.Clock()

ARENA_W, ARENA_H = 700, 500
ARENA_X = (WIDTH - ARENA_W) // 2
ARENA_Y = (HEIGHT - ARENA_H) // 2
ARENA_LEFT = ARENA_X
ARENA_RIGHT = ARENA_X + ARENA_W
ARENA_TOP = ARENA_Y
ARENA_BOTTOM = ARENA_Y + ARENA_H
ARENA_CENTER_X = ARENA_X + ARENA_W // 2
ARENA_CENTER_Y = ARENA_Y + ARENA_H // 2

POWER_COLORS = {
    "uva": ((180,0,255), (180,0,255,120)),
    "melancia": ((0,255,120), (0,255,120,120)),
    "banana": ((255,255,0), (255,255,0,120)),
    "morango": ((255,0,0), (255,0,0,120)),
    "blueberry": ((80,180,255), (80,180,255,120)),
}

musica_menu_tocando = False
musica_fundo_tocando = False
festival = FestivalDasFrutas(POWER_COLORS)

game_state = "menu"
impact_left = False
impact_right = False

l_paddle = Raquete(ARENA_LEFT + 30, ARENA_CENTER_Y, is_left_paddle=True)
r_paddle = Raquete(ARENA_RIGHT - 30, ARENA_CENTER_Y, is_left_paddle=False)
ball = Bola(ARENA_CENTER_X, ARENA_CENTER_Y)
placar = Placar()
GAME_TIME_LIMIT = 5 * 60
start_time = None

selected_map_idx = 0

menu_state = MenuState(WIDTH, HEIGHT, som)
gerenciador_habilidades = GerenciadorHabilidades(POWER_COLORS, max_frutas=1, spawn_interval=20)

running = True
while running:
    tempo_str = ""

    # --- CONTROLE DE MÚSICA DO MENU ---
    if game_state in ["menu", "modo", "ajuda", "creditos", "map_select"]:
        if musica_fundo_tocando:
            som.stop_musica_fundo()
            musica_fundo_tocando = False
        # Sempre para a música antes de tocar de novo
        if not pygame.mixer.music.get_busy():
            print("Tocando música do menu")
            som.play_musica_menu(volume=0.2)
            musica_menu_tocando = True
    else:
        if musica_menu_tocando:
            som.stop_musica_menu()
            musica_menu_tocando = False

    # --- CONTROLE DE MÚSICA DA PARTIDA ---
    if game_state == "playing":
        if not musica_fundo_tocando:
            som.play_musica_fundo(volume=0.1)
            musica_fundo_tocando = True
        if musica_menu_tocando:
            som.stop_musica_menu()
            musica_menu_tocando = False
    else:
        if musica_fundo_tocando:
            som.stop_musica_fundo()
            musica_fundo_tocando = False

    # --- MENU GERENCIADO EM menu.py ---
    if game_state in ["menu", "modo", "ajuda", "creditos", "map_select"]:
        next_state, extra = menu_state.run(game_state, selected_map_idx)
        if next_state == "quit":
            running = False
            continue
        # Salva o modo escolhido quando vier do menu de modo
        if next_state == "map_select":
            # Se veio do modo, salva modo_escolhido
            if extra in ["local", "bot"]:
                modo_escolhido = extra
            # Se veio do menu de mapas, salva o índice
            elif isinstance(extra, int):
                selected_map_idx = extra
            game_state = next_state
            continue
        if next_state == "playing":
            mapa_escolhido = selected_map_idx
            game_state = "playing"
            start_time = time.time()
            placar.l_score = 0
            placar.r_score = 0
            ball.reset_position(ARENA_CENTER_X, ARENA_CENTER_Y)
            l_paddle.y = ARENA_CENTER_Y
            r_paddle.y = ARENA_CENTER_Y
            gerenciador_habilidades.reset()
            tempo_acabando_avisado = False
            tempo_acabando_start = None
            musica_tempo_acabando_tocando = False
            continue
        if next_state != game_state:
            game_state = next_state
            if game_state == "menu":
                menu_state.reset()
                tempo_acabando_avisado = False
                tempo_acabando_start = None
                musica_tempo_acabando_tocando = False
        continue

    # --- PARTIDA ---
    if game_state == "playing":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    som.play_som_menu_selecao()
                    game_state = "menu"
                    musica_menu_tocando = False
                    menu_state.reset()
                    tempo_acabando_avisado = False
                    tempo_acabando_start = None
                    musica_tempo_acabando_tocando = False

        keys = pygame.key.get_pressed()
        festival.tentar_iniciar()

        tempo_passado = 0 if start_time is None else time.time() - start_time
        tempo_restante = max(0, GAME_TIME_LIMIT - tempo_passado)
        minutos = int(tempo_restante // 60)
        segundos = int(tempo_restante % 60)
        tempo_str = f"{minutos:02d}:{segundos:02d}"

        # --- TEMPO ACABANDO ---
        if tempo_restante <= 240 and not tempo_acabando_avisado:
            tempo_acabando_avisado = True
            tempo_acabando_start = time.time()
            som.fadeout_musica(ms=1800)
            musica_tempo_acabando_tocando = False

        if tempo_acabando_avisado and not musica_tempo_acabando_tocando:
            if not pygame.mixer.music.get_busy():
                som.play_musica_tempo_acabando(volume=0.5)
                musica_tempo_acabando_tocando = True

        from game.entities.habilidade import Habilidade
        festival.atualizar(gerenciador_habilidades.frutas, Habilidade)
        gerenciador_habilidades.update()

        # Movimento das raquetes
        if modo_escolhido == "local":
            if keys[pygame.K_w]:
                l_paddle.start_move_up()
            else:
                l_paddle.stop_move_up()
            if keys[pygame.K_s]:
                l_paddle.start_move_down()
            else:
                l_paddle.stop_move_down()
            if keys[pygame.K_UP]:
                r_paddle.start_move_up()
            else:
                r_paddle.stop_move_up()
            if keys[pygame.K_DOWN]:
                r_paddle.start_move_down()
            else:
                r_paddle.stop_move_down()
        elif modo_escolhido == "bot":
            bot = BotController(r_paddle, ball, ARENA_TOP, ARENA_BOTTOM)
            bot.update()
            if keys[pygame.K_w]:
                l_paddle.start_move_up()
            else:
                l_paddle.stop_move_up()
            if keys[pygame.K_s]:
                l_paddle.start_move_down()
            else:
                l_paddle.stop_move_down()

        l_paddle.move(ARENA_TOP, ARENA_BOTTOM)
        r_paddle.move(ARENA_TOP, ARENA_BOTTOM)

        import visual
        visual.fan_angle += 0.04
        fan_angle_atual = visual.fan_angle

        impact_left, impact_right = ball.update(
            l_paddle,
            r_paddle,
            placar,
            som,
            fake_balls,
            impact_left,
            impact_right,
            ARENA_LEFT,
            ARENA_RIGHT,
            ARENA_TOP,
            ARENA_BOTTOM,
            ARENA_CENTER_X,
            ARENA_CENTER_Y,
            tempo_passado,
            fan_angle=visual.fan_angle,
            mapa_escolhido=mapa_escolhido
        )

        l_paddle.update_power()
        r_paddle.update_power()

        for h in gerenciador_habilidades.frutas[:]:
            if (abs(l_paddle.x - h.x) < l_paddle.width//2 + h.radius and
                abs(l_paddle.y - h.y) < l_paddle.height//2 + h.radius):
                l_paddle.activate_power_up(h.tipo_habilidade)
                l_paddle.update_power()
                gerenciador_habilidades.remover_fruta(h)
                som.play_som_coletar_fruta()
                continue
            if (abs(r_paddle.x - h.x) < r_paddle.width//2 + h.radius and
                abs(r_paddle.y - h.y) < r_paddle.height//2 + h.radius):
                r_paddle.activate_power_up(h.tipo_habilidade)
                r_paddle.update_power()
                gerenciador_habilidades.remover_fruta(h)
                som.play_som_coletar_fruta()
                continue

        winner = placar.check_winner()
        if winner or tempo_restante <= 0:
            game_state = "gameover"

        pygame.festival_ativo = festival.ativo

        render_visual(
            l_paddle.x, l_paddle.y, l_paddle.get_power(), l_paddle.get_power_time_left(),
            r_paddle.x, r_paddle.y, r_paddle.get_power(), r_paddle.get_power_time_left(),
            ball.x, ball.y, list(ball.rastro),
            [{"x": h.x, "y": h.y, "tipo": h.tipo_habilidade} for h in gerenciador_habilidades.frutas],
            placar.l_score, placar.r_score,
            tempo_str,
            ball_color=ball.color,
            impact_left=impact_left, impact_right=impact_right,
            fake_balls=fake_balls,
            festival=festival,
            mapa_escolhido=mapa_escolhido,
            ball=ball,
            tempo_acabando=(tempo_acabando_avisado and tempo_restante <= 240),
            tempo_acabando_start=tempo_acabando_start
        )

        pygame.display.flip()
        clock.tick(60)
        continue

    # --- GAME OVER ---
    if game_state == "gameover":
        winner = "ESQUERDA" if placar.l_score > placar.r_score else "DIREITA"
        import visual
        visual.draw_gameover(winner)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    som.play_som_menu_selecao()
                    game_state = "menu"
                    musica_menu_tocando = False
                    menu_state.reset()
                    tempo_acabando_avisado = False
                    tempo_acabando_start = None
                    musica_tempo_acabando_tocando = False
        pygame.display.flip()
        clock.tick(60)
        continue

pygame.quit()