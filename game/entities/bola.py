import math
import time
import random
from game.systems.determinacao import aplicar_determinacao_na_bola


# CLASSE PRINCIPAL DA BOLA

class Bola:
    """
    Representa a bola principal do jogo.
    
    Esta classe gerencia a posição da bola, seu movimento, colisões com
    as paredes, raquetes e obstáculos também controla efeitos visuais
    como o rastro e os efeitos de "fogo" que alteram sua velocidade e cor
    """

    def __init__(self, x, y):
        """
        Inicializa um novo objeto Bola

        Args:
            x: A posição inicial da bola no eixo X
            y: A posição inicial da bola no eixo Y
        """
        # Atributos de Posição e Aparencia 
        self.x = x
        self.y = y
        self.radius = 14  # Raio da bola em pixels
        self.color = (255, 255, 255)  # Cor inicial da bola 
        self.rastro = []  # Lista de dicionários para criar o efeito de rastro

        #  Atributos de Movimento e Velocidade
        self.base_speed = 3  # Velocidade inicial padrão
        self.x_move = self.base_speed  # Velocidade atual no eixo X
        self.y_move = self.base_speed  # Velocidade atual no eixo Y
        self.incremento_raquetada = 0.2  # Aumento de velocidade a cada rebatida

        # Atributos de Estado e Controle 
        self.last_hit_by = None  # Indica qual jogador rebateu por ultimo 
        self.spawn_time = time.time()  # Timestamp de quando a bola foi criada

        # Atributos para Efeitos Especiais
        self.raquetadas_consecutivas = 0  # Contador de rebatidas para ativar efeitos
        self.fogo_ativo = False  # Flag para o efeito de fogo laranja
        self.fogo_azul = False  # Flag para o efeito de fogo azul

    @property
    def angle(self):
        """
        Calcula e retorna o ângulo do vetor de movimento da bola em graus
        
        A propriedade é calculada dinamicamente com base nas velocidades
        `x_move` e `y_move`. O sinal negativo ajusta o ângulo para o
        sistema de coordenadas da tela.

        Returns:
            float: O ângulo do movimento em graus
        """
        return -math.degrees(math.atan2(self.y_move, self.x_move))

    def move(self, fan_angle=None, mapa_escolhido=0, center_x=0, center_y=0):
        """
        Atualiza a posição da bola, gerencia o rastro e verifica a colisão
        com a barra giratória (no mapa beta)

        Args:
            fan_angle (float, optional): O ângulo atual da barra giratória. Default é None
            mapa_escolhido (int, optional): O ID do mapa atual. Default é 0
            center_x (int, optional): Posição X do centro da arena. Default é 0
            center_y (int, optional): Posição Y do centro da arena. Default é 0
        """
        # Gerenciamento do Rastro
        # Adiciona a posição atual ao rastro
        self.rastro.append({'x': self.x, 'y': self.y, 'radius': self.radius, 'alpha': 180, 'color': self.color})
        
        # Atualiza cada partícula do rastro
        for r in self.rastro:
            r['radius'] *= 0.85  # Reduz o tamanho
            r['alpha'] -= 15  
            r['radius'] = max(2, r['radius'])  
            r['alpha'] = max(0, r['alpha'])  
        
        # Remove as partículas do rastro que se tornaram invisíveis
        self.rastro = [r for r in self.rastro if r['alpha'] > 0 and r['radius'] > 1]
        
        # Atualização da Posição
        self.x += self.x_move
        self.y += self.y_move
        
        # Lógica de Colisão Específica do Mapa BETA 
        if mapa_escolhido == 1 and fan_angle is not None:
            # Só checa colisão após 1 segundo para evitar colidir ao nascer
            if time.time() - self.spawn_time > 1:
                if colide_barra_giratoria(self.x, self.y, self.radius, center_x, center_y, 170, 18, fan_angle):
                    # Determina a direção do rebote com base na posição relativa a barra
                    dx = self.x - center_x
                    dy = self.y - center_y
                    barra_dx = math.cos(fan_angle)
                    barra_dy = math.sin(fan_angle)
                    
                    if abs(dx * barra_dx) > abs(dy * barra_dy):
                        self.bounce_x()
                    else:
                        self.bounce_y()

    def bounce_y(self):
        """Inverte a direção do movimento no eixo Y (colisão vertical)"""
        self.y_move *= -1

    def bounce_x(self):
        """Inverte a direção do movimento no eixo X (colisão horizontal)"""
        self.x_move *= -1

    def reset_position(self, center_x, center_y, tempo_passado=0):
        """
        Reseta a bola para o centro da arena após um ponto
        
        Esta função também atualiza a velocidade base e reinicia todos
        os efeitos especiais e contadores relacionados a eles

        Args:
            center_x (int): A posição X do centro da arena
            center_y (int): A posição Y do centro da arena
            tempo_passado (float, optional): O tempo total de jogo, para ajustar a dificuldade. Default é 0
        """
        self.atualizar_velocidade(tempo_passado)
        
        # Reposiciona a bola no centro
        self.x = center_x
        self.y = center_y
        
        # Define uma nova direção inicial aleatória
        self.x_move = self.base_speed if random.choice([True, False]) else -self.base_speed
        self.y_move = self.base_speed if random.choice([True, False]) else -self.base_speed
        
        # Limpa o rastro e reseta os contadores e flags de estado
        self.rastro.clear()
        self.spawn_time = time.time()
        self.raquetadas_consecutivas = 0
        self.fogo_ativo = False
        self.fogo_azul = False


    def atualizar_velocidade(self, tempo_passado):
        """
        Aumenta a velocidade base da bola e o incremento por raquetada com o tempo
        Isso serve para aumentar a dificuldade do jogo progressivamente

        Args:
            tempo_passado (float): O tempo total de jogo decorrido em segundos
        """
        # A velocidade base aumenta a cada 60 segundos
        self.base_speed = 5 + 1.5 * int(tempo_passado // 60)
        # O incremento por raquetada aumenta a cada 30 segundos
        self.incremento_raquetada = 0.2 + 0.1 * int(tempo_passado // 30)

    def aumentar_velocidade_raquetada(self):
        """
        Aumenta a velocidade da bola após ser rebatida por uma raquete
        e gerencia a ativação dos efeitos de fogo
        """
        self.raquetadas_consecutivas += 1

        # Ativa o efeito de fogo normal após 10 rebatidas consecutivas
        if not self.fogo_ativo and self.raquetadas_consecutivas >= 10:
            self.fogo_ativo = True

        # Ativa o efeito de fogo azul após 25 rebatidas consecutivas se o fogo normal já estiver ativo
        if self.fogo_ativo and not self.fogo_azul and self.raquetadas_consecutivas >= 25:
            self.fogo_azul = True

        # Determina o incremento de velocidade com base nos efeitos ativos
        incremento = self.incremento_raquetada
        if self.fogo_azul:
            incremento += 0.6
        elif self.fogo_ativo:
            incremento += 0.2
            
        # Aplica o incremento na direção atual da bola
        if self.x_move > 0:
            self.x_move += incremento
        else:
            self.x_move -= incremento
            
        if self.y_move > 0:
            self.y_move += incremento
        else:
            self.y_move -= incremento

    def update(
        self,
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
        fan_angle=None,
        mapa_escolhido=0,
        determinacao_manager=None,
        obstacles=None
    ):
        """
        Função principal de atualização da bola, chamada a cada frame do jogo
        
        Ela orquestra o movimento e as colisões 
        e a lógica de pontuação, além de gerenciar os efeitos visuais e sonoros

        Args:
            (Vários): Parâmetros que representam o estado do jogo, como
                      as raquetes, placar, sistema de som e limites da arena

        Returns:
            tuple: Um par de booleanos (impact_left, impact_right) indicando
                   se houve colisão com as raquetes neste frame
        """
        # 1. Movimenta a bola
        self.move(
            fan_angle=fan_angle,
            mapa_escolhido=mapa_escolhido,
            center_x=ARENA_CENTER_X,
            center_y=ARENA_CENTER_Y
        )

        # 2. Lógica de Colisão com Obstáculos do Mapa 2
        if mapa_escolhido == 2 and obstacles:
            for obstacle in obstacles:
                if obstacle.check_collision(self):
                    som.play_som_parede()
                    break  # Evita múltiplas colisões com obstáculos no mesmo frame

        # 3. Gerencia a Cor da Bola e do Rastro com base nos Poderes e Efeitos
        power_left = l_paddle.get_power()
        power_right = r_paddle.get_power()
        morango_ativo = (
            (self.last_hit_by == "left" and power_left == "morango") or
            (self.last_hit_by == "right" and power_right == "morango")
        )

        if morango_ativo:
            self.color = (255, 0, 0)  # Vermelho
        elif self.fogo_azul:
            self.color = (80, 120, 255)  # Azul
        elif self.fogo_ativo:
            self.color = (255, 120, 0)  # Laranja
        else:
            self.color = (255, 255, 255)  # Branco
        
        # Garante que a cor do rastro seja a mesma da bola
        for r in self.rastro:
            r['color'] = self.color

        # 4. Atualiza Bolas Falsas (Blueberry)
        for fake in fake_balls[:]:  # Itera sobre uma cópia da lista
            fake.move(ARENA_LEFT=ARENA_LEFT, ARENA_RIGHT=ARENA_RIGHT, ARENA_TOP=ARENA_TOP, ARENA_BOTTOM=ARENA_BOTTOM)
            if fake.wall_hits >= 9:
                fake_balls.remove(fake)
                som.play_som_habilidade_desaparece()

        # 5. Colisão com as Paredes Superior e Inferior
        if self.y - self.radius < ARENA_TOP or self.y + self.radius > ARENA_BOTTOM:
            self.bounce_y()
            som.play_som_parede()

        # 6. Lógica de Pontuação 
        # Ponto para o jogador da direita-----
        if self.x - self.radius < ARENA_LEFT:
            placar.r_score += 3 if morango_ativo else 1
            som.play_som_pontuacao()
            self.reset_position(ARENA_CENTER_X, ARENA_CENTER_Y, tempo_passado)

        # Ponto para o jogador da esquerda-----
        elif self.x + self.radius > ARENA_RIGHT:
            placar.l_score += 3 if morango_ativo else 1
            som.play_som_pontuacao()
            self.reset_position(ARENA_CENTER_X, ARENA_CENTER_Y, tempo_passado)

        # 7. Colisão com as Raquetes-----------------------------------------------------------------------------------------------------------

        # Raquete Esquerda 
        if (l_paddle.x - l_paddle.width // 2 < self.x < l_paddle.x + l_paddle.width // 2 and
                l_paddle.y - l_paddle.height // 2 < self.y < l_paddle.y + l_paddle.height // 2):
            self.x = l_paddle.x + l_paddle.width // 2 + self.radius  # Corrige posição para evitar bugs rs
            self.aumentar_velocidade_raquetada()
            self.bounce_x()
            self.last_hit_by = "left"
            impact_left = True
            
            power = l_paddle.get_power()
            if power == "banana" and not l_paddle.power_used:
                self.x_move *= 10  # Aumenta drasticamente a velocidade
                self.y_move *= 10
                l_paddle.power_used = True
                som.play_som_tiro_poderoso()
            else:
                som.play_som_raquete()
                
            if power == "blueberry":
                # Cria a fake ball com direção diferente da bola original
                angle = random.uniform(0, 2 * math.pi)
                speed = math.hypot(self.x_move, self.y_move)
                fake_x_move = math.cos(angle) * speed
                fake_y_move = math.sin(angle) * speed
                fake_balls.append(BolaFake(self.x, self.y, fake_x_move, fake_y_move))
                som.play_som_habilidade_coletada()
                
            aplicar_determinacao_na_bola(self, l_paddle, r_paddle, determinacao_manager)
        else:
            impact_left = False

        # Raquete Esquerda (Espelhada - Melancia)
        if l_paddle.get_power() == "melancia":
            espelhada_y = ARENA_BOTTOM - (l_paddle.y - ARENA_TOP)
            if (l_paddle.x - l_paddle.width // 2 < self.x < l_paddle.x + l_paddle.width // 2 and
                    espelhada_y - l_paddle.height // 2 < self.y < espelhada_y + l_paddle.height // 2):
                self.x = l_paddle.x + l_paddle.width // 2 + self.radius
                self.aumentar_velocidade_raquetada()
                self.bounce_x()
                self.last_hit_by = "left"
                impact_left = True
                som.play_som_raquete()

        #  Raquete Direita 
        if (r_paddle.x - r_paddle.width // 2 < self.x < r_paddle.x + r_paddle.width // 2 and
                r_paddle.y - r_paddle.height // 2 < self.y < r_paddle.y + r_paddle.height // 2):
            self.x = r_paddle.x - r_paddle.width // 2 - self.radius
            self.aumentar_velocidade_raquetada()
            self.bounce_x()
            self.last_hit_by = "right"
            impact_right = True
            
            power = r_paddle.get_power()
            if power == "banana" and not r_paddle.power_used:
                self.x_move *= 10
                self.y_move *= 10
                r_paddle.power_used = True
                som.play_som_tiro_poderoso()
            else:
                som.play_som_raquete()

            if power == "blueberry":
                # Cria a fake ball com direção diferente da bola original
                angle = random.uniform(0, 2 * math.pi)
                speed = math.hypot(self.x_move, self.y_move)
                fake_x_move = math.cos(angle) * speed
                fake_y_move = math.sin(angle) * speed
                fake_balls.append(BolaFake(self.x, self.y, fake_x_move, fake_y_move))
                som.play_som_habilidade_coletada()

            aplicar_determinacao_na_bola(self, l_paddle, r_paddle, determinacao_manager)
        else:
            impact_right = False
        
        # Raquete Direita (Espelhada - Melancia)
        if r_paddle.get_power() == "melancia":
            espelhada_y = ARENA_BOTTOM - (r_paddle.y - ARENA_TOP)
            if (r_paddle.x - r_paddle.width // 2 < self.x < r_paddle.x + r_paddle.width // 2 and
                    espelhada_y - r_paddle.height // 2 < self.y < espelhada_y + r_paddle.height // 2):
                self.x = r_paddle.x - r_paddle.width // 2 - self.radius
                self.aumentar_velocidade_raquetada()
                self.bounce_x()
                self.last_hit_by = "right"
                impact_right = True
                som.play_som_raquete()

        return impact_left, impact_right



# CLASSE DA BOLA FALSA (BLUEBERRY)


class BolaFake(Bola):
    """
    Representa uma bola falsa gerada pela habilidade blueberry
    
    Esta classe herda da `Bola` principal, mas tem um comportamento
    mais simples. Ela se move e quica nas paredes, mas não interage
    com as raquetes e desaparece após um certo número de colisões
    """

    def __init__(self, x, y, x_move, y_move):
        """
        Inicializa a bola falsa.

        Args:
            x (int): Posição X inicial.
            y (int): Posição Y inicial.
            x_move (float): Velocidade X inicial (herdada da bola principal)
            y_move (float): Velocidade Y inicial (herdada da bola principal)
        """
        super().__init__(x, y)
        self.x_move = x_move
        self.y_move = y_move
        self.wall_hits = 0  # Contador de colisões com a parede para autodestruição
        self.color = (120, 200, 255)  # Cor azulada para diferenciar
        self.rastro = []  # Rastro independente na cor da bola falsa

    def move(self, ARENA_LEFT=0, ARENA_RIGHT=0, ARENA_TOP=0, ARENA_BOTTOM=0):
        """
        Atualiza a posição da bola falsa e checa colisões com as bordas da arena
        O método é sobrescrito para remover interações complexas.
        """
        # Gerenciamento do rastro (idêntico à classe pai)
        self.rastro.append({'x': self.x, 'y': self.y, 'radius': self.radius, 'alpha': 180, 'color': self.color})
        for r in self.rastro:
            r['radius'] = max(2, r['radius'] * 0.85)
            r['alpha'] = max(0, r['alpha'] - 15)
        self.rastro = [r for r in self.rastro if r['alpha'] > 0 and r['radius'] > 1]
        
        # Movimento
        self.x += self.x_move
        self.y += self.y_move
        
        # Checa colisão com as paredes e incrementa o contador
        if self.y - self.radius < ARENA_TOP or self.y + self.radius > ARENA_BOTTOM:
            self.bounce_y()
            self.wall_hits += 1
        if self.x - self.radius < ARENA_LEFT or self.x + self.radius > ARENA_RIGHT:
            self.bounce_x()
            self.wall_hits += 1



# FUNÇÃO AUXILIAR DE COLISÃO


def colide_barra_giratoria(ball_x, ball_y, ball_radius, center_x, center_y, barra_len, barra_thick, angle):
    """
    Função auxiliar para verificar a colisão entre a bola e a barra giratória

    A lógica funciona rotacionando o sistema de coordenadas para que a barra
    fique alinhada com o eixo X. Nesse novo sistema, a verificação de colisão
    se torna uma simples checagem de limites de um retângulo (AABB).

    Args:
        ball_x (float): Posição X da bola
        ball_y (float): Posição Y da bola
        ball_radius (float): Raio da bola
        center_x (float): Posição X do centro da barra
        center_y (float): Posição Y do centro da barra
        barra_len (float): Comprimento da barra
        barra_thick (float): Espessura da barra
        angle (float): Ângulo de rotação da barra em radianos

    Returns:
        bool: True se houver colisão, False caso contrário
    """
    # Calcula a posição da bola relativa ao centro da barra
    dx = ball_x - center_x
    dy = ball_y - center_y
    
    # Rotaciona as coordenadas da bola pelo ângulo inverso da barra
    # Isso alinha a barra com o eixo horizontal no novo sistema de coordenadas
    rx = dx * math.cos(-angle) - dy * math.sin(-angle)
    ry = dx * math.sin(-angle) + dy * math.cos(-angle)
    
    # Agora, verifica a colisão como se fosse um retângulo não rotacionado
    if abs(rx) < barra_len / 2 + ball_radius and abs(ry) < barra_thick / 2 + ball_radius:
        return True
        
    return False