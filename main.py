import pygame

class Environment:
    """ Defines the boundary of a simulation and its properties """

    def __init__(self, (width, height)):
        self.width = width
        self.height = height

(width, height) = (800, 800)
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Gravity Test')

universe = Environment((width, height))
universe.colour = (0,0,0)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(universe.colour)
    pygame.display.flip()