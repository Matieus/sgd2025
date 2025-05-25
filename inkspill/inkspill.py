# Ink Spill (a Flood It clone), by Al Sweigart               (c) Al Sweigart
# (Pygame) Try to make the entire field a single color.

import random, sys, webbrowser, copy, pygame
from pygame.locals import *

# ---------------------------------------------------------------------------
#                             USTAWIENIA GRY
# ---------------------------------------------------------------------------
SMALLBOXSIZE = 60
MEDIUMBOXSIZE = 20
LARGEBOXSIZE = 11

SMALLBOARDSIZE = 6
MEDIUMBOARDSIZE = 17
LARGEBOARDSIZE = 30

SMALLMAXLIFE = 10
MEDIUMMAXLIFE = 30
LARGEMAXLIFE = 64

FPS = 30
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
boxSize = MEDIUMBOXSIZE
PALETTEGAPSIZE = 10
PALETTESIZE = 45

EASY, MEDIUM, HARD = 0, 1, 2
difficulty = MEDIUM
maxLife = MEDIUMMAXLIFE
boardWidth = MEDIUMBOARDSIZE
boardHeight = MEDIUMBOARDSIZE

# ----------------------- KOLORY & SCHEMATY ---------------------------------
WHITE = (255, 255, 255)
DARKGRAY = (70, 70, 70)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 128, 0)
PURPLE = (255, 0, 255)

COLORSCHEMES = (
    ((150, 200, 255), RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE),
    (
        (0, 155, 104),
        (97, 215, 164),
        (228, 0, 69),
        (0, 125, 50),
        (204, 246, 0),
        (148, 0, 45),
        (241, 109, 149),
    ),
    (
        (195, 179, 0),
        (255, 239, 115),
        (255, 226, 0),
        (147, 3, 167),
        (24, 38, 176),
        (166, 147, 0),
        (197, 97, 211),
    ),
    (
        (85, 0, 0),
        (155, 39, 102),
        (0, 201, 13),
        (255, 118, 0),
        (206, 0, 113),
        (0, 130, 9),
        (255, 180, 115),
    ),
    (
        (191, 159, 64),
        (183, 182, 208),
        (4, 31, 183),
        (167, 184, 45),
        (122, 128, 212),
        (37, 204, 7),
        (88, 155, 213),
    ),
    (
        (200, 33, 205),
        (116, 252, 185),
        (68, 56, 56),
        (52, 238, 83),
        (23, 149, 195),
        (222, 157, 227),
        (212, 86, 185),
    ),
)
for scheme in COLORSCHEMES:
    assert len(scheme) == 7, "Each color scheme must have 7 entries."

bgColor = COLORSCHEMES[0][0]
paletteColors = COLORSCHEMES[0][1:]


# ---------------------------------------------------------------------------
#                               MAIN
# ---------------------------------------------------------------------------
def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT  # <<< NEW
    global LOGOIMAGE, SPOTIMAGE, SETTINGSIMAGE, SETTINGSBUTTONIMAGE, RESETBUTTONIMAGE

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font("freesansbold.ttf", 18)  # <<< NEW

    # ----- grafiki -----
    LOGOIMAGE = pygame.image.load("inkspilllogo.png")
    SPOTIMAGE = pygame.image.load("inkspillspot.png")
    SETTINGSIMAGE = pygame.image.load("inkspillsettings.png")
    SETTINGSBUTTONIMAGE = pygame.image.load("inkspillsettingsbutton.png")
    RESETBUTTONIMAGE = pygame.image.load("inkspillresetbutton.png")

    pygame.display.set_caption("Ink Spill")

    mainBoard = generateRandomBoard(boardWidth, boardHeight, difficulty)
    life = maxLife
    moveCount = 0  # <<< NEW
    lastPaletteClicked = None

    while True:  # ---------------- GŁÓWNA PĘTLA GRY -----------------
        paletteClicked = None
        resetGame = False

        # ------- RYSOWANIE EKRANU --------
        DISPLAYSURF.fill(bgColor)
        drawLogoAndButtons()
        drawBoard(mainBoard)
        drawLifeMeter(life)
        drawPalettes()
        drawMoveCounter(moveCount)  # <<< NEW

        checkForQuit()
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                # --- klik na przycisk "Settings"
                if pygame.Rect(
                    WINDOWWIDTH - SETTINGSBUTTONIMAGE.get_width(),
                    WINDOWHEIGHT - SETTINGSBUTTONIMAGE.get_height(),
                    SETTINGSBUTTONIMAGE.get_width(),
                    SETTINGSBUTTONIMAGE.get_height(),
                ).collidepoint(mousex, mousey):
                    resetGame = showSettingsScreen()
                # --- klik na przycisk "Reset"
                elif pygame.Rect(
                    WINDOWWIDTH - RESETBUTTONIMAGE.get_width(),
                    WINDOWHEIGHT
                    - SETTINGSBUTTONIMAGE.get_height()
                    - RESETBUTTONIMAGE.get_height(),
                    RESETBUTTONIMAGE.get_width(),
                    RESETBUTTONIMAGE.get_height(),
                ).collidepoint(mousex, mousey):
                    resetGame = True
                # --- klik na paletę
                else:
                    paletteClicked = getColorOfPaletteAt(mousex, mousey)

        # -------- LOGIKA GRY ------------
        if paletteClicked is not None and paletteClicked != lastPaletteClicked:
            lastPaletteClicked = paletteClicked
            floodAnimation(mainBoard, paletteClicked)
            life -= 1
            moveCount += 1  # <<< NEW

            if hasWon(mainBoard):
                for _ in range(4):
                    flashBorderAnimation(WHITE, mainBoard)
                resetGame = True
                pygame.time.wait(2000)
            elif life == 0:
                drawLifeMeter(0)
                pygame.display.update()
                pygame.time.wait(400)
                for _ in range(4):
                    flashBorderAnimation(BLACK, mainBoard)
                resetGame = True
                pygame.time.wait(2000)

        if resetGame:
            mainBoard = generateRandomBoard(boardWidth, boardHeight, difficulty)
            life = maxLife
            moveCount = 0  # <<< NEW
            lastPaletteClicked = None

        pygame.display.update()
        FPSCLOCK.tick(FPS)


