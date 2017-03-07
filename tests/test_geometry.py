import unittest
import geometry
import math

class TestVector2D(unittest.TestCase):

    def setUp(self):
        # Vectors in each quadrant
        # Q1 is top right: x>0, y>0, and goes counter clockwise
        self.vectorQ1 = geometry.Vector2D(3, 4)
        self.vectorQ2 = geometry.Vector2D(-3, 4)
        self.vectorQ3 = geometry.Vector2D(-1, -1)
        self.vectorQ4 = geometry.Vector2D(6, -8)
        self.vectors = [
            self.vectorQ1, self.vectorQ2, self.vectorQ3, self.vectorQ4]

    def testAdditionToZero(self):
        for vector in self.vectors:
            actual = vector + geometry.Vector2D.zero()
            expected = vector
            self.assertEqual(actual, expected)

    def testAddition(self):
        actual = self.vectorQ1 + self.vectorQ2
        expected = geometry.Vector2D(0, 8)
        self.assertEqual(actual, expected)

        actual = self.vectorQ1 + 3
        expected = geometry.Vector2D(6, 7)
        self.assertEqual(actual, expected)

    def testAdditionToSelf(self):
        actual = geometry.Vector2D.zero()
        actual += self.vectorQ1
        expected = geometry.Vector2D(3, 4)
        self.assertEqual(actual, expected)

        actual = geometry.Vector2D(3, 4)
        actual += 3
        expected = geometry.Vector2D(6, 7)
        self.assertEqual(actual, expected)

    def testSubtraction(self):
        actual = self.vectorQ1 - self.vectorQ2
        expected = geometry.Vector2D(6, 0)
        self.assertEqual(actual, expected)

        actual = self.vectorQ1 - 3
        expected = geometry.Vector2D(0, 1)
        self.assertEqual(actual, expected)

    def testSubtractionToSelf(self):
        actual = geometry.Vector2D.zero()
        actual -= self.vectorQ1
        expected = geometry.Vector2D(-3, -4)
        self.assertEqual(actual, expected)

        actual = geometry.Vector2D(3, 4)
        actual -= 3
        expected = geometry.Vector2D(0, 1)
        self.assertEqual(actual, expected)

    def testScalarMultiplication(self):
        actual = self.vectorQ1 * 2
        expected = geometry.Vector2D(6, 8)
        self.assertEqual(actual, expected)

        actual = 2 * self.vectorQ1
        self.assertEqual(actual, expected)

    def testScalarDivision(self):
        actual = self.vectorQ1 / 2
        expected = geometry.Vector2D(1.5, 2)
        self.assertEqual(actual, expected)

    def testLength(self):
        actual = geometry.Vector2D(3, 4).length()
        expected = 5
        self.assertEqual(actual, expected)

    def testDotProduct(self):
        actual = self.vectorQ1.dot(self.vectorQ2)
        expected = 7
        self.assertEqual(actual, expected)

    def testCopy(self):
        actual = self.vectorQ1.copy()
        actual += 3
        expected = geometry.Vector2D(6, 7)
        self.assertEqual(actual, expected)
        self.assertNotEqual(actual, self.vectorQ1)

    def testAngles(self):
        north = geometry.Vector2D(0, 1)
        south = geometry.Vector2D(0, -1)
        west = geometry.Vector2D(-1, 0)
        east = geometry.Vector2D(1, 0)
        northeast = geometry.Vector2D(1, 1)
        northwest = geometry.Vector2D(-1, 1)
        southeast = geometry.Vector2D(1, -1)
        southwest = geometry.Vector2D(-1, -1)

        specialTriangle = geometry.Vector2D.create_from_angle(math.pi/6, 2)

        self.assertEqual(north.angle(), math.pi/2)
        self.assertEqual(south.angle(), -math.pi/2)
        self.assertEqual(west.angle(), math.pi)
        self.assertEqual(east.angle(), 0)

        self.assertAlmostEqual(northeast.angle(), math.pi/4, delta=0.01)
        self.assertAlmostEqual(northwest.angle(), 3*math.pi/4, delta=0.01)
        self.assertAlmostEqual(southeast.angle(), -math.pi/4, delta=0.01)
        self.assertAlmostEqual(southwest.angle(), -3*math.pi/4, delta=0.01)

        self.assertAlmostEqual(specialTriangle.angle(), math.pi/6, delta=0.01)

    def testAngleBetween(self):
        north = geometry.Vector2D(0, 1)
        south = geometry.Vector2D(0, -1)
        west = geometry.Vector2D(-1, 0)
        east = geometry.Vector2D(1, 0)
        northeast = geometry.Vector2D(1, 1)
        northwest = geometry.Vector2D(-1, 1)
        southeast = geometry.Vector2D(1, -1)
        southwest = geometry.Vector2D(-1, -1)

        self.assertAlmostEqual(
            geometry.Vector2D.angle_between(north, south), math.pi)
        self.assertAlmostEqual(
            geometry.Vector2D.angle_between(east, west), math.pi)
        self.assertAlmostEqual(
            geometry.Vector2D.angle_between(north, east), -math.pi/2)
        self.assertAlmostEqual(
            geometry.Vector2D.angle_between(north, west), math.pi/2)
        self.assertAlmostEqual(
            geometry.Vector2D.angle_between(southeast, south), -math.pi/4)
        self.assertAlmostEqual(
            geometry.Vector2D.angle_between(southeast, northeast), math.pi/2)
        self.assertAlmostEqual(
            geometry.Vector2D.angle_between(southeast, northwest), math.pi, places=5)
        self.assertAlmostEqual(
            geometry.Vector2D.angle_between(southeast, west), -3*math.pi/4)
        self.assertAlmostEqual(
            geometry.Vector2D.angle_between(southwest, north), -3*math.pi/4)
        self.assertAlmostEqual(
            geometry.Vector2D.angle_between(southwest, southeast), math.pi/2)
        self.assertAlmostEqual(
            geometry.Vector2D.angle_between(southwest, west), -math.pi/4)
        self.assertAlmostEqual(
            geometry.Vector2D.angle_between(southwest, southwest), 0, 5)

    def testCreateFromAngle(self):
        specialTriangle30 = geometry.Vector2D.create_from_angle(math.pi/6, 2)
        specialTriangle60 = geometry.Vector2D.create_from_angle(math.pi/3, 2)
        specialTriangle45 = geometry.Vector2D.create_from_angle(
            math.pi/4, math.sqrt(2))

        self.assertAlmostEqual(specialTriangle30.x, math.sqrt(3))
        self.assertAlmostEqual(specialTriangle30.y, 1)

        self.assertAlmostEqual(specialTriangle60.x, 1)
        self.assertAlmostEqual(specialTriangle60.y, math.sqrt(3))

        self.assertAlmostEqual(specialTriangle45.x, 1)
        self.assertAlmostEqual(specialTriangle45.y, 1)

    # Also checks for immutability
    def tearDown(self):
        self.assertTrue(self.vectorQ1 == geometry.Vector2D(3, 4))
        self.assertTrue(self.vectorQ2 == geometry.Vector2D(-3, 4))
        self.assertTrue(self.vectorQ3 == geometry.Vector2D(-1, -1))
        self.assertTrue(self.vectorQ4 == geometry.Vector2D(6, -8))
        self.assertTrue(self.vectorQ1 == [3, 4])
        self.assertTrue(self.vectorQ2 == [-3, 4])
        self.assertTrue(self.vectorQ3 == [-1, -1])
        self.assertTrue(self.vectorQ4 == [6, -8])


