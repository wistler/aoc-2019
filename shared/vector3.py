import math

class Vector3(object):
    AXES = ['x', 'y', 'z']

    @staticmethod
    def unit(axis):
        return Vector3(**{axis: 1})

    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def __getitem__(self, axis):
        if axis == 'x':
            return self.x
        elif axis == 'y':
            return self.y
        elif axis == 'z':
            return self.z
        else:
            raise Exception("Invalid axis: {}".format(axis))
    
    def __setitem__(self, axis, value):
        if axis == 'x':
            self.x = value
        elif axis == 'y':
            self.y = value
        elif axis == 'z':
            self.z = value
        else:
            raise Exception("Invalid axis: {}".format(axis))

    def __repr__(self):
        return "<x={:3d}, y={:3d}, z={:3d}>".format(self.x, self.y, self.z)

    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def abs_sum(self):
        return abs(self.x) + abs(self.y) + abs(self.z)

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.x == other.x and 
            self.y == other.y and
            self.z == other.z
        )
    
    def __hash__(self):
        return hash(self.x) * 5 + hash(self.y) * 3 + hash(self.z)
    
    def clone(self):
        return Vector3(self.x, self.y, self.z)


ZERO = Vector3(0,0,0)
ONE = Vector3(1,1,1)
