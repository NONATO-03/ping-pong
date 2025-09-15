import pygame
import math
import random

# FUNÇOES DE DESENHO DAS ARENAS


def draw_arena_alpha(screen, ARENA_X, ARENA_Y, ARENA_W, ARENA_H):
    """
    Desenha uma arena de Pong padrão
    
    Args:
        screen (pygame.Surface): A superfície da tela onde a arena será desenhada.
        ARENA_X, ARENA_Y, ARENA_W, ARENA_H (int): As dimensoes e posição da arena.
    """
    # Desenha o retângulo externo da arena com uma borda 
    pygame.draw.rect(screen, (255, 255, 255), (ARENA_X, ARENA_Y, ARENA_W, ARENA_H), width=8)
    
    # Calcula o centro horizontal da arena
    center_x = ARENA_X + ARENA_W // 2
    
    # Desenha a linha divisória vertical no meio da arena
    pygame.draw.line(screen, (180, 180, 180), (center_x, ARENA_Y), (center_x, ARENA_Y + ARENA_H), width=6)

def draw_arena_beta(screen, ARENA_X, ARENA_Y, ARENA_W, ARENA_H, angle=0):
    """
    Desenha a arena padrão com uma barra giratória no centro.

    Args:
        screen (pygame.Surface): A superfície da tela.
        ARENA_X, ARENA_Y, ARENA_W, ARENA_H (int): Dimensões e posição da arena.
        angle (float): O ângulo atual da barra giratória em radianos.
    """
    # Desenho da Arena Padrão 
    # Desenha o contorno retangular e a linha central.
    pygame.draw.rect(screen, (255, 255, 255), (ARENA_X, ARENA_Y, ARENA_W, ARENA_H), width=8)
    center_x = ARENA_X + ARENA_W // 2
    center_y = ARENA_Y + ARENA_H // 2
    pygame.draw.line(screen, (180, 180, 180), (center_x, ARENA_Y), (center_x, ARENA_Y + ARENA_H), width=6)

    # Desenho da Barra Giratória 
    barra_len = 170   # Comprimento da barra.
    barra_thick = 18  # Espessura da barra.
    
    # Usa seno e cosseno para calcular as coordenadas x, y das duas extremidades da barra com base no ângulo de rotação
    x1 = center_x - math.cos(angle) * barra_len / 2
    y1 = center_y - math.sin(angle) * barra_len / 2
    x2 = center_x + math.cos(angle) * barra_len / 2
    y2 = center_y + math.sin(angle) * barra_len / 2
    
    # Desenha a linha que representa a barra giratória
    pygame.draw.line(screen, (255, 255, 255), (x1, y1), (x2, y2), barra_thick)

def draw_arena_gamma(screen, ARENA_X, ARENA_Y, ARENA_W, ARENA_H):
    """
    Desenha uma arena com as paredes laterais curvadas para dentro ("barrigas")

    Args:
        screen (pygame.Surface): A superfície da tela
        ARENA_X, ARENA_Y, ARENA_W, ARENA_H (int): Dimensões e posição da arena
    """
    ARENA_BOTTOM = ARENA_Y + ARENA_H
    border_color = (255, 255, 255)
    border_width = 8
    
    # Desenha a curva do lado esquerdo usando um arco, O retângulo do arco é
    # posicionado parcialmente fora da arena para criar a curvatura para dentro
    # Os ângulos 1.57 a 4.71 radianos correspondem a desenhar do sul ao norte no sentido anti-horário
    pygame.draw.arc(screen, border_color, pygame.Rect(ARENA_X - 50, ARENA_Y, 100, ARENA_H), 1.57, 4.71, border_width)
    
    # Desenha a curva do lado direito de forma similar
    # Os ângulos -1.57 a 1.57 radianos correspondem a desenhar do norte ao sul
    pygame.draw.arc(screen, border_color, pygame.Rect(ARENA_X + ARENA_W - 50, ARENA_Y, 100, ARENA_H), -1.57, 1.57, border_width)
    
    # Desenha as bordas superior e inferior retas para fechar a arena
    pygame.draw.line(screen, border_color, (ARENA_X, ARENA_Y), (ARENA_X + ARENA_W, ARENA_Y), border_width)
    pygame.draw.line(screen, border_color, (ARENA_X, ARENA_BOTTOM), (ARENA_X + ARENA_W, ARENA_BOTTOM), border_width)

    # Desenha a linha divisória
    center_x = ARENA_X + ARENA_W // 2
    pygame.draw.line(screen, (180, 180, 180), (center_x, ARENA_Y), (center_x, ARENA_Y + ARENA_H), width=6)

