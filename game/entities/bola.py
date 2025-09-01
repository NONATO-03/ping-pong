import math
import time

class Bola:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 14
        self.color = (255,255,255)
        self.base_speed = 3
        self.x_move = self.base_speed
        self.y_move = self.base_speed
        self.rastro = []
        self.incremento_raquetada = 0.2
        self.last_hit_by = None
        self.spawn_time = time.time()
        self.raquetadas_consecutivas = 0
        self.fogo_ativo = False
        self.queimando_audio_tocando = False

    def move(self, fan_angle=None, mapa_escolhido=0, center_x=0, center_y=0):
        self.rastro.append({'x': self.x, 'y': self.y, 'radius': self.radius, 'alpha': 180, 'color': self.color})
        for r in self.rastro:
            r['radius'] = max(2, r['radius'] * 0.85)
            r['alpha'] = max(0, r['alpha'] - 15)
        self.rastro = [r for r in self.rastro if r['alpha'] > 0 and r['radius'] > 1]
        self.x += self.x_move
        self.y += self.y_move
        if mapa_escolhido == 1 and fan_angle is not None:
            if time.time() - self.spawn_time > 1:
                if colide_barra_giratoria(self.x, self.y, self.radius, center_x, center_y, 170, 18, fan_angle):
                    dx = self.x - center_x
                    dy = self.y - center_y
                    barra_dx = math.cos(fan_angle)
                    barra_dy = math.sin(fan_angle)
                    if abs(dx * barra_dx) > abs(dy * barra_dy):
                        self.bounce_x()
                    else:
                        self.bounce_y()

    def bounce_y(self):
        self.y_move *= -1

    def bounce_x(self):
        self.x_move *= -1

    def reset_position(self, center_x, center_y, tempo_passado=0):
        self.atualizar_velocidade(tempo_passado)
        self.x = center_x
        self.y = center_y
        import random
        self.x_move = self.base_speed if random.choice([True, False]) else -self.base_speed
        self.y_move = self.base_speed if random.choice([True, False]) else -self.base_speed
        self.rastro.clear()
        self.spawn_time = time.time()
        self.raquetadas_consecutivas = 0
        self.fogo_ativo = False
        self.queimando_audio_tocando = False

    def atualizar_velocidade(self, tempo_passado):
        self.base_speed = 5 + 1.5 * int(tempo_passado // 60)
        self.incremento_raquetada = 0.2 + 0.1 * int(tempo_passado // 30)

    def aumentar_velocidade_raquetada(self):
        self.raquetadas_consecutivas += 1
        if not self.fogo_ativo and self.raquetadas_consecutivas >= 30:
            self.fogo_ativo = True
        incremento = self.incremento_raquetada
        if self.fogo_ativo:
            incremento += 0.3
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
        mapa_escolhido=0
    ):  
        self.move(
            fan_angle=fan_angle,
            mapa_escolhido=mapa_escolhido,
            center_x=ARENA_CENTER_X,
            center_y=ARENA_CENTER_Y
        )

        # Efeito de fogo
        if self.fogo_ativo:
            if not hasattr(self, "queimando_audio_tocando") or not self.queimando_audio_tocando:
                som.play_som_queimando()
                self.queimando_audio_tocando = True
        else:
            if hasattr(self, "queimando_audio_tocando") and self.queimando_audio_tocando:
                som.stop_som_queimando()
                self.queimando_audio_tocando = False

        # Move e remove bolas falsas (blueberry)
        for fake in fake_balls[:]:
            fake.move(ARENA_LEFT=ARENA_LEFT, ARENA_RIGHT=ARENA_RIGHT, ARENA_TOP=ARENA_TOP, ARENA_BOTTOM=ARENA_BOTTOM)
            if fake.wall_hits >= 9: # bater até sumir
                fake_balls.remove(fake)
                som.play_som_habilidade_desaparece()

        # Rebater nas bordas
        if self.y - 8 < ARENA_TOP + 5 or self.y + 8 > ARENA_BOTTOM - 5:
            self.bounce_y()
            som.play_som_parede()

        # Marcar ponto esquerda/direita
        if self.x - 8 < ARENA_LEFT + 5:
            if self.last_hit_by == "right" and r_paddle.get_power() == "morango":
                placar.r_score += 3
            else:
                placar.r_score += 1
            som.play_som_pontuacao()
            self.color = (255,255,255)
            for r in self.rastro:
                r['color'] = (255,255,255)
            self.rastro = []
            self.reset_position(ARENA_CENTER_X, ARENA_CENTER_Y, tempo_passado)
            som.stop_som_queimando()
            self.queimando_audio_tocando = False

        elif self.x + 8 > ARENA_RIGHT - 5:
            if self.last_hit_by == "left" and l_paddle.get_power() == "morango":
                placar.l_score += 3
            else:
                placar.l_score += 1
            som.play_som_pontuacao()
            self.color = (255,255,255)
            for r in self.rastro:
                r['color'] = (255,255,255)
            self.rastro = []
            self.reset_position(ARENA_CENTER_X, ARENA_CENTER_Y, tempo_passado)
            som.stop_som_queimando()
            self.queimando_audio_tocando = False

        # Colisão com raquete esquerda (principal)
        if (self.x - self.radius <= l_paddle.x + l_paddle.width//2 and
            self.x + self.radius >= l_paddle.x - l_paddle.width//2 and
            l_paddle.y - l_paddle.height//2 <= self.y <= l_paddle.y + l_paddle.height//2):
            self.x = l_paddle.x + l_paddle.width//2 + self.radius
            self.aumentar_velocidade_raquetada()
            power = l_paddle.get_power()
            if power == "morango":
                self.color = (255,0,0)
                for r in self.rastro:
                    r['color'] = (255,0,0)
            else:
                self.color = (255,255,255)
                for r in self.rastro:
                    r['color'] = (255,255,255)
            if power == "blueberry":
                fake_balls.append(BolaFake(self.x, self.y, self.x_move, self.y_move))
                som.play_som_habilidade_coletada()
            if power == "banana" and not r_paddle.power_used:
                som.play_som_tiro_poderoso()
            else:
                som.play_som_raquete()
            self.bounce_x()
            self.last_hit_by = "left"
            impact_left = True
            if power == "banana" and not l_paddle.power_used:
                self.x_move *= 10
                self.y_move *= 10
                l_paddle.power_used = True
        else:
            impact_left = False

        # Colisão com raquete espelhada esquerda (melancia)
        if l_paddle.get_power() == "melancia":
            espelhada_y = ARENA_BOTTOM - (l_paddle.y - ARENA_TOP)
            if (self.x - self.radius <= l_paddle.x + l_paddle.width//2 and
                self.x + self.radius >= l_paddle.x - l_paddle.width//2 and
                espelhada_y - l_paddle.height//2 <= self.y <= espelhada_y + l_paddle.height//2):
                self.x = l_paddle.x + l_paddle.width//2 + self.radius
                self.aumentar_velocidade_raquetada()
                if l_paddle.get_power() == "blueberry":
                    fake_balls.append(BolaFake(self.x, self.y, self.x_move, self.y_move))
                    som.play_som_habilidade_coletada()
                self.bounce_x()
                self.last_hit_by = "left"
                impact_left = True
                som.play_som_raquete()

        # Colisão com raquete direita (principal)
        if (self.x - self.radius <= r_paddle.x + r_paddle.width//2 and
            self.x + self.radius >= r_paddle.x - r_paddle.width//2 and
            r_paddle.y - r_paddle.height//2 <= self.y <= r_paddle.y + r_paddle.height//2):
            self.x = r_paddle.x - r_paddle.width//2 - self.radius
            self.aumentar_velocidade_raquetada()
            power = r_paddle.get_power()
            if power == "morango":
                self.color = (255,0,0)
                for r in self.rastro:
                    r['color'] = (255,0,0)
            else:
                self.color = (255,255,255)
                for r in self.rastro:
                    r['color'] = (255,255,255)
            if power == "blueberry":
                fake_balls.append(BolaFake(self.x, self.y, self.x_move, self.y_move))
                som.play_som_habilidade_coletada()
            if power == "banana" and not r_paddle.power_used:
                som.play_som_tiro_poderoso()
            else:
                som.play_som_raquete()
            self.bounce_x()
            self.last_hit_by = "right"
            impact_right = True
            if power == "banana" and not r_paddle.power_used:
                self.x_move *= 10
                self.y_move *= 10
                r_paddle.power_used = True
        else:
            impact_right = False

        # Colisão com raquete espelhada direita (melancia)
        if r_paddle.get_power() == "melancia":
            espelhada_y = ARENA_BOTTOM - (r_paddle.y - ARENA_TOP)
            if (self.x - self.radius <= r_paddle.x + r_paddle.width//2 and
                self.x + self.radius >= r_paddle.x - r_paddle.width//2 and
                espelhada_y - r_paddle.height//2 <= self.y <= espelhada_y + r_paddle.height//2):
                self.x = r_paddle.x - r_paddle.width//2 - self.radius
                self.aumentar_velocidade_raquetada()
                if r_paddle.get_power() == "blueberry":
                    fake_balls.append(BolaFake(self.x, self.y, self.x_move, self.y_move))
                    som.play_som_habilidade_coletada()
                self.bounce_x()
                self.last_hit_by = "right"
                impact_right = True
                som.play_som_raquete()

        return impact_left, impact_right

class BolaFake(Bola):
    def __init__(self, x, y, x_move, y_move):
        super().__init__(x, y)
        self.x_move = x_move
        self.y_move = y_move
        self.wall_hits = 0
        self.color = (120, 200, 255)
        self.rastro = []

    def move(self, ARENA_LEFT=0, ARENA_RIGHT=0, ARENA_TOP=0, ARENA_BOTTOM=0):
        self.rastro.append({'x': self.x, 'y': self.y, 'radius': self.radius, 'alpha': 180, 'color': self.color})
        for r in self.rastro:
            r['radius'] = max(2, r['radius'] * 0.85)
            r['alpha'] = max(0, r['alpha'] - 15)
        self.rastro = [r for r in self.rastro if r['alpha'] > 0 and r['radius'] > 1]
        self.x += self.x_move
        self.y += self.y_move
        if self.y - self.radius < ARENA_TOP or self.y + self.radius > ARENA_BOTTOM:
            self.bounce_y()
            self.wall_hits += 1
        if self.x - self.radius < ARENA_LEFT or self.x + self.radius > ARENA_RIGHT:
            self.bounce_x()
            self.wall_hits += 1

def colide_barra_giratoria(ball_x, ball_y, ball_radius, center_x, center_y, barra_len, barra_thick, angle):
    dx = ball_x - center_x
    dy = ball_y - center_y
    rx = dx * math.cos(-angle) - dy * math.sin(-angle)
    ry = dx * math.sin(-angle) + dy * math.cos(-angle)
    if abs(rx) < barra_len//2 + ball_radius and abs(ry) < barra_thick//2 + ball_radius:
        return True
    return False