# ---------------------------------------------------------------------------
#                  DODATKOWA FUNKCJA – LICZNIK RUCHÓW
# ---------------------------------------------------------------------------
def drawMoveCounter(count):  # <<< NEW
    """Wyświetla na ekranie liczbę wykonanych ruchów."""
    textSurf = BASICFONT.render(f"Moves: {count}", True, WHITE, bgColor)
    textRect = textSurf.get_rect()
    textRect.topleft = (10, 10)
    DISPLAYSURF.blit(textSurf, textRect)


# ---------------------------------------------------------------------------
#                     POZOSTAŁE FUNKCJE (bez zmian lub skrócone)
# ---------------------------------------------------------------------------
def checkForQuit():
    for event in pygame.event.get(QUIT):
        pygame.quit()
        sys.exit()
    for event in pygame.event.get(KEYUP):
        if event.key == K_ESCAPE:
            pygame.quit()
            sys.exit()
        pygame.event.post(event)


def hasWon(board):
    first = board[0][0]
    return all(
        board[x][y] == first for x in range(boardWidth) for y in range(boardHeight)
    )


# -------- Settings screen, board utilities, rysowanie itd. ----------
# (kod poniżej jest identyczny jak w oryginale – nie został zmieniony,
#  pomijam komentarze, zostawiam tylko treść dla kompletności)


