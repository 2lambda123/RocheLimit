import math
import random
from geometry import Vector2D

# Gravitational Constant
G = 0.2

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

    def update(self):
        """  Calls particle functions """

        for i, planet in enumerate(self.planets):
            # One planet functions get called here
            planet.move()

            # Two planet functions get called here
            for planet2 in self.planets[i + 1:]:
                planet.attract(planet2)

class Planet:
    """ A circular planet with a velocity, size and density """

    def __init__(self, (x, y), size, density=1):
        self.position = Vector2D(x, y)
        self.size = size
        self.colour = (255, 255, 255)
        self.thickness = 0
        self.density = density
        # cube the radius for a sphere
        self.mass = density * size ** 3
        self.velocity = Vector2D.zero()
        self.fixed = False

    def move(self):
        """ Update position based on velocity """
        if not self.fixed:
            self.position += self.velocity

    def accelerate(self, acceleration):
        """ Change velocity by vector a """
        self.velocity += acceleration

    def verlet(self, other, fx, fy, dt=0.01):
        self.velocity += 0.5 * dt * self.getForce(other)
        self.position += dt*self.velocity
        self.velocity += 0.5 * dt * self.getForce(other)  # right now this requires two function calls

    def attract(self, other):
        dr = self.position - other.position
        dist = dr.length()

        theta = dr.angle()
        force = G * self.mass * other.mass / dist ** 2
        self.accelerate(-Vector2D.create_from_angle(theta, force / self.mass))
        other.accelerate(Vector2D.create_from_angle(theta, force / other.mass))

    def getForce(self, other):  # this isn't where this function should go
        dr = self.position - other.position
        dist = dr.length()

        theta = dr.angle()
        force = G * self.mass * other.mass / dist ** 2
        fx, fy = -Vector2D.create_from_angle(theta, force / self.mass)  # this feels wrong
        return(fx, fy)