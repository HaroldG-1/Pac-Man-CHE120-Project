#Abiram Sarvananthan
#Harold Guo
#Matthew Kennedy - Commenter
#Gabriel Tirona
import math


###########################
# Vector2 Class
# Custom 2D vector used for movement, positioning, and math operations.
###########################
class Vector2(object):
    def __init__(self, x=0, y=0):
        # Coordinates stored as floating point
        self.x = x
        self.y = y

        # Threshold used to compare floating point precision errors
        self.thresh = 0.000001


    ###########################
    # Operator Overloads
    # Allows Vector2 to behave like a math object:
    # +, -, *, ==, /
    ###########################

    # Vector addition: v1 + v2
    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    # Vector subtraction: v1 - v2
    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    # Unary negation: -v
    def __neg__(self):
        return Vector2(-self.x, -self.y)

    # Scalar multiplication: v * scalar
    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)

    # Python 2 style division support
    def __div__(self, scalar):
        if scalar != 0:
            return Vector2(self.x / float(scalar), self.y / float(scalar))
        return None

    # Python 3 style division: v / scalar
    def __truediv__(self, scalar):
        return self.__div__(scalar)

    # Equality check with threshold tolerance to avoid floating precision issues
    def __eq__(self, other):
        if abs(self.x - other.x) < self.thresh:
            if abs(self.y - other.y) < self.thresh:
                return True
        return False


    ###########################
    # Utility Functions
    ###########################

    # Returns squared magnitude (avoids expensive sqrt when not needed)
    def magnitudeSquared(self):
        return self.x**2 + self.y**2

    # Returns magnitude (vector length)
    def magnitude(self):
        return math.sqrt(self.magnitudeSquared())

    # Returns a duplicate of this Vector2 instance
    def copy(self):
        return Vector2(self.x, self.y)

    # Returns vector as a tuple (x,y)
    def asTuple(self):
        return self.x, self.y

    # Returns vector position as integers (useful for pixel drawing)
    def asInt(self):
        return int(self.x), int(self.y)


    ###########################
    # Display Formatting
    ###########################
    def __str__(self):
        return "<" + str(self.x) + ", " + str(self.y) + ">"
