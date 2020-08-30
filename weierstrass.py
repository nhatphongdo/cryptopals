from utils import invmod, sqrtmod
from ecc import EllipticCurve, EllipticPoint
from random import randrange

class WeierstrassCurve(EllipticCurve):
    def __init__(self, a, b, p, g, q, order):
        '''
        @a, b   params of the curve equation
                    y^2 = x^3 + ax + b
        @p      the GF(p) to work on
        @g      the coordinates of the generator
        @q      the order of the generator
        @order  the number of elements in the finite field
                    generated by the curve on GF(p)
        '''
        self.a = a
        self.b = b
        self.p = p
        self.q = q
        self.order = order
        self.g = self.point(*g)
        self.id = self.point(0, 1)

        assert self.g * q == self.id
    
    def point(self, x, y):
        return WeierstrassPoint(self, x, y)


class WeierstrassPoint(EllipticPoint):
    def __init__(self, curve, x, y):
        super().__init__(curve, x, y)

        # make sure the point is valid
        if x != 0 or y != 1:
            assert (pow(x, 3, curve.p) + curve.a * x + curve.b) % curve.p == pow(y, 2, curve.p), "Point not on the curve!"

    def _add(self, obj):
        curve = self.curve
        m = ((obj.y - self.y) * invmod(obj.x - self.x, curve.p)) % curve.p
        new_x = (m * m - self.x - obj.x) % curve.p
        new_y = (m * (self.x - new_x) - self.y) % curve.p

        return WeierstrassPoint(curve, new_x, new_y)

    def _double(self):
        curve = self.curve
        m = ((3 * self.x * self.x + curve.a) * invmod(2 * self.y, curve.p)) % curve.p
        new_x = (m * m - self.x - self.x) % curve.p
        new_y = (m * (self.x - new_x) - self.y) % curve.p

        return WeierstrassPoint(curve, new_x, new_y)
