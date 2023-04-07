from abc import ABC, abstractmethod

import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *

from misc import try_cast


class Color:
    RED = (1, 0, 0)
    GREEN = (0, 1, 0)
    BLUE = (0, 1, 1)
    WHITE = (1, 1, 1)
    BLACK = (0, 0, 0)

    TWILIGHT = (0.26, 0.22, 0.8)


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
        if type(other) is Point:
            return Point(self.x * other.x, self.y * other.y, self.z * other.z)
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

    @staticmethod
    def from_list(coords: list | np.ndarray):
        return Point(coords[0], coords[1], coords[2])


class Object3D(ABC):

    def __init__(self, pos=Point(0, 0, 0), rot=Point(0, 0, 0), size=Point(1, 1, 1)):
        self.pos = pos
        self.rot = rot
        self.size = size

    @abstractmethod
    def get_edges(self):
        """
        edges indexes
        :return:
        """
        pass

    @abstractmethod
    def get_verts(self):
        """
        vertexes
        :return:
        """
        pass

    @abstractmethod
    def get_surfs(self):
        """
        surfaces indexes
        :return:
        """
        pass

    def draw(self):
        vertexes = self.get_verts()
        edges = self.get_edges()
        surfaces = self.get_surfs()

        glBegin(GL_TRIANGLES)
        for surface in surfaces:
            x = 0

            ps = np.array([vertexes[p].to_list() for p in surface])
            v1 = ps[2] - ps[0]
            v2 = ps[1] - ps[0]
            norm = np.cross(v1, v2)

            for vertex in surface:
                x += 1
                # glColor3fv(colors[x])
                # color = (lambda: Color.GREEN if vertex % 2 == 0 else Color.RED if vertex % 3 == 0 else Color.BLUE)()
                color = Color.TWILIGHT
                glColor3fv(color)
                glNormal(norm[0], norm[1], norm[2])
                point = self.pos + vertexes[vertex] * self.size
                glVertex3fv(point.to_list())
        glEnd()

        glColor3fv(Color.WHITE)

        glBegin(GL_LINES)
        for edge in edges:
            for vertex in edge:
                point = self.pos + vertexes[vertex] * self.size
                glVertex3fv(point.to_list())
        glEnd()

    pass


class Cube3D(Object3D):

    def get_edges(self):
        edges = (
            (0, 1),
            (0, 3),
            (0, 4),
            (2, 1),
            (2, 3),
            (2, 7),
            (6, 3),
            (6, 4),
            (6, 7),
            (5, 1),
            (5, 4),
            (5, 7)
        )
        return edges

    def get_surfs(self):
        surfaces = (
            (0, 1, 2, 3),
            (3, 2, 7, 6),
            (6, 7, 5, 4),
            (4, 5, 1, 0),
            (1, 5, 7, 2),
            (4, 0, 3, 6)
        )
        return surfaces

    def get_verts(self):
        vertexes = (
            Point(1, -1, -1),
            Point(1, 1, -1),
            Point(-1, 1, -1),
            Point(-1, -1, -1),
            Point(1, -1, 1),
            Point(1, 1, 1),
            Point(-1, -1, 1),
            Point(-1, 1, 1)
        )
        return vertexes


class Composed():
    def __init__(self, objects: list[Object3D] | np.ndarray = []):
        self.objects = objects

    def drawAll(self):
        for o in self.objects:
            o.draw()
