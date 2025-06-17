import sys
import pygame
import ChessEngine
import menu
import AIEngine
import Config
import time

WIDTH = Config.Config.WIDTH
HEIGHT = Config.Config.HEIGHT
MOVE_LOG_W = Config.Config.MOVE_LOG_W
MOVE_LOG_H = Config.Config.MOVE_LOG_H
DIMENSION = Config.Config.DIMENSION  # chiều của bàn cờ là 8x8
SQ_SIZE = Config.Config.SQ_SIZE  # kich cỡ của một ô vuông trong bàn cờ
MAX_FPS = Config.Config.MAX_FPS  # for animation
IMAGES = {}
TIME_WHILE_END = 2  # đợi màn hình hiển thị khi end game (seconds)
"""
khởi tạo một từ điển hình ảnh toàn cục. sẽ được gọi một lần duy nhât trong main
"""


def loadImages():
    pieces = ["wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bR", "bN", "bB", "bQ", "bK"]
    for pi in pieces:
        # hàm pygame.transform.scale để scale lại tỉ lệ của hình ảnh sao cho khớp với ô vuông trong bàn cờ
        IMAGES[pi] = pygame.transform.scale(
            pygame.image.load("assets/images/" + pi + ".png"),
            (SQ_SIZE, SQ_SIZE),
        )
    # giờ chúng ta có thể dẫn tới hình ảnh bằng cách gọi : "IMAGES['wp']"


"""
phần chính của code. đoạn này sẽ kiểm soát đầu vào của người dùng và cập nhập đồ hoạ
"""


def play(AI):
    pygame.init()
    pygame.display.set_caption("Play with Player")
    screen = pygame.display.set_mode((WIDTH + MOVE_LOG_W, HEIGHT))
    clock = pygame.time.Clock()
    screen.fill(pygame.Color("white"))
    moveLogFont = pygame.font.SysFont("Arial", 20, False, False)
    # khởi tạo một game state ban đầu
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False  # một biến cờ khi mà một nước đi được tạo ra
    animate = False  # một biến để ktra xem khi nào nên tạo hoạt ảnh cho nước đi
    loadImages()
    running = True
    sqSelected = ()  # ko có hình vuông nào được chọn, theo dõi lần click chuột cuối cùng của user ( tuple : (row, col))
    playerClicks = []  # keep track of player clicks (two tuple [(6,4), (4,4)])
    gameOver = False
    playerOne = True  # nếu người chơi đang chơi màu trắng, biến này sẽ là true. Nếu AI đang chơi màu trắng, biến này là False
    playerTwo = AI
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (
            not gs.whiteToMove and not playerTwo
        )
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
                break
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = pygame.mouse.get_pos()  # trả về một cặp toạ độ x y
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if (
                        sqSelected == (row, col) or col >= 8
                    ):  # hành động chọn 2 lần vào một ô vuông
                        # hoàn tác lại các giá trị
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2:  # sau 2 lan click chuot
                        move = ChessEngine.Move(
                            playerClicks[0], playerClicks[1], gs.board
                        )
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
            # key handler
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_z:  # undo
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                if e.key == pygame.K_r:
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                if e.key == pygame.K_m:
                    running = False
                    Menu.main_menu()
        # AI move finder
        if not gameOver and not humanTurn:
            AImove = AIEngine.findBestMove(gs, validMoves)
            if AImove is None:
                AImove = AIEngine.findRandomMove(validMoves)
            gs.makeMove(AImove)
            moveMade = True
            animate = True
        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected, moveLogFont)

        end_text = None
        if gs.checkMate:
            gameOver = True
            running = False
            if gs.whiteToMove:
                end_text = "Black wins!"
                # drawText(screen, " Black wins by checkmate")
            else:
                end_text = "White wins!"
                # drawText(screen, " White wins by checkmate")
        elif gs.staleMate:
            gameOver = True
            running = False
            end_text = "Draw!"
            # drawText(screen, "Stalemate")

        clock.tick(MAX_FPS)
        pygame.display.flip()

        if gameOver:
            start_time = time.time()
            while True:
                if time.time() - start_time > TIME_WHILE_END:
                    break
            Menu.end_menu(end_text)


"""
chịu trách nhiệm vẽ các quân cờ của trạng thái hiện tại
"""


def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == (
            "w" if gs.whiteToMove else "b"
        ):  # sqSelected là một quân cờ có thể di chuyển đc
            s = pygame.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(
                100
            )  # mức độ trong suốt : = 0: trong suốt hoàn toàn, = 255 : đục ngầu
            s.fill(pygame.Color("blue"))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            s.fill(pygame.Color("yellow"))
            # làm nổi bật các ô mà quân cờ có thể di chuyển đến
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


def drawGameState(screen, gs, validMoves, sqSelected, moveLogFont):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPiece(screen, gs.board)
    drawMoveLog(screen, gs, moveLogFont)


# làm nổ bật ô vuông được chọn và các ô có thể di chuyển được


"""
vẽ các hình vuông trên bàn cờ
"""


def drawBoard(screen):
    global colors
    colors = [pygame.Color("white"), pygame.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            pygame.draw.rect(
                screen, color, pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            )


# vẽ các quân cờ trên bàn cờ sử dụnng GameState.board khởi đầu
def drawPiece(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(
                    IMAGES[piece],
                    pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE),
                )


# vẽ lịch sử cách nước đi
def drawMoveLog(screen, gs, font):
    moveLogRect = pygame.Rect(WIDTH, 0, MOVE_LOG_W, MOVE_LOG_H)
    pygame.draw.rect(screen, pygame.Color("Black"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i // 2 + 1) + ". " + str(moveLog[i]) + " "
        if i + 1 < len(moveLog):
            moveString += str(moveLog[i + 1]) + "  "
        moveTexts.append(moveString)
    movePerRow = 3
    padding = 5
    lineSpacing = 2
    textY = padding
    for i in range(0, len(moveTexts), movePerRow):
        text = ""
        for j in range(movePerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i + j]
        textObject = font.render(text, True, pygame.Color("White"))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing


# tạo ra hiệu ứng cho nước đi
def animateMove(move, screen, board, clock):
    global colors
    coords = []  # danh sách các toạ độ mà hoạt ảnh sẽ di chuyển qua
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol

    framesPerSquare = (
        10  # số khung hình mà ô vuong di chuyển ( kiểu như tốc độ nhanh hay chậm)
    )
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (
            move.startRow + dR * frame / frameCount,
            move.startCol + dC * frame / frameCount,
        )
        drawBoard(screen)
        drawPiece(screen, board)

        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = pygame.Rect(
            move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE
        )
        pygame.draw.rect(screen, color, endSquare)

        if move.pieceCaptured != "--":
            if move.isEnpassantMove:
                enPassantRow = (
                    move.endRow + 1 if move.pieceCaptured[0] == "b" else move.endRow - 1
                )
                endSquare = pygame.Rect(
                    move.endCol * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE
                )
            screen.blit(IMAGES[move.pieceCaptured], endSquare)

        screen.blit(
            IMAGES[move.pieceMoved],
            pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE),
        )
        pygame.display.flip()
        clock.tick(60)


def drawText(screen, text):
    font = pygame.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, pygame.Color("Black"))
    textLocation = pygame.Rect(0, 0, WIDTH, HEIGHT).move(
        WIDTH / 2 - textObject.get_width() / 2, HEIGHT / 2 - textObject.get_height() / 2
    )
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, pygame.Color("Black"))
    screen.blit(textObject, textLocation.move(2, 2))
