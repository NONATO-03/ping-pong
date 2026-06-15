"""Garante que config e visual compartilham a MESMA geometria.

Antes da Fase 1, visual.py recalculava WIDTH/HEIGHT e todas as constantes
ARENA_* por conta propria, duplicando config.py. Agora visual importa do config
(fonte unica de verdade). Este teste protege contra a volta da duplicacao.
"""

import config
import visual

# Apenas as constantes que visual.py de fato usa (e portanto importa do config).
GEOMETRIA = [
    "WIDTH", "HEIGHT",
    "ARENA_W", "ARENA_H", "ARENA_X", "ARENA_Y",
    "ARENA_LEFT", "ARENA_TOP", "ARENA_BOTTOM",
    "ARENA_CENTER_X",
]


def test_visual_usa_geometria_do_config():
    for nome in GEOMETRIA:
        assert getattr(visual, nome) == getattr(config, nome), nome


def test_carregar_fruta_images_removido():
    # Funcao morta (visual.get_fruit_image cuida das imagens de fruta).
    assert not hasattr(config, "carregar_fruta_images")
