import pygame, math, random
from roche import Environment, Body
from geometry import Vector2D


# =========== START OF SIMULATION CODE ============

(width, height) = (1300, 700)
screen = pygame.display.set_mode((width, height))
pygame.display.set_icon(pygame.image.load('sigurdson_kris.png'))
pygame.display.set_caption('Roche Limit')

pygame.font.init()
# font = pygame.font.SysFont('Sans', 60)

clock = pygame.time.Clock()



# Defines distance from the sides of the screen the orbit can be, in pixels.
hmargin = 25
vmargin = 25


# Input Coordinates for Moon's orbit
# Essentially the 'user input' for this simulation.
# Earth's radius is 6 371 000 m for reference.

# May transition to scientific notation in the future...

# The apoapsis (apogee in Earth-Moon system) is the highest point in an orbit, 
# input in metres from centre body's core. The Moon's apogee IRL is 4.054 * 10**8 m.
apoapsis = 5.00e7

# The periapsis (perigee in Earth-Moon system) is the lowest point in an orbit, 
# input in metres from centre body's core. The Moon's perigee IRL is 3.626 * 10**8 m.
periapsis = 5.00e7

# Because I have definitely input a smaller value for the apoapsis before.
if apoapsis < periapsis:
    apoapsis, periapsis = periapsis, apoapsis

# To get the COM orbiting, we have to reduce the calculated speed.
SPEED_REDUCER = 0.7

# Pixel-to-Metre conversion.

# As we already defined the apoapsis, we'll use its height as our base 
# 'kilometre unit' by which we can convert to and from pixels to metres at will.


m = (apoapsis + periapsis)/(float(width - 2 * hmargin)) # in m / pixel


# I have the if statement there to check if the height of the window will be too
# small for the orbit. The program then adjusts the horizontal margin to fit
# properly 

if 2 * (apoapsis * periapsis)**0.5/m > height - 2 * vmargin:
    m = 2 * (apoapsis * periapsis)**0.5 / float(height - 2 * vmargin)
    hmargin = abs((width - (apoapsis + periapsis)/ m )/2)
    

# This G is in pixels
G = (6.674e-11)/m**3

moon_radius = 1737500 / m # in km, converted to pixels
universe = Environment((width, height), moon_radius)
universe.colour = (0,0,0)

earth_radius = 6371000 / m # in metres, converted to pixels through m
earth_mass = 5.972e24 # kg
earth = Body((hmargin + (apoapsis / m), height / 2), earth_radius, earth_mass)
earth.fixed = True
earth.colour = (100, 100, 255) # baby blue
universe.origin = earth

# percentage mass that the moon has
MOON_FRACTION = 0.9

moon_mass = 7.348e22 # kg
centerPos = Vector2D(hmargin, height/2)
moon = Body((centerPos.x, centerPos.y), MOON_FRACTION * moon_radius, MOON_FRACTION * moon_mass)

# create N bodies around the Moon
bodies = []
N = 100
for i in range(N):
    angle = random.uniform(0, 2 * math.pi)
    radius = random.uniform(moon_radius, 2*moon_radius)
    pos = centerPos + Vector2D.create_from_angle(angle, radius)
    body = Body((pos.x, pos.y), 0.1 * moon_radius, (1 - MOON_FRACTION) / N * moon_mass)
    bodies.append(body)


# Based on the periapsis and apoapsis from earlier, this will provide the Moon
# with an initial velocity to make said orbit. We'll assume that the Moon's
# starting location is at the apoapsis, on the left side of the screen.

v = ((2 * m**3 * G * (earth_mass + moon_mass)) *
    ((1 / apoapsis) - (1 / (periapsis + apoapsis))))**0.5

v = SPEED_REDUCER*v

moon.velocity = Vector2D(0, - v/m) #m/s
for body in bodies:
    body.velocity = Vector2D(0, - v/m) #m/s

moon.colour = (100, 100, 100)
universe.bodies.append(moon)
for body in bodies:
    universe.bodies.append(body)

# Time between simulation steps, increase to increase speed of moon. In ms.
dt = 100

# Time scale factor
TIME_SCALE = 0.0001

# Keeps track of times the loop has run
i = 0

# Time between drawing the trail step in frames. Large values lead to geodesic-esque patterns!
line_period = 5


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

    # ~~~~~ Planet Trail Drawing Code ~~~~~ #

    # Placed prior to the planet drawing code to draw the trail underneath the planet.

    # Appends the trail list with the particle's current position.
    # For whatever reason, if these two ifs are compiled into one, everything breaks.
    # Hence the double if. 
    # if i == line_period:
    #     moon.appendTrail(height)
    # if i > line_period:
    #     i = 0

    # If the trail has more than one point (necessary to actually make a line), draw the trail.
    # if len(moon.trail) > 1:
    #     pygame.draw.aalines(screen, moon.line_colour, False, moon.trail)

    if i == line_period:
        universe.appendCOMTrail()
        i = 0

    if len(universe.trail) > 1:
        pygame.draw.aalines(screen, moon.line_colour, False, universe.trail)


    # ~~~~~ End Planet Trail Drawing Code ~~~~~ #

    # Draw origin body
    pygame.draw.aalines(screen, universe.origin.colour, True, universe.origin.findOutline(height, 1), 1)
    pygame.draw.aalines(screen, universe.origin.colour, True, universe.origin.findOutline(height, 0), 1)

    pygame.draw.circle(screen, universe.origin.colour, (int(universe.origin.position.x), height - int(universe.origin.position.y)), int(universe.origin.size), 0)


    for p in universe.bodies:

        # I may have got text working
        if moon.areWeDead(earth) == True:
            # screen.blit(font.render('YOU KILLED', True, (255,0,0), (255,255,255)), (100, 400))
            # screen.blit(font.render('EVERYONE', True, (255,0,0), (255,255,255)), (110, 465))
            print "YOU KILLED EVERYONE!"


        # Draws it so that (0,0) is the bottom left corner
        if p.size < 2:
            pygame.draw.rect(screen, p.colour, (int(p.position.x), height - int(p.position.y), 2, 2))
        else:
            
            # Draws pretty anti-aliased outlines for each body.
            # There are two lines to make the outline a bit thicker.
            pygame.draw.aalines(screen, p.colour, True, p.findOutline(height, 1), 1)
            pygame.draw.aalines(screen, p.colour, True, p.findOutline(height, 0), 1)

            pygame.draw.circle(screen, p.colour, (int(p.position.x), height - int(p.position.y)), int(p.size), 0)

        pygame.draw.rect(screen, p.line_colour, (universe.COM.x, height - universe.COM.y, 5, 5), 0)

    pygame.display.flip()

    pygame.time.delay(int(TIME_SCALE * dt * 1000))

pygame.quit()  # IDLE interpreter friendly
