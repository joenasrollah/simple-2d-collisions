import sys
import os
import time
import math as m
import random as rand
from time import process_time
import pygame

# Ensure local module imports resolve regardless of working directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from engine import circle, button, randcol, momentum, kinetic, resolve_collision

pygame.init()

screenx = 1000  # screen width
screeny = 608   # screen height
screen = pygame.display.set_mode((screenx + 400, screeny))  # set screen config
pygame.display.set_caption("2D Rigid-Body Physics Engine")

# constants and colours ----------------------------------------------------------------
yellow = (228, 208, 10)
red = (200, 0, 0)
white = (255, 255, 255)
bkgclr = (10, 108, 3)
black = (0, 0, 0)
buttonhover = (50, 50, 50)
buttonidle = (100, 100, 100)

announcego = 100  # starting countdown for pause in Shoot! command
shootpower = potted = spamcount = 0  # declaring global variables used in functions
tempvarmbdd = wballpot = mbd = kbd = vecindicator = gravitytog = False  # user inputs starting false

gravity = 9.81  # gravity (not to scale at all and just for a constant)

Font = pygame.font.SysFont('Arial', 30)
Fontsmall = pygame.font.SysFont('Arial', 22)

totmomen = totkinetic = 0  # beginning values for system kinetic and momentum

WallDrag = -1  # simulates lost kinetic energy upon collision with walls and floor
shapes = []    # list of shapes
clist = []     # list of colliding objects in collision equation

mousestrength = 0.00025  # how strong the mouse is for pulling objects
airdrag = 1              # set to below 1 to cause drag in regular sim
framecap = 1 / 120
# --------------------------------------------------------------------------------------


def wallcoll(Spherex):
    """Flips velocity on wall collision to bounce at incident angle."""
    # right wall and pot basket walls
    if Spherex.x + Spherex.rad > screenx and Spherex.x < screenx + 20:  # bounce off right green wall if not potted
        Spherex.Vx = Spherex.Vx * WallDrag
        if Spherex.x < (screenx + 20):  # fix gliding glitch when in pool mode and ball potted
            Spherex.x -= 1

    if Spherex.x - Spherex.rad < screenx + 21 and Spherex.x + Spherex.rad > screenx + 20:
        # bounce ball off the left black wall when in pot basket
        Spherex.Vx = Spherex.Vx * WallDrag

    if Spherex.x + Spherex.rad > screenx + 400:  # bounce off right black wall in pool mode when in pot basket
        Spherex.Vx = Spherex.Vx * WallDrag
        if Spherex.x > (screenx + 400):  # fix gliding glitch on right black wall
            Spherex.x -= 1

    # three other walls in green normal mode
    if Spherex.x - Spherex.rad < 0:
        Spherex.Vx = Spherex.Vx * WallDrag
        Spherex.x += 1

    if Spherex.y + Spherex.rad > screeny:
        Spherex.Vy = Spherex.Vy * WallDrag
        Spherex.y -= 1

    if Spherex.y - Spherex.rad < 0:
        Spherex.Vy = Spherex.Vy * WallDrag
        Spherex.y += 1


def pot(Spherex):
    """Teleports potted ball into basket on right of screen."""
    global wballpot, potted, ballcount
    if Spherex == shapes[15]:  # if white ball is potted...
        print("WHITE POTTED")
        Spherex.x = -25000     # set x far away so it is hidden but active
        Spherex.y = screeny / 2
        Spherex.Vx = Spherex.Vy = 0
        wballpot = True
    else:
        Spherex.Vx = Spherex.Vy = 2  # boost to simulate dropping into basket
        Spherex.x = screenx + 100
        Spherex.y = 200
        potted += 1
        ballcount -= 1


# UI Button Tick Functions ------------------------------------------------------------
def mousestrengthtick(tick):
    global mousestrength
    if mousestrength >= 0.000025:
        mousestrength += tick
    else:
        mousestrength = 0.000025


