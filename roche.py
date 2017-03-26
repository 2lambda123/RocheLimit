import math
import random
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
        self.planets = []
        self.collision_radius = collision_radius

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

    def update(self, G, dt=0.01):
        """  Calls particle functions """

        if self.origin:
            for body in self.planets:
                body.verlet(self.origin, G, dt)

        # Center of mass calculation
        R = Vector2D.zero()
        M = 0
        for body in self.planets:
            M = M + body.mass
            R = R + body.mass * body.position
        R = R/M

        for body in self.planets:
            Rnew = R - body.mass * body.position/M
            body.verletCOM(M, R, G,self.collision_radius, dt)
        
##        for i, planet in enumerate(self.planets):
##            # One planet functions get called here
##            # planet.move()
##
##            # # Two planet functions get called here
##            for planet2 in self.planets[i + 1:]:
##            #     planet.attract(planet2)
##                planet.verlet(planet2, G, dt)
##                planet2.verlet(planet, G, dt)


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

    def verletCOM(self, M, R, G, collision_radius, dt):
        if not self.fixed:
            self.velocity += 0.5 * dt * self.acceleration
            self.position += dt * self.velocity
            self.acceleration = self.getGravityAccelerationCOM(G, M, R, collision_radius)
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
            force = 0
            # Also reduces the velocity, for shits & gigs.
            # self.velocity *= 0.9

            # Obviously replace this in the future when we have multiple particles working, 
            # I just did it because I was tired of planets shooting off to infinity.
        else:
            force = G * (M - self.mass) * self.mass / dist ** 2

        return  Vector2D.create_from_angle(theta, force / self.mass)  # this feels wrong
        

    def getGravityAcceleration(self, other, G):  # this isn't where this function should go
        dr = self.position - other.position
        dist = dr.length()

        theta = dr.angle()

        # Implementing Sigurdson's suggestion for constant force for particles inside others.
        # I modified it somewhat to instead only take into account the mass it 'sees' from its current radius.
        if dist < other.size + self.size:
            force = G * self.mass * other.mass * (dist / other.size)**3 / dist ** 2
            # Also reduces the velocity, for shits & gigs.
            self.velocity *= 0.9

            # Obviously replace this in the future when we have multiple particles working, 
            # I just did it because I was tired of planets shooting off to infinity.
        else:
            force = G * self.mass * other.mass / dist ** 2

        return - Vector2D.create_from_angle(theta, force / self.mass)  # this feels wrong
