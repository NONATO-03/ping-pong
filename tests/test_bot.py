"""Testes da logica do bot (pura, sem pygame).

BotController so segue a posicao vertical do alvo. Usamos stubs simples no lugar
de Raquete/Bola para exercitar a decisao de movimento.
"""

from game.systems.bot import BotController


class RaqueteStub:
    def __init__(self, y, height=80, move_speed=7):
        self.y = y
        self.height = height
        self.move_speed = move_speed
        self.is_moving_up = False
        self.is_moving_down = False


class BolaStub:
    def __init__(self, y):
        self.y = y


def _bot(paddle_y, ball_y, top=0, bottom=500):
    return BotController(RaqueteStub(paddle_y), BolaStub(ball_y), top, bottom)


def test_move_para_baixo_quando_alvo_abaixo():
    bot = _bot(paddle_y=100, ball_y=300)
    bot.update()
    assert bot.paddle.is_moving_down is True
    assert bot.paddle.is_moving_up is False


def test_move_para_cima_quando_alvo_acima():
    bot = _bot(paddle_y=300, ball_y=100)
    bot.update()
    assert bot.paddle.is_moving_up is True
    assert bot.paddle.is_moving_down is False


def test_alinha_quando_perto_do_alvo():
    # Diferenca menor que move_speed: para de mover e alinha exatamente.
    bot = _bot(paddle_y=250, ball_y=252)
    bot.update()
    assert bot.paddle.is_moving_up is False
    assert bot.paddle.is_moving_down is False
    assert bot.paddle.y == 252


def test_alvo_respeita_limites_da_arena():
    # Bola muito abaixo: alvo e limitado para nao sair da arena.
    bot = _bot(paddle_y=100, ball_y=10_000, top=0, bottom=500)
    bot.update()
    # Limite inferior = bottom - height/2 - 8 = 500 - 40 - 8 = 452
    assert bot.paddle.is_moving_down is True


def test_prioriza_bola_extra_quando_ativa():
    paddle = RaqueteStub(y=100)
    ball = BolaStub(y=110)

    class BolaExtra:
        ativo = True
        y = 400

    ball.bola_extra = BolaExtra()
    bot = BotController(paddle, ball, 0, 500)
    bot.update()
    # Deve seguir a bola extra (y=400, abaixo), nao a principal (y=110).
    assert paddle.is_moving_down is True