def draw_arena_delta(screen, ARENA_X, ARENA_Y, ARENA_W, ARENA_H):
    """
    Desenha uma arena de Pong com paredes laterais que possuem uma
    depressão retangular no centro, no formato '[ ]'.
    A arena é totalmente fechada.
    """
    # Pensa numa arena díficil de fazer...

    # MODIFICAÇÃO PARA AUMENTAR A LARGURA 
    fator_largura = 1.2
    largura_original = ARENA_W
    ARENA_W = int(ARENA_W * fator_largura)
    # Ajusta a posição X para manter a arena centralizada
    ARENA_X = int(ARENA_X - (ARENA_W - largura_original) / 2)
    # --- FIM DA MODIFICAÇÃO ---

    border_color = (255, 255, 255)
    line_width = 8

    # 1. Desenha as partes simples 
    # Linha divisória central e bordas retas superior/inferior
    center_x = ARENA_X + ARENA_W // 2
    pygame.draw.line(screen, (180, 180, 180), (center_x, ARENA_Y), (center_x, ARENA_Y + ARENA_H), width=6)
    pygame.draw.line(screen, border_color, (ARENA_X, ARENA_Y), (ARENA_X + ARENA_W, ARENA_Y), line_width)
    pygame.draw.line(screen, border_color, (ARENA_X, ARENA_Y + ARENA_H), (ARENA_X + ARENA_W, ARENA_Y + ARENA_H), line_width)

    # 2. Define o formato das depressões laterais "indents"
    indent_height = ARENA_H / 3  # A depressão terá 1/3 da altura da arena
    indent_depth = ARENA_W / 15  # A profundidade da depressão.
    indent_start_y = ARENA_Y + (ARENA_H - indent_height) / 2
    indent_end_y = indent_start_y + indent_height

    # 3. Desenha as paredes laterais 
    # Para cada parede, uma lista de pontos é criada para desenhar o formato
    
    # Parede Esquerda formato ']'
    left_wall_points = [
        (ARENA_X, ARENA_Y),
        (ARENA_X, indent_start_y),
        (ARENA_X + indent_depth, indent_start_y),
        (ARENA_X + indent_depth, indent_end_y),
        (ARENA_X, indent_end_y),
        (ARENA_X, ARENA_Y + ARENA_H)
    ]
    pygame.draw.lines(screen, border_color, False, left_wall_points, line_width)

    # Parede Direita formato '['
    right_wall_x = ARENA_X + ARENA_W
    right_wall_points = [
        (right_wall_x, ARENA_Y),
        (right_wall_x, indent_start_y),
        (right_wall_x - indent_depth, indent_start_y),
        (right_wall_x - indent_depth, indent_end_y),
        (right_wall_x, indent_end_y),
        (right_wall_x, ARENA_Y + ARENA_H)
    ]
    pygame.draw.lines(screen, border_color, False, right_wall_points, line_width)

