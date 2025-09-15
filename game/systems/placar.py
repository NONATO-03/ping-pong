
import time

# CLASSE DO PLACAR


class Placar:
    """
    Gerencia a pontuação dos jogadores e verifica as condições de vitória.
    """

    def __init__(self):
        """
        Inicializa o placar com as pontuações zeradas.
        """
        self.l_score = 0  # Pontuação do jogador da esquerda
        self.r_score = 0  # Pontuação do jogador da direita
        # A variável 'start_time' é inicializada mas não é utilizada no restante da classe
        self.start_time = time.time()

    def l_point(self, pontos=1):
        """
        Adiciona pontos ao jogador da esquerda

        Args:
            pontos (int): O número de pontos a serem adicionados (padrão é 1)
        """
        self.l_score += pontos

    def r_point(self, pontos=1):
        """
        Adiciona pontos ao jogador da direita

        Args:
            pontos (int): O número de pontos a serem adicionados (padrão é 1)
        """
        self.r_score += pontos

    def check_winner(self):
        """
        Verifica se algum jogador atingiu a pontuação necessária para vencer

        Returns:
            str or None: O nome do vencedor ("Jogador Esquerda" ou "Jogador Direita")
                         se a condição de vitória for atingida, ou None caso contrário
        """
        if self.l_score >= 20:
            return "Jogador Esquerda"
        elif self.r_score >= 20:
            return "Jogador Direita"
        return None  # Retorna None se ninguém venceu ainda