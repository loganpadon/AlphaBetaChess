#See also https://colab.research.google.com/drive/1c7717_Mq0fPQNYHNbAvPiEI55pDCyCtR
from ChessState import ChessState
import chess
from math import inf
import pickle
from numpy import argmax
#from anytree import Node, RenderTree

class ChessStateTree:
    def __init__(self, initState, movesToMate):
        self.headState = ChessState(initState)
        self.depth = movesToMate + 1
        self.lowestRow = []
        self.lowestRow.append(self.headState)
        self.nodesExplored = 0

    def createTree(self):
        for i in range(1, self.depth):
            print(i)
            temp = []
            # Generates the moves for White
            for state in self.lowestRow:
                state.generateNextMoves()
                for child in state.children:
                    temp.append(child)
            self.lowestRow = temp
            temp = []
            # Generates the moves for Black, if it's not at the end of the tree
            if i != self.depth-1:
                print("black " + str(i))
                for state in self.lowestRow:
                    state.generateNextMoves()
                    for child in state.children:
                        temp.append(child)
                self.lowestRow = temp

    def scoreTree(self, scorer):
        for state in self.lowestRow:
            state.score(scorer)

    def printLeaves(self):
        for state in self.lowestRow:
            print(state.value)

    def getSuccessors(self, node):
        assert node is not None
        return node.children

    def isTerminal(self, node):
        assert node is not None
        return len(node.children) == 0

    def getUtility(self, node):
        assert node is not None
        return node.value

    def alpha_beta_search(self):
        node = self.headState
        best_val = -inf
        beta = inf

        successors = self.getSuccessors(node)
        best_state = None
        self.nodesExplored += 1
        for state in successors:
            value = self.min_value(state, best_val, beta)
            if value > best_val:
                best_val = value
                best_state = state
        print("AlphaBeta:  Utility Value of Root Node: = " + str(best_val))
        print("AlphaBeta:  Best State is: " + str(best_state.state.move_stack))
        return best_state, best_val

    def max_value(self, node, alpha, beta):
        #print("AlphaBeta-->MAX: Visited Node :: " + str(node.state.peek()))
        self.nodesExplored += 1
        if self.isTerminal(node):
            return self.getUtility(node)
        value = -inf

        successors = self.getSuccessors(node)
        for state in successors:
            value = max(value, self.min_value(state, alpha, beta))
            if value >= beta:
                return value
            alpha = max(alpha, value)
        return value

    def min_value(self, node, alpha, beta):
        #print("AlphaBeta-->MIN: Visited Node :: " + str(node.state.peek()))
        self.nodesExplored += 1
        if self.isTerminal(node):
            return self.getUtility(node)
        value = inf

        successors = self.getSuccessors(node)
        for state in successors:
            value = min(value, self.max_value(state, alpha, beta))
            if value <= alpha:
                return value
            beta = min(beta, value)
        return value


def easyScorer(board):
    if board.result() == '1-0':
        return inf
    if board.result() == '0-1' or board.result() == '1/2-1/2':
        return -inf
    if board.result() == '*':
        return 0


def pieceScorer(board):
    if board.result() == '1-0':
        return inf
    if board.result() == '0-1' or board.result() == '1/2-1/2':
        return -inf
    if board.result() == '*':
        fen = board.fen()
        fen = fen.split()
        fen = fen[0]
        blackScore = 0
        whiteScore = 0
        for char in fen:
            if char == 'p':
                blackScore += 1
            elif char == 'n':
                blackScore += 3
            elif char == 'b':
                blackScore += 3
            elif char == 'r':
                blackScore += 5
            elif char == 'q':
                blackScore += 9
            elif char == 'P':
                whiteScore += 1
            elif char == 'N':
                whiteScore += 3
            elif char == 'B':
                whiteScore += 3
            elif char == 'R':
                whiteScore += 5
            elif char == 'Q':
                whiteScore += 9
        return whiteScore - blackScore


