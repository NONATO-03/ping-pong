import pygame
import time
import random
import visual
from game.entities.bola import Bola
from game.entities.raquete import Raquete
from game.entities.habilidade import GerenciadorHabilidades
from game.entities.obstaculo_2 import ObstaculoCruz
from game.systems.placar import Placar
from game.systems.bot import BotController
from game.systems.som import SistemaDeSom
from game.systems.eventos import FestivalDasFrutas, GerenciadorEventos
from visual import render_visual  # Importa a função de renderização diretamente
from game.states.menu import MenuState
from game.systems.determinacao import DeterminacaoCutscene, DeterminacaoManager, pode_coletar_fruta
from config import (
    POWER_COLORS, ARENA_TOP, ARENA_BOTTOM, ARENA_LEFT, ARENA_RIGHT,
    ARENA_CENTER_X, ARENA_CENTER_Y, WIDTH, HEIGHT, FONT_PATH,
    ARENA_X, ARENA_Y, ARENA_W, ARENA_H
)

# ARQUIVO PRINCIPAL DO JOGO


# VARIÁVEIS GLOBAIS E ESTADO DO JOGO
# Essas variáveis mantêm o estado do jogo entre os loops.

def get_ball():
    """Função auxiliar para passar o objeto bola para outros módulos."""
    return ball

# Flags e Variáveis de Controle 
cutscene_determinacao = None
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
arena_aleatoria_idx = None
INDICE_DA_ARENA_ALEATORIA = 5 

# INICIALIZAÇÃO DO PYGAME

pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Ping Pong")
clock = pygame.time.Clock()

# INSTANCIAÇÃO DOS MÓDULOS DO JOGO
# Cria os objetos principais que vão gerenciar as diferentes partes do jogo.

gerenciador_eventos = GerenciadorEventos(
    POWER_COLORS, ARENA_TOP, ARENA_BOTTOM, ARENA_LEFT, ARENA_RIGHT, get_ball
)

# Flags de controle de música.
musica_menu_tocando = False
musica_fundo_tocando = False

festival = FestivalDasFrutas(POWER_COLORS)
game_state = "menu"
impact_left = False
impact_right = False

# Criação das entidades do jogo.
l_paddle = Raquete(ARENA_LEFT + 30, ARENA_CENTER_Y, is_left_paddle=True)
r_paddle = Raquete(ARENA_RIGHT - 30, ARENA_CENTER_Y, is_left_paddle=False)
ball = Bola(ARENA_CENTER_X, ARENA_CENTER_Y)
placar = Placar()
determinacao_manager = DeterminacaoManager(l_paddle, r_paddle, placar, som)
GAME_TIME_LIMIT = 5 * 60

# Criação dos obstáculos em forma de cruz 
obstacle1 = ObstaculoCruz(ARENA_X + ARENA_W * 0.25, ARENA_Y + ARENA_H * 0.25, size=80)
obstacle2 = ObstaculoCruz(ARENA_X + ARENA_W * 0.75, ARENA_Y + ARENA_H * 0.75, size=80)
obstacles = [obstacle1, obstacle2]
# Fim da criação dos obstáculos

start_time = None

selected_map_idx = 0
menu_state = MenuState(WIDTH, HEIGHT, som)
gerenciador_habilidades = GerenciadorHabilidades(POWER_COLORS, max_frutas=1, spawn_interval=20)



