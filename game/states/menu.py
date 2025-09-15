import pygame
import random
import webbrowser
import time
from visual import (
    draw_menu_principal,
    draw_ajuda,
    draw_creditos,
    draw_modo_menu,
    draw_map_select_menu
)


# CLASSE DA BOLA QUE FICA DE DECORAÇÃO NO MENU

class BolaMenu:
    """
    Representa uma bola decorativa que quica pelas bordas da tela do menu.
    
    Esta classe é puramente visual e serve para dar vida ao fundo do menu.
    """
    def __init__(self, x, y, som, radius=14, color=(255, 255, 255)):
        """
        Inicializa a bola do menu.

        Args:
            x (int): Posição X inicial.
            y (int): Posição Y inicial.
            som (SoundManager): Objeto para tocar sons de colisão.
            radius (int): Raio da bola.
            color (tuple): Cor da bola em formato (R, G, B).
        """
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        # Define uma velocidade e direção iniciais aleatórias
        self.x_move = random.choice([-1, 1]) * random.uniform(3, 5)
        self.y_move = random.choice([-1, 1]) * random.uniform(3, 5)
        self.rastro = []  
        self.som = som

    def move(self, WIDTH, HEIGHT):
        """
        Atualiza a posição da bola, gerencia seu rastro e detecta colisões com as bordas.

        Args:
            WIDTH (int): Largura da tela.
            HEIGHT (int): Altura da tela.
        """
        # Gerenciamento do Rastro 
        self.rastro.append({'x': self.x, 'y': self.y, 'radius': self.radius, 'alpha': 180, 'color': self.color})
        for r in self.rastro:
            r['radius'] *= 0.85  
            r['alpha'] -= 15  
        self.rastro = [r for r in self.rastro if r['alpha'] > 0 and r['radius'] > 1]

        # Movimento e Colisão
        self.x += self.x_move
        self.y += self.y_move
        
        bateu = False
        if self.x - self.radius < 0 or self.x + self.radius > WIDTH:
            self.x_move *= -1
            bateu = True
        if self.y - self.radius < 0 or self.y + self.radius > HEIGHT:
            self.y_move *= -1
            bateu = True
            
        if bateu:
            try:
                self.som.play_som_parede(volume=0.01)
            except TypeError:
                self.som.play_som_parede()



# FUNÇÃO DE DESENHO DA BOLA


def draw_bola_menu(screen, bola_menu):
    """
    Desenha a bola do menu e seu rastro na tela

    Args:
        screen (pygame.Surface): A superfície onde desenhar
        bola_menu (BolaMenu): O objeto da bola a ser desenhado
    """
    # Desenha cada partícula do rastro com a transparência calculada
    for r in bola_menu.rastro:
        surf = pygame.Surface((r['radius'] * 2, r['radius'] * 2), pygame.SRCALPHA)
        cor = r.get('color', (255, 255, 255))
        pygame.draw.circle(surf, cor + (int(r['alpha']),), (int(r['radius']), int(r['radius'])), int(r['radius']))
        screen.blit(surf, (r['x'] - r['radius'], r['y'] - r['radius']))
        
    # Desenha a bola principal
    pygame.draw.circle(screen, bola_menu.color, (int(bola_menu.x), int(bola_menu.y)), bola_menu.radius)



# CLASSE DE ESTADO DO MENU 


