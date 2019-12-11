
class Coord(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return "[{},{}]".format(self.x, self.y)

    def __add__(self, other):
        return Coord(self.x + other.x, self.y + other.y)

    def manhattenDist(self, other):
        return abs(self.x - other.x) + abs(self.y - other.y)

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.x == other.x and 
            self.y == other.y
        )
    
    def __hash__(self):
        return hash(self.x) * 3 + hash(self.y)

    def onLine(self, o1, o2, debug=False):
        x1 = min(o1.x, o2.x)
        x2 = max(o1.x, o2.x)
        y1 = min(o1.y, o2.y)
        y2 = max(o1.y, o2.y)

        if not (y1 <= self.y <= y2 and x1 <= self.x <= x2):
            # not within box
            return False

        if (x1 == self.x == x2) or (y1 == self.y == y2):
            # not in straight line
            return True
        
        if (x1 == self.x != x2) or (x1 != self.x == x2) or (y1 != self.y == y2) or (y1 == self.y != y2):
            # two of them in line, but not all three
            return False

        if (self.x - o1.x)/(self.y - o1.y) == (o2.x - o1.x)/(o2.y - o1.y):
            # have same slope
            return True

        return False