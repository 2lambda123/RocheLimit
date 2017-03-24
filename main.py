import pygame
from roche import Environment, Planet
from geometry import Vector2D


# =========== START OF SIMULATION CODE ============

(width, height) = (700, 700)
screen = pygame.display.set_mode((width, height))
pygame.display.set_icon(pygame.image.load('sigurdson_kris.png'))
pygame.display.set_caption('Gravity Test')

pygame.font.init()
font = pygame.font.SysFont('Sans', 60)

clock = pygame.time.Clock()

universe = Environment((width, height))
universe.colour = (0,0,0)


# Input Coordinates for Moon's orbit

# The apoapsis (apogee in Earth-Moon system) is the highest point in an orbit, input in kilometres from centre body's core.
# IRL the Moon's apogee is 405400000 m.
apoapsis = 100000000.

# The periapsis (perogee in Earth-Moon system) is the lowest point in an orbit, input in kilometres from centre body's core.
# IRL the Moon's perigee is 362600000 m.
periapsis = 362600.

# Because I have definitely input a smaller value for the apoapsis before
if apoapsis < periapsis:
    temp = apoapsis
    apoapsis = periapsis
    periapsis = temp



# Setting up pixel-to-metre conversion.
# Assuming that this is the Earth-Moon scenario

# We'll use the height of the Moon's orbit as our base 'kilometre unit' by which we multiply all length values by.
# 384 748 000 metres = width/2 - 25 pixels

m = apoapsis/(float(width) / 2 - 25.)
print m
# This is what we multiply to every distance in pixels to convert it to metres.

# Orbit Paramatizer
# A tool such that we can specify initial orbit requirements and it will provide the Moon with a velocity and initial height to make said orbit.
# We'll assume that the Moon's starting location is at the apoapsis.


# This G is in pixels
G = (6.674*10**-11)/m**3


# The Earth and Moon aren't really this large wrt each other, but I made them big so that we can see them.
# Go play Orbiter for excessive physical accuracy.
earth_radius = 6371000 / m # in metres, converted to pixels through m
earth_mass = 5.972*10**24 # kg
earth = Planet((width/2, height/2), earth_radius, earth_mass)
earth.fixed = True
earth.colour = (100, 100, 255)
universe.planets.append(earth)



# Parametarize Moon's Orbit
# Find semi-major axis
a = ( periapsis + apoapsis ) / 2
print a

# Find necessary initial velocity to produce said orbit
v = ((m**3 * G * earth_mass) * ((2 / apoapsis) - (1 / a)))**0.5
print v, ' m/s'

moon_radius = 1737500 / m
moon_mass = 7.348*10**22 # kg
moon = Planet((25, height/2), moon_radius, moon_mass)
moon.velocity = Vector2D(0, v/m) #m/s)
moon.colour = (100, 100, 100)
universe.planets.append(moon)

# Time between simulation steps, increase to increase speed of moon
dt = 50

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

    universe.update(G, dt)
    screen.fill(universe.colour)


    for p in universe.planets:

        # ~~~~~ Planet Trail Drawing Code ~~~~~ #

        # Placed prior to the planet drawing code to draw the trail underneath the planet.

        # Appends the trail list with the particle's current position.
        # For whatever reason, if these two ifs are compiled into one, everything breaks.
        # Hence the double if. 
        if i == timeStep:
            p.appendTrail(height)
        if i > timeStep:
            i = 0

        # If the trail has more than one point (necessary to actually make a line), draw the trail.
        if len(p.trail) > 1:
            pygame.draw.lines(screen, p.line_colour, False, p.trail)

        # ~~~~~ End Planet Trail Drawing Code ~~~~~ #

        death = moon.areWeDead(earth)
        if death == True:
            screen.blit(font.render('YOU KILLED', True, (255,0,0), (255,255,255)), (100, 400))
            screen.blit(font.render('EVERYONE', True, (255,0,0), (255,255,255)), (110, 465))


        # Draws it so that (0,0) is the bottom left corner
        if p.size < 2:
            pygame.draw.rect(screen, p.colour, (int(p.position.x), height - int(p.position.y), 2, 2))
        else:
            
            # Draws pretty anti-aliased outlines for each body.
            # There are two lines to make the outline a bit thicker.
            pygame.draw.aalines(screen, p.colour, True, p.findOutline(height, 1), 1)
            pygame.draw.aalines(screen, p.colour, True, p.findOutline(height, 0), 1)

            pygame.draw.circle(screen, p.colour, (int(p.position.x), height - int(p.position.y)), int(p.size), 0)


    pygame.display.flip()

    # pygame.time.delay(int(dt * 1000))

pygame.quit()  # IDLE interpreter friendly