import random
import time
from visual import ARENA_LEFT, ARENA_RIGHT, ARENA_TOP, ARENA_BOTTOM, ARENA_CENTER_X, ARENA_CENTER_Y

# CLASSE DA HABILIDADE (FRUTA)


class Habilidade:
    """
    Representa um item de poder que aparece na arena
    
    Este objeto, visualizado como uma fruta e se move pela tela e pode ser
    coletado pelos jogadores para ativar um poder especial
    """

    def __init__(self, cor, tipo_habilidade):
        """
        Inicializa uma nova habilidade (fruta).

        Args:
            cor (tuple): Uma tupla (R, G, B) representando a cor da fruta
            tipo_habilidade (str): O nome do poder que esta fruta concede 
        """
        fruta_radius = 28  # Define o raio padrão para todas as frutas.

        # Atributos de Posição e Movimento 
        self.x = ARENA_CENTER_X  # Posição inicial X no centro da arena
        self.y = ARENA_CENTER_Y  # Posição inicial Y no centro da arena
        self.x_move = random.choice([-7, 7])  # Define uma velocidade horizontal inicial aleatória
        self.y_move = random.choice([-7, 7])  # Define uma velocidade vertical inicial aleatória
        self.radius = fruta_radius

        # Atributos de Identificação
        self.cor = cor
        self.tipo_habilidade = tipo_habilidade

    def move(self):
        """
        Atualiza a posição da fruta e a faz quicar nas paredes da arena
        """
        # Atualiza as coordenadas com base na velocidade
        self.x += self.x_move
        self.y += self.y_move

        # Verifica colisão com as paredes horizontais
        if self.x - self.radius <= ARENA_LEFT or self.x + self.radius >= ARENA_RIGHT:
            self.bounce_x()
            # Garante que a fruta não fique "presa" fora da tela após a colisão
            self.x = max(ARENA_LEFT + self.radius, min(self.x, ARENA_RIGHT - self.radius))

        # Verifica colisão com as paredes verticais 
        if self.y - self.radius <= ARENA_TOP or self.y + self.radius >= ARENA_BOTTOM:
            self.bounce_y()
            # Garante que a fruta não fique presa fora da tela após a colisão
            self.y = max(ARENA_TOP + self.radius, min(self.y, ARENA_BOTTOM - self.radius))

    def bounce_x(self):
        """Inverte a direção do movimento no eixo X"""
        self.x_move *= -1

    def bounce_y(self):
        """Inverte a direção do movimento no eixo Y"""
        self.y_move *= -1

    def reset_position(self):
        """
        Move a fruta para uma posição fora da tela visível
        
        Isso é uma forma de esconder a fruta sem removê-la da memória
        """
        self.x = 1000
        self.y = 1000


# CLASSE DO GERENCIADOR DE HABILIDADES

class GerenciadorHabilidades:
    """
    Controla o ciclo de vida das habilidades no jogo.
    
    É responsável por criar novas frutas em intervalos de tempo
    atualizar suas posições e gerenciá-las em uma lista
    """

    def __init__(self, power_colors, max_frutas=1, spawn_interval=20):
        """
        Inicializa o gerenciador de habilidades

        Args:
            power_colors (dict): Dicionário que mapeia tipos de habilidade para suas cores
            max_frutas (int): O número máximo de frutas que podem estar na tela ao mesmo tempo
            spawn_interval (int): O intervalo em segundos entre o surgimento de novas frutas
        """
        self.power_colors = power_colors
        self.max_frutas = max_frutas
        self.spawn_interval = spawn_interval
        
        # Atributos de Controle 
        self.frutas = []  # Lista que armazena as frutas ativas na arena
        self.last_spawn = time.time()  # Timestamp do último surgimento de fruta

    def update(self):
        """
        Função principal de atualização, chamada a cada frame do jogo
        
        Move as frutas existentes e verifica se uma nova fruta deve ser criada
        """
        # 1. Move todas as frutas que estão na arena
        for fruta in self.frutas:
            fruta.move()

        # 2. Verifica se é hora de criar uma nova fruta
        now = time.time()
        pode_criar = len(self.frutas) < self.max_frutas  # Checa se há espaço para mais frutas
        tempo_passou = (now - self.last_spawn) > self.spawn_interval  # Checa se o tempo de espera passou

        if pode_criar and tempo_passou:
            # Escolhe um tipo de habilidade aleatoriamente do dicionário
            tipo = random.choice(list(self.power_colors.keys()))
            cor = self.power_colors[tipo][0]
            
            # Cria a nova fruta e a adiciona à lista de frutas ativas
            self.frutas.append(Habilidade(cor, tipo))
            self.last_spawn = now  

    def reset(self):
        """
        Limpa todas as frutas da arena e reinicia o contador de tempo
        
        Útil para ser chamado no início de uma nova partida
        """
        self.frutas.clear()
        self.last_spawn = time.time()

    def remover_fruta(self, fruta):
        """
        Remove uma fruta específica da lista de frutas ativas
        
        Geralmente chamado quando um jogador coleta a fruta

        Args:
            fruta (Habilidade): O objeto da fruta a ser removido
        """
        if fruta in self.frutas:
            self.frutas.remove(fruta)