from math import inf
import chess


class ChessState:
    def __init__(self, initState, parent=None):
        #self.parent = parent
        self.state = initState
        # self.alpha = -inf
        # self.beta = inf
        self.children = []
        if self.state.turn:
            self.value = -inf
        else:
            self.value = inf
        # if not parent:
        #     self.color = 'W'
        #     self.value = -inf
        # elif parent.color == 'W':
        #     self.color = 'B'
        #     self.value = inf
        # elif parent.color == 'B':
        #     self.color = 'W'
        #     self.value = -inf

    def generateNextMoves(self):
        for move in self.state.legal_moves:
            move = chess.Move.from_uci(move.uci())
            self.state.push(move)
            tBoard = chess.Board(self.state.fen())
            tBoard.starting_fen = self.state.starting_fen
            array = []
            for move in self.state.move_stack:
                array.append(move)
            tBoard.move_stack = array
            array = []
            for boardState in self.state._stack:
                array.append(boardState)
            tBoard._stack = array
            self.children.append(ChessState(initState=tBoard, parent=self))
            self.state.pop()

    def score(self, scorer):
        self.value = scorer(self.state)

    def __str__(self):
        return self.state.__str__()
