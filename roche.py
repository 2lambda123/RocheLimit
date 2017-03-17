import math
import random
from geometry import Vector2D

# Gravitational Constant
G = (6.674*10**-11)/(384748)**3


class Environment:
    """ Defines the boundary of a simulation and its properties """

    def __init__(self, (width, height)):
        self.width = width
        self.height = height
        self.colour = (255, 255, 255)
        self.planets = []

    def addPlanets(self, n=1, **kargs):
        """ Add n planets with properties given by keyword arguments """

        for i in range(n):
            size = kargs.get('size', random.randint(10, 20))
            if 'density' in kargs:
                density = kargs.get('density', 1)
                mass = density * (size ** 2)
            else:
                mass = kargs.get('mass', random.randint(100, 10000))

            x = kargs.get('x', random.uniform(size, self.width - size))
            y = kargs.get('y', random.uniform(size, self.height - size))

            planet = Planet((x, y), size, mass)
            speed = kargs.get('speed', random.random())
            angle = kargs.get('angle', random.uniform(0, math.pi * 2))
            planet.velocity = Vector2D.create_from_angle(angle, speed)
            planet.colour = kargs.get('colour', (0, 0, 255))

            self.planets.append(planet)

    def update(self, dt=0.01):
        """  Calls particle functions """

        for i, planet in enumerate(self.planets):
            # One planet functions get called here
            # planet.move()

            # # Two planet functions get called here
            for planet2 in self.planets[i + 1:]:
            #     planet.attract(planet2)
                planet.verlet(planet2, dt)
                planet2.verlet(planet, dt)


class Planet:
    """ A circular planet with a velocity, size and density """

    def __init__(self, (x, y), size, mass):
        self.position = Vector2D(x, y)
        self.size = size
        self.colour = (255, 255, 255)
        self.line_colour = (120, 255, 120)
        self.thickness = 0
        self.mass = mass
        self.velocity = Vector2D.zero()
        self.acceleration = Vector2D.zero()
        self.fixed = False
        self.trail = []
        self.maxTrailLength = 200

    # Appends the particle's current position onto the trail list when called.
    # If the trail has exceeded a certain length, the oldest values are deleted.
    def appendTrail(self, height):
        self.trail.append([self.position.x, height - self.position.y])

        if len(self.trail) > self.maxTrailLength:
            self.trail.pop(0)


    def verlet(self, other, dt=0.01):
        if not self.fixed:
            self.velocity += 0.5 * dt * self.acceleration
            self.position += dt*self.velocity
            self.acceleration = self.getGravityAcceleration(other)
            self.velocity += 0.5 * dt * self.acceleration

    def getGravityAcceleration(self, other):  # this isn't where this function should go
        dr = self.position - other.position
        dist = dr.length()

        theta = dr.angle()

        force = G * self.mass * other.mass / dist ** 2
        return -Vector2D.create_from_angle(theta, force / self.mass)  # this feels wrong
