import math as m
import random as rand
import pygame


def randcol():
    """Gives a random colour (not black)."""
    return (rand.randint(20, 255), rand.randint(20, 255), rand.randint(20, 255))


def momentum(Spherex):
    """Calculates momentum of a given sphere."""
    return float(((m.pi * Spherex.rad**2) * Spherex.Vx) + ((m.pi * Spherex.rad**2) * Spherex.Vy))


def kinetic(Spherex):
    """Calculates kinetic energy a given sphere has."""
    return float(0.5 * (Spherex.mass) * (m.sqrt((Spherex.Vx**2) + (Spherex.Vy**2)))**2)


# Collision mathematics from first principles
def dotproductcoeff(M, N, O, P):
    # C
    return float(((M * O) + (N * P)) / (O**2 + P**2))


def masscoeff(p1mass, p2mass):
    # B
    return (2 * p2mass) / (p1mass + p2mass)


def coeffs(p1, p2):
    # BC of inputted variable
    return masscoeff(p1.mass, p2.mass) * (
        dotproductcoeff((p1.Vx - p2.Vx), (p1.Vy - p2.Vy), (p1.x - p2.x), (p1.y - p2.y))
    )


def resolve_collision(p1, p2):
    """
    Resolves 2D elastic impulse and updates velocities and positions
    to prevent overlap at slow velocities.
    """
    # Following sheet explaining collisions:
    newp1vx = p1.Vx - (coeffs(p1, p2) * (p1.x - p2.x))  # setting the new vectors
    newp1vy = p1.Vy - (coeffs(p1, p2) * (p1.y - p2.y))
    # the equation is the exact same for the second particle, just flipped inputs:
    newp2vx = p2.Vx - (coeffs(p2, p1) * (p2.x - p1.x))
    newp2vy = p2.Vy - (coeffs(p2, p1) * (p2.y - p1.y))

    # setting the new vectors:
    p1.Vx = newp1vx
    p1.Vy = newp1vy
    p2.Vx = newp2vx
    p2.Vy = newp2vy

    # there is a bug where they travel too slow and glitch. this is similar to the wall bug at slow velocities.
    # so this moves them a pixel apart to stop that occuring.
    if p1.x > p2.x:
        p1.x += p1.Vx
    else:
        p2.x += 1

    if p1.y > p2.y:
        p1.y += 1
    else:
        p2.y += 1


class circle:
    """Set up class for circles."""
    def __init__(self, ID, rad, Vx, Vy, x, y, col):
        # local ID, global ID, radius, x vector, y vector, x position, y position, colour
        self.ID = ID
        self.rad = rad
        self.mass = m.pi * rad**2  # this works as all density is the same
        self.Vx = Vx
        self.Vy = Vy
        self.x = x
        self.y = y
        self.col = col

    def veltick(self, airdrag, dt, gravitytog=False, gravity=9.81):
        self.Vx = self.Vx * airdrag  # if there is air drag set then it will coefficient the vectors and reduce the speed.
        self.Vy = self.Vy * airdrag
        self.x += self.Vx * dt  # increase/decrease the position with the vector with each iteration.
        self.y += self.Vy * dt  # this will be called every tick in order to have a time component and thus movement.
        if gravitytog:
            self.Vy += gravity * 0.01  # gravity toggle


class button:
    """Interactive button class."""
    def __init__(self, text, x, y, width, height, inactive_color, active_color, tick, function, spamcount):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.inactive_color = inactive_color  # light gray colour
        self.active_color = active_color      # dark gray colour
        self.tick = tick
        self.function = function
        self.spamcount = spamcount            # spamcounter

    def buttondraw(self, screen, font, mouse_pos, mbd, text_color=(255, 255, 255)):
        """Draws and executes upon click."""
        self.spamcount -= 1  # spamcounter ticker

        if self.x < mouse_pos[0] < self.x + self.width and self.y < mouse_pos[1] < self.y + self.height:  # if mouse hovering
            pygame.draw.rect(screen, self.active_color, (self.x, self.y, self.width, self.height))        # draw with dark gray
            textsurface = font.render(self.text, False, text_color)                                       # enter the text into the button
            screen.blit(textsurface, (self.x + 5, self.y + 1))

            if mbd and self.spamcount < 2:  # if spamcount is reduced enough and the mbd is true
                self.function(self.tick)    # tick the respective function
                self.spamcount = 25
            elif not mbd:
                self.spamcount = 0          # reset spamcount
        else:
            pygame.draw.rect(screen, self.inactive_color, (self.x, self.y, self.width, self.height))     # draw with light gray
            textsurface = font.render(self.text, False, text_color)
            screen.blit(textsurface, (self.x + 5, self.y + 1))