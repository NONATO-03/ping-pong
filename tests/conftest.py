"""Configuracao compartilhada dos testes.

Forca o pygame a usar os drivers "dummy" do SDL, para que seja possivel
importar o jogo e exercitar a logica pura sem um display ou dispositivo de
audio reais (necessario em CI / execucao headless). As variaveis precisam
ser definidas ANTES de qualquer ``import pygame``.
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
