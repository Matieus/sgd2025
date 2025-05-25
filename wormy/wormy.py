# Wormy, by Al Sweigart al@inventwithpython.com
# (Pygame) Lead the green snake around the screen eating red apples.

import random, pygame, sys
from pygame.locals import *

FPS = 15
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
CELLSIZE = 20
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = WINDOWWIDTH // CELLSIZE
CELLHEIGHT = WINDOWHEIGHT // CELLSIZE

#             R    G    B
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARKGREEN = (0, 155, 0)
DARKGRAY = (40, 40, 40)
BGCOLOR = BLACK

UP, DOWN, LEFT, RIGHT = "up", "down", "left", "right"
HEAD = 0  # syntactic sugar: index of the worm's head


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font("freesansbold.ttf", 18)
    pygame.display.set_caption("Wormy")

    showStartScreen()
    while True:
        runGame()
        showGameOverScreen()


def runGame():
    startx = random.randint(5, CELLWIDTH - 6)
    starty = random.randint(5, CELLHEIGHT - 6)
    wormCoords = [
        {"x": startx, "y": starty},
        {"x": startx - 1, "y": starty},
        {"x": startx - 2, "y": starty},
    ]
    direction = RIGHT
    apple = getRandomLocation()

    paused = False  # <<< NEW: stan pauzy

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                elif event.key == K_p:  # <<< NEW
                    paused = not paused
                elif not paused:  # <<< NEW
                    if (event.key in (K_LEFT, K_a)) and direction != RIGHT:
                        direction = LEFT
                    elif (event.key in (K_RIGHT, K_d)) and direction != LEFT:
                        direction = RIGHT
                    elif (event.key in (K_UP, K_w)) and direction != DOWN:
                        direction = UP
                    elif (event.key in (K_DOWN, K_s)) and direction != UP:
                        direction = DOWN

        if paused:  # <<< NEW
            DISPLAYSURF.fill(BGCOLOR)
            drawGrid()
            drawWorm(wormCoords)
            drawApple(apple)
            drawScore(len(wormCoords) - 3)
            drawPause()
            pygame.display.update()
            FPSCLOCK.tick(FPS)
            continue

        if wormCoords[HEAD]["x"] in (-1, CELLWIDTH) or wormCoords[HEAD]["y"] in (
            -1,
            CELLHEIGHT,
        ):
            return  # game over
        for segment in wormCoords[1:]:
            if (
                segment["x"] == wormCoords[HEAD]["x"]
                and segment["y"] == wormCoords[HEAD]["y"]
            ):
                return  # game over

        if wormCoords[HEAD]["x"] == apple["x"] and wormCoords[HEAD]["y"] == apple["y"]:
            apple = getRandomLocation()
        else:
            wormCoords.pop()

        if direction == UP:
            newHead = {"x": wormCoords[HEAD]["x"], "y": wormCoords[HEAD]["y"] - 1}
        elif direction == DOWN:
            newHead = {"x": wormCoords[HEAD]["x"], "y": wormCoords[HEAD]["y"] + 1}
        elif direction == LEFT:
            newHead = {"x": wormCoords[HEAD]["x"] - 1, "y": wormCoords[HEAD]["y"]}
        elif direction == RIGHT:
            newHead = {"x": wormCoords[HEAD]["x"] + 1, "y": wormCoords[HEAD]["y"]}
        wormCoords.insert(0, newHead)

        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        drawWorm(wormCoords)
        drawApple(apple)
        drawScore(len(wormCoords) - 3)
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def drawPause():  # <<< NEW
    pauseSurf = BASICFONT.render("PAUSE", True, WHITE)
    pauseRect = pauseSurf.get_rect()
    pauseRect.center = (WINDOWWIDTH // 2, WINDOWHEIGHT // 2)
    DISPLAYSURF.blit(pauseSurf, pauseRect)


def drawPressKeyMsg():
    surf = BASICFONT.render("Press a key to play.", True, DARKGRAY)
    rect = surf.get_rect()
    rect.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(surf, rect)


def checkForKeyPress():
    if pygame.event.get(QUIT):
        terminate()
    keyUpEvents = pygame.event.get(KEYUP)
    if not keyUpEvents:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key


def showStartScreen():
    titleFont = pygame.font.Font("freesansbold.ttf", 100)
    titleSurf1 = titleFont.render("Wormy!", True, WHITE, DARKGREEN)
    titleSurf2 = titleFont.render("Wormy!", True, GREEN)
    deg1, deg2 = 0, 0
    while True:
        DISPLAYSURF.fill(BGCOLOR)
        rSurf1 = pygame.transform.rotate(titleSurf1, deg1)
        rRect1 = rSurf1.get_rect()
        rRect1.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rSurf1, rRect1)
        rSurf2 = pygame.transform.rotate(titleSurf2, deg2)
        rRect2 = rSurf2.get_rect()
        rRect2.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rSurf2, rRect2)
        drawPressKeyMsg()
        if checkForKeyPress():
            pygame.event.get()  # clear queue
            return
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        deg1 += 3
        deg2 += 7


def terminate():
    pygame.quit()
    sys.exit()


def getRandomLocation():
    return {
        "x": random.randint(0, CELLWIDTH - 1),
        "y": random.randint(0, CELLHEIGHT - 1),
    }


def showGameOverScreen():
    gameOverFont = pygame.font.Font("freesansbold.ttf", 150)
    gameSurf = gameOverFont.render("Game", True, WHITE)
    overSurf = gameOverFont.render("Over", True, WHITE)
    gRect = gameSurf.get_rect()
    gRect.midtop = (WINDOWWIDTH / 2, 10)
    oRect = overSurf.get_rect()
    oRect.midtop = (WINDOWWIDTH / 2, gRect.height + 35)
    DISPLAYSURF.blit(gameSurf, gRect)
    DISPLAYSURF.blit(overSurf, oRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress()
    while True:
        if checkForKeyPress():
            pygame.event.get()
            return


def drawScore(score):
    surf = BASICFONT.render(f"Score: {score}", True, WHITE)
    rect = surf.get_rect()
    rect.topleft = (WINDOWWIDTH - 120, 10)
    DISPLAYSURF.blit(surf, rect)


def drawWorm(coords):
    for c in coords:
        x, y = c["x"] * CELLSIZE, c["y"] * CELLSIZE
        outer = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        inner = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, DARKGREEN, outer)
        pygame.draw.rect(DISPLAYSURF, GREEN, inner)


def drawApple(coord):
    x, y = coord["x"] * CELLSIZE, coord["y"] * CELLSIZE
    pygame.draw.rect(DISPLAYSURF, RED, pygame.Rect(x, y, CELLSIZE, CELLSIZE))


def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE):
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE):
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))


if __name__ == "__main__":
    main()
