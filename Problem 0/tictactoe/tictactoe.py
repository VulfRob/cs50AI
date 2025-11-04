"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    x_count = 0
    o_count = 0

    for i in range(3):
        for j in range(3):
            if board[i][j] == "X":
                x_count += 1
            elif board[i][j] == "O":
                o_count += 1

    # Если X и O равны → ходит X
    if x_count <= o_count:
        return "X"
    else:
        return "O"



def actions(board):
    acts = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] is None:
                acts.add((i, j))
    return acts


def result(board, action):
    i, j = action

    # Проверка допустимости хода
    if not (0 <= i < 3 and 0 <= j < 3):
        raise Exception("Invalid action")
    if board[i][j] is not None:
        raise Exception("Invalid action")

    # Копируем доску, чтобы не изменить исходную
    new_board = copy.deepcopy(board)

    # Ставим метку текущего игрока
    from tictactoe import player  # если ты в другом файле
    new_board[i][j] = player(board)

    return new_board



def winner(board):
    # Проверка строк
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != None:
            return board[i][0]

    # Проверка столбцов
    for i in range(3):
        if board[0][i] == board[1][i] == board[2][i] != None:
            return board[0][i]

    # Проверка диагоналей
    if board[0][0] == board[1][1] == board[2][2] != None:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != None:
        return board[0][2]

    # Если никто не выиграл
    return None



def terminal(board):
    # Если кто-то выиграл
    if winner(board) is not None:
        return True

    # Если нет пустых клеток (ничья)
    for row in board:
        if None in row:
            return False

    return True



def utility(board):
    if winner(board) == "X":
        return 1
    elif winner(board) == "O":
        return -1
    else:
        return 0



def minimax(board):
    """
    Returns the optimal action (i, j) for the current player on the board.
    If the game is over, returns None.
    """

    # Если игра уже закончена
    if terminal(board):
        return None

    # Текущий игрок
    current_player = player(board)

    # Вложенные функции для рекурсии
    def max_value(state):
        if terminal(state):
            return utility(state)
        v = float("-inf")
        for action in actions(state):
            v = max(v, min_value(result(state, action)))
        return v

    def min_value(state):
        if terminal(state):
            return utility(state)
        v = float("inf")
        for action in actions(state):
            v = min(v, max_value(result(state, action)))
        return v

    # Основная часть minimax
    best_action = None

    if current_player == "X":
        best_score = float("-inf")
        for action in actions(board):
            score = min_value(result(board, action))
            if score > best_score:
                best_score = score
                best_action = action
    else:
        best_score = float("inf")
        for action in actions(board):
            score = max_value(result(board, action))
            if score < best_score:
                best_score = score
                best_action = action

    return best_action

