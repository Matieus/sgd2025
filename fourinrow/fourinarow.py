import random, copy, sys, pygame
from pygame.locals import *

BOARDWIDTH = 7
BOARDHEIGHT = 6
assert BOARDWIDTH >= 4 and BOARDHEIGHT >= 4, "Board must be at least 4x4."

DIFFICULTY = 2
SPACESIZE = 50
FPS = 30
WINDOWWIDTH = 640
WINDOWHEIGHT = 480

XMARGIN = int((WINDOWWIDTH - BOARDWIDTH * SPACESIZE) / 2)
YMARGIN = int((WINDOWHEIGHT - BOARDHEIGHT * SPACESIZE) / 2)

BRIGHTBLUE = (0, 50, 255)
WHITE = (255, 255, 255)

BGCOLOR = BRIGHTBLUE
TEXTCOLOR = WHITE

RED = "red"
BLACK = "black"
EMPTY = None
HUMAN = "human"
COMPUTER = "computer"


def main():
    global FPSCLOCK, DISPLAYSURF, REDPILERECT, BLACKPILERECT, REDTOKENIMG
    global BLACKTOKENIMG, BOARDIMG, ARROWIMG, ARROWRECT, HUMANWINNERIMG
    global COMPUTERWINNERIMG, WINNERRECT, TIEWINNERIMG

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption("Four in a Row")

    REDPILERECT = pygame.Rect(
        int(SPACESIZE / 2), WINDOWHEIGHT - int(3 * SPACESIZE / 2), SPACESIZE, SPACESIZE
    )
    BLACKPILERECT = pygame.Rect(
        WINDOWWIDTH - int(3 * SPACESIZE / 2),
        WINDOWHEIGHT - int(3 * SPACESIZE / 2),
        SPACESIZE,
        SPACESIZE,
    )
    REDTOKENIMG = pygame.image.load("4row_red.png")
    REDTOKENIMG = pygame.transform.smoothscale(REDTOKENIMG, (SPACESIZE, SPACESIZE))
    BLACKTOKENIMG = pygame.image.load("4row_black.png")
    BLACKTOKENIMG = pygame.transform.smoothscale(BLACKTOKENIMG, (SPACESIZE, SPACESIZE))
    BOARDIMG = pygame.image.load("4row_board.png")
    BOARDIMG = pygame.transform.smoothscale(BOARDIMG, (SPACESIZE, SPACESIZE))

    HUMANWINNERIMG = pygame.image.load("4row_humanwinner.png")
    COMPUTERWINNERIMG = pygame.image.load("4row_computerwinner.png")
    TIEWINNERIMG = pygame.image.load("4row_tie.png")
    WINNERRECT = HUMANWINNERIMG.get_rect()
    WINNERRECT.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))

    ARROWIMG = pygame.image.load("4row_arrow.png")
    ARROWRECT = ARROWIMG.get_rect()
    ARROWRECT.left = REDPILERECT.right + 10
    ARROWRECT.centery = REDPILERECT.centery

    isFirstGame = True

    while True:
        runGame(isFirstGame)
        isFirstGame = False


def runGame(isFirstGame):
    if isFirstGame:
        turn = COMPUTER
        showHelp = True
    else:
        turn = COMPUTER if random.randint(0, 1) == 0 else HUMAN
        showHelp = False

    mainBoard = getNewBoard()

    while True:
        if turn == HUMAN:
            getHumanMove(mainBoard, showHelp)
            if showHelp:
                showHelp = False
            if isWinner(mainBoard, RED):
                winnerImg = HUMANWINNERIMG
                break
            turn = COMPUTER
        else:
            column = getComputerMove(mainBoard)
            animateComputerMoving(mainBoard, column)
            makeMove(mainBoard, BLACK, column)
            if isWinner(mainBoard, BLACK):
                winnerImg = COMPUTERWINNERIMG
                break
            turn = HUMAN

        if isBoardFull(mainBoard):
            winnerImg = TIEWINNERIMG
            break

    while True:
        drawBoard(mainBoard, turn=turn)
        DISPLAYSURF.blit(winnerImg, WINNERRECT)
        pygame.display.update()
        FPSCLOCK.tick()
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONUP:
                return