def draw_arena_epsilon(screen, ARENA_X, ARENA_Y, ARENA_W_original, ARENA_H,
                                         fator_largura=1.3,
                                         top_line_reduction=0, 
                                         bottom_line_reduction=0):
    """
    Desenha uma arena de Pong com paredes laterais personalizadas e aberturas
    - A largura total da arena é ajustada pelo 'fator_largura'
    - Parede Esquerda: Metade inferior com formato '['
    - Parede Direita: Metade superior com formato ']'
    - Os parâmetros 'top_line_reduction' e 'bottom_line_reduction'
      permitem encurtar as respectivas linhas para criar aberturas
    """
    border_color = (255, 255, 255)
    line_width = 8

    # MODIFICAÇÃO PARA AUMENTAR A LARGURA DA ARENA 
    ARENA_W = int(ARENA_W_original * fator_largura)
    ARENA_X = int(ARENA_X - (ARENA_W - ARENA_W_original) / 2) # Centraliza a arena


    center_x = ARENA_X + ARENA_W // 2
    pygame.draw.line(screen, (180, 180, 180), (center_x, ARENA_Y), (center_x, ARENA_Y + ARENA_H), width=6)

    indent_height = ARENA_H / 2
    indent_depth = ARENA_W / 15
    right_wall_x = ARENA_X + ARENA_W

    # Desenho das paredes laterais (com aberturas) 
    # Parede Esquerda (metade inferior com formato '['
    left_wall_points = [
        (ARENA_X, ARENA_Y),
        (ARENA_X, ARENA_Y + indent_height),
        (ARENA_X + indent_depth, ARENA_Y + indent_height),
        (ARENA_X + indent_depth, ARENA_Y + ARENA_H),
        # (ARENA_X, ARENA_Y + ARENA_H)  
    ]
    pygame.draw.lines(screen, border_color, False, left_wall_points, line_width)

    # Parede Direita (metade superior com formato ']'
    right_wall_points = [
        # (right_wall_x, ARENA_Y),  
        (right_wall_x - indent_depth, ARENA_Y),
        (right_wall_x - indent_depth, ARENA_Y + indent_height),
        (right_wall_x, ARENA_Y + indent_height),
        (right_wall_x, ARENA_Y + ARENA_H)
    ]
    pygame.draw.lines(screen, border_color, False, right_wall_points, line_width)
    
    # Desenha as BORDAS SUPERIOR E INFERIOR com controle de tamanho 
    # Borda Superior:
    start_pos_top = (ARENA_X, ARENA_Y)
    end_pos_top = (right_wall_x - indent_depth - top_line_reduction, ARENA_Y)
    if end_pos_top[0] > start_pos_top[0]:
        pygame.draw.line(screen, border_color, start_pos_top, end_pos_top, line_width)
    
    # Borda Inferior:
    start_pos_bottom = (ARENA_X + indent_depth + bottom_line_reduction, ARENA_Y + ARENA_H)
    end_pos_bottom = (ARENA_X + ARENA_W, ARENA_Y + ARENA_H)
    if start_pos_bottom[0] < end_pos_bottom[0]:
        pygame.draw.line(screen, border_color, start_pos_bottom, end_pos_bottom, line_width)

def draw_arena_aleatoria(screen, ARENA_X, ARENA_Y, ARENA_W, ARENA_H):
    """
    Desenha uma arena aleatória escolhendo uma das outras arenas (exceto ela mesma)
    """
    # Lista de funções das arenas
    arenas = [
        draw_arena_alpha,
        draw_arena_beta,
        draw_arena_gamma,
        draw_arena_delta,
        draw_arena_epsilon
    ]
    # Escolhe uma arena aleatória a cada chamada
    arena_func = random.choice(arenas)
    # Chama a função sorteada
    if arena_func == draw_arena_beta:
        # Beta precisa do parâmetro angle
        angle = random.uniform(0, 2 * math.pi)
        arena_func(screen, ARENA_X, ARENA_Y, ARENA_W, ARENA_H, angle=angle)
    elif arena_func == draw_arena_epsilon:
        arena_func(screen, ARENA_X, ARENA_Y, ARENA_W, ARENA_H)
    else:
        arena_func(screen, ARENA_X, ARENA_Y, ARENA_W, ARENA_H)