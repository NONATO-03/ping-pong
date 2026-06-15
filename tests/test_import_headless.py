"""Smoke test: garante que os modulos centrais importam sem display/audio reais.

Hoje ``config`` chama ``pygame.init()`` e carrega imagens no momento do import
(efeito colateral). Com os drivers "dummy" do SDL (ver conftest.py) isso deve
funcionar em ambiente headless. Quando a Fase 1 remover esses efeitos de import,
este teste continua valido como protecao contra regressao.
"""


def test_config_importa_headless():
    import config

    # Constantes de geometria devem existir e ser coerentes.
    assert config.ARENA_W > 0
    assert config.ARENA_H > 0
    assert config.ARENA_RIGHT > config.ARENA_LEFT


def test_definicoes_de_poderes_consistentes():
    import config

    # Toda fruta com timer precisa ter cor e texto associados.
    for fruta in config.POWER_TOTAL_TIMER:
        assert fruta in config.POWER_COLORS
        assert fruta in config.POWER_TEXTS
