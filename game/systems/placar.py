import time

class Placar:
    def __init__(self):
        self.l_score = 0
        self.r_score = 0
        self.start_time = time.time()

    def l_point(self, pontos=1):
        self.l_score += pontos

    def r_point(self, pontos=1):
        self.r_score += pontos

    def check_winner(self):
        if self.l_score >= 20:
            return "Jogador Esquerda"
        elif self.r_score >= 20:
            return "Jogador Direita"
        return None
    