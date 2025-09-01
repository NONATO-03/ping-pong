import random
import time
from visual import ARENA_LEFT, ARENA_RIGHT, ARENA_TOP, ARENA_BOTTOM, ARENA_CENTER_X, ARENA_CENTER_Y

class Habilidade:
    def __init__(self, cor, tipo_habilidade):
        fruta_radius = 28
        self.x = ARENA_CENTER_X
        self.y = ARENA_CENTER_Y
        self.x_move = random.choice([-7, 7])
        self.y_move = random.choice([-7, 7])
        self.cor = cor
        self.tipo_habilidade = tipo_habilidade
        self.radius = fruta_radius

    def move(self):
        self.x += self.x_move
        self.y += self.y_move
        if self.x - self.radius <= ARENA_LEFT or self.x + self.radius >= ARENA_RIGHT:
            self.bounce_x()
            self.x = max(ARENA_LEFT + self.radius, min(self.x, ARENA_RIGHT - self.radius))
        if self.y - self.radius <= ARENA_TOP or self.y + self.radius >= ARENA_BOTTOM:
            self.bounce_y()
            self.y = max(ARENA_TOP + self.radius, min(self.y, ARENA_BOTTOM - self.radius))

    def bounce_x(self):
        self.x_move *= -1

    def bounce_y(self):
        self.y_move *= -1

    def reset_position(self):
        self.x = 1000
        self.y = 1000

class GerenciadorHabilidades:
    def __init__(self, power_colors, max_frutas=1, spawn_interval=20):
        self.power_colors = power_colors
        self.max_frutas = max_frutas
        self.spawn_interval = spawn_interval
        self.frutas = []
        self.last_spawn = time.time()

    def update(self):
        # Move todas as frutas
        for fruta in self.frutas:
            fruta.move()
        # Spawn de frutas
        now = time.time()
        if len(self.frutas) < self.max_frutas and (now - self.last_spawn) > self.spawn_interval:
            tipo = random.choice(list(self.power_colors.keys()))
            cor = self.power_colors[tipo][0]
            self.frutas.append(Habilidade(cor, tipo))
            self.last_spawn = now

    def reset(self):
        self.frutas.clear()
        self.last_spawn = time.time()

    def remover_fruta(self, fruta):
        if fruta in self.frutas:
            self.frutas.remove(fruta)