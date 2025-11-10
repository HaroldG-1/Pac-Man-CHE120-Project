import math
from numbers import Real

class Vector2:
    def __init__(self, x=0.0, y=0.0, thresh=1e-6):
        self.x = x
        self.y = y
        self.thresh = thresh

    # +, -
    def __add__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x + other.x, self.y + other.y)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x - other.x, self.y - other.y)
        return NotImplemented

    def __neg__(self):
        return Vector2(-self.x, -self.y)

    # scalar * vector  and  vector * scalar
    def __mul__(self, other):
        if isinstance(other, Real):
            return Vector2(self.x * other, self.y * other)
        # Optional: dot product if multiplying by another Vector2
        if isinstance(other, Vector2):
            return self.x * other.x + self.y * other.y
        return NotImplemented

    def __rmul__(self, other):
        # enable float * Vector2
        return self.__mul__(other)

    # vector / scalar
    def __truediv__(self, other):
        if isinstance(other, Real):
            if abs(other) < self.thresh:
                raise ZeroDivisionError("Division by (near) zero scalar")
            return Vector2(self.x / other, self.y / other)
        return NotImplemented

    # equality with tolerance
    def __eq__(self, other):
        if not isinstance(other, Vector2):
            return NotImplemented
        return (abs(self.x - other.x) < self.thresh and
                abs(self.y - other.y) < self.thresh)

    # magnitude
    def magnitudeSquared(self):
        return self.x * self.x + self.y * self.y

    def magnitude(self):
        return math.sqrt(self.magnitudeSquared())

    # helpers
    def copy(self):
        return Vector2(self.x, self.y, self.thresh)

    def asTuple(self):
        return (self.x, self.y)

    def asInt(self):
        return (int(self.x), int(self.y))

    def __repr__(self):
        return f"Vector2({self.x}, {self.y})"

    def __str__(self):
        return f"<{self.x},{self.y}>"
