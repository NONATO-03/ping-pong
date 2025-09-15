import time
import math
import pygame


# CLASSE DA RAQUETE


class Raquete:
    """
    Representa a raquete dos jogadores
    
    Esta classe controla a posição, movimento, aparência e os poderes
    especiais da raquete. Ela também gerencia efeitos visuais como
    o rastro de movimento e uma animação de "gelatina" ao parar
    """

    def __init__(self, x, y, is_left_paddle=False):
        """
        Inicializa um novo objeto Raquete.

        Args:
            x (int): A posição inicial da raquete no eixo X
            y (int): A posição inicial da raquete no eixo Y
            is_left_paddle (bool): True se for a raquete da esquerda False se for a da direita
        """
        # Atributos de Posição e Dimensão 
        self.x = x
        self.y = y
        self.width = 28  # Largura da raquete
        self.height = 120  # Altura atual da raquete (pode mudar com poderes)
        self.base_height = 120  # Altura padrão para resetar após poderes

        # Atributos de Aparência e Efeitos Visuais
        self.color = (255, 255, 255)  # Cor principal da raquete
        self.glow = (255, 255, 255, 80)  # Cor do brilho (não utilizado no código fornecido)
        self.trail = []  # Lista para armazenar partículas do rastro de movimento
        self.shake_time = 0  # Timestamp para controlar o efeito de "gelatina"
        self.shake_offset = 0  # Deslocamento vertical do efeito (não utilizado)

        # Atributos de Movimento
        self.move_speed = 20  # Velocidade de movimento em pixels por frame
        self.is_moving_up = False  # Flag que indica se está se movendo para cima
        self.is_moving_down = False  # Flag que indica se está se movendo para baixo
        self.last_move_dir = 0  # Guarda a última direção de movimento (-1 para cima, 1 para baixo, 0 parado)

        # Atributos de Poderes (Power-ups) 
        self.is_left_paddle = is_left_paddle  # Identificador da raquete
        self.power_ups = {
            "uva": False, "melancia": False, "banana": False,
            "morango": False, "blueberry": False
        }  # Dicionário para rastrear quais poderes estão ativos
        self.active_power_ups = {}  # Dicionário para rastrear o tempo de ativação dos poderes
        self.power_used = False  # Flag especial para poderes de uso único (banana, morango)
        self.espelhada = None  # Atributo para possível raquete espelhada (não utilizado)

    def draw(self, screen):
        """
        Desenha a raquete e seus efeitos visuais na tela.

        Args:
            screen (pygame.Surface): A superfície da tela onde a raquete será desenhada.
        """
        # Efeito de Gelatinoso ao Parar 
        shake = 0
        # O efeito dura 0.25 segundos após a raquete parar
        if self.shake_time and time.time() - self.shake_time < 0.25:
            # Usa uma função seno para criar uma oscilação suave
            shake = math.sin((time.time() - self.shake_time) * 20) * 8
        
        # Cria o retângulo da raquete, aplicando o deslocamento do shake
        rect = pygame.Rect(self.x - self.width // 2, self.y - self.height // 2 + shake, self.width, self.height)
        pygame.draw.rect(screen, self.color, rect, border_radius=8)

        # Efeito de Rastro Animado
        # Itera sobre cada partícula do rastro
        for t in self.trail:
            # Calcula a transparência (alpha) com base no tempo de vida da partícula
            alpha = int(120 * (1 - (time.time() - t["time"]) / 0.3))
            if alpha > 0:
                # Cria uma superfície temporária para desenhar o rastro com transparência
                trail_surf = pygame.Surface((self.width, 24), pygame.SRCALPHA)
                trail_rect = trail_surf.get_rect()
                pygame.draw.rect(trail_surf, t["color"] + (alpha,), trail_rect, border_radius=8)
                
                # Posiciona e desenha a partícula do rastro na tela principal
                screen.blit(trail_surf, (t["x"] - self.width / 2, t["y"] - 12))

    def update_trail(self, dir):
        """
        Adiciona novas partículas ao rastro e remove as antigas

        Args:
            dir: A direção do movimento atual (-1 para cima, 1 para baixo, 0 parado)
        """
        if dir != 0:
            # Define a cor do rastro com base no jogador.
            color = (180, 180, 255) if self.is_left_paddle else (255, 180, 180)
            
            # Calcula a posição inicial da partícula (na extremidade oposta ao movimento)
            offset = -self.height / 2 - 10 if dir == -1 else self.height / 2 + 10
            
            # Adiciona a nova partícula à lista do rastro
            self.trail.append({
                "x": self.x, "y": self.y + offset, "dir": dir,
                "time": time.time(), "color": color
            })
            
        # Remove as partículas que já expiraram 
        self.trail = [t for t in self.trail if time.time() - t["time"] < 0.3]

    # Métodos de Controle de Movimento
    def start_move_up(self):
        """Ativa o movimento para cima."""
        self.is_moving_up = True

    def stop_move_up(self):
        """Desativa o movimento para cima"""
        self.is_moving_up = False

    def start_move_down(self):
        """Ativa o movimento para baixo"""
        self.is_moving_down = True

    def stop_move_down(self):
        """Desativa o movimento para baixo"""
        self.is_moving_down = False

    def move(self, arena_top, arena_bottom):
        """
        Atualiza a posição da raquete com base nas flags de movimento e nos limites da arena

        Args:
            arena_top (int): A coordenada Y do topo da área de jogo
            arena_bottom (int): A coordenada Y da base da área de jogo
        """
        moved = False
        dir = 0  

        if self.is_moving_up:
            # Verifica se a raquete não ultrapassará o limite superior
            if self.y - self.height / 2 > arena_top + 8:
                self.y -= self.move_speed
                moved = True
                dir = -1
            else:
                self.y = arena_top + self.height / 2 + 8  # Trava a posição no limite
        
        elif self.is_moving_down:
            # Verifica se a raquete não ultrapassará o limite inferior
            if self.y + self.height / 2 < arena_bottom - 8:
                self.y += self.move_speed
                moved = True
                dir = 1
            else:
                self.y = arena_bottom - self.height / 2 - 8  # Trava a posição no limite

        # Se a raquete parou de se mover neste frame, inicia o timer do efeito gelatina
        if not moved and self.last_move_dir != 0:
            self.shake_time = time.time()
        
        self.last_move_dir = dir  # Atualiza a última direção de movimento
        self.update_trail(dir)  # Atualiza o rastro com a direção atual

    # Métodos de Gerenciamento de Poderes
    def activate_power_up(self, power_up_type):
        """
        Ativa um poder, desativando qualquer outro que estivesse ativo

        Args:
            power_up_type (str): O nome do poder a ser ativado (ex: "uva")
        """
        # Garante que apenas um poder esteja ativo por vez
        for other_power in list(self.power_ups.keys()):
            if self.power_ups[other_power] and other_power != power_up_type:
                self.deactivate_power_up(other_power)
        
        self.power_ups[power_up_type] = True
        self.active_power_ups[power_up_type] = time.time()
        
        # Aplica o efeito específico do poder
        if power_up_type == "uva":
            self.height = 160
        else:
            self.height = self.base_height

    def deactivate_power_up(self, power_up_type):
        """
        Desativa um poder específico e restaura o estado padrão da raquete

        Args:
            power_up_type O nome do poder a ser desativado
        """
        self.power_ups[power_up_type] = False
        if power_up_type in self.active_power_ups:
            del self.active_power_ups[power_up_type]
        
        # Restaura a altura original da raquete.
        self.height = self.base_height

    def get_power(self):
        """Retorna o nome do poder atualmente ativo, ou None se não houver nenhum"""
        for power_name, is_active in self.power_ups.items():
            if is_active:
                return power_name
        return None
    
    def get_power_time_left(self):
        """
        Calcula e retorna o tempo restante do poder ativo

        Returns:
            float or None: O tempo restante em segundos, ou None se não houver poder ativo
        """
        power = self.get_power()
        if not power or power not in self.active_power_ups:
            return None
            
        elapsed_time = time.time() - self.active_power_ups[power]
        time_left = 20 - elapsed_time
        return max(0, time_left)  # Garante que não retorne um tempo negativado

    def update_power(self):
        """
        Verifica o estado dos poderes ativos e os desativa se o tempo acaboa
        ou se já foram utilizados.
        """
        power = self.get_power()
        if not power:
            return

        time_left = self.get_power_time_left()

        # Desativa poderes de uso único (banana, morango) após serem usados
        if power in ["banana", "morango"] and self.power_used:
            self.deactivate_power_up(power)
            self.power_used = False
        
        # Desativa poderes com tempo limite quando o tempo expira
        elif time_left is not None and time_left <= 0:
            self.deactivate_power_up(power)
            self.power_used = False