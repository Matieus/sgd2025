# Slide Puzzle, by Al Sweigart al@inventwithpython.com
# (Pygame) The classic 15-tile slide puzzle.

import pygame, sys, random
from pygame.locals import *

# ---------------------- stałe konfiguracyjne ----------------------
BOARDWIDTH = 4  # kolumny
BOARDHEIGHT = 4  # wiersze
TILESIZE = 80
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
FPS = 30
BLANK = None

#                 R    G    B
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BRIGHTBLUE = (0, 50, 255)
DARKTURQUOISE = (3, 54, 73)
GREEN = (0, 204, 0)

BGCOLOR = DARKTURQUOISE
TILECOLOR = GREEN
TEXTCOLOR = WHITE
BORDERCOLOR = BRIGHTBLUE
BASICFONTSIZE = 20

BUTTONCOLOR = WHITE
BUTTONTEXTCOLOR = BLACK
MESSAGECOLOR = WHITE

XMARGIN = int((WINDOWWIDTH - (TILESIZE * BOARDWIDTH + (BOARDWIDTH - 1))) / 2)
YMARGIN = int((WINDOWHEIGHT - (TILESIZE * BOARDHEIGHT + (BOARDHEIGHT - 1))) / 2)

UP, DOWN, LEFT, RIGHT = "up", "down", "left", "right"

# -----------------------------------------------------------------


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT
    global RESET_SURF, RESET_RECT, NEW_SURF, NEW_RECT, SOLVE_SURF, SOLVE_RECT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption("Slide Puzzle")
    BASICFONT = pygame.font.Font("freesansbold.ttf", BASICFONTSIZE)

    # przyciski w prawym-dolnym rogu
    RESET_SURF, RESET_RECT = makeText(
        "Reset", TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 90
    )
    NEW_SURF, NEW_RECT = makeText(
        "New Game", TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 60
    )
    SOLVE_SURF, SOLVE_RECT = makeText(
        "Solve", TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 30
    )

    mainBoard, solutionSeq = generateNewPuzzle(80)
    SOLVEDBOARD = getStartingBoard()
    allMoves = []  # historia ruchów
    moveCount = 0  # <<< LICZNIK RUCHÓW >>>

    # --------------------------- pętla gry ------------------------
    while True:
        slideTo = None
        msg = "Click tile or press arrow keys to slide."
        if mainBoard == SOLVEDBOARD:
            msg = "Solved!"

        drawBoard(mainBoard, msg, moveCount)  # przekazujemy licznik

        checkForQuit()
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                spotx, spoty = getSpotClicked(mainBoard, *event.pos)

                if (spotx, spoty) == (None, None):
                    # kliknięto przyciski opcji
                    if RESET_RECT.collidepoint(event.pos):
                        resetAnimation(mainBoard, allMoves)
                        allMoves.clear()
                        moveCount = 0
                    elif NEW_RECT.collidepoint(event.pos):
                        mainBoard, solutionSeq = generateNewPuzzle(80)
                        allMoves.clear()
                        moveCount = 0
                    elif SOLVE_RECT.collidepoint(event.pos):
                        resetAnimation(mainBoard, solutionSeq + allMoves)
                        allMoves.clear()
                        moveCount = 0
                else:
                    blankx, blanky = getBlankPosition(mainBoard)
                    if spotx == blankx + 1 and spoty == blanky:
                        slideTo = LEFT
                    elif spotx == blankx - 1 and spoty == blanky:
                        slideTo = RIGHT
                    elif spotx == blankx and spoty == blanky + 1:
                        slideTo = UP
                    elif spotx == blankx and spoty == blanky - 1:
                        slideTo = DOWN

            elif event.type == KEYUP:
                if event.key in (K_LEFT, K_a) and isValidMove(mainBoard, LEFT):
                    slideTo = LEFT
                elif event.key in (K_RIGHT, K_d) and isValidMove(mainBoard, RIGHT):
                    slideTo = RIGHT
                elif event.key in (K_UP, K_w) and isValidMove(mainBoard, UP):
                    slideTo = UP
                elif event.key in (K_DOWN, K_s) and isValidMove(mainBoard, DOWN):
                    slideTo = DOWN

        if slideTo:
            slideAnimation(mainBoard, slideTo, msg, 8)
            makeMove(mainBoard, slideTo)
            allMoves.append(slideTo)
            moveCount += 1  # zwiększamy licznik ruchów

        pygame.display.update()
        FPSCLOCK.tick(FPS)


