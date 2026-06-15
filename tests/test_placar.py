"""Testes da logica pura do placar (sem dependencia de pygame)."""

from game.systems.placar import Placar


def test_placar_comeca_zerado():
    placar = Placar()
    assert placar.l_score == 0
    assert placar.r_score == 0


def test_pontuacao_acumula():
    placar = Placar()
    placar.l_point()
    placar.l_point(2)
    placar.r_point()
    assert placar.l_score == 3
    assert placar.r_score == 1


def test_sem_vencedor_no_inicio():
    assert Placar().check_winner() is None


def test_vencedor_esquerda_aos_20():
    placar = Placar()
    placar.l_point(20)
    assert placar.check_winner() == "Jogador Esquerda"


def test_vencedor_direita_aos_20():
    placar = Placar()
    placar.r_point(20)
    assert placar.check_winner() == "Jogador Direita"