class TestVector3D(unittest.TestCase):

    def setUp(self):
        # Vectors in each quadrant
        # Q1 is top right: x>0, y>0, and goes counter clockwise
        self.vectorQ1 = geometry.Vector3D(2, 3, 4)
        self.vectorQ2 = geometry.Vector3D(2, -3, 4)
        self.vectorQ3 = geometry.Vector3D(-2, -1, -1)
        self.vectorQ4 = geometry.Vector3D(-4, 6, -8)
        self.vectors = [
            self.vectorQ1, self.vectorQ2, self.vectorQ3, self.vectorQ4]

    def testAdditionToZero(self):
        for vector in self.vectors:
            actual = vector + geometry.Vector3D.zero()
            expected = vector
            self.assertEqual(actual, expected)

    def testAddition(self):
        actual = self.vectorQ1 + self.vectorQ2
        expected = geometry.Vector3D(4, 0, 8)
        self.assertEqual(actual, expected)

        actual = self.vectorQ1 + 3
        expected = geometry.Vector3D(5, 6, 7)
        self.assertEqual(actual, expected)

    def testAdditionToSelf(self):
        actual = geometry.Vector3D.zero()
        actual += self.vectorQ1
        expected = geometry.Vector3D(2, 3, 4)
        self.assertEqual(actual, expected)

        actual = geometry.Vector3D(2, 3, 4)
        actual += 3
        expected = geometry.Vector3D(5, 6, 7)
        self.assertEqual(actual, expected)

    def testSubtraction(self):
        actual = self.vectorQ1 - self.vectorQ2
        expected = geometry.Vector3D(0, 6, 0)
        self.assertEqual(actual, expected)

        actual = self.vectorQ1 - 3
        expected = geometry.Vector3D(-1, 0, 1)
        self.assertEqual(actual, expected)

    def testSubtractionToSelf(self):
        actual = geometry.Vector3D.zero()
        actual -= self.vectorQ1
        expected = geometry.Vector3D(-2, -3, -4)
        self.assertEqual(actual, expected)

        actual = geometry.Vector3D(2, 3, 4)
        actual -= 3
        expected = geometry.Vector3D(-1, 0, 1)
        self.assertEqual(actual, expected)

    def testScalarMultiplication(self):
        actual = self.vectorQ1 * 2
        expected = geometry.Vector3D(4, 6, 8)
        self.assertEqual(actual, expected)

        actual = 2 * self.vectorQ1
        self.assertEqual(actual, expected)

    def testScalarDivision(self):
        actual = self.vectorQ1 / 2
        expected = geometry.Vector3D(1, 1.5, 2)
        self.assertEqual(actual, expected)

    def testLength(self):
        actual = self.vectorQ1.length()
        expected = math.sqrt(2*2 + 3*3 + 4*4)
        self.assertAlmostEqual(actual, expected)

    def testDotProduct(self):
        actual = self.vectorQ1.dot(self.vectorQ2)
        expected = 11
        self.assertEqual(actual, expected)

    def testCrossProduct(self):
        actual = geometry.Vector3D(1,0,0).cross(geometry.Vector3D(0,1,0))
        expected = geometry.Vector3D(0,0,1)
        self.assertEqual(actual, expected)

        actual = geometry.Vector3D(0,1,0).cross(geometry.Vector3D(1,0,0))
        expected = geometry.Vector3D(0,0,-1)
        self.assertEqual(actual, expected)

        actual = self.vectorQ1.cross(self.vectorQ2)
        expected = geometry.Vector3D(24, 0, -12)
        self.assertEqual(actual, expected)

    # Also checks for immutability
    def tearDown(self):
        self.assertTrue(self.vectorQ1 == geometry.Vector3D(2, 3, 4))
        self.assertTrue(self.vectorQ2 == geometry.Vector3D(2, -3, 4))
        self.assertTrue(self.vectorQ3 == geometry.Vector3D(-2, -1, -1))
        self.assertTrue(self.vectorQ4 == geometry.Vector3D(-4, 6, -8))
        self.assertTrue(self.vectorQ1 == [2, 3, 4])
        self.assertTrue(self.vectorQ2 == [2, -3, 4])
        self.assertTrue(self.vectorQ3 == [-2, -1, -1])
        self.assertTrue(self.vectorQ4 == [-4, 6, -8])