# --------------------- funkcje pomocnicze -------------------------


def terminate():
    pygame.quit()
    sys.exit()


def checkForQuit():
    for event in pygame.event.get(QUIT):
        terminate()
    for event in pygame.event.get(KEYUP):
        if event.key == K_ESCAPE:
            terminate()
        pygame.event.post(event)


def getStartingBoard():
    counter = 1
    board = []
    for x in range(BOARDWIDTH):
        column = []
        for y in range(BOARDHEIGHT):
            column.append(counter)
            counter += BOARDWIDTH
        board.append(column)
        counter -= BOARDWIDTH * (BOARDHEIGHT - 1) + BOARDWIDTH - 1
    board[BOARDWIDTH - 1][BOARDHEIGHT - 1] = BLANK
    return board


def getBlankPosition(board):
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] == BLANK:
                return (x, y)


def makeMove(board, move):
    blankx, blanky = getBlankPosition(board)
    if move == UP:
        board[blankx][blanky], board[blankx][blanky + 1] = (
            board[blankx][blanky + 1],
            board[blankx][blanky],
        )
    elif move == DOWN:
        board[blankx][blanky], board[blankx][blanky - 1] = (
            board[blankx][blanky - 1],
            board[blankx][blanky],
        )
    elif move == LEFT:
        board[blankx][blanky], board[blankx + 1][blanky] = (
            board[blankx + 1][blanky],
            board[blankx][blanky],
        )
    elif move == RIGHT:
        board[blankx][blanky], board[blankx - 1][blanky] = (
            board[blankx - 1][blanky],
            board[blankx][blanky],
        )


def isValidMove(board, move):
    blankx, blanky = getBlankPosition(board)
    return (
        (move == UP and blanky != len(board[0]) - 1)
        or (move == DOWN and blanky != 0)
        or (move == LEFT and blankx != len(board) - 1)
        or (move == RIGHT and blankx != 0)
    )


def getRandomMove(board, lastMove=None):
    validMoves = [UP, DOWN, LEFT, RIGHT]
    if lastMove == UP or not isValidMove(board, DOWN):
        validMoves.remove(DOWN)
    if lastMove == DOWN or not isValidMove(board, UP):
        validMoves.remove(UP)
    if lastMove == LEFT or not isValidMove(board, RIGHT):
        validMoves.remove(RIGHT)
    if lastMove == RIGHT or not isValidMove(board, LEFT):
        validMoves.remove(LEFT)
    return random.choice(validMoves)


def getLeftTopOfTile(tileX, tileY):
    left = XMARGIN + tileX * TILESIZE + (tileX - 1)
    top = YMARGIN + tileY * TILESIZE + (tileY - 1)
    return (left, top)


def getSpotClicked(board, x, y):
    for tileX in range(len(board)):
        for tileY in range(len(board[0])):
            left, top = getLeftTopOfTile(tileX, tileY)
            tileRect = pygame.Rect(left, top, TILESIZE, TILESIZE)
            if tileRect.collidepoint(x, y):
                return (tileX, tileY)
    return (None, None)