def airdragtick(tick):
    global airdrag
    if airdrag == 1:
        airdrag -= 0.001
    elif 0 < airdrag < 1:
        airdrag += tick
    else:
        airdrag = 0.999


def vecindtick(tick):
    global vecindicator
    vecindicator = tick


def gravitytogfunc(tick):
    global gravitytog
    gravitytog = tick


msbuttonneg = button("-", screenx + 250, 30, 25, 25, buttonidle, buttonhover, -0.0001, mousestrengthtick, 0)
msbuttonpos = button("+", screenx + 280, 30, 25, 25, buttonidle, buttonhover, 0.0001, mousestrengthtick, 0)

adbuttonneg = button("-", screenx + 250, 125, 25, 25, buttonidle, buttonhover, 0.001, airdragtick, 0)
adbuttonpos = button("+", screenx + 280, 125, 25, 25, buttonidle, buttonhover, -0.001, airdragtick, 0)

vecindon = button("On", screenx + 15, 570, 40, 25, buttonidle, buttonhover, True, vecindtick, 0)
vecindoff = button("Off", screenx + 65, 570, 40, 25, buttonidle, buttonhover, False, vecindtick, 0)

gravityonbut = button("On", screenx + 290, 570, 40, 25, buttonidle, buttonhover, True, gravitytogfunc, 0)
gravityoffbut = button("Off", screenx + 340, 570, 40, 25, buttonidle, buttonhover, False, gravitytogfunc, 0)

buttons = [msbuttonpos, msbuttonneg, adbuttonneg, adbuttonpos, vecindon, vecindoff, gravityonbut, gravityoffbut]
# --------------------------------------------------------------------------------------


# Mode Initialisation
startspawninput = input("Manual or Auto Simulation (M/A) or Billiards Game (P): ").strip().upper()

if startspawninput == "M":
    ballcount = int(input("How many balls? (int): "))
    sizeBoundLow = int(input("Lower Bound for random ball size? (px): "))
    sizeBoundHigh = int(input("Higher Bound for random ball size? (px): "))
    spawnVelLow = float(input("Lower Bound for spawn velocity? (float, neg incl.): "))
    spawnVelHigh = float(input("Higher Bound for spawn velocity? (float): "))
    colpick = input("Random colour, or input yourself? (random,choose): ").strip().lower()
    mousestrength = float(input("input mouse strength, 1 being default: ")) * 0.00025
    airdrag = float(input("airdrag (1000 default, 1000 -> 0): ")) * 0.001
    framecap = float(1 / int(input("frame rate cap, default 100: ")))

    if colpick == "random":
        for i in range(ballcount):
            shapes.append(circle(
                i, rand.randint(sizeBoundLow, sizeBoundHigh),
                0.1 * rand.randint(int(spawnVelLow), int(spawnVelHigh)),
                0.1 * rand.randint(int(spawnVelLow), int(spawnVelHigh)),
                rand.randint(50, screenx - 50), rand.randint(50, screeny - 50), randcol()
            ))
    elif colpick == "choose":
        coldecr = int(input("Give red values as int (0-254): "))
        coldecg = int(input("Give green values as int (0-254): "))
        coldecb = int(input("Give blue values as int (0-254): "))
        for i in range(ballcount):
            shapes.append(circle(
                i, rand.randint(sizeBoundLow, sizeBoundHigh),
                0.1 * rand.randint(int(spawnVelLow), int(spawnVelHigh)),
                0.1 * rand.randint(int(spawnVelLow), int(spawnVelHigh)),
                rand.randint(50, screenx - 50), rand.randint(50, screeny - 50),
                (coldecr, coldecg, coldecb)
            ))
    else:
        print("incorrect input")

elif startspawninput == "A":
    sizeBoundLow = 20
    sizeBoundHigh = 20
    spawnVelLow = -9
    spawnVelHigh = 9
    ballcount = rand.randint(5, 10)
    for i in range(ballcount):
        shapes.append(circle(
            i, rand.randint(sizeBoundLow, sizeBoundHigh),
            0.1 * rand.randint(spawnVelLow, spawnVelHigh),
            0.1 * rand.randint(spawnVelLow, spawnVelHigh),
            rand.randint(50, screenx - 50), rand.randint(50, screeny - 50), randcol()
        ))

