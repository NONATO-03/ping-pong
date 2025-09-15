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

# CONTROLA TODAS AS ABAS DO MENU DO JOGO

class BolaMenu:
    def __init__(self, x, y, som, radius=14, color=(255,255,255)):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.x_move = random.choice([-1,1]) * random.uniform(3,5)
        self.y_move = random.choice([-1,1]) * random.uniform(3,5)
        self.rastro = []
        self.som = som

    def move(self, WIDTH, HEIGHT):
        self.rastro.append({'x': self.x, 'y': self.y, 'radius': self.radius, 'alpha': 180, 'color': self.color})
        for r in self.rastro:
            r['radius'] = max(2, r['radius'] * 0.85)
            r['alpha'] = max(0, r['alpha'] - 15)
        self.rastro = [r for r in self.rastro if r['alpha'] > 0 and r['radius'] > 1]
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

def draw_bola_menu(screen, bola_menu):
    for r in bola_menu.rastro:
        surf = pygame.Surface((r['radius']*2, r['radius']*2), pygame.SRCALPHA)
        cor = r.get('color', (255,255,255))
        pygame.draw.circle(surf, cor + (int(r['alpha']),), (int(r['radius']), int(r['radius'])), int(r['radius']))
        screen.blit(surf, (r['x']-r['radius'], r['y']-r['radius']))
    pygame.draw.circle(screen, bola_menu.color, (int(bola_menu.x), int(bola_menu.y)), bola_menu.radius)