class MenuState:
    """
    Gerencia todo o fluxo de navegação e a lógica das telas de menu

    """
    def __init__(self, WIDTH, HEIGHT, som):
        """
        Inicializa o gerenciador de estado do menu

        Args:
            WIDTH (int): Largura da tela
            HEIGHT (int): Altura da tela
            som (SoundManager): Objeto para tocar sons de interface
        """
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.som = som
        
        # Estado do Menu Principal
        self.menu_selected_idx = 0  # Índice da opção de menu selecionada (0: Jogar, 1: Ajuda, etc.)
        self.menu_continuar = False  # Flag para saber se as opções do menu (Jogar, etc.) estão visíveis

        # Estado da Animação das Letras(segredo)
        self.letras_quicando = False  # Flag para indicar se a animação das letras do título está ativa
        self.letras_quicando_start = 0  # Timestamp de quando a animação começou
        self.letras_bolas = []  # Lista de dicionários, cada um representando uma letra animada
        self.letras_voltando = False  # Flag para indicar se as letras estão na fase de retorno à posição original

        # Objeto Decorativo
        self.bola_menu = BolaMenu(WIDTH // 2, HEIGHT // 2, som)

    def reset(self):
        """Reseta o estado do menu para suas configurações iniciais"""
        self.menu_selected_idx = 0
        self.menu_continuar = False
        self.letras_quicando = False
        self.letras_voltando = False
        self.letras_bolas = []
        self.letras_quicando_start = 0

    def run(self, game_state, selected_map_idx=0):
        """
        Ponto de entrada principal que direciona para a função correta
        com base no estado atual do jogo.

        Args:
            game_state: O estado atual do menu
            selected_map_idx: O índice do mapa selecionado na tela de mapas

        Returns:
            tuple: Um novo estado de jogo e o índice do mapa
        """
        if game_state == "menu":
            return self.run_principal()
        elif game_state == "ajuda":
            return self.run_ajuda()
        elif game_state == "creditos":
            return self.run_creditos()
        elif game_state == "modo":
            return self.run_modo()
        elif game_state == "map_select":
            return self.run_map_select(selected_map_idx)
        else:
            return game_state, selected_map_idx

    # Funções de Loop para Cada Tela do Menu 

    def run_principal(self):
        """Executa a lógica e o loop de eventos para a tela do menu principal"""
        screen = pygame.display.get_surface()

        # Se a animação das letras estiver ativa entra em um loop 
        if self.letras_quicando:
            draw_menu_principal(self.menu_selected_idx, mostrar_opcoes=self.menu_continuar,
                                letras_bolas=self.letras_bolas, letras_voltando=self.letras_voltando)
            # FASE 1: Letras se espalham e quicam
            if not self.letras_voltando:
                for letra in self.letras_bolas:
                    letra['x'] += letra['vx']
                    letra['y'] += letra['vy']
                    if letra['x'] < 0 or letra['x'] > self.WIDTH: letra['vx'] *= -1
                    if letra['y'] < 0 or letra['y'] > self.HEIGHT: letra['vy'] *= -1
                # Após 5 segundos, inicia a fase de retorno
                if time.time() - self.letras_quicando_start > 5:
                    self.letras_voltando = True
                    for letra in self.letras_bolas:
                        # Calcula a velocidade necessária para voltar à posição original em 30 frames
                        letra['vx'] = (letra['target_x'] - letra['x']) / 30
                        letra['vy'] = (letra['target_y'] - letra['y']) / 30
            # FASE 2: Letras retornam à posição original
            else:
                todas_no_lugar = True
                for letra in self.letras_bolas:
                    letra['x'] += letra['vx']
                    letra['y'] += letra['vy']
                    if abs(letra['x'] - letra['target_x']) > 2 or abs(letra['y'] - letra['target_y']) > 2:
                        todas_no_lugar = False
                if todas_no_lugar:
                    self.letras_quicando = False  
            
            self.bola_menu.move(self.WIDTH, self.HEIGHT)
            draw_bola_menu(screen, self.bola_menu)
            
            # Loop de eventos simplificado durante a animação
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_x):
                    return "quit", 0
            
            pygame.display.flip()
            pygame.time.Clock().tick(60)
            return "menu", 0

        # Loop principal quando a animação nao está ativada
        letras_rects, mouse_idx, exit_rect = draw_menu_principal(self.menu_selected_idx, mostrar_opcoes=self.menu_continuar)
        self.bola_menu.move(self.WIDTH, self.HEIGHT)
        draw_bola_menu(screen, self.bola_menu)

        # Ativa o menu de opções se o mouse passar sobre Pressione Espaço
        if not self.menu_continuar and mouse_idx is not None:
            self.menu_continuar = True
            self.menu_selected_idx = mouse_idx

        # Loop de eventos principal
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_x):
                return "quit", 0
            if event.type == pygame.MOUSEBUTTONDOWN and exit_rect.collidepoint(event.pos):
                return "quit", 0

            # Lógica de seleção das opções do menu 
            if self.menu_continuar:
                if mouse_idx is not None:
                    self.menu_selected_idx = mouse_idx
                if event.type == pygame.MOUSEBUTTONDOWN and mouse_idx is not None:
                    self.som.play_som_menu_selecao()
                    if mouse_idx == 0: return "modo", 0
                    if mouse_idx == 1: return "ajuda", 0
                    if mouse_idx == 2: return "creditos", 0
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        self.menu_selected_idx = (self.menu_selected_idx + 1) % 3
                        self.som.play_som_menu_selecao()
                    elif event.key == pygame.K_UP:
                        self.menu_selected_idx = (self.menu_selected_idx - 1) % 3
                        self.som.play_som_menu_selecao()
                    elif event.key == pygame.K_RETURN:
                        self.som.play_som_menu_selecao()
                        if self.menu_selected_idx == 0: return "modo", 0
                        if self.menu_selected_idx == 1: return "ajuda", 0
                        if self.menu_selected_idx == 2: return "creditos", 0
            
            # Ativa as opções do menu com a tecla Espaço
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.som.play_som_menu_selecao()
                self.menu_continuar = True

            # Lógica para iniciar a animação das letras (segredo)
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                if not self.letras_quicando and not self.menu_continuar:
                    ativar_animacao = False
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        for _, rect in letras_rects:
                            if rect.collidepoint(event.pos):
                                ativar_animacao = True
                                break
                    else: # KEYDOWN
                        letra = pygame.key.name(event.key).upper()
                        if letra in "PINGPONG":
                            ativar_animacao = True
                    
                    if ativar_animacao:
                        self.letras_quicando = True
                        self.letras_quicando_start = time.time()
                        self.letras_bolas = []
                        title = "PING-PONG"
                        total_w = len(title) * 92
                        start_x = self.WIDTH // 2 - total_w // 2 + 92 // 2
                        for i, l in enumerate(title):
                            x = start_x + i * 92
                            y = self.HEIGHT // 2 - 160
                            self.letras_bolas.append({
                                'letra': l, 'x': x, 'y': y,
                                'vx': random.choice([-1, 1]) * random.uniform(8, 14),
                                'vy': random.choice([-1, 1]) * random.uniform(8, 14),
                                'target_x': x, 'target_y': y
                            })
                        return "menu", 0
                        
        pygame.display.flip()
        pygame.time.Clock().tick(60)
        return "menu", 0

    def run_ajuda(self):
        """Executa a lógica e o loop de eventos para a tela de Ajuda"""
        exit_rect = draw_ajuda()
        self.bola_menu.move(self.WIDTH, self.HEIGHT)
        draw_bola_menu(pygame.display.get_surface(), self.bola_menu)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "quit", 0
            if event.type == pygame.KEYDOWN and event.key == pygame.K_z:
                self.som.play_som_menu_selecao()
                return "menu", 0
            if event.type == pygame.MOUSEBUTTONDOWN and exit_rect.collidepoint(event.pos):
                self.som.play_som_menu_selecao()
                return "menu", 0
        
        pygame.display.flip()
        pygame.time.Clock().tick(60)
        return "ajuda", 0

    def run_creditos(self):
        """Executa a lógica e o loop de eventos para a tela de Créditos"""
        link_area, exit_rect = draw_creditos()
        self.bola_menu.move(self.WIDTH, self.HEIGHT)
        draw_bola_menu(pygame.display.get_surface(), self.bola_menu)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "quit", 0
            if event.type == pygame.KEYDOWN and event.key == pygame.K_z:
                self.som.play_som_menu_selecao()
                return "menu", 0
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Abre o link do LinkedIn se clicado.
                if link_area.collidepoint(pygame.mouse.get_pos()):
                    webbrowser.open("https://www.linkedin.com/in/vitor-n-9441932b1/")
                if exit_rect.collidepoint(event.pos):
                    self.som.play_som_menu_selecao()
                    return "menu", 0
        
        pygame.display.flip()
        pygame.time.Clock().tick(60)
        return "creditos", 0

    def run_modo(self):
        """Executa a lógica e o loop de eventos para a tela de Seleção de Modo"""
        _, mouse_idx, exit_rect = draw_modo_menu(self.menu_selected_idx)
        self.bola_menu.move(self.WIDTH, self.HEIGHT)
        draw_bola_menu(pygame.display.get_surface(), self.bola_menu)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "quit", None
            
            if mouse_idx is not None:
                self.menu_selected_idx = mouse_idx
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if mouse_idx is not None:
                    self.som.play_som_menu_selecao()
                    if mouse_idx == 0: return "map_select", "local"
                    if mouse_idx == 1: return "map_select", "bot"
                if exit_rect.collidepoint(event.pos):
                    self.som.play_som_menu_selecao()
                    return "menu", None

            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_1, pygame.K_2]:
                    self.som.play_som_menu_selecao()
                    return "map_select", "local" if event.key == pygame.K_1 else "bot"
                if event.key == pygame.K_DOWN:
                    self.menu_selected_idx = (self.menu_selected_idx + 1) % 2
                    self.som.play_som_menu_selecao()
                if event.key == pygame.K_UP:
                    self.menu_selected_idx = (self.menu_selected_idx - 1) % 2
                    self.som.play_som_menu_selecao()
                if event.key == pygame.K_RETURN:
                    self.som.play_som_menu_selecao()
                    return "map_select", "local" if self.menu_selected_idx == 0 else "bot"
                if event.key == pygame.K_z:
                    self.som.play_som_menu_selecao()
                    return "menu", None
        
        pygame.display.flip()
        pygame.time.Clock().tick(60)
        return "modo", None

    def run_map_select(self, selected_map_idx):
        """Executa a lógica e o loop de eventos para a tela de Seleção de Mapa"""
        _, mouse_idx = draw_map_select_menu(selected_map_idx)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "quit", selected_map_idx
            
            if mouse_idx is not None:
                selected_map_idx = mouse_idx

            if event.type == pygame.MOUSEBUTTONDOWN and mouse_idx is not None:
                self.som.play_som_menu_selecao()
                return "playing", selected_map_idx
            
            if event.type == pygame.KEYDOWN:
                last_selected_map_idx = selected_map_idx
                if event.key == pygame.K_LEFT and selected_map_idx % 3 > 0: selected_map_idx -= 1
                if event.key == pygame.K_RIGHT and selected_map_idx % 3 < 2: selected_map_idx += 1
                if event.key == pygame.K_UP and selected_map_idx >= 3: selected_map_idx -= 3
                if event.key == pygame.K_DOWN and selected_map_idx < 3: selected_map_idx += 3
                
                if selected_map_idx != last_selected_map_idx:
                    self.som.play_som_menu_selecao()
                
                if event.key == pygame.K_RETURN:
                    return "playing", selected_map_idx
        
        pygame.display.flip()
        pygame.time.Clock().tick(60)
        return "map_select", selected_map_idx