def showSettingsScreen():
    global difficulty, boxSize, boardWidth, boardHeight, maxLife, paletteColors, bgColor
    origDifficulty, origBoxSize = difficulty, boxSize
    screenNeedsRedraw = True
    while True:
        if screenNeedsRedraw:
            DISPLAYSURF.fill(bgColor)
            DISPLAYSURF.blit(SETTINGSIMAGE, (0, 0))
            if difficulty == EASY:
                DISPLAYSURF.blit(SPOTIMAGE, (30, 4))
            if difficulty == MEDIUM:
                DISPLAYSURF.blit(SPOTIMAGE, (8, 41))
            if difficulty == HARD:
                DISPLAYSURF.blit(SPOTIMAGE, (30, 76))
            if boxSize == SMALLBOXSIZE:
                DISPLAYSURF.blit(SPOTIMAGE, (22, 150))
            if boxSize == MEDIUMBOXSIZE:
                DISPLAYSURF.blit(SPOTIMAGE, (11, 185))
            if boxSize == LARGEBOXSIZE:
                DISPLAYSURF.blit(SPOTIMAGE, (24, 220))
            for i in range(len(COLORSCHEMES)):
                drawColorSchemeBoxes(500, i * 60 + 30, i)
            pygame.display.update()
        screenNeedsRedraw = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYUP and event.key == K_ESCAPE:
                return not (origDifficulty == difficulty and origBoxSize == boxSize)
            elif event.type == MOUSEBUTTONUP:
                screenNeedsRedraw = True
                mx, my = event.pos
                if pygame.Rect(74, 16, 111, 30).collidepoint(mx, my):
                    difficulty = EASY
                elif pygame.Rect(53, 50, 104, 29).collidepoint(mx, my):
                    difficulty = MEDIUM
                elif pygame.Rect(72, 85, 65, 31).collidepoint(mx, my):
                    difficulty = HARD
                elif pygame.Rect(63, 156, 84, 31).collidepoint(mx, my):
                    boxSize, boardWidth, boardHeight, maxLife = (
                        SMALLBOXSIZE,
                        SMALLBOARDSIZE,
                        SMALLBOARDSIZE,
                        SMALLMAXLIFE,
                    )
                elif pygame.Rect(52, 192, 106, 32).collidepoint(mx, my):
                    boxSize, boardWidth, boardHeight, maxLife = (
                        MEDIUMBOXSIZE,
                        MEDIUMBOARDSIZE,
                        MEDIUMBOARDSIZE,
                        MEDIUMMAXLIFE,
                    )
                elif pygame.Rect(67, 228, 58, 37).collidepoint(mx, my):
                    boxSize, boardWidth, boardHeight, maxLife = (
                        LARGEBOXSIZE,
                        LARGEBOARDSIZE,
                        LARGEBOARDSIZE,
                        LARGEMAXLIFE,
                    )
                elif pygame.Rect(14, 299, 371, 97).collidepoint(mx, my):
                    webbrowser.open("http://inventwithpython.com")
                elif pygame.Rect(178, 418, 215, 34).collidepoint(mx, my):
                    return not (origDifficulty == difficulty and origBoxSize == boxSize)
                for i in range(len(COLORSCHEMES)):
                    if pygame.Rect(
                        500, 30 + i * 60, MEDIUMBOXSIZE * 3, MEDIUMBOXSIZE * 2
                    ).collidepoint(mx, my):
                        bgColor = COLORSCHEMES[i][0]
                        paletteColors = COLORSCHEMES[i][1:]


def drawColorSchemeBoxes(x, y, schemeNum):
    for boxy in range(2):
        for boxx in range(3):
            pygame.draw.rect(
                DISPLAYSURF,
                COLORSCHEMES[schemeNum][3 * boxy + boxx + 1],
                (
                    x + MEDIUMBOXSIZE * boxx,
                    y + MEDIUMBOXSIZE * boxy,
                    MEDIUMBOXSIZE,
                    MEDIUMBOXSIZE,
                ),
            )
    if paletteColors == COLORSCHEMES[schemeNum][1:]:
        DISPLAYSURF.blit(SPOTIMAGE, (x - 50, y))


def flashBorderAnimation(color, board, animationSpeed=30):
    origSurf = DISPLAYSURF.copy()
    flashSurf = pygame.Surface(DISPLAYSURF.get_size()).convert_alpha()
    for start, end, step in ((0, 256, 1), (255, 0, -1)):
        for trans in range(start, end, animationSpeed * step):
            DISPLAYSURF.blit(origSurf, (0, 0))
            r, g, b = color
            flashSurf.fill((r, g, b, trans))
            DISPLAYSURF.blit(flashSurf, (0, 0))
            drawBoard(board)
            pygame.display.update()
            FPSCLOCK.tick(FPS)
    DISPLAYSURF.blit(origSurf, (0, 0))


def floodAnimation(board, paletteClicked, animationSpeed=25):
    origBoard = copy.deepcopy(board)
    floodFill(board, board[0][0], paletteClicked, 0, 0)
    for trans in range(0, 255, animationSpeed):
        drawBoard(origBoard)
        drawBoard(board, trans)
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def generateRandomBoard(width, height, difficulty=MEDIUM):
    board = [
        [random.randint(0, len(paletteColors) - 1) for _ in range(height)]
        for _ in range(width)
    ]
    if difficulty == EASY:
        boxesToChange = 100 if boxSize == SMALLBOXSIZE else 1500
    elif difficulty == MEDIUM:
        boxesToChange = 5 if boxSize == SMALLBOXSIZE else 200
    else:
        boxesToChange = 0
    for _ in range(boxesToChange):
        x, y = random.randint(1, width - 2), random.randint(1, height - 2)
        direction = random.randint(0, 3)
        if direction == 0:
            board[x - 1][y] = board[x][y]
            board[x][y - 1] = board[x][y]
        elif direction == 1:
            board[x + 1][y] = board[x][y]
            board[x][y + 1] = board[x][y]
        elif direction == 2:
            board[x][y - 1] = board[x][y]
            board[x + 1][y] = board[x][y]
        else:
            board[x][y + 1] = board[x][y]
            board[x - 1][y] = board[x][y]
    return board


