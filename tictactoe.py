import socket

class TicTacToe:
    def __init__(self):
        self.gameSize = 3
        self.turn = 1
        if self.turn != 1 and self.turn != 2:
            self.__init__()
            return
        self.board = [[0 for i in range(self.gameSize)] for i in range(self.gameSize)]
        self.winner = None
        self.state = 0
        self.lastMove = None
        self.turns = 0

    def getMark(self, val):
        if val == 1:
            return 'X'
        elif val == 2:
            return 'O'
        else:
            return " "

    def printGame(self):
        print("ESTADO ATUAL DO TABULEIRO")

        print(" ", end=" ")
        for i in range(self.gameSize):
            print(i, end=" ")
        print()

        for i in range(self.gameSize):
            print(i, end=" ")
            for j in range(self.gameSize):
                print(self.getMark(self.board[i][j]), end=" ")
            print()

    def changeTurn(self):
        self.turn = self.turn % 2 + 1

    def makeMove(self, move):
        x, y = move
        if self.board[x][y] != 0:
            print("Movimento ilegal, casa já está ocupada!")
            return
        self.board[x][y] = self.turn
        self.lastMove = (move, self.turn)
        self.turns += 1
        self.changeTurn()

    def checkWin(self):
        (x, y), mark = self.lastMove

        # Check row
        for i in range(self.gameSize):
            if self.board[x][i] != mark:
                break
            if i == self.gameSize-1:
                self.winner = mark
                self.state = 1
                return True

        # Check column
        for i in range(self.gameSize):
            if self.board[i][y] != mark:
                break
            if i == self.gameSize-1:
                self.winner = mark
                self.state = 1
                return True

        # Check main diagonal
        if x == y:
            for i in range(self.gameSize):
                if self.board[i][i] != mark:
                    break
                if i == self.gameSize-1:
                    self.winner = mark
                    self.state = 1
                    return True

            # Check secondary diagonal
        if x + y == self.gameSize - 1:
            for i in range(self.gameSize):
                if self.board[i][self.gameSize-1-i] != mark:
                    break
                if i == self.gameSize-1:
                    self.winner = mark
                    self.state = 1
                    return True

        return False

    def checkTie(self):
        if self.turns == self.gameSize*self.gameSize:
            self.state = 2

    def updateState(self):
        if not self.checkWin():
            self.checkTie()

    def possibleMoves(self):
        moves = []
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == 0:
                    moves.append((i, j))
        return moves


def miniMax(game):
    mark = 0
    scores = []
    (a, b), turn = game.lastMove
    turn = (turn % 2) + 1
    if turn == 1:
        mark = 1
    else:
        mark = -1
    game.updateState()
    if game.state == 1:
        return -mark
    if game.state == 2:
        return 0

    lastMove = game.lastMove
    for move in game.possibleMoves():
        game.makeMove(move)
        scores.append(miniMax(game))
        x, y = move
        game.board[x][y] = 0
        game.lastMove = lastMove
        game.turns -= 1
        game.changeTurn()

    game.state = 0
    game.winner = None
    return max(scores) if mark == 1 else min(scores)

def alphaBeta(game, alpha = -10, beta = 10, aiPlayer = 1):
    mark = 0
    scores = []
    (a, b), turn = game.lastMove
    turn = (turn % 2) + 1
    if turn == aiPlayer:
        mark = 1
    else:
        mark = -1
    game.updateState()
    if game.state == 1:
        return -mark
    if game.state == 2:
        return 0

    lastMove = game.lastMove
    if mark == 1:
        value = -10
        for move in game.possibleMoves():
             game.makeMove(move)
             value = max(value, alphaBeta(game, alpha, beta, aiPlayer))
             alpha = max(alpha, value)
             x, y = move
             game.board[x][y] = 0
             game.lastMove = lastMove
             game.turns -= 1
             game.changeTurn()
             if alpha >= beta:
                 break
        game.state = 0
        game.winner = None
        return value

    else:
        value = 10
        for move in game.possibleMoves():
             game.makeMove(move)
             value = min(value, alphaBeta(game, alpha, beta, aiPlayer))
             beta = min(beta, value)
             x, y = move
             game.board[x][y] = 0
             game.lastMove = lastMove
             game.turns -= 1
             game.changeTurn()
             if beta <= alpha:
                 break
        game.state = 0
        game.winner = None
        return value


def makeAiMove(game, ai):
    bestMove = None
    bestValue = -5
    for move in game.possibleMoves():
        lastMove = game.lastMove
        game.makeMove(move)
        #value = miniMax(game)
        value = alphaBeta(game, aiPlayer = ai)
        if value > bestValue:
            bestMove = move
            bestValue = value
        x, y = move
        game.board[x][y] = 0
        game.lastMove = lastMove
        game.turns -= 1
        game.changeTurn()

    game.state = 0
    game.winner = None

    x, y = bestMove
    return f'send {x} {y}'
