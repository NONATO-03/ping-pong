
# CLASSE DO CONTROLE DO BOT


class BotController:
    """
    Implementa a inteligência artificial (IA) para controlar uma raquete
    
    A lógica do bot é seguir a posição vertical da bola para tentar interceptá-la
    """

    def __init__(self, paddle, ball, arena_top, arena_bottom):
        """
        Inicializa o controlador do bot.

        Args:
            paddle (Raquete): O objeto da raquete que este bot irá controlar
            ball (Bola): O objeto da bola que o bot irá seguir
            arena_top (int): A coordenada Y do topo da arena
            arena_bottom (int): A coordenada Y da base da arena
        """
        self.paddle = paddle
        self.ball = ball
        self.arena_top = arena_top
        self.arena_bottom = arena_bottom

    def update(self):
        """
        Executa a lógica de decisão do bot a cada frame

        Determina para onde a raquete deve se mover com base na posição da bola
        """
        # Define o alvo vertical (target_y) 
        # Verifica se existe uma "bola extra" ativa e a torna o alvo prioritário
        if hasattr(self.ball, "bola_extra") and self.ball.bola_extra is not None and self.ball.bola_extra.ativo:
            target_y = self.ball.bola_extra.y
        else:
            # Caso contrário, o alvo é a bola principal
            target_y = self.ball.y
        
        #  Limita o movimento da raquete dentro da arena 
        # Calcula as posições verticais mínima e máxima que a raquete pode alcançar
        min_y = self.arena_top + self.paddle.height // 2 + 8
        max_y = self.arena_bottom - self.paddle.height // 2 - 8
        target_y = max(min_y, min(max_y, target_y))

        # Lógica de Movimento 
        # Calcula a distância vertical entre a raquete e o alvo
        diff = target_y - self.paddle.y
        speed = self.paddle.move_speed

        # Se a distância for maior que a velocidade da raquete em um frame,
        # define a direção do movimento.
        if abs(diff) > speed:
            if diff > 0:  # Se o alvo está abaixo da raquete
                self.paddle.is_moving_up = False
                self.paddle.is_moving_down = True
            else:  # Se o alvo está acima da raquete
                self.paddle.is_moving_down = False
                self.paddle.is_moving_up = True
        else:
            # Se a raquete já está perto o suficiente do alvo, para de se mover
            # e "teleporta" para a posição exata para um alinhamento perfeito
            self.paddle.is_moving_up = False
            self.paddle.is_moving_down = False
            self.paddle.y = target_y