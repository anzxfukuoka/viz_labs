import math
from scipy.interpolate import BPoly
import numpy as np
from geometrix import Point


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
