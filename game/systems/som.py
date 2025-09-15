import pygame
import os
import random

# CLASSE DE SOM
# Esta classe é responsável por gerenciar todos os áudios do jogo

class SistemaDeSom:
    # --- Método Construtor (__init__) ---
    # O construtor é executado automaticamente quando um novo objeto SistemaDeSom é criado
    # Sua função é inicializar o sistema de áudio e pré-carregar todos os sons necessários
    def __init__(self):
        # Inicializa todos os módulos do mixer do Pygame. 
        pygame.mixer.init()

        # --- Dicionários de Áudio ---
        # `self.sons` armazena os objetos de som (SFX) já carregados para acesso rápido
        # evitando carregar o mesmo arquivo do disco várias vezes
        self.sons = {}

        # --- Construção de Caminhos (Paths) ---
        # Define o caminho absoluto para a pasta 'assets'. Isso garante que o programa
        # encontre os arquivos de áudio, não importa de onde o script seja executado
        # `os.path.dirname(__file__)` pega o diretório do arquivo atual (som.py)
        # `os.path.join('..', '..', 'assets')` volta duas pastas e entra em 'assets'
        self.assets_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..', 'assets')
        )

        # Caminhos para as pastas específicas de música e efeitos sonoros
        self.music_path_folder = os.path.join(self.assets_path, 'music')
        self.sfx_path_folder = os.path.join(self.assets_path, 'sfx')

        # Listas de Músicas 
        # Agrupar as músicas em listas facilita a seleção aleatória
        self.musicas_menu = [
            os.path.join(self.music_path_folder, 'musica_menu.wav'),
            os.path.join(self.music_path_folder, 'musica_menu_2.wav')
        ]
        self.musicas_fundo = [
            os.path.join(self.music_path_folder, 'musica.wav'),
            os.path.join(self.music_path_folder, 'musica_2.wav'),
            os.path.join(self.music_path_folder, 'musica_3.wav'),
            os.path.join(self.music_path_folder, 'musica_4.wav'),
            os.path.join(self.music_path_folder, 'musica_5.wav'),
            os.path.join(self.music_path_folder, 'musica_6.wav')
        ]
        self.musicas_tempo_acabando = [
            os.path.join(self.music_path_folder, 'musica_tempo_acabando_1.wav'),
            os.path.join(self.music_path_folder, 'musica_tempo_acabando_2.wav'),
            os.path.join(self.music_path_folder, 'musica_tempo_acabando_3.wav')
        ]

        # Carregamento dos Efeitos Sonoros
        # Dicionário 
        efeitos_sonoros = {
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
            'tempo_parando': 'som_tempo_parando.wav',
            'tempo_voltando': 'som_tempo_voltando.wav',
            'click': 'som_click.wav' 
        }

        # Itera sobre o dicionário para carregar cada efeito sonoro
        for nome, arquivo in efeitos_sonoros.items():
            caminho_completo = os.path.join(self.sfx_path_folder, arquivo)
            # Verifica se o arquivo de som realmente existe antes de tentar carregá-lo
            if os.path.exists(caminho_completo):
                # Carrega o som e o armazena no dicionário `self.sons`
                self.sons[nome] = pygame.mixer.Sound(caminho_completo)
            else:
                # Se o arquivo não for encontrado, exibe uma mensagem de erro no console
                print(f"AVISO: Som '{nome}' não encontrado no caminho: {caminho_completo}")

        # Configuração de Volumes Padrão
        # Define um volume padrão de 5% para todos os efeitos sonoros
        for sfx in self.sons.values():
            sfx.set_volume(0.05)

    # Métodos de Controle de Efeitos Sonoros 
    # Cada método toca um som específico. O nome do método descreve a ação

    def play_som_habilidade_desaparece(self):
        if 'desaparece' in self.sons: self.sons['desaparece'].play()

    def play_som_habilidade_coletada(self):
        if 'coleta' in self.sons: self.sons['coleta'].play()


    def play_som_parede(self):
        if 'parede' in self.sons: self.sons['parede'].play()

    def play_som_coletar_fruta(self):
        if 'coletar_fruta' in self.sons: self.sons['coletar_fruta'].play()

    def play_som_raquete(self):
        if 'raquete' in self.sons: self.sons['raquete'].play()

    def play_som_pontuacao(self):
        if 'pontuacao' in self.sons: self.sons['pontuacao'].play()

    def play_som_tiro_poderoso(self):
        if 'poder_amarelo' in self.sons: self.sons['poder_amarelo'].play()

    def play_som_acabar_poder(self):
        if 'acabar_poder' in self.sons: self.sons['acabar_poder'].play()

    def play_som_fim_jogo(self):
        if 'fim_jogo' in self.sons: self.sons['fim_jogo'].play()

    def play_som_menu_selecao(self):
        if 'menu_selecao' in self.sons: self.sons['menu_selecao'].play()

    def play_som_click(self):
        if 'click' in self.sons: self.sons['click'].play()

    # Métodos de Controle de Músicas de Fundo 
    # As músicas usam o canal de música do Pygame (`pygame.mixer.music`)
    # que é diferente dos canais de SFX e só pode tocar um áudio por vez

    def play_musica_menu(self, volume=0.1):
        """
        Toca uma música aleatória para o menu principal em loop
        O volume padrão é 0.31(31%)
        """
        pygame.mixer.music.stop() # Garante que qualquer música anterior pare
        musica_escolhida = random.choice(self.musicas_menu)
        pygame.mixer.music.load(musica_escolhida)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1) # O argumento -1 faz a música tocar em loop

    def play_musica_fundo(self, volume=0.1):
        """
        Toca uma música aleatória durante o jogo em loop
        O volume padrão é 0.1 (10%)
        """
        pygame.mixer.music.stop()
        musica_escolhida = random.choice(self.musicas_fundo)
        pygame.mixer.music.load(musica_escolhida)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)

    def play_musica_tempo_acabando(self, volume=0.1):
        """
        Toca uma música de tensão quando o tempo está acabando
        O volume padrão é 0.1 (10%)
        """
        pygame.mixer.music.stop()
        musica_escolhida = random.choice(self.musicas_tempo_acabando)
        pygame.mixer.music.load(musica_escolhida)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)

    def stop_musica_fundo(self):
        """Para qualquer música que estiver tocando"""
        pygame.mixer.music.stop()

    def stop_musica_menu(self):
        """Para qualquer música que estiver tocando"""
        pygame.mixer.music.stop()

    def stop_musica_tempo_acabando(self):
        """Para qualquer música que estiver tocando"""
        pygame.mixer.music.stop()

    def fadeout_musica(self, tempo_ms=2000):
        """
        Para a música gradualmente ao longo de um período de tempo
        `tempo_ms` é o tempo em milissegundos para o fade out (padrão: 2 segundos)
        """
        pygame.mixer.music.fadeout(tempo_ms)