import math
import random
import numpy as np
import matplotlib.pyplot as plt
from geometry import Vector2D

# Gravitational Constant
# Converted to pixels using the conversion factor from main.
# G = (6.674*10**-11)/(124738.461538)**3 # m^3 / kg s^2

class Environment:
    """ Defines the boundary of a simulation and its properties """

    def __init__(self, (width, height)):
        self.width = width
        self.height = height
        self.colour = (255, 255, 255)
        self.primary = None
        self.bodies = []
        self.COM = Vector2D.zero()
        self.M = 0
        self.trail = []
        self.maxTrailLength = 1000

    def update(self, G, dt=0.01):
        """  Calls particle functions """
        # Uncomment to draw COM trail
        # self.calculateCOM(),

        self.verlet(G, dt)
        # self.euler(G, dt)


    def calculateCOM(self):
        # Center of mass calculation
        self.COM = Vector2D.zero()
        self.M = 0
        for body in self.bodies:
            self.M = self.M + body.mass
            self.COM = self.COM + body.mass * body.position
        self.COM = self.COM/self.M

    def appendCOMTrail(self):
        # Appends the particle's current position onto the trail list when called.
        self.trail.append([self.COM.x, self.height - self.COM.y])

        # If the trail has exceeded a certain length, the oldest values are deleted.
        if len(self.trail) > self.maxTrailLength:
            self.trail.pop(0)

    def verlet(self, G, dt):
        for body in self.bodies:
            body.velocity += 0.5 * dt * body.acceleration
            body.position += dt * body.velocity
            body.acceleration = Vector2D.zero()
        for i, body in enumerate(self.bodies):
            if self.primary:
                body.acceleration += body.getGravityAcceleration(self.primary, G)
            for other in self.bodies[i+1:]:
                body.acceleration += body.getGravityAcceleration(other, G)
                other.acceleration += other.getGravityAcceleration(body, G)
        for body in self.bodies:
            body.velocity += 0.5 * dt * body.acceleration

    def euler(self, G, dt):
        for body in self.bodies:
            body.acceleration = Vector2D.zero()
        for i, body in enumerate(self.bodies):
            if self.primary:
                body.acceleration += body.getGravityAcceleration(self.primary, G)
            for other in self.bodies[i+1:]:
                body.acceleration += body.getGravityAcceleration(other, G)
                other.acceleration += other.getGravityAcceleration(body, G)
        for body in self.bodies:
            body.velocity, body.position = body.velocity + dt * body.acceleration, body.position + dt * body.velocity




class Body:
    """ A circular planet with a velocity, size and density """

    # If the body has a radius greater than this, the body is treated as a gas cloud
    GAS_PLANET_RADIUS = 5

    def __init__(self, (x, y), size, mass):
        self.position = Vector2D(x, y)
        self.size = size
        self.colour = (255, 255, 255)
        self.line_colour = (255, 0, 0)
        self.thickness = 0
        self.mass = mass
        self.velocity = Vector2D.zero()
        self.acceleration = Vector2D.zero()
        self.fixed = False
        self.trail = []
        self.maxTrailLength = 1200

    
    # Used to find the points necessary to draw the planet trails. 
    def appendTrail(self, height):
        # Obviously fixed planets do not need trails.
        if not self.fixed:
            # Appends the particle's current position onto the trail list when called.
            self.trail.append([self.position.x, height - self.position.y])

            # If the trail has exceeded a certain length, the oldest values are deleted.
            if len(self.trail) > self.maxTrailLength:
                self.trail.pop(0)

    # Finds a series of points every around the outline of a planet to give it a nice anti-aliased outline.
    def findOutline(self, height, scale):
        # Defines how many degrees we should insert a line. Decrease to decrease performance.
        step = 2
        edge = []
        for n in range(0, int(360/step)):
            edge.append([self.position.x + (self.size - scale) * math.cos(math.pi * n * step / 180), height - (self.position.y + (self.size - scale) * math.sin(math.pi * n * step / 180))])
        return edge

    def areWeDead(self, other):
        dr = self.position - other.position
        dist = dr.length()

        if dist < other.size + self.size:
            return True

    def getGravityAcceleration(self, other, G):  # this isn't where this function should go
        if other is None:
            return Vector2D.zero()

        dr = other.position - self.position
        dist = dr.length()

        if dist < other.size + self.size:
            if other.size > self.GAS_PLANET_RADIUS:
                force = (G * self.mass * other.mass / other.size ** 2) * (dist/other.size)
            elif self.size > self.GAS_PLANET_RADIUS:
                force = (G * self.mass * other.mass / self.size ** 2) * (dist/self.size)
            else:
                force = 0
        else:
            force = G * self.mass * other.mass / dist ** 2

        return (dr/dist)*force/self.mass

    def getKineticEnergy(self):
        return 0.5 * self.mass * self.velocity.dot(self.velocity)

    def getPotentialEnergyWRT(self, other, G):
        if other is None:
            return 0

        if other is self:
            return 0

        dr = other.position - self.position
        dist =  dr.length()

        if dist < other.size + self.size:
            if other.size > self.GAS_PLANET_RADIUS:
                U = -(G * self.mass * other.mass / other.size ** 2) * (dist ** 2 / (2 * other.size))
            elif self.size > self.GAS_PLANET_RADIUS:
                U = -(G * self.mass * other.mass / self.size ** 2) * (dist ** 2 / (2 * self.size))
            else:
                U = -(G * self.mass * other.mass) / (self.size + other.size)
        else:
            U = -G * self.mass * other.mass / dist

        return U


