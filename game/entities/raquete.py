import time
import math
import pygame

class Raquete:
    def __init__(self, x, y, is_left_paddle=False):
        self.x = x
        self.y = y
        self.width = 28
        self.height = 120
        self.base_height = 120
        self.color = (255,255,255)
        self.glow = (255,255,255,80)
        self.move_speed = 20
        self.is_left_paddle = is_left_paddle
        self.is_moving_up = False
        self.is_moving_down = False
        self.power_ups = {
            "uva": False,
            "melancia": False,
            "banana": False,
            "morango": False,
            "blueberry": False
        }
        self.active_power_ups = {}
        self.espelhada = None
        self.power_used = False
        self.shake_time = 0
        self.shake_offset = 0
        self.last_move_dir = 0
        self.trail = []

    def draw(self, screen):
        # Shake/gelatina ao parar
        shake = 0
        if self.shake_time and time.time() - self.shake_time < 0.25:
            shake = math.sin((time.time() - self.shake_time)*20) * 8
        rect = pygame.Rect(self.x - self.width//2, self.y - self.height//2 + shake, self.width, self.height)
        pygame.draw.rect(screen, self.color, rect, border_radius=8)

        # Rastro animado
        for t in self.trail:
            alpha = int(120 * (1 - (time.time() - t["time"])/0.3))
            trail_surf = pygame.Surface((self.width, 24), pygame.SRCALPHA)
            pygame.draw.rect(trail_surf, t["color"] + (alpha,), trail_surf.get_rect(), border_radius=8)
            trail_x = self.x - self.width//2
            trail_y = t["y"] - 12
            screen.blit(trail_surf, (trail_x, trail_y))

    def update_trail(self, dir):
        # Adiciona rastro conforme direção
        color = (180,180,255) if self.is_left_paddle else (255,180,180)
        offset = -self.height//2-10 if dir == -1 else self.height//2+10 if dir == 1 else 0
        if dir != 0:
            self.trail.append({
                "x": self.x,
                "y": self.y + offset,
                "dir": dir,
                "time": time.time(),
                "color": color
            })
        # Limita tamanho do rastro
        self.trail = [t for t in self.trail if time.time() - t["time"] < 0.3]

    def start_move_up(self):
        self.is_moving_up = True

    def stop_move_up(self):
        self.is_moving_up = False

    def start_move_down(self):
        self.is_moving_down = True

    def stop_move_down(self):
        self.is_moving_down = False

    def move(self, arena_top, arena_bottom):
        moved = False
        dir = 0
        if self.is_moving_up:
            if self.y - self.height//2 > arena_top + 8:
                self.y -= self.move_speed
                moved = True
                dir = -1
            else:
                self.y = arena_top + self.height//2 + 8
        elif self.is_moving_down:
            if self.y + self.height//2 < arena_bottom - 8:
                self.y += self.move_speed
                moved = True
                dir = 1
            else:
                self.y = arena_bottom - self.height//2 - 8

        # Detecta parada para iniciar shake
        if not moved and self.last_move_dir != 0:
            self.shake_time = time.time()
        self.last_move_dir = dir

        # Atualiza rastro
        self.update_trail(dir)

    def activate_power_up(self, power_up_type):
        # Desativa outros poderes
        for other_power in list(self.power_ups.keys()):
            if self.power_ups[other_power] and other_power != power_up_type:
                self.deactivate_power_up(other_power)
        self.power_ups[power_up_type] = True
        self.active_power_ups[power_up_type] = time.time()
        if power_up_type == "uva":
            self.height = 160
        else:
            self.height = self.base_height

    def deactivate_power_up(self, power_up_type):
        self.power_ups[power_up_type] = False
        if power_up_type in self.active_power_ups:
            del self.active_power_ups[power_up_type]
        self.height = self.base_height

    def get_power(self):
        for k, v in self.power_ups.items():
            if v:
                return k
        return None
    
    def get_power_time_left(self):
        power = self.get_power()
        if not power or power not in self.active_power_ups:
            return None
        time_left = 20 - (time.time() - self.active_power_ups[power])
        return max(0, time_left)

    def update_power(self):
        power = self.get_power()
        if not power:
            return
        time_left = self.get_power_time_left()
        if power in ["banana", "morango"] and self.power_used:
            self.deactivate_power_up(power)
            self.power_used = False
        elif time_left is not None and time_left <= 0:
            self.deactivate_power_up(power)
            self.power_used = False