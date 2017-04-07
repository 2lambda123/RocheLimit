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
        self.bodies = []
        self.collision_radius = collision_radius
        self.COM = Vector2D.zero()
        self.M = 0
        self.trail = []
        self.maxTrailLength = 1000

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
        #
        # for body in self.bodies:
        #     # calculate COM for all other particles
        #     if len(self.bodies) > 1:
        #         Rnew = (self.COM - body.mass*body.position/self.M)*self.M/(self.M - body.mass)
        #     else:
        #         Rnew = Vector2D.zero()  # arbitrary since the force is zero when len(bodies) == 1
        #     body.verletCOM(self.M, Rnew, G, self.collision_radius, self.origin, dt)

        self.verlet(G, dt)


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



class Body:
    """ A circular planet with a velocity, size and density """

    # If the body has a radius greater than this, the body is treated as a gas cloud
    COLLISION_RADIUS = 5

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
            force = 0.01* G * (M - self.mass) * self.mass / collision_radius ** 2 * dist/collision_radius
        else:
            force = G * (M - self.mass) * self.mass / dist ** 2

        # return  Vector2D.create_from_angle(theta, force / self.mass)  # this feels wrong
        return (dr/dist)*force/self.mass

    def getGravityAcceleration(self, other, G):  # this isn't where this function should go
        if other is None:
            return Vector2D.zero()

        dr = other.position - self.position
        dist = dr.length()

        theta = dr.angle()

        if other.size > self.COLLISION_RADIUS:
            Fmax = G * self.mass * other.mass / other.size ** 2
        elif self.size > self.COLLISION_RADIUS:
            Fmax = G * self.mass * other.mass / self.size ** 2
        else:
            Fmax = 0

        rmin = other.size + self.size

        # Implementing James' 'collision' code
        if dist < rmin/3:
            force = - 3 * Fmax * dist / rmin
        elif dist > rmin/3 and dist < rmin:
            force = (3 * Fmax * dist / rmin) - 2 * Fmax
        else:
            force = G * self.mass * other.mass / dist ** 2

        return (dr/dist)*force/self.mass
