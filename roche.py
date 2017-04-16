import math
import random
import numpy as np
import matplotlib.pyplot as plt
from geometry import Vector2D

# Gravitational Constant
# Converted to pixels using the conversion factor from main.
# G = (6.674*10**-11)/(124738.461538)**3 # m^3 / kg s^2
# I am currently doing a hacky way of transferring G through, so if there's a better way, please let me know!

class Environment:
    """ Defines the boundary of a simulation and its properties """

    def __init__(self, (width, height), collision_radius):
        self.width = width
        self.height = height
        self.colour = (255, 255, 255)
        self.origin = None
        self.bodies = []
        self.collision_radius = collision_radius
        self.COM = Vector2D.zero()
        self.M = 0
        self.trail = []
        self.maxTrailLength = 1000

        self.oscEnergy, = plt.plot([], [], 'b-', label='Numerical Energy')
        # self.constEnergy, = plt.plot([], [], 'r-', label='Theoretical Energy')
        plt.ion() # turn on interactive mode
        self.axes = plt.gca()
        self.axes.set_autoscale_on(True)
        plt.title("Energy vs. Time")
        plt.xlabel("Timestep")
        plt.ylabel("Total Energy (J)")
        plt.legend()


    def addBodies(self, n=1, **kargs):
        """ Add n planets with properties given by keyword arguments """

        for i in range(n):
            size = kargs.get('size', random.randint(10, 20))
            if 'density' in kargs:
                density = kargs.get('density', 1)
                mass = 4/3 * math.pi * density * (size ** 3)
            else:
                mass = kargs.get('mass', random.randint(100, 10000))

            x = kargs.get('x', random.uniform(size, self.width - size))
            y = kargs.get('y', random.uniform(size, self.height - size))

            planet = Body((x, y), size, mass)
            speed = kargs.get('speed', random.random())
            angle = kargs.get('angle', random.uniform(0, math.pi * 2))
            planet.velocity = Vector2D.create_from_angle(angle, speed)
            planet.colour = kargs.get('colour', (0, 0, 255))

            self.bodies.append(planet)

    def update(self, G, dt=0.01):
        """  Calls particle functions """

        # self.calculateCOM()

        self.verlet(G, dt)
        # self.euler(G, dt)

        Ttotal = 0 # total Kinetic Energy of all bodies
        Utotal = 0 # total Potential Energy of all bodies
        for i, body in enumerate(self.bodies):
            U = 0
            for other in self.bodies:
                U += body.getPotentialEnergyWRT(other, G)
            U += body.getPotentialEnergyWRT(self.origin, G)
            Utotal += U
            Ttotal += body.getKineticEnergy()

        time = self.oscEnergy.get_xdata()
        energy = self.oscEnergy.get_ydata()
        # constEnergy = self.constEnergy.get_ydata()

        if len(time) == 0:
            time = np.append(time, 1)
        else:
            time = np.append(time, time[-1] + 1)
        energy = np.append(energy, Ttotal + Utotal)

        # moon = self.bodies[0]
        # dist = (self.origin.position - moon.position).length()
        # E = -G * moon.mass * self.origin.mass / (2*dist)
        # constEnergy = np.append(constEnergy, E)

        self.oscEnergy.set_xdata(time)
        self.oscEnergy.set_ydata(energy)
        # self.constEnergy.set_xdata(time)
        # self.constEnergy.set_ydata(constEnergy)
        self.axes.relim()
        self.axes.autoscale_view()
        plt.draw()
        plt.pause(0.01)

        # print Ttotal + Utotal



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
            body.acceleration += body.getGravityAcceleration(self.origin, G)
            for other in self.bodies[i+1:]:
                body.acceleration += body.getGravityAcceleration(other, G)
                other.acceleration += other.getGravityAcceleration(body, G)
        for body in self.bodies:
            body.velocity += 0.5 * dt * body.acceleration

    def euler(self, G, dt):
        for body in self.bodies:
            body.acceleration = Vector2D.zero()
        for i, body in enumerate(self.bodies):
            body.acceleration += body.getGravityAcceleration(self.origin, G)
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


    def verlet(self, other, G, dt):
        if not self.fixed:
            self.velocity += 0.5 * dt * self.acceleration
            self.position += dt * self.velocity
            self.acceleration = self.getGravityAcceleration(other, G)
            self.velocity += 0.5 * dt * self.acceleration

    # Verlet calculation using COM
    def verletCOM(self, M, R, G, collision_radius, origin, dt):
        if not self.fixed:
            self.velocity += 0.5 * dt * self.acceleration
            self.position += dt * self.velocity
            self.acceleration = self.getGravityAccelerationCOM(G, M, R, collision_radius) + self.getGravityAcceleration(origin, G)
            self.velocity += 0.5 * dt * self.acceleration

    def areWeDead(self, other):
        dr = self.position - other.position
        dist = dr.length()

        if dist < other.size + self.size:
            return True

    def getGravityAccelerationCOM(self, G, M, R, collision_radius):
        dr = R - self.position
        dist = dr.length()

        theta = dr.angle()
        
        if dist < collision_radius:
            # could be changed to linear function
            force = G * (M - self.mass) * self.mass / collision_radius ** 2 * dist/collision_radius
        else:
            force = G * (M - self.mass) * self.mass / dist ** 2

        # return  Vector2D.create_from_angle(theta, force / self.mass)  # this feels wrong
        return (dr/dist)*force/self.mass

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


