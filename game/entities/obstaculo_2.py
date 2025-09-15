import pygame
import math

class ObstaculoCruz:
    """
    Representa um obstáculo em forma de cruz na arena delta
    Gerencia a rotação e a colisão com a bola
    """

    def __init__(self, x, y, size=80):
        """Inicializa o obstáculo com a posição, tamanho e velocidade de rotação"""
        self.x = x
        self.y = y
        self.size = size
        self.angle = 0  # Angulo de rotação em graus
        self.rotation_speed = 1  # Velocidade de rotação em graus por frame
        self.color = (200, 200, 200)  # Cor do obstáculo
        self.segments = []  # Segmentos que formam a cruz
        self.create_segments()

    def create_segments(self):
        """Cria os dois retangulos que formam a cruz"""
        self.segments = [
            # Retângulo horizontal
            pygame.Rect(self.x - self.size / 2, self.y - self.size / 8, self.size, self.size / 4),
            # Retângulo vertical
            pygame.Rect(self.x - self.size / 8, self.y - self.size / 2, self.size / 4, self.size)
        ]

    def rotate(self):
        """Atualiza o ângulo de rotação do obstáculo"""
        self.angle += self.rotation_speed
        if self.angle >= 360:
            self.angle -= 360

    def draw(self, screen):
        """Desenha o obstáculo na tela com a rotação aplicada"""
        for segment in self.segments:
            temp_surface = pygame.Surface(segment.size, pygame.SRCALPHA)
            pygame.draw.rect(temp_surface, self.color, (0, 0, segment.width, segment.height))
            temp_surface = pygame.transform.rotate(temp_surface, self.angle)
            rotated_rect = temp_surface.get_rect(center=segment.center)
            screen.blit(temp_surface, rotated_rect.topleft)

    def check_collision(self, ball):
        """
        Verifica a colisão da bola com o obstáculo
        Se houver colisão, ajusta a posição da bola e inverte sua direção
        Retorna True se houve colisão, False caso contrário
        """
        # Posição da bola em relação ao centro do obstáculo
        rel_x = ball.x - self.x
        rel_y = ball.y - self.y

        # Rotação inversa da bola para o sistema de coordenadas do obstáculo
        rad_angle = math.radians(-self.angle)
        rot_x = rel_x * math.cos(rad_angle) - rel_y * math.sin(rad_angle)
        rot_y = rel_x * math.sin(rad_angle) + rel_y * math.cos(rad_angle)

        # Retângulos do obstáculo em seu sistema de coordenadas local
        local_segments = [
            pygame.Rect(-self.size / 2, -self.size / 8, self.size, self.size / 4),
            pygame.Rect(-self.size / 8, -self.size / 2, self.size / 4, self.size)
        ]

        # Checa colisão com cada segmento
        for segment in local_segments:
            if segment.collidepoint(rot_x, rot_y):
                # Encontrou o segmento de colisão
                
                # Encontra o ponto de colisão e a direção de rebote
                # Baseado na distância do centro do segmento
                dx = abs(rot_x - segment.centerx) - segment.width / 2
                dy = abs(rot_y - segment.centery) - segment.height / 2
                
                if dx > dy:
                    # Colisão horizontal
                    ball.x_move *= -1
                else:
                    # Colisão vertical 
                    ball.y_move *= -1

                # Reverte a rotação para a posição original
                inv_rad_angle = math.radians(self.angle)
                new_rel_x = rot_x * math.cos(inv_rad_angle) - rot_y * math.sin(inv_rad_angle)
                new_rel_y = rot_x * math.sin(inv_rad_angle) + rot_y * math.cos(inv_rad_angle)

                # Ajusta a posição da bola para que ela não fique presa
                ball.x = self.x + new_rel_x
                ball.y = self.y + new_rel_y

                # Retorna True para indicar que a colisão aconteceu
                return True

        # Se não houve colisão com nenhum segmento, retorna False
        return False
        
    def dist_point_to_line(self, px, py, x1, y1, x2, y2):
        # Função que ajuda a calcular uma distanciaa do ponto até a linha de segment
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0 and dy == 0:
            return math.sqrt((px - x1)**2 + (py - y1)**2)
        
        t = ((px - x1) * dx + (py - y1) * dy) / (dx**2 + dy**2)
        
        if t < 0:
            closest_x, closest_y = x1, y1
        elif t > 1:
            closest_x, closest_y = x2, y2
        else:
            closest_x = x1 + t * dx
            closest_y = y1 + t * dy
            
        return math.sqrt((px - closest_x)**2 + (py - closest_y)**2)

    def bounce_ball(self, ball, obstacle_angle):
        # Calcula o vetor normal para a superficie do obstaculo
        normal_angle = obstacle_angle + math.pi/2
        normal_x = math.cos(normal_angle)
        normal_y = math.sin(normal_angle)
        
        
        dot_product = ball.x_move * normal_x + ball.y_move * normal_y
        
        # Velocidade do vetor
        ball.x_move -= 2 * dot_product * normal_x
        ball.y_move -= 2 * dot_product * normal_y
        
        # Normaliza a nova velocidade para manter
        current_speed = math.sqrt(ball.x_move**2 + ball.y_move**2)
        factor = ball.base_speed / current_speed
        ball.x_move *= factor
        ball.y_move *= factor