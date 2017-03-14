import pygame
from roche import Environment, Planet
from geometry import Vector2D


# =========== START OF SIMULATION CODE ============

(width, height) = (700, 700)
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Gravity Test')

universe = Environment((width, height))
universe.colour = (0,0,0)

# Setting up pixel-to-kilometre conversion.
# Assuming that this is the Earth-Moon scenario


# 384748 = width/2 - 25
# Hence we will work in km

km = (width/2 - 25)/384748

# This is real life, things are small
earth_radius = 40
earth_mass = 10**30 # kg, approx
earth = Planet((width/2, height/2), earth_radius, earth_mass)
earth.fixed = True
earth.colour = (100, 100, 255)
universe.planets.append(earth)

moon_radius = 10
moon_mass = 10**29 #kg, approx
moon = Planet((25, height/2), moon_radius, moon_mass)
moon.velocity = Vector2D(0, 1)
moon.colour = (100, 100, 100)
universe.planets.append(moon)

# Time between simulation steps, in seconds?
dt = 0.5

# Keeps track of times the loop has run
i = 0

# Time between drawing the trail step in frames. Large values lead to geodesic-esque patterns!
timeStep = 5

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