class MenuState:
    def __init__(self, WIDTH, HEIGHT, som):
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.som = som
        self.menu_selected_idx = 0
        self.menu_continuar = False
        self.letras_quicando = False
        self.letras_quicando_start = 0
        self.letras_bolas = []
        self.letras_voltando = False
        self.bola_menu = BolaMenu(WIDTH//2, HEIGHT//2, som)

    def reset(self):
        self.menu_selected_idx = 0
        self.menu_continuar = False
        self.letras_quicando = False
        self.letras_voltando = False
        self.letras_bolas = []
        self.letras_quicando_start = 0

    def run(self, game_state, selected_map_idx=0):
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

    def run_principal(self):
        screen = pygame.display.get_surface()
        if self.letras_quicando:
            letras_rects, _, exit_rect = draw_menu_principal(
                self.menu_selected_idx,
                mostrar_opcoes=self.menu_continuar,
                letras_bolas=self.letras_bolas,
                letras_voltando=self.letras_voltando
            )
            # ANIMAÇÃO DAS LETRAS
            if not self.letras_voltando:
                for letra in self.letras_bolas:
                    letra['x'] += letra['vx']
                    letra['y'] += letra['vy']
                    if letra['x'] < 0 or letra['x'] > self.WIDTH:
                        letra['vx'] *= -1
                    if letra['y'] < 0 or letra['y'] > self.HEIGHT:
                        letra['vy'] *= -1
                if time.time() - self.letras_quicando_start > 5:
                    self.letras_voltando = True
                    for letra in self.letras_bolas:
                        dx = letra['target_x'] - letra['x']
                        dy = letra['target_y'] - letra['y']
                        letra['vx'] = dx / 30
                        letra['vy'] = dy / 30
            else:
                todas_no_lugar = True
                for letra in self.letras_bolas:
                    letra['x'] += letra['vx']
                    letra['y'] += letra['vy']
                    if abs(letra['x'] - letra['target_x']) > 2 or abs(letra['y'] - letra['target_y']) > 2:
                        todas_no_lugar = False
                if todas_no_lugar:
                    self.letras_quicando = False
                    self.letras_voltando = False
            self.bola_menu.move(self.WIDTH, self.HEIGHT)
            draw_bola_menu(screen, self.bola_menu)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit", 0
                if event.type == pygame.KEYDOWN and event.key == pygame.K_x:
                    return "quit", 0
                if event.type == pygame.MOUSEBUTTONDOWN and exit_rect.collidepoint(event.pos):
                    return "quit", 0
            pygame.display.flip()
            pygame.time.Clock().tick(60)
            return "menu", 0

        letras_rects, mouse_idx, exit_rect = draw_menu_principal(
            self.menu_selected_idx,
            mostrar_opcoes=self.menu_continuar
        )
        self.bola_menu.move(self.WIDTH, self.HEIGHT)
        draw_bola_menu(screen, self.bola_menu)
        mx, my = pygame.mouse.get_pos()
        # Ativa menu de seleção ao passar mouse sobre opções
        if not self.menu_continuar and mouse_idx is not None:
            self.menu_continuar = True
            self.menu_selected_idx = mouse_idx
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", 0
            if event.type == pygame.KEYDOWN and event.key == pygame.K_x:
                return "quit", 0
            if event.type == pygame.MOUSEBUTTONDOWN and exit_rect.collidepoint(event.pos):
                return "quit", 0
            if self.menu_continuar and event.type == pygame.MOUSEBUTTONDOWN and mouse_idx is not None:
                self.menu_selected_idx = mouse_idx
                self.som.play_som_menu_selecao()
                if mouse_idx == 0:
                    return "modo", 0
                elif mouse_idx == 1:
                    return "ajuda", 0
                elif mouse_idx == 2:
                    return "creditos", 0
            if self.menu_continuar and mouse_idx is not None:
                self.menu_selected_idx = mouse_idx
            if event.type == pygame.MOUSEBUTTONDOWN and not self.letras_quicando and not self.menu_continuar:
                mx, my = event.pos
                for letra, rect in letras_rects:
                    if rect.collidepoint(mx, my):
                        self.letras_quicando = True
                        self.letras_quicando_start = time.time()
                        self.letras_bolas = []
                        title = "PING-PONG"
                        base_x = self.WIDTH // 2
                        base_y = self.HEIGHT // 2 - 160
                        spacing = 92
                        total_w = len(title) * spacing
                        start_x = base_x - total_w // 2 + spacing // 2
                        for i, l in enumerate(title):
                            x = start_x + i * spacing
                            y = base_y
                            vx = random.choice([-1,1]) * random.uniform(8,14)
                            vy = random.choice([-1,1]) * random.uniform(8,14)
                            self.letras_bolas.append({
                                'letra': l,
                                'x': x,
                                'y': y,
                                'vx': vx,
                                'vy': vy,
                                'target_x': x,
                                'target_y': y
                            })
                        self.letras_voltando = False
                        break
                return "menu", 0
            if event.type == pygame.KEYDOWN:
                if not self.letras_quicando and not self.menu_continuar:
                    letra = pygame.key.name(event.key).upper()
                    if letra in "PINGPONG":
                        self.letras_quicando = True
                        self.letras_quicando_start = time.time()
                        self.letras_bolas = []
                        title = "PING-PONG"
                        base_x = self.WIDTH // 2
                        base_y = self.HEIGHT // 2 - 160
                        spacing = 92
                        total_w = len(title) * spacing
                        start_x = base_x - total_w // 2 + spacing // 2
                        for i, l in enumerate(title):
                            x = start_x + i * spacing
                            y = base_y
                            vx = random.choice([-1,1]) * random.uniform(8,14)
                            vy = random.choice([-1,1]) * random.uniform(8,14)
                            self.letras_bolas.append({
                                'letra': l,
                                'x': x,
                                'y': y,
                                'vx': vx,
                                'vy': vy,
                                'target_x': x,
                                'target_y': y
                            })
                        self.letras_voltando = False
                        return "menu", 0
                if not self.menu_continuar and event.key == pygame.K_SPACE:
                    self.som.play_som_menu_selecao()
                    self.menu_continuar = True
                elif self.menu_continuar:
                    if event.key == pygame.K_x:
                        return "quit", 0
                    elif event.key == pygame.K_DOWN:
                        self.menu_selected_idx = (self.menu_selected_idx + 1) % 3
                        self.som.play_som_menu_selecao()
                    elif event.key == pygame.K_UP:
                        self.menu_selected_idx = (self.menu_selected_idx - 1) % 3
                        self.som.play_som_menu_selecao()
                    elif event.key == pygame.K_RETURN:
                        self.som.play_som_menu_selecao()
                        if self.menu_selected_idx == 0:
                            return "modo", 0
                        elif self.menu_selected_idx == 1:
                            return "ajuda", 0
                        elif self.menu_selected_idx == 2:
                            return "creditos", 0
        pygame.display.flip()
        pygame.time.Clock().tick(60)
        return "menu", 0

    def run_ajuda(self):
        screen = pygame.display.get_surface()
        exit_rect = draw_ajuda()
        self.bola_menu.move(self.WIDTH, self.HEIGHT)
        draw_bola_menu(screen, self.bola_menu)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", 0
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    self.som.play_som_menu_selecao()
                    return "menu", 0
            if event.type == pygame.MOUSEBUTTONDOWN and exit_rect.collidepoint(event.pos):
                self.som.play_som_menu_selecao()
                return "menu", 0
        pygame.display.flip()
        pygame.time.Clock().tick(60)
        return "ajuda", 0

    def run_creditos(self):
        screen = pygame.display.get_surface()
        link_area, exit_rect = draw_creditos()
        self.bola_menu.move(self.WIDTH, self.HEIGHT)
        draw_bola_menu(screen, self.bola_menu)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", 0
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    self.som.play_som_menu_selecao()
                    return "menu", 0
            if event.type == pygame.MOUSEBUTTONDOWN:
                if link_area.collidepoint(pygame.mouse.get_pos()):
                    webbrowser.open("https://www.linkedin.com/in/vitor-n-9441932b1/")
                if exit_rect.collidepoint(event.pos):
                    self.som.play_som_menu_selecao()
                    return "menu", 0
        pygame.display.flip()
        pygame.time.Clock().tick(60)
        return "creditos", 0

    def run_modo(self):
        screen = pygame.display.get_surface()
        frames, mouse_idx, exit_rect = draw_modo_menu(self.menu_selected_idx)
        self.bola_menu.move(self.WIDTH, self.HEIGHT)
        draw_bola_menu(screen, self.bola_menu)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", None
            if mouse_idx is not None:
                self.menu_selected_idx = mouse_idx
            if event.type == pygame.MOUSEBUTTONDOWN and mouse_idx is not None:
                self.som.play_som_menu_selecao()
                if mouse_idx == 0:
                    return "map_select", "local"
                if mouse_idx == 1:
                    return "map_select", "bot"
            if event.type == pygame.MOUSEBUTTONDOWN and exit_rect.collidepoint(event.pos):
                self.som.play_som_menu_selecao()
                return "menu", None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.som.play_som_menu_selecao()
                    return "map_select", "local"
                if event.key == pygame.K_2:
                    self.som.play_som_menu_selecao()
                    return "map_select", "bot"
                if event.key == pygame.K_DOWN:
                    self.menu_selected_idx = (self.menu_selected_idx + 1) % 2
                    self.som.play_som_menu_selecao()
                if event.key == pygame.K_UP:
                    self.menu_selected_idx = (self.menu_selected_idx - 1) % 2
                    self.som.play_som_menu_selecao()
                if event.key == pygame.K_RETURN:
                    self.som.play_som_menu_selecao()
                    if self.menu_selected_idx == 0:
                        return "map_select", "local"
                    if self.menu_selected_idx == 1:
                        return "map_select", "bot"
                if event.key == pygame.K_z:
                    self.som.play_som_menu_selecao()
                    return "menu", None
        pygame.display.flip()
        pygame.time.Clock().tick(60)
        return "modo", None

    def run_map_select(self, selected_map_idx):
        frame_rects, mouse_idx = draw_map_select_menu(selected_map_idx)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", selected_map_idx
            if mouse_idx is not None:
                selected_map_idx = mouse_idx
            if event.type == pygame.MOUSEBUTTONDOWN and mouse_idx is not None:
                self.som.play_som_menu_selecao()
                return "playing", selected_map_idx
            if event.type == pygame.KEYDOWN:
                last_selected_map_idx = selected_map_idx
                if event.key == pygame.K_LEFT and selected_map_idx % 3 > 0:
                    selected_map_idx -= 1
                if event.key == pygame.K_RIGHT and selected_map_idx % 3 < 2:
                    selected_map_idx += 1
                if event.key == pygame.K_UP and selected_map_idx >= 3:
                    selected_map_idx -= 3
                if event.key == pygame.K_DOWN and selected_map_idx < 3:
                    selected_map_idx += 3
                if selected_map_idx != last_selected_map_idx:
                    self.som.play_som_menu_selecao()
                if event.key == pygame.K_RETURN:
                    return "playing", selected_map_idx
        pygame.display.flip()
        pygame.time.Clock().tick(60)
        return "map_select", selected_map_idx