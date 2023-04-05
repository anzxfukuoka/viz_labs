import math
from scipy.interpolate import BPoly
import numpy as np


def try_cast(x, to_type: __build_class__, default=None):
    """
    tries cast value to type
    :param x: value
    :param to_type: cast type
    :param default: default return value
    :return: if success -> converted value, else -> default
    """
    try:
        return to_type(x)
    except (ValueError, TypeError) as e:
        return default


class Point:
    """
    Helper class \n
    represents 3d point
    """

    def _set_coords(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __init__(self,
                 x: float,
                 y: float,
                 z: str | float,
                 depth: float | int = 0):
        """
            Point(x: float, y: float, z: float): \n
        Defines 3d point (x; y; z). \n
            Point(a: float, b: float, surface_type: str): \n
        Defines 2d point on plane: "xy", "xz" or "yz".
        :param depth: plane depth
        """

        if try_cast(z, float) is not None:
            self._set_coords(x, y, z)
        elif try_cast(z, str) is not None:
            a = x
            b = y
            surf = z

            if surf == "xy":
                self._set_coords(a, b, depth)
            elif surf == "xz":
                self._set_coords(a, depth, b)
            elif surf == "yz":
                self._set_coords(depth, a, b)
            else:
                raise Exception("Invalid surface type")
        else:
            raise Exception("Invalid argument {}, type({})".format(z, type(z)))

    def __mul__(self, other):
        return Point(self.x * other, self.y * other, self.z * other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __floordiv__(self, other):

        if try_cast(other, float):
            return Point(self.x / other, self.y / other, self.z / other)
        else:
            # assume other is Point
            return Point(self.x / other.x, self.y / other.y, self.z / other.z)

    def __truediv__(self, other):
        return self.__floordiv__(other)

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return self.__add__(other * -1)

    def __str__(self):
        return "P({x}, {y}, {z})".format(x=self.x, y=self.y, z=self.z)

    def __repr__(self):
        return self.__str__()

    def to_list(self):
        return [self.x, self.y, self.z]

    def from_list(coords: list):
        return Point(coords[0], coords[1], coords[2])


class BezierCurve:
    """
    Bézier curve degree \n
    control_points: array of Points np.array(type=Point)
    """

    def _B(self, t: float):
        """
        :param t: param t є [0, 1]
        :return: Point
        """

        points_list = [[f.to_list()] for f in self.control_points]
        bp = BPoly(points_list, [0, 1])
        result = Point.from_list(bp(t))

        ''' Bernstein polynomial 
        points_count = len(self.control_points) - 1

        result = Point(0, 0, 0)  # первая операция - mul

        numerator = Point(0, 0, 0)
        denominator = Point(0, 0, 0)

        for i, p in enumerate(self.control_points):
            bin_coof = np.math.factorial(points_count) / (np.math.factorial(i) * np.math.factorial(points_count - i))

            t_coof = lambda x, n: x ** n

            aa = t_coof(t, i)
            bb = t_coof(1 - t, points_count - i)

            numerator += bin_coof * t_coof(t, i) * t_coof(1 - t, points_count - i) * self.control_points[i] * \
                         self.weights[i]

            denominator += bin_coof * t_coof(t, i) * t_coof(1 - t, points_count - i) * self.weights[i] * Point(1, 1, 1)

        result = numerator / denominator
        
        '''

        return result

    def __init__(self, control_points: list[Point], weights: list[float] = None, quality=10):
        """
        Bézier curve
        :param control_points: points
        :param weights: points weights
        :param quality: count of interpolated points
        """
        self.control_points = control_points

        if weights:
            self.weights = weights
        else:
            self.weights = np.ones(len(control_points))

        self.quality = quality

    def verts(self):
        step = 1 / self.quality
        vertexes = []
        for i in range(self.quality + 1):
            vertexes.append(self._B(i * step))
        return vertexes

    def edges(self):
        return zip(range(self.quality), range(1, self.quality + 1))

    def __len__(self):
        return len(self.control_points)


class BezierSurface:

    def _S(self, t, u, segments_count=3):
        """
        :param t: t param
        :param u: u param
        :return: Point on surface
        """

        result = Point(0, 0, 0)

        for curve in self.secondary_curves:
            points_list = [[f.to_list()] for f in curve.control_points]
            bp = BPoly(points_list, [0, 1])
            result += Point.from_list(bp(t))

        '''
        result = Point(0, 0, 0)
        
        
        for i, p in enumerate(self.curves):
            bin_coof = np.math.factorial(segments_count) / (np.math.factorial(i) * np.math.factorial(segments_count - i))

            t_coof = lambda x, n: x ** n

            aa = t_coof(u, i)
            bb = t_coof(1 - u, segments_count - i)

            result += bin_coof * t_coof(u, i) * t_coof(1 - u, segments_count - i) * self.curves[i]._B(t)
        '''

        return result

    def __init__(self, curves: list[BezierCurve], quality: int = 10, count: int = 0, last: bool = True):
        """
        Bezier Surface
        :param curves: generating curves
        :param quality: generated curves quality
        :param count: secondary curves count. non-positive value: count = len(curves)
        :param last: create last curve
        """
        self.curves = curves
        self.quality = quality

        curves_count = len(self.curves)

        if count > 0:
            secondary_curves_count = count
        else:
            # square net
            secondary_curves_count = (lambda: curves_count + 1 if last else curves_count)()

        self.secondary_curves = []

        for i in range(secondary_curves_count):
            points = []
            for j in range(curves_count):
                points.append(self.curves[j]._B(i / curves_count))

            self.secondary_curves.append(BezierCurve(points, quality=quality))

    def verts(self):
        step = 1 / self.quality
        vertexes = []
        for curve in self.curves:
            for i in range(self.quality + 1):
                vertexes.append(curve._B(i * step))
        return vertexes

    def edges(self):
        edges = []
        # for i in range(len(self.curves)):
        return (x.edges() for x in self.curves)
