import pygame
import os
import random

class SistemaDeSom:
    def __init__(self):
        self.sons = {}
        pygame.mixer.init()
        self.assets_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..', 'assets')
        )
        self.music_path = os.path.join(self.assets_path, 'music', 'musica.wav')
        self.menu_music_path = os.path.join(self.assets_path, 'music', 'musica_menu.wav')
        self.sfx_path = os.path.join(self.assets_path, 'sfx')
        self.music_path_2 = os.path.join(self.assets_path, 'music', 'musica_2.wav')
        self.music_tempo_acabando_1 = os.path.join(self.assets_path, 'music', 'musica_tempo_acabando_1.wav')
        self.music_tempo_acabando_2 = os.path.join(self.assets_path, 'music', 'musica_tempo_acabando_2.wav')

    

        # Carrega todos os efeitos
        efeitos = {
            'desaparece': 'som_poder_desaparece.wav',
            'coleta': 'som_coleta.wav',
            'parede': 'som_parede.wav',
            'raquete': 'som_raquete.wav',
            'coletar_fruta': 'som_coletar_fruta.wav',
            'pontuacao': 'som_pontuacao.wav',
            'poder_amarelo': 'som_poder_amarelo.wav',
            'acabar_poder': 'som_acabar_poder.wav',
            'fim_jogo': 'fim_jogo.wav',
            'menu_selecao': 'som_menu_selecao.wav',
            'queimando': 'queimando.wav',
            'tempo_parando': 'som_tempo_parando.wav',
            'tempo_voltando': 'som_tempo_voltando.wav'
        }
        for nome, arquivo in efeitos.items():
            caminho = os.path.join(self.sfx_path, arquivo)
            if os.path.exists(caminho):
                self.sons[nome] = pygame.mixer.Sound(caminho)
                if nome == 'queimando':
                    self.sons[nome].set_volume(0.2)
            else:
                print(f"Som '{nome}' não encontrado: {caminho}")

    def play_som_habilidade_desaparece(self):
        self.sons['desaparece'].play()

    def play_som_habilidade_coletada(self):
        self.sons['coleta'].play()

    def play_som_queimando(self):
        self.sons['queimando'].play(-1)  # loop infinito

    def stop_som_queimando(self):
        self.sons['queimando'].stop()

    def play_musica_menu(self, volume=1.0):
        pygame.mixer.music.stop() 
        pygame.mixer.music.load(self.menu_music_path)
        pygame.mixer.music.set_volume(0.6)
        pygame.mixer.music.play(-1)

    def stop_musica_menu(self):
        pygame.mixer.music.stop()    

    def play_som_tempo_parando(self):
        self.sons['tempo_parando'].play()

    def play_som_tempo_voltando(self):
        self.sons['tempo_voltando'].play()

    def play_som_parede(self):
        self.sons['parede'].play()

    def play_som_coletar_fruta(self):
        self.sons['coletar_fruta'].play()

    def play_som_raquete(self):
        self.sons['raquete'].play()

    def play_som_pontuacao(self):
        self.sons['pontuacao'].play()

    def play_som_tiro_poderoso(self):
        self.sons['poder_amarelo'].play()

    def play_som_acabar_poder(self):
        self.sons['acabar_poder'].play()

    def play_som_fim_jogo(self):
        self.sons['fim_jogo'].play()

    def play_som_menu_selecao(self):
        self.sons['menu_selecao'].play()

    def play_musica_fundo(self, volume=1.0):
        # Escolhe aleatoriamente entre musica.wav e musica_2.wav
        music_choice = random.choice([self.music_path, self.music_path_2])
        pygame.mixer.music.load(music_choice)
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)

    def stop_musica_fundo(self):
        pygame.mixer.music.stop()

    def play_musica_tempo_acabando(self, volume=1.0):
        # Escolhe aleatoriamente entre as duas músicas de tempo acabando
        music_choice = random.choice([self.music_tempo_acabando_1, self.music_tempo_acabando_2])
        pygame.mixer.music.load(music_choice)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)

    def fadeout_musica(self, ms=2000):
        pygame.mixer.music.fadeout(ms)