elif startspawninput == "P":
    # pool spawn
    ballcount = 16
    airdrag = 0.999
    WallDrag = -0.95
    shapes.append(circle(1, 20, 0, 0, 960, 200, red))
    shapes.append(circle(2, 20, 0, 0, 960, 242, yellow))
    shapes.append(circle(3, 20, 0, 0, 960, 284, red))
    shapes.append(circle(4, 20, 0, 0, 960, 326, yellow))
    shapes.append(circle(5, 20, 0, 0, 960, 368, red))
    shapes.append(circle(6, 20, 0, 0, 920, 222, yellow))
    shapes.append(circle(7, 20, 0, 0, 920, 264, red))
    shapes.append(circle(8, 20, 0, 0, 920, 306, yellow))
    shapes.append(circle(9, 20, 0, 0, 920, 348, red))
    shapes.append(circle(10, 20, 0, 0, 880, 242, yellow))
    shapes.append(circle(11, 20, 0, 0, 880, 284, black))
    shapes.append(circle(12, 20, 0, 0, 880, 326, yellow))
    shapes.append(circle(13, 20, 0, 0, 840, 264, red))
    shapes.append(circle(14, 20, 0, 0, 840, 306, yellow))
    shapes.append(circle(15, 20, 0, 0, 800, 286, red))
    shapes.append(circle(0, 20, 0, 0, 300, 286, white))

active = True
clock = pygame.time.Clock()
held = ""