def readfile(filename, count=10000):
    i = 1
    boardNames = []
    solutions = []
    with open(filename) as f:
        for line in f:
            if i % 5 == 2:
                boardNames.append(line)
            elif i % 5 == 3:
                solutions.append(line)
            i += 1
            if i >= count*5:
                break
    return boardNames, solutions


def getAllTrees(filename='2movestomate.txt'):
    #boardNames, solutions = readfile(filename)
    scrubbedFilename = filename.split(".")
    scrubbedFilename = scrubbedFilename[0]
    i = 1
    matchesEasy = 0
    successesEasy = 0
    nodesEasy = 0
    matchesPiece = 0
    successesPiece = 0
    nodesPiece = 0
    totalBoards = 0

    skip = False
    with open(filename) as f:
        for line in f:
            print(line + " " + str(i))
            if i % 5 == 2:
                skip = False
                boardName = line
                board = chess.Board(boardName)
                boardSplit = boardName.split(" ")
                if boardSplit[1] == 'b':
                    skip = True
            elif i % 5 == 3 and not skip:
                totalBoards += 1
                solutions = line.split(" ")
                solution = solutions[1]
                solution = board.parse_san(solution)
                cst = ChessStateTree(board, 2)
                cst.createTree()
                cst.scoreTree(easyScorer)
                best_state, best_val = cst.alpha_beta_search()
                if solution == best_state.state.move_stack[0]:
                    matchesEasy += 1
                if best_val == inf:
                    successesEasy += 1
                matchPercent = matchesEasy/totalBoards
                print("Percent Match: " + str(matchPercent))
                percentSuccess = successesEasy/totalBoards
                print("Percent Success: " + str(percentSuccess))
                nodesEasy += cst.nodesExplored
                averageNodes = nodesEasy/totalBoards
                print("Average Nodes: " + str(averageNodes))
                with open('easyScorer' + scrubbedFilename + '.pkl', 'wb') as f:
                    print("dumpin time")
                    pickle.dump([matchPercent, percentSuccess, averageNodes, totalBoards], f)

                cst.scoreTree(pieceScorer)
                best_state, best_val = cst.alpha_beta_search()
                if solution == best_state.state.move_stack[0]:
                    matchesPiece += 1
                if best_val == inf:
                    successesPiece += 1
                matchPercent = matchesPiece / totalBoards
                print("Percent Match: " + str(matchPercent))
                percentSuccess = successesPiece / totalBoards
                print("Percent Success: " + str(percentSuccess))
                nodesPiece += cst.nodesExplored
                averageNodes = nodesPiece / totalBoards
                print("Average Nodes: " + str(averageNodes))
                with open('pieceScorer' + scrubbedFilename + '.pkl', 'wb') as f:
                    print("dumpin time")
                    pickle.dump([matchPercent, percentSuccess, averageNodes, totalBoards], f)
            i += 1

    # for board in boardName:
    #     cst = ChessStateTree(board, 2)
    #     cst.createTree()
    #     cst.scoreTree(easyScorer)
    #     cst.alpha_beta_search()
    #     i += 1


if __name__ == '__main__':
    PKLFILE = False
    # boardName = "r2qkb1r/pp2nppp/3p4/2pNN1B1/2BnP3/3P4/PPP2PPP/R2bK2R w KQkq - 1 0"
    boardName = "6qk/8/5P1p/8/8/6QP/5PP1/4R1K1 w KQkq - 1 0"
    #boardName = "7p/8/8/8/8/8/8/P7"
    board = chess.Board(boardName)
    if not PKLFILE:
        cst = ChessStateTree(board, 2)
        cst.createTree()
        cst.scoreTree(pieceScorer)
        # with open('cst2movesToMate.pkl', 'wb') as f:
        #     print("dumpin time")
        #     pickle.dump([cst, boardName], f)
        # cst.scoreTree(easyScorer)
        # with open('cst2movesToMate.pkl', 'wb') as f:
        #     print("dumpin time")
        #     pickle.dump([cst, boardName], f)
    else:
        pickle_in = open('cst2movesToMate.pkl', "rb")
        asdf = pickle.load(pickle_in)
        cst = asdf[0]
        asdf = None

    cst.alpha_beta_search()