def drawLogoAndButtons():
    DISPLAYSURF.blit(LOGOIMAGE, (WINDOWWIDTH - LOGOIMAGE.get_width(), 0))
    DISPLAYSURF.blit(
        SETTINGSBUTTONIMAGE,
        (
            WINDOWWIDTH - SETTINGSBUTTONIMAGE.get_width(),
            WINDOWHEIGHT - SETTINGSBUTTONIMAGE.get_height(),
        ),
    )
    DISPLAYSURF.blit(
        RESETBUTTONIMAGE,
        (
            WINDOWWIDTH - RESETBUTTONIMAGE.get_width(),
            WINDOWHEIGHT
            - SETTINGSBUTTONIMAGE.get_height()
            - RESETBUTTONIMAGE.get_height(),
        ),
    )


def drawBoard(board, transparency=255):
    temp = pygame.Surface(DISPLAYSURF.get_size()).convert_alpha()
    temp.fill((0, 0, 0, 0))
    for x in range(boardWidth):
        for y in range(boardHeight):
            left, top = leftTopPixelCoordOfBox(x, y)
            r, g, b = paletteColors[board[x][y]]
            pygame.draw.rect(
                temp, (r, g, b, transparency), (left, top, boxSize, boxSize)
            )
    left, top = leftTopPixelCoordOfBox(0, 0)
    pygame.draw.rect(
        temp,
        BLACK,
        (left - 1, top - 1, boxSize * boardWidth + 1, boxSize * boardHeight + 1),
        1,
    )
    DISPLAYSURF.blit(temp, (0, 0))


def drawPalettes():
    num = len(paletteColors)
    xmargin = int(
        (WINDOWWIDTH - ((PALETTESIZE * num) + (PALETTEGAPSIZE * (num - 1)))) / 2
    )
    for i in range(num):
        left = xmargin + i * (PALETTESIZE + PALETTEGAPSIZE)
        top = WINDOWHEIGHT - PALETTESIZE - 10
        pygame.draw.rect(
            DISPLAYSURF, paletteColors[i], (left, top, PALETTESIZE, PALETTESIZE)
        )
        pygame.draw.rect(
            DISPLAYSURF,
            bgColor,
            (left + 2, top + 2, PALETTESIZE - 4, PALETTESIZE - 4),
            2,
        )


def drawLifeMeter(currentLife):
    lifeBoxSize = int((WINDOWHEIGHT - 40) / maxLife)
    pygame.draw.rect(DISPLAYSURF, bgColor, (20, 20, 20, 20 + maxLife * lifeBoxSize))
    for i in range(maxLife):
        if currentLife >= (maxLife - i):
            pygame.draw.rect(
                DISPLAYSURF, RED, (20, 20 + i * lifeBoxSize, 20, lifeBoxSize)
            )
        pygame.draw.rect(
            DISPLAYSURF, WHITE, (20, 20 + i * lifeBoxSize, 20, lifeBoxSize), 1
        )


def getColorOfPaletteAt(x, y):
    num = len(paletteColors)
    xmargin = int(
        (WINDOWWIDTH - ((PALETTESIZE * num) + (PALETTEGAPSIZE * (num - 1)))) / 2
    )
    top = WINDOWHEIGHT - PALETTESIZE - 10
    for i in range(num):
        left = xmargin + i * (PALETTESIZE + PALETTEGAPSIZE)
        if pygame.Rect(left, top, PALETTESIZE, PALETTESIZE).collidepoint(x, y):
            return i
    return None


def floodFill(board, oldColor, newColor, x, y):
    if oldColor == newColor or board[x][y] != oldColor:
        return
    board[x][y] = newColor
    if x > 0:
        floodFill(board, oldColor, newColor, x - 1, y)
    if x < boardWidth - 1:
        floodFill(board, oldColor, newColor, x + 1, y)
    if y > 0:
        floodFill(board, oldColor, newColor, x, y - 1)
    if y < boardHeight - 1:
        floodFill(board, oldColor, newColor, x, y + 1)


def leftTopPixelCoordOfBox(bx, by):
    xmargin = int((WINDOWWIDTH - (boardWidth * boxSize)) / 2)
    ymargin = int((WINDOWHEIGHT - (boardHeight * boxSize)) / 2)
    return bx * boxSize + xmargin, by * boxSize + ymargin


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()