def drawTile(tilex, tiley, number, adjx=0, adjy=0):
    left, top = getLeftTopOfTile(tilex, tiley)
    pygame.draw.rect(
        DISPLAYSURF, TILECOLOR, (left + adjx, top + adjy, TILESIZE, TILESIZE)
    )
    textSurf = BASICFONT.render(str(number), True, TEXTCOLOR)
    textRect = textSurf.get_rect()
    textRect.center = (left + TILESIZE // 2 + adjx, top + TILESIZE // 2 + adjy)
    DISPLAYSURF.blit(textSurf, textRect)


def makeText(text, color, bgcolor, top, left):
    textSurf = BASICFONT.render(text, True, color, bgcolor)
    textRect = textSurf.get_rect()
    textRect.topleft = (top, left)
    return (textSurf, textRect)


# --------------------------- RYSOWANIE -----------------------------


def drawBoard(board, message, moveCount=0):
    """Rysuje całą planszę + komunikat + licznik ruchów."""
    DISPLAYSURF.fill(BGCOLOR)

    # komunikat (górny wiersz)
    if message:
        textSurf, textRect = makeText(message, MESSAGECOLOR, BGCOLOR, 5, 5)
        DISPLAYSURF.blit(textSurf, textRect)

    # licznik ruchów – drugi wiersz
    moveText = f"Moves: {moveCount}"
    moveSurf, moveRect = makeText(moveText, MESSAGECOLOR, BGCOLOR, 5, 25)
    DISPLAYSURF.blit(moveSurf, moveRect)

    # kafelki
    for tilex in range(len(board)):
        for tiley in range(len(board[0])):
            if board[tilex][tiley]:
                drawTile(tilex, tiley, board[tilex][tiley])

    # ramka planszy
    left, top = getLeftTopOfTile(0, 0)
    width = BOARDWIDTH * TILESIZE
    height = BOARDHEIGHT * TILESIZE
    pygame.draw.rect(
        DISPLAYSURF, BORDERCOLOR, (left - 5, top - 5, width + 11, height + 11), 4
    )

    # przyciski
    DISPLAYSURF.blit(RESET_SURF, RESET_RECT)
    DISPLAYSURF.blit(NEW_SURF, NEW_RECT)
    DISPLAYSURF.blit(SOLVE_SURF, SOLVE_RECT)


# ---------------------- ANIMACJE I PUZZLE -------------------------


def slideAnimation(board, direction, message, animationSpeed):
    blankx, blanky = getBlankPosition(board)
    if direction == UP:
        movex, movey = blankx, blanky + 1
    elif direction == DOWN:
        movex, movey = blankx, blanky - 1
    elif direction == LEFT:
        movex, movey = blankx + 1, blanky
    elif direction == RIGHT:
        movex, movey = blankx - 1, blanky

    drawBoard(board, message)  # podkład
    baseSurf = DISPLAYSURF.copy()
    moveLeft, moveTop = getLeftTopOfTile(movex, movey)
    pygame.draw.rect(baseSurf, BGCOLOR, (moveLeft, moveTop, TILESIZE, TILESIZE))

    for i in range(0, TILESIZE, animationSpeed):
        checkForQuit()
        DISPLAYSURF.blit(baseSurf, (0, 0))
        if direction == UP:
            drawTile(movex, movey, board[movex][movey], 0, -i)
        elif direction == DOWN:
            drawTile(movex, movey, board[movex][movey], 0, i)
        elif direction == LEFT:
            drawTile(movex, movey, board[movex][movey], -i, 0)
        elif direction == RIGHT:
            drawTile(movex, movey, board[movex][movey], i, 0)
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def generateNewPuzzle(numSlides):
    sequence = []
    board = getStartingBoard()
    drawBoard(board, "")
    pygame.display.update()
    pygame.time.wait(500)
    lastMove = None
    for _ in range(numSlides):
        move = getRandomMove(board, lastMove)
        slideAnimation(
            board, move, "Generating new puzzle...", animationSpeed=TILESIZE // 3
        )
        makeMove(board, move)
        sequence.append(move)
        lastMove = move
    return board, sequence


def resetAnimation(board, allMoves):
    revMoves = list(reversed(allMoves))
    for move in revMoves:
        opposite = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}[move]
        slideAnimation(board, opposite, "", animationSpeed=TILESIZE // 2)
        makeMove(board, opposite)


# ------------------------------------------------------------------

if __name__ == "__main__":
    main()