#               LOOP PRINCIPAL DO JOGO
running = True
while running:
    tempo_str = ""

    
    # 1. CONTROLE DE MÚSICA GLOBAL
    
    if game_state in ["menu", "modo", "ajuda", "creditos", "map_select"]:
        if not musica_menu_tocando:
            som.stop_musica_fundo()
            som.stop_musica_tempo_acabando()
            som.stop_musica_menu()
            som.play_musica_menu()
            musica_menu_tocando = True
            musica_fundo_tocando = False
            musica_tempo_acabando_tocando = False
    else:
        if musica_menu_tocando:
            som.stop_musica_menu()
            musica_menu_tocando = False

        # CONTROLE DE MÚSICA DA PARTIDA 
        if game_state == "playing":
            # Calcula o tempo restante
            tempo_passado = 0 if start_time is None else time.time() - start_time
            tempo_restante = max(0, GAME_TIME_LIMIT - tempo_passado)

            # 1. Determinação ativa (prioridade máxima)
            if determinacao_manager.is_active() or (cutscene_determinacao and cutscene_determinacao.is_active()):
                if musica_fundo_tocando:
                    som.stop_musica_fundo()
                    musica_fundo_tocando = False
                if musica_tempo_acabando_tocando:
                    som.stop_musica_tempo_acabando()
                    musica_tempo_acabando_tocando = False
                # A música de determinação é controlada pelo DeterminacaoManager

            # 2. Tempo acabando (últimos 60s)
            elif tempo_restante <= 60:
                if not musica_tempo_acabando_tocando:
                    som.stop_musica_fundo()
                    som.stop_musica_tempo_acabando()
                    som.play_musica_tempo_acabando()
                    musica_tempo_acabando_tocando = True
                    musica_fundo_tocando = False
            # 3. Música normal da partida
            else:
                if not musica_fundo_tocando:
                    som.stop_musica_fundo()
                    som.stop_musica_tempo_acabando()
                    som.play_musica_fundo()
                    musica_fundo_tocando = True
                    musica_tempo_acabando_tocando = False

    
    # 2. LÓGICA DOS MENUS
    
    if game_state in ["menu", "modo", "ajuda", "creditos", "map_select"]:
        next_state, extra = menu_state.run(game_state, selected_map_idx)
        if next_state == "quit":
            running = False
            continue
        
        if next_state == "map_select":
            if extra in ["local", "bot"]:
                modo_escolhido = extra
            elif isinstance(extra, int):
                selected_map_idx = extra
            game_state = next_state
            continue
        
        # Inicia a partida quando o estado muda para "playing"
        if next_state == "playing":
            mapa_escolhido = selected_map_idx  
            if mapa_escolhido == INDICE_DA_ARENA_ALEATORIA:  
                arena_aleatoria_idx = random.randint(0, INDICE_DA_ARENA_ALEATORIA - 1)
            else:
                arena_aleatoria_idx = None
            game_state = "playing"
            start_time = time.time()
            # Reseta o estado do jogo para uma nova partida
            placar.l_score = 0
            placar.r_score = 0
            ball.reset_position(ARENA_CENTER_X, ARENA_CENTER_Y)
            l_paddle.y = ARENA_CENTER_Y
            r_paddle.y = ARENA_CENTER_Y
            gerenciador_habilidades.reset()
            tempo_acabando_avisado = False
            tempo_acabando_start = None
            musica_tempo_acabando_tocando = False
            som.stop_musica_menu()
            musica_menu_tocando = False
            continue

        if next_state != game_state:
            game_state = next_state
            if game_state == "menu":
                menu_state.reset()
                # Garante que o estado da música de tempo acabando seja resetado
                tempo_acabando_avisado = False
                tempo_acabando_start = None
                musica_tempo_acabando_tocando = False
            continue

    
    # 3. LÓGICA DA PARTIDA
    
    if game_state == "playing":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z: # Volta para o menu
                    som.play_som_menu_selecao()
                    game_state = "menu"
                    musica_menu_tocando = False
                    menu_state.reset()
                    tempo_acabando_avisado = False
                    tempo_acabando_start = None
                    musica_tempo_acabando_tocando = False
                    determinacao_manager.desativar()

        # --- CUTSCENE DE DETERMINAÇÃO ---
        # Se a cutscene estiver ativa, ela assume o controle do loop
        if cutscene_determinacao and cutscene_determinacao.is_active():
            cutscene_determinacao.update()
            cutscene_determinacao.draw()
            pygame.display.flip()
            clock.tick(60)
            continue

        keys = pygame.key.get_pressed()
        determinacao_manager.update()

        # Verifica se as condições para ativar a cutscene foram atingidas
        if not determinacao_manager.is_active():
            if determinacao_manager.r_seq >= 15:
                som.stop_musica_fundo()
                musica_fundo_tocando = False
                determinacao_manager.play_music()
                cutscene_determinacao = DeterminacaoCutscene(
                    screen, "left", "ESQUERDA", determinacao_manager.ativar
                )
                determinacao_manager.r_seq = 0
            elif determinacao_manager.l_seq >= 15:
                som.stop_musica_fundo()
                musica_fundo_tocando = False
                determinacao_manager.play_music()
                cutscene_determinacao = DeterminacaoCutscene(
                    screen, "right", "DIREITA", determinacao_manager.ativar
                )
                determinacao_manager.l_seq = 0
        
        # LÓGICA DOS OBSTÁCULOS E ARENAS ESPECIAIS
        arena_idx = mapa_escolhido
        if mapa_escolhido == INDICE_DA_ARENA_ALEATORIA and arena_aleatoria_idx is not None:
            arena_idx = arena_aleatoria_idx

        if arena_idx == 2:  # Gamma 
            for obstacle in obstacles:
                obstacle.rotate()

        from game.entities.habilidade import Habilidade
        gerenciador_eventos.tentar_iniciar(WIDTH, FONT_PATH, sistema_som=som)
        tempo_passado = 0 if start_time is None else time.time() - start_time
        gerenciador_eventos.atualizar(
            gerenciador_habilidades.frutas, Habilidade,
            l_paddle, r_paddle, placar, som, fake_balls,
            impact_left, impact_right,
            ARENA_LEFT, ARENA_RIGHT, ARENA_TOP, ARENA_BOTTOM,
            ARENA_CENTER_X, ARENA_CENTER_Y, tempo_passado
        )

        # ATUALIZAÇÃO DAS FRUTAS
        gerenciador_habilidades.update()

        # CONTROLE DO TEMPO 
        tempo_passado = 0 if start_time is None else time.time() - start_time
        tempo_restante = max(0, GAME_TIME_LIMIT - tempo_passado)
        minutos = int(tempo_restante // 60)
        segundos = int(tempo_restante % 60)
        tempo_str = f"{minutos:02d}:{segundos:02d}"

        # AVISO DE TEMPO ACABANDO
        if tempo_restante <= 60 and not tempo_acabando_avisado:
            tempo_acabando_avisado = True
            tempo_acabando_start = time.time()
        elif tempo_restante > 60 and tempo_acabando_avisado:
            tempo_acabando_avisado = False
            tempo_acabando_start = None

        # MOVIMENTO DAS RAQUETES
        if modo_escolhido == "local":
            if keys[pygame.K_w]: l_paddle.start_move_up()
            else: l_paddle.stop_move_up()
            if keys[pygame.K_s]: l_paddle.start_move_down()
            else: l_paddle.stop_move_down()
            if keys[pygame.K_UP]: r_paddle.start_move_up()
            else: r_paddle.stop_move_up()
            if keys[pygame.K_DOWN]: r_paddle.start_move_down()
            else: r_paddle.stop_move_down()
        elif modo_escolhido == "bot":
            bot = BotController(r_paddle, ball, ARENA_TOP, ARENA_BOTTOM)
            bot.update()
            if keys[pygame.K_w]: l_paddle.start_move_up()
            else: l_paddle.stop_move_up()
            if keys[pygame.K_s]: l_paddle.start_move_down()
            else: l_paddle.stop_move_down()

        l_paddle.move(ARENA_TOP, ARENA_BOTTOM)
        r_paddle.move(ARENA_TOP, ARENA_BOTTOM)

        # LÓGICA DOS OBSTÁCULOS E ARENAS ESPECIAIS 
        arena_idx = mapa_escolhido
        if mapa_escolhido == INDICE_DA_ARENA_ALEATORIA and arena_aleatoria_idx is not None:
            arena_idx = arena_aleatoria_idx

        # Rotação da barra da Beta
        if arena_idx == 1:
            visual.fan_angle += 0.04

        # Obstáculos da Gamma
        if arena_idx == 2:
            for obstacle in obstacles:
                obstacle.rotate()

        # Atualiza a bola
        impact_left, impact_right = ball.update(
            l_paddle, r_paddle, placar, som, fake_balls,
            impact_left, impact_right,
            ARENA_LEFT, ARENA_RIGHT, ARENA_TOP, ARENA_BOTTOM,
            ARENA_CENTER_X, ARENA_CENTER_Y, tempo_passado,
            fan_angle=visual.fan_angle,
            mapa_escolhido=arena_idx, 
            determinacao_manager=determinacao_manager,
            obstacles=obstacles if arena_idx == 2 else None  
        )

        l_paddle.update_power()
        r_paddle.update_power()

        # LÓGICA DE COLETA DE FRUTAS 
        for h in gerenciador_habilidades.frutas[:]:
            if pode_coletar_fruta(l_paddle, determinacao_manager):
                if (abs(l_paddle.x - h.x) < l_paddle.width//2 + h.radius and
                    abs(l_paddle.y - h.y) < l_paddle.height//2 + h.radius):
                    l_paddle.activate_power_up(h.tipo_habilidade)
                    gerenciador_habilidades.remover_fruta(h)
                    som.play_som_coletar_fruta()
                    continue
            if pode_coletar_fruta(r_paddle, determinacao_manager):
                if (abs(r_paddle.x - h.x) < r_paddle.width//2 + h.radius and
                    abs(r_paddle.y - h.y) < r_paddle.height//2 + h.radius):
                    r_paddle.activate_power_up(h.tipo_habilidade)
                    gerenciador_habilidades.remover_fruta(h)
                    som.play_som_coletar_fruta()
                    continue

        # CONDIÇÃO DE FIM DE JOGO 
        winner = placar.check_winner()
        if winner or tempo_restante <= 0:
            game_state = "gameover"
            som.stop_musica_fundo()
            som.stop_musica_tempo_acabando()
            determinacao_manager.desativar()

        pygame.festival_ativo = festival.ativo

        # RENDERIZAÇÃO 
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
            tempo_acabando=(tempo_acabando_avisado and tempo_restante <= 60),
            tempo_acabando_start=tempo_acabando_start,
            get_fruit_image=visual.get_fruit_image,
            determinacao_manager=determinacao_manager,
            arena_aleatoria_idx=arena_aleatoria_idx,
            indice_arena_aleatoria=INDICE_DA_ARENA_ALEATORIA
        )
        
        # Desenha os novos obstáculos se o mapa 2 estiver ativo
        if arena_idx == 2:
            for obstacle in obstacles:
                obstacle.draw(screen)

        # Desenha elementos de eventos por cima do jogo
        gerenciador_eventos.draw(
            screen, WIDTH, HEIGHT, ARENA_LEFT, ARENA_RIGHT, ARENA_TOP, "assets/fonts/PressStart2P-Regular.ttf",
            ball_draw_func=visual.draw_ball
        )

        pygame.display.flip()
        clock.tick(60)
        continue

    # 4. TELA DE GAME OVER
    
    if game_state == "gameover":
        winner = "ESQUERDA" if placar.l_score > placar.r_score else "DIREITA"
        som.play_som_fim_jogo()
        visual.draw_gameover(winner)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    som.play_som_menu_selecao()
                    game_state = "menu"
                    # Reseta todo o estado do jogo para poder voltar ao menu
                    musica_menu_tocando = False
                    menu_state.reset()
                    tempo_acabando_avisado = False
                    tempo_acabando_start = None
                    musica_tempo_acabando_tocando = False
                    determinacao_manager.desativar()
                    if hasattr(festival, "reset"): festival.reset()
                    if hasattr(gerenciador_eventos, "reset"): gerenciador_eventos.reset()
                    for tipo in ["morango", "banana", "melancia", "uva", "blueberry"]:
                        l_paddle.deactivate_power_up(tipo)
                        r_paddle.deactivate_power_up(tipo)
                    gerenciador_habilidades.frutas.clear()
        pygame.display.flip()
        clock.tick(60)
        continue

pygame.quit()