def drawTurnIndicator(turn):
    font = pygame.font.Font(None, 36)
    if turn == HUMAN:
        text = font.render("Tura gracza (Czerwony)", True, WHITE)
    else:
        text = font.render("Tura komputera (Czarny)", True, WHITE)
    textRect = text.get_rect()
    textRect.center = (WINDOWWIDTH // 2, YMARGIN // 2)
    DISPLAYSURF.blit(text, textRect)


def drawBoard(board, extraToken=None, turn=None):
    DISPLAYSURF.fill(BGCOLOR)

    spaceRect = pygame.Rect(0, 0, SPACESIZE, SPACESIZE)
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            spaceRect.topleft = (XMARGIN + (x * SPACESIZE), YMARGIN + (y * SPACESIZE))
            if board[x][y] == RED:
                DISPLAYSURF.blit(REDTOKENIMG, spaceRect)
            elif board[x][y] == BLACK:
                DISPLAYSURF.blit(BLACKTOKENIMG, spaceRect)

    if extraToken is not None:
        if extraToken["color"] == RED:
            DISPLAYSURF.blit(
                REDTOKENIMG, (extraToken["x"], extraToken["y"], SPACESIZE, SPACESIZE)
            )
        elif extraToken["color"] == BLACK:
            DISPLAYSURF.blit(
                BLACKTOKENIMG, (extraToken["x"], extraToken["y"], SPACESIZE, SPACESIZE)
            )

    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            spaceRect.topleft = (XMARGIN + (x * SPACESIZE), YMARGIN + (y * SPACESIZE))
            DISPLAYSURF.blit(BOARDIMG, spaceRect)

    DISPLAYSURF.blit(REDTOKENIMG, REDPILERECT)
    DISPLAYSURF.blit(BLACKTOKENIMG, BLACKPILERECT)

    if turn is not None:
        drawTurnIndicator(turn)


def getNewBoard():
    return [[EMPTY] * BOARDHEIGHT for _ in range(BOARDWIDTH)]


def getHumanMove(board, isFirstMove):
    draggingToken = False
    tokenx, tokeny = None, None
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif (
                event.type == MOUSEBUTTONDOWN
                and not draggingToken
                and REDPILERECT.collidepoint(event.pos)
            ):
                draggingToken = True
                tokenx, tokeny = event.pos
            elif event.type == MOUSEMOTION and draggingToken:
                tokenx, tokeny = event.pos
            elif event.type == MOUSEBUTTONUP and draggingToken:
                if tokeny < YMARGIN and XMARGIN < tokenx < WINDOWWIDTH - XMARGIN:
                    column = int((tokenx - XMARGIN) / SPACESIZE)
                    if isValidMove(board, column):
                        animateDroppingToken(board, column, RED)
                        board[column][getLowestEmptySpace(board, column)] = RED
                        drawBoard(board, turn=HUMAN)
                        pygame.display.update()
                        return
                tokenx, tokeny = None, None
                draggingToken = False

        if tokenx is not None and tokeny is not None:
            drawBoard(
                board,
                {
                    "x": tokenx - int(SPACESIZE / 2),
                    "y": tokeny - int(SPACESIZE / 2),
                    "color": RED,
                },
                turn=HUMAN,
            )
        else:
            drawBoard(board, turn=HUMAN)

        if isFirstMove:
            DISPLAYSURF.blit(ARROWIMG, ARROWRECT)

        pygame.display.update()
        FPSCLOCK.tick()


def animateDroppingToken(board, column, color):
    x = XMARGIN + column * SPACESIZE
    y = YMARGIN - SPACESIZE
    dropSpeed = 1.0
    lowestEmptySpace = getLowestEmptySpace(board, column)
    while True:
        y += int(dropSpeed)
        dropSpeed += 0.5
        if int((y - YMARGIN) / SPACESIZE) >= lowestEmptySpace:
            return
        drawBoard(board, {"x": x, "y": y, "color": color})
        pygame.display.update()
        FPSCLOCK.tick()


def animateComputerMoving(board, column):
    x = BLACKPILERECT.left
    y = BLACKPILERECT.top
    speed = 1.0
    while y > (YMARGIN - SPACESIZE):
        y -= int(speed)
        speed += 0.5
        drawBoard(board, {"x": x, "y": y, "color": BLACK}, turn=COMPUTER)
        pygame.display.update()
        FPSCLOCK.tick()
    y = YMARGIN - SPACESIZE
    speed = 1.0
    while x > (XMARGIN + column * SPACESIZE):
        x -= int(speed)
        speed += 0.5
        drawBoard(board, {"x": x, "y": y, "color": BLACK}, turn=COMPUTER)
        pygame.display.update()
        FPSCLOCK.tick()
    animateDroppingToken(board, column, BLACK)


def makeMove(board, player, column):
    row = getLowestEmptySpace(board, column)
    if row != -1:
        board[column][row] = player


def getComputerMove(board):
    potentialMoves = getPotentialMoves(board, BLACK, DIFFICULTY)
    bestMoveFitness = -1
    for i in range(BOARDWIDTH):
        if potentialMoves[i] > bestMoveFitness and isValidMove(board, i):
            bestMoveFitness = potentialMoves[i]
    bestMoves = [
        i
        for i in range(len(potentialMoves))
        if potentialMoves[i] == bestMoveFitness and isValidMove(board, i)
    ]
    return random.choice(bestMoves)


def getPotentialMoves(board, tile, lookAhead):
    if lookAhead == 0 or isBoardFull(board):
        return [0] * BOARDWIDTH
    enemyTile = RED if tile == BLACK else BLACK
    potentialMoves = [0] * BOARDWIDTH
    for firstMove in range(BOARDWIDTH):
        dupeBoard = copy.deepcopy(board)
        if not isValidMove(dupeBoard, firstMove):
            continue
        makeMove(dupeBoard, tile, firstMove)
        if isWinner(dupeBoard, tile):
            potentialMoves[firstMove] = 1
            break
        elif isBoardFull(dupeBoard):
            potentialMoves[firstMove] = 0
        else:
            for counterMove in range(BOARDWIDTH):
                dupeBoard2 = copy.deepcopy(dupeBoard)
                if not isValidMove(dupeBoard2, counterMove):
                    continue
                makeMove(dupeBoard2, enemyTile, counterMove)
                if isWinner(dupeBoard2, enemyTile):
                    potentialMoves[firstMove] = -1
                    break
                else:
                    results = getPotentialMoves(dupeBoard2, tile, lookAhead - 1)
                    potentialMoves[firstMove] += (
                        sum(results) / BOARDWIDTH
                    ) / BOARDWIDTH
    return potentialMoves


def getLowestEmptySpace(board, column):
    for y in range(BOARDHEIGHT - 1, -1, -1):
        if board[column][y] == EMPTY:
            return y
    return -1


def isValidMove(board, column):
    return 0 <= column < BOARDWIDTH and board[column][0] == EMPTY


def isBoardFull(board):
    return all(
        board[x][y] != EMPTY for x in range(BOARDWIDTH) for y in range(BOARDHEIGHT)
    )


def isWinner(board, tile):
    for x in range(BOARDWIDTH - 3):
        for y in range(BOARDHEIGHT):
            if all(board[x + i][y] == tile for i in range(4)):
                return True
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT - 3):
            if all(board[x][y + i] == tile for i in range(4)):
                return True
    for x in range(BOARDWIDTH - 3):
        for y in range(3, BOARDHEIGHT):
            if all(board[x + i][y - i] == tile for i in range(4)):
                return True
    for x in range(BOARDWIDTH - 3):
        for y in range(BOARDHEIGHT - 3):
            if all(board[x + i][y + i] == tile for i in range(4)):
                return True
    return False


if __name__ == "__main__":
    main()