while active:
    dt = clock.tick(60)
    tstart = process_time()
    pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if pygame.mouse.get_pressed(num_buttons=3)[0]:
        mbd = True
    else:
        mbd = False

    if pygame.key.get_pressed()[pygame.K_d]:
        kbd = True
    else:
        kbd = False

    screen.fill(bkgclr)

    fps = clock.get_fps()
    textsurface = Font.render("Fps: " + str(m.ceil(fps)), False, white)
    screen.blit(textsurface, (45, 5))

    totmomen = 0
    totkinetic = 0

    # Wall collisions
    for i in range(len(shapes)):
        wallcoll(shapes[i])

    # Circle-circle collision detection
    for i in range(len(shapes)):
        p1 = shapes[i]
        for j in range(len(shapes)):
            p2 = shapes[j]
            if p1 != p2 and clist.count(p1.ID) == 0 and clist.count(p2.ID) == 0:
                if m.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2) <= (p1.rad + p2.rad):
                    clist.append(p1.ID)
                    clist.append(p2.ID)
                    resolve_collision(p1, p2)

    clist = []

    # Calculate total momentum
    for i in range(len(shapes)):
        Spherex = shapes[i]
        if startspawninput == "P":
            if Spherex.x < screenx + 2:
                totmomen += momentum(Spherex)
        else:
            totmomen += momentum(Spherex)

    # Mouse drag interactions for free simulation
    if startspawninput != "P":
        if not mbd:
            held = ""
        if held == "":
            for i in range(len(shapes)):
                Spherex = shapes[i]
                mx = pos[0]
                my = pos[1]
                if ((mx - Spherex.x)**2) + ((my - Spherex.y)**2) < Spherex.rad**2 and mbd:
                    held = Spherex
                if mbd and held == Spherex:
                    accx = Spherex.x - mx
                    accy = Spherex.y - my
                    Spherex.Vx = Spherex.Vx * 0.99 - accx * mousestrength
                    Spherex.Vy = Spherex.Vy * 0.99 - accy * mousestrength
                    pygame.draw.line(screen, black, (Spherex.x, Spherex.y), (mx, my))
        elif mbd:
            Spherex = held
            mx = pos[0]
            my = pos[1]
            if held == Spherex:
                accx = Spherex.x - mx
                accy = Spherex.y - my
                Spherex.Vx = Spherex.Vx * 0.99 - accx * mousestrength
                Spherex.Vy = Spherex.Vy * 0.99 - accy * mousestrength
                pygame.draw.line(screen, black, (Spherex.x, Spherex.y), (mx, my))

    # Calculate total kinetic energy
    for i in range(len(shapes)):
        Spherex = shapes[i]
        if startspawninput == "P":
            if Spherex.x < screenx + 2:
                totkinetic += kinetic(Spherex)
        else:
            totkinetic += kinetic(Spherex)

    # Pool shooting controls
    if startspawninput == "P":
        if totkinetic < 0.002:
            wball = shapes[15]
            if wballpot:
                wball.x = 300
                wballpot = False

            if wball.x < screenx - 100:
                textsurface = Font.render("Shoot! ", False, white)
                screen.blit(textsurface, (wball.x + 25, wball.y - 7))
            else:
                textsurface = Font.render("Shoot! ", False, white)
                screen.blit(textsurface, (wball.x - 90, wball.y - 7))

            if wball.y < screeny - 50:
                textsurface = Font.render(str(m.ceil(shootpower * 10000) / 10), False, white)
                screen.blit(textsurface, (wball.x - 12, wball.y + 20))
            else:
                textsurface = Font.render(str(m.ceil(shootpower * 10000) / 10), False, white)
                screen.blit(textsurface, (wball.x - 12, wball.y - 37))

            mx = pos[0]
            my = pos[1]
            if mbd:
                tempvarmbdd = True
                if shootpower <= 0.015:
                    shootpower = (shootpower + 0.000015) * 1.006
                pygame.draw.line(screen, black, (wball.x, wball.y), (mx, my))

            if not mbd and tempvarmbdd:
                tempvarmbdd = False
                accx = 0.1 * (wball.x - mx)
                accy = 0.1 * (wball.y - my)
                wball.Vx = wball.Vx * 0.97 - accx * shootpower * 10
                wball.Vy = wball.Vy * 0.97 - accy * shootpower * 10
                shootpower = 0

    if vecindicator:
        for i in range(len(shapes)):
            Spherex = shapes[i]
            pygame.draw.line(screen, white, (Spherex.x, Spherex.y), ((Spherex.x + (Spherex.Vx * 100)), (Spherex.y + (Spherex.Vy * 100))))

    # Velocity integration
    for i in range(len(shapes)):
        Spherex = shapes[i]
        if startspawninput == "P":
            if Spherex.Vx > 0:
                Spherex.Vx = (Spherex.Vx - 0.0005) * 0.996
            if Spherex.Vy > 0:
                Spherex.Vy = (Spherex.Vy - 0.0005) * 0.996
            if Spherex.Vx < 0:
                Spherex.Vx = (Spherex.Vx + 0.0005) * 0.996
            if Spherex.Vy < 0:
                Spherex.Vy = (Spherex.Vy + 0.0005) * 0.996
            Spherex.x += Spherex.Vx
            Spherex.y += Spherex.Vy
            if Spherex.x > (screenx + 20):
                Spherex.Vy += gravity * 0.01
        else:
            Spherex.veltick(airdrag, dt, gravitytog, gravity)

    if startspawninput != "P":
        if kbd and spamcount < 2:
            shapes.append(circle(len(shapes), rand.randint(sizeBoundLow, sizeBoundHigh),
                                 0.1 * rand.randint(int(spawnVelLow), int(spawnVelHigh)),
                                 0.1 * rand.randint(int(spawnVelLow), int(spawnVelHigh)),
                                 pos[0], pos[1], white))
            ballcount += 1
            spamcount = 50
        elif not kbd:
            spamcount = 0
        spamcount -= 1

    # Pocket detection
    if startspawninput == "P":
        for i in range(len(shapes)):
            Spherex = shapes[i]
            if Spherex.x < screenx:
                if m.sqrt((Spherex.x - 0)**2 + (Spherex.y - 0)**2) <= 43:
                    pot(Spherex)
                if m.sqrt((Spherex.x - screenx / 2)**2 + (Spherex.y + 10)**2) <= 40:
                    pot(Spherex)
                if m.sqrt((Spherex.x - screenx)**2 + (Spherex.y - 0)**2) <= 43:
                    pot(Spherex)
                if m.sqrt((Spherex.x - 0)**2 + (Spherex.y - screeny)**2) <= 43:
                    pot(Spherex)
                if m.sqrt((Spherex.x - screenx / 2)**2 + (Spherex.y - screeny - 10)**2) <= 40:
                    pot(Spherex)
                if m.sqrt((Spherex.x - screenx)**2 + (Spherex.y - screeny)**2) <= 43:
                    pot(Spherex)

        pygame.draw.circle(screen, black, (0, 0), 40)
        pygame.draw.circle(screen, black, (int(screenx / 2), 0), 32)
        pygame.draw.circle(screen, black, (screenx, 0), 40)
        pygame.draw.circle(screen, black, (0, screeny), 40)
        pygame.draw.circle(screen, black, (int(screenx / 2), screeny), 32)
        pygame.draw.circle(screen, black, (screenx, screeny), 40)

    # Configuration panel
    pygame.draw.line(screen, white, (screenx, 0), (screenx, screeny), 10)
    pygame.draw.rect(screen, black, pygame.Rect(screenx, 0, screenx + 400, screeny))

    textsurface = Font.render("Ball Count: " + str(ballcount), False, white)
    screen.blit(textsurface, (screenx + 15, 5))

    textsurface = Font.render("Mouse Strength: " + str(m.ceil(mousestrength * 10000) / 10), False, white)
    screen.blit(textsurface, (screenx + 15, 35))

    textsurface = Font.render("Momentum: " + str(m.ceil(totmomen * 10000) / 10000), False, white)
    screen.blit(textsurface, (screenx + 15, 65))

    textsurface = Font.render("Kinetic Energy: " + str(m.ceil(totkinetic * 10000) / 10000), False, white)
    screen.blit(textsurface, (screenx + 15, 95))

    textsurface = Font.render("Drag: " + str(m.ceil(((1 / airdrag) - 1) * 10000) / 10000), False, white)
    screen.blit(textsurface, (screenx + 15, 125))

    if startspawninput != "P":
        textsurface = Font.render("Press D to spawn ball!", False, white)
        screen.blit(textsurface, (screenx + 15, 455))

        for i in range(len(buttons)):
            buttons[i].buttondraw(screen, Font, pos, mbd)

        textsurface = Font.render("Velocity Indicator", False, white)
        screen.blit(textsurface, (screenx + 15, 540))

        textsurface = Font.render("Gravity", False, white)
        screen.blit(textsurface, (screenx + 290, 540))

    if startspawninput == "P":
        textsurface = Font.render("Power: " + str(m.ceil(shootpower * 10000) / 10), False, white)
        screen.blit(textsurface, (screenx + 15, 155))

        textsurface = Font.render("Potted: " + str(potted), False, white)
        screen.blit(textsurface, (screenx + 15, 185))

        if wballpot:
            textsurface = Font.render("White Potted!", False, white)
            screen.blit(textsurface, (int(screenx / 2 - 70), 60))

        textsurface = Fontsmall.render("To shoot, hold the left mouse button down", False, white)
        screen.blit(textsurface, (screenx + 15, 250))
        textsurface = Fontsmall.render("anywhere on the screen and release!", False, white)
        screen.blit(textsurface, (screenx + 15, 270))

    # Render spheres
    for i in range(len(shapes)):
        Spherex = shapes[i]
        pygame.draw.circle(screen, black, (int(Spherex.x), int(Spherex.y)), Spherex.rad, round(Spherex.rad * 0.25))
        pygame.draw.circle(screen, Spherex.col, (int(Spherex.x), int(Spherex.y)), int(Spherex.rad * 0.8))
        if Spherex.col == black and startspawninput == "P":
            textsurface = Font.render("8", False, white)
            screen.blit(textsurface, (Spherex.x - 6, Spherex.y - 7))

    pygame.display.update()