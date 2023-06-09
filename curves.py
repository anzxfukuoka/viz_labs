from scipy.interpolate import BPoly
import numpy as np
from geometrix import Point, Object3D


class BezierCurve(Object3D):
    """
    Bézier curve degree \n
    control_points: array of Points np.array(type=Point)
    """

    def set_tex_coords(self):
        return []

    def set_edges(self):
        return zip(range(self.quality), range(1, self.quality + 1))

    def set_verts(self):
        step = 1 / self.quality
        vertexes = []
        for i in range(self.quality + 1):
            vertexes.append(self.B(i * step))
        return vertexes

    def set_surfs(self):
        return []

    def B(self, t: float):
        """
        :param t: param t є [0, 1]
        :return: Point
        """

        points_list = [[f.to_list()] for f in self.control_points]
        bp = BPoly(points_list, [0, 1])  # Bernstein polynomial
        result = Point.from_list(bp(t))

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

        super(BezierCurve, self).__init__()

    def __len__(self):
        """
        count of control points
        :return: list[Point]
        """
        return len(self.control_points)


class BezierSurface(Object3D):

    def set_tex_coords(self):
        coords = [[i % self.quality, (len(self.vertexes) - i) % self.quality] for i in range(len(self.vertexes))]
        coords = np.array(coords) / len(self.vertexes)
        return coords

    def set_edges(self):
        curves_count = len(self.secondary_curves)
        edges = []

        for i in range(1, (curves_count - 1) * (self.quality + 1)):
            if i % (self.quality + 1) == 0:
                continue
            edge1 = (i - 1, i)
            edge2 = (i, self.quality + i + 1)
            edge3 = (i - 1, self.quality + i + 1)

            edges.append(edge1)
            edges.append(edge2)
            edges.append(edge3)

        return edges

    def set_verts(self):
        step = 1 / self.quality
        vertexes = []
        for curve in self.secondary_curves:
            for i in range(self.quality + 1):
                vertexes.append(curve.B(i * step))
        return vertexes

    def set_surfs(self):
        curves_count = len(self.secondary_curves)
        surfs = []

        for i in range(1, (curves_count - 1) * (self.quality + 1)):
            if i % (self.quality + 1) == 0:
                continue

            trn1 = (
                self.quality + i + 1,
                self.quality + i - 0,
                i,)

            trn2 = (self.quality + i + 0,
                    i - 1,
                    i

                    )

            surfs.append(trn1)
            surfs.append(trn2)

        return surfs


    def S(self, t, u, segments_count=3):
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
        self.last = last

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
                points.append(self.curves[j].B(i / curves_count))

            self.secondary_curves.append(BezierCurve(points, quality=quality))

        super(BezierSurface, self).__init__()

    def verts(self):
        step = 1 / self.quality
        vertexes = []
        for curve in self.curves:
            for i in range(self.quality + 1):
                vertexes.append(curve.B(i * step))
        return vertexes

    def edges(self):
        edges = []
        # for i in range(len(self.curves)):
        return (x.edges() for x in self.curves)
