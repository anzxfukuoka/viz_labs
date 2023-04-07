import math
from abc import ABC, abstractmethod

import numpy as np
from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.GLU import *
from OpenGL.arrays import vbo

from misc import try_cast, load_file


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


class Transform:
    def __init__(self, position=[0, 0, 0], rotation=[0, 0, 0], size=[1, 1, 1]):
        self.position = position
        self.rotation = rotation
        self.size = size
        pass

    def local_to_global(self, v3):
        v4 = np.array(v3 + [1])
        scaled_v = np.dot(self._scale_matrix(), v4)
        rmx, rmy, rmz = self._rotation_matrix()
        rotated_vx = np.dot(rmx, scaled_v)
        rotated_vy = np.dot(rmy, rotated_vx)
        rotated_vz = np.dot(rmz, rotated_vy)
        translated_v = np.dot(self._translate_matrix(), rotated_vz)
        transformed_v = translated_v[:-1]

        return transformed_v

    def _translate_matrix(self):
        mx = np.array([[1, 0, 0, self.position[0]],
                       [0, 1, 0, self.position[1]],
                       [0, 0, 1, self.position[2]],
                       [0, 0, 0,               1]])
        return mx

    def _rotation_matrix(self):
        x, y, z = [math.radians(rot_deg) for rot_deg in self.rotation]

        rmz = np.array([[math.cos(z), -math.sin(z), 0, 0],
                        [math.sin(z), math.cos(z),  0, 0],
                        [0, 0,                      1, 0],
                        [0, 0,                      0, 1]])

        rmx = np.array([[1, 0, 0,                      0],
                        [0, math.cos(x), -math.sin(x), 0],
                        [0, math.sin(x), math.cos(x),  0],
                        [0, 0, 0,                      1]])


        rmy = np.array([[math.cos(y),  0, math.sin(y), 0],
                        [0,            1,           0, 0],
                        [-math.sin(y), 0, math.cos(y), 0],
                        [0,            0,           0, 1]])

        return rmy, rmx, rmz

    def _scale_matrix(self):
        mx = np.array([[self.size[0], 0, 0, 0],
                       [0, self.size[1], 0, 0],
                       [0, 0, self.size[2], 0],
                       [0, 0, 0,            1]])
        return mx


class Object3D(ABC):

    def _compile_shader(self):
        VERTEX_SHADER = load_file("vertex_shader.vsh")
        FRAGMENT_SHADER = load_file("fragment_shader.fsh")

        compiled_vertex_shader = shaders.compileShader(VERTEX_SHADER, GL_VERTEX_SHADER)
        compiled_fragment_shader = shaders.compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)

        shader = shaders.compileProgram(compiled_vertex_shader, compiled_fragment_shader)

        vertexes = np.array([p.to_list() for p in self.get_verts()], dtype=np.float32)

        self.vbo = vbo.VBO(vertexes)

        # get memory locations for
        # shader uniform variables
        uniform_values = (
            'Global_ambient',
            'Light_ambient',
            'Light_diffuse',
            'Light_location',
            'Material_ambient',
            'Material_diffuse'
        )
        for uniform in uniform_values:
            location = glGetUniformLocation(shader, uniform)
            if location in (None, -1):
                print('Warning, no uniform {}'.format(uniform))
            else:
                set_attrib = uniform + '_loc'
                setattr(self, set_attrib, location)

        # get the memory locations for
        # shader attribute variables
        attribute_values = (
            'Vertex_position'
            , 'Vertex_normal'
        )
        for attribute in attribute_values:
            location = glGetAttribLocation(shader, attribute)
            if location in (None, -1):
                print('Warning, no attribute {}'.format(attribute))
            else:
                set_attrib = attribute + '_loc'
                setattr(self, set_attrib, location)

        return shader

    def apply_material(self):

        if len(self.get_surfs()) == 0:
            return

        self.shader = self._compile_shader()
        glUseProgram(self.shader)
        try:
            # bind data into gpu
            self.vbo.bind()
            try:
                # tells opengl to access vertex once
                # we call a draw function
                glEnableClientState(GL_VERTEX_ARRAY)
                # point at our vbo data
                glVertexPointerf(self.vbo)
                # actually tell opengl to draw
                # the stuff in the VBO as a series
                # of triangles
                glDrawArrays(GL_TRIANGLES, 0, len(self.get_verts()))
            finally:
                # cleanup, unbind the our data from gpu ram
                # and tell opengl that it should not
                # expect vertex arrays anymore
                self.vbo.unbind()
                glDisableClientState(GL_VERTEX_ARRAY)
        finally:
            # stop using our shader
            glUseProgram(0)

    def __init__(self):
        self.shader = None
        self.transform = Transform()

    def get_normals(self):
        """
        normal vectors for each point
        :return:
        """
        surfs = self.get_surfs()
        verts = self.get_verts()
        norms = []
        for s in surfs:
            v1 = verts[s[2]] - verts[s[0]]
            v2 = verts[s[1]] - verts[s[0]]
            norm = np.cross(v1.to_list(), v2.to_list())
            norm = norm / np.linalg.norm(norm)  # normalized
            norms.append((norm[0], norm[1], norm[2]))
        return norms

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
        normals = self.get_normals()

        self.apply_material()

        glBegin(GL_TRIANGLES)

        for i, surface in enumerate(surfaces):
            x = 0

            for vertex in surface:
                x += 1
                # glColor3fv(colors[x])
                # color = (lambda: Color.GREEN if vertex % 2 == 0 else Color.RED if vertex % 3 == 0 else Color.BLUE)()
                color = Color.TWILIGHT
                glColor3fv(color)
                nx, ny, nz = normals[i]
                glNormal(nx, ny, nz)
                #point = self.pos + vertexes[vertex] * self.size
                v = vertexes[vertex].to_list()
                point = self.transform.local_to_global(v)
                #glVertex3fv(point.to_list())
                glVertex3fv(point)
        glEnd()

        glColor3fv(Color.WHITE)

        glBegin(GL_LINES)

        for edge in edges:
            for vertex in edge:
                #point = self.pos + vertexes[vertex] * self.size
                #point = vertexes[vertex]
                v = vertexes[vertex].to_list()
                point = self.transform.local_to_global(v)
                #glVertex3fv(point.to_list())
                glVertex3fv(point)

        # for i, surface in enumerate(surfaces):
        #     nx, ny, nz = normals[i]
        #     center = self.pos + vertexes[surfaces[i][0]]
        #     norm = self.pos + center + Point(nx, ny, nz)
        #
        #     glVertex3fv(center.to_list())
        #     glVertex3fv(norm.to_list())

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

    def set_material_all(self):
        for o in self.objects:
            o.set_material()

    def __init__(self, objects: list[Object3D] | np.ndarray = []):
        self.transform = Transform()
        self.objects = objects

    def draw_all(self):
        for o in self.objects:
            o.transform = self.transform
            o.draw()
