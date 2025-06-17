import random
import ChessEngine as CE

# Điểm số cho các quân cờ
pieceScore = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "p": 1}

# Bảng điểm vị trí cho các quân cờ (giữ nguyên như cũ)
knightScores = [[1,1,1,1,1,1,1,1],
                [1,2,2,2,2,2,2,1],
                [1,2,3,3,3,3,2,1],
                [1,2,3,4,4,3,2,1],
                [1,2,3,4,4,3,2,1],
                [1,2,3,3,3,3,2,1],
                [1,2,2,2,2,2,2,1],
                [1,1,1,1,1,1,1,1]]

bishopScores = [[4,3,2,1,1,2,3,4],
                [3,4,3,2,2,3,4,3],
                [2,3,4,3,3,4,3,2],
                [1,2,3,4,4,3,2,1],
                [1,2,3,4,4,3,2,1],
                [2,3,4,3,3,4,3,2],
                [3,4,3,2,2,3,4,3],
                [4,3,2,1,1,2,3,4]]

queenScores =  [[1,1,1,3,1,1,1,1],
                [1,2,3,3,3,1,1,1],
                [1,4,3,3,3,4,2,1],
                [1,2,3,3,3,2,2,1],
                [1,2,3,3,3,2,2,1],
                [1,4,3,3,3,4,2,1],
                [1,1,2,3,3,1,1,1],
                [1,1,1,3,1,1,1,1]]

rookScores =  [[4,3,4,4,4,4,3,4],
                [4,4,4,4,4,4,4,4],
                [1,1,2,3,3,2,1,1],
                [1,2,3,4,4,3,2,1],
                [1,2,3,4,4,3,2,1],
                [1,1,2,3,3,2,1,1],
                [4,4,4,4,4,4,4,4],
                [4,3,4,4,4,4,3,4]]

whitePawnScores = [[8,8,8,8,8,8,8,8],
                    [8,8,8,8,8,8,8,8],
                    [5,6,6,7,7,6,6,5],
                    [2,3,3,5,5,3,3,2],
                    [1,2,3,4,4,3,2,1],
                    [1,1,2,3,3,2,1,1],
                    [1,1,1,0,0,1,1,1],
                    [0,0,0,0,0,0,0,0]]

blackPawnScores = [[0,0,0,0,0,0,0,0],
                    [1,1,1,0,0,1,1,1],
                    [1,1,2,3,3,2,1,1],
                    [1,2,3,4,4,3,2,1],
                    [2,3,3,5,5,3,3,2],
                    [5,6,6,7,7,6,6,5],
                    [8,8,8,8,8,8,8,8],
                    [8,8,8,8,8,8,8,8]]

piecePositionScores = {"N": knightScores, "Q": queenScores, "B": bishopScores, "R": rookScores, 
                       "bp": blackPawnScores, "wp": whitePawnScores}

CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3

def findRandomMove(validMoves):
    return random.choice(validMoves)

def findBestMove(gs, validMoves):
    global nextMove
    nextMove = None

    tempCastleRight = CE.CastleRight(gs.currentCastlingRight.wks, gs.currentCastlingRight.bks,
                                    gs.currentCastlingRight.wqs, gs.currentCastlingRight.bqs)
    
    validMoves = orderMoves(gs, validMoves)
    
    findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    
    gs.currentCastlingRight = tempCastleRight
    return nextMove if nextMove else findRandomMove(validMoves)

def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove
    
    if depth == 0:
        return quiescenceSearch(gs, alpha, beta, turnMultiplier)
    
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        nextMoves = orderMoves(gs, nextMoves)
        
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth-1, -beta, -alpha, -turnMultiplier)
        
        gs.undoMove()
        
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        
        # Alpha-Beta Pruning
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break
    
    return maxScore

def quiescenceSearch(gs, alpha, beta, turnMultiplier):
    # Đánh giá tĩnh vị trí hiện tại
    standPat = turnMultiplier * scoreBoard(gs)
    
    if standPat >= beta:
        return beta
    if alpha < standPat:
        alpha = standPat
    
    captures = [move for move in gs.getValidMoves() if move.isCapture]
    captures = orderMoves(gs, captures)
    
    for move in captures:
        gs.makeMove(move)
        score = -quiescenceSearch(gs, -beta, -alpha, -turnMultiplier)
        gs.undoMove()
        
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
    
    return alpha

def scoreBoard(gs):
    if gs.checkMate:
        return -CHECKMATE if gs.whiteToMove else CHECKMATE
    if gs.staleMate:
        return STALEMATE
    
    score = 0
    for row in range(8):
        for col in range(8):
            piece = gs.board[row][col]
            if piece != "--":
                # Điểm cơ bản của quân cờ
                pieceValue = pieceScore[piece[1]]
                
                # Điểm vị trí (chỉ áp dụng cho các quân không phải vua)
                positionScore = 0
                if piece[1] != "K":
                    if piece[1] == "p":
                        positionScore = piecePositionScores[piece][row][col]
                    else:
                        positionScore = piecePositionScores[piece[1]][row][col]
                
                # Tổng điểm với trọng số
                total = pieceValue + positionScore * 0.1
                
                # Cộng/trừ điểm tùy màu quân
                score += total if piece[0] == 'w' else -total
    
    return score

def orderMoves(gs, moves):
    moveScores = []
    for move in moves:
        score = 0
        # Ưu tiên nước đi bắt quân
        if move.isCapture:
            score = 10 * pieceScore[move.pieceCaptured[1]] - pieceScore[move.pieceMoved[1]]
        
        # Ưu tiên thăng cấp tốt
        if move.isPawnPromotion:
            score += pieceScore["Q"]
        
        # Ưu tiên di chuyển đến vị trí tốt
        if move.pieceMoved[1] != "K":
            if move.pieceMoved[1] == "p":
                score += piecePositionScores[move.pieceMoved][move.endRow][move.endCol] - \
                         piecePositionScores[move.pieceMoved][move.startRow][move.startCol]
            else:
                score += piecePositionScores[move.pieceMoved[1]][move.endRow][move.endCol] - \
                         piecePositionScores[move.pieceMoved[1]][move.startRow][move.startCol]
        
        moveScores.append(score)
    
    # Sắp xếp các nước đi theo điểm số giảm dần
    return [move for _, move in sorted(zip(moveScores, moves), key=lambda x: x[0], reverse=True)]