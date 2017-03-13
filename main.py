import pygame
from roche import Environment, Planet
from geometry import Vector2D


# =========== START OF SIMULATION CODE ============

(width, height) = (700, 700)
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Gravity Test')

universe = Environment((width, height))
universe.colour = (0,0,0)

# Setting up pixel-to-metre conversion.
# Assuming that this is the Sun-Earth scenario

# 1 AU = width/2 - 25
# Hence we will work in AU, as it keeps numbers fairly small

AU = (width/2 - 25)

# This is real life, things are small
sun_radius = 0.00463672*AU
sun = Planet((width/2, height/2), sun_radius, density=1.408)
sun.fixed = True
sun.colour = (255, 255, 0)
universe.planets.append(sun)


planet = Planet((25, height/2), 0.000042473*AU, density=5.514)
planet.velocity = Vector2D(0, 7)
planet.colour = (100, 100, 255)
universe.planets.append(planet)

# Time between simulation steps, in seconds?
dt = 0.01

# Keeps track of times the loop has run
i = 0

# Time between drawing the trail step in frames. Large values lead to geodesic-esque patterns!
timeStep = 10

running = True
while running:

    i += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    universe.update(dt)
    screen.fill(universe.colour)

    for p in universe.planets:

        # ~~~~~ Planet Trail Funtime Code ~~~~~ #

        # Appends the trail list with the particle's current position.
        # For whatever reason, if these two ifs are compiled into one, everything breaks.
        # Hence the double if. 
        if i == timeStep:
            p.appendTrail(height)
        if i > timeStep:
            i = 0

        # If the trail has more than one point (necessary to actually draw a line), draw the trail.
        # Placed prior to the planet drawing code to draw the trail underneath the planet.
        if len(p.trail) > 2:
            pygame.draw.aalines(screen, p.line_colour, False, p.trail, 1)

        # ~~~~~ End Planet Trail Funtime Code ~~~~~ #


        # Draws it so that (0,0) is the bottom left corner
        if p.size < 2:
            pygame.draw.rect(screen, p.colour, (int(p.position.x), height - int(p.position.y), 2, 2))
        else:
            pygame.draw.circle(screen, p.colour, (int(p.position.x), height - int(p.position.y)), int(p.size), 0)


        


    pygame.display.flip()

    # pygame.time.delay(int(dt * 1000))

pygame.quit()  # IDLE interpreter friendly