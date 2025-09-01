class BotController:
    def __init__(self, paddle, ball, arena_top, arena_bottom):
        self.paddle = paddle
        self.ball = ball
        self.arena_top = arena_top
        self.arena_bottom = arena_bottom

    def update(self):
        # Movimento suave: aproxima a raquete da bola
        target_y = self.ball.y
        # Limita target_y para não ultrapassar a arena
        min_y = self.arena_top + self.paddle.height // 2 + 8
        max_y = self.arena_bottom - self.paddle.height // 2 - 8
        target_y = max(min_y, min(max_y, target_y))

        diff = target_y - self.paddle.y
        speed = self.paddle.move_speed
        if abs(diff) > speed:
            if diff > 0:
                self.paddle.is_moving_up = False
                self.paddle.is_moving_down = True
            else:
                self.paddle.is_moving_down = False
                self.paddle.is_moving_up = True
        else:
            self.paddle.is_moving_up = False
            self.paddle.is_moving_down = False
            self.paddle.y = target_y  # Centraliza se estiver perto