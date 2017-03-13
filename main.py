import pygame
from roche import Environment, Planet
from geometry import Vector2D


# =========== START OF SIMULATION CODE ============

(width, height) = (500, 500)
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Gravity Test')

universe = Environment((width, height))
universe.colour = (0,0,0)

sun_radius = 50
sun = Planet((width/2, height/2), sun_radius, density=1)
sun.fixed = True
sun.colour = (255, 255, 0)
universe.planets.append(sun)

planet = Planet((100, 250), 15, density=0.1)
planet.velocity = Vector2D(0, 12)
planet.colour = (100, 100, 255)
universe.planets.append(planet)

dt = 0.01

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    universe.update(dt)
    screen.fill(universe.colour)

    for p in universe.planets:
        # Draws it so that (0,0) is the bottom left corner
        if p.size < 2:
            pygame.draw.rect(screen, p.colour, (int(p.position.x), height - int(p.position.y), 2, 2))
        else:
            pygame.draw.circle(screen, p.colour, (int(p.position.x), height - int(p.position.y)), int(p.size), 0)

    pygame.display.flip()

    pygame.time.delay(int(dt * 1000))

pygame.quit()  # IDLE interpreter friendly