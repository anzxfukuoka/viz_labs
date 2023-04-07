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
    def __init__(self, position=None, rotation=None, size=None):
        if size is None:
            size = [1, 1, 1]
        if rotation is None:
            rotation = [0, 0, 0]
        if position is None:
            position = [0, 0, 0]

        self.position = position
        self.rotation = rotation
        self.size = size
        pass

    def local_to_global(self, v3):
        v4 = np.array([v3[0], v3[1], v3[2], 1])
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
                       [0, 0, 0, 1]])
        return mx

    def _rotation_matrix(self):
        x, y, z = [math.radians(rot_deg) for rot_deg in self.rotation]

        rmz = np.array([[math.cos(z), -math.sin(z), 0, 0],
                        [math.sin(z), math.cos(z), 0, 0],
                        [0, 0, 1, 0],
                        [0, 0, 0, 1]])

        rmx = np.array([[1, 0, 0, 0],
                        [0, math.cos(x), -math.sin(x), 0],
                        [0, math.sin(x), math.cos(x), 0],
                        [0, 0, 0, 1]])

        rmy = np.array([[math.cos(y), 0, math.sin(y), 0],
                        [0, 1, 0, 0],
                        [-math.sin(y), 0, math.cos(y), 0],
                        [0, 0, 0, 1]])

        return rmy, rmx, rmz

    def _scale_matrix(self):
        mx = np.array([[self.size[0], 0, 0, 0],
                       [0, self.size[1], 0, 0],
                       [0, 0, self.size[2], 0],
                       [0, 0, 0, 1]])
        return mx


class Object3D(ABC):

    def __init__(self, transform=None):
        self.shader = None

        if transform is None:
            self.transform = Transform()

        self.vertexes = self.set_verts()
        self.edges = self.set_edges()
        self.surfaces = self.set_surfs()
        self.normals = self.calc_normals()
        # color = (lambda: Color.GREEN if vertex % 2 == 0 else Color.RED if vertex % 3 == 0 else Color.BLUE)()
        self.colors = np.array([Color.TWILIGHT] * len(self.vertexes))

    def _compile_shader(self):
        VERTEX_SHADER = load_file("vertex_shader.vsh")
        FRAGMENT_SHADER = load_file("fragment_shader.fsh")

        compiled_vertex_shader = shaders.compileShader(VERTEX_SHADER, GL_VERTEX_SHADER)
        compiled_fragment_shader = shaders.compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)

        shader = shaders.compileProgram(compiled_vertex_shader, compiled_fragment_shader)

        # vertexes = np.array([p.to_list() for p in self.get_verts()], dtype=np.float32)
        vertexes = np.array([p.to_list() + [0, 0, 0] for p in self.set_verts()], dtype=np.float32)
        # normals = self.get_verts_normals()

        # vbo = np.append(vertexes, normals, axis=1)

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

        if len(self.set_surfs()) == 0:
            return

        self.shader = self._compile_shader()
        glUseProgram(self.shader)
        try:
            self.vbo.bind()
            try:
                # use the memory locations we found earlier (now python attributes
                # on the current class) for shader variables and put data into
                # the shader variables
                glUniform4f(self.Global_ambient_loc, .3, .05, .05, .1)
                glUniform4f(self.Light_ambient_loc, .2, .2, .2, 1.0)
                glUniform4f(self.Light_diffuse_loc, 1, 1, 1, 1)
                glUniform3f(self.Light_location_loc, 2, 2, 10)
                glUniform4f(self.Material_ambient_loc, .2, .2, .2, 1.0)
                glUniform4f(self.Material_diffuse_loc, 1, 1, 1, 1)

                glEnableVertexAttribArray(self.Vertex_position_loc)
                glEnableVertexAttribArray(self.Vertex_normal_loc)

                # reference our vertex data and normals data
                stride = 6 * 4
                glVertexAttribPointer(
                    self.Vertex_position_loc,
                    3, GL_FLOAT, False, stride, self.vbo
                )
                glVertexAttribPointer(
                    self.Vertex_normal_loc,
                    3, GL_FLOAT, False, stride, self.vbo + 12
                )

                trns_count = len(self.set_surfs())

                glDrawArrays(GL_TRIANGLES, 0, trns_count)
            finally:
                self.vbo.unbind()
                glDisableVertexAttribArray(self.Vertex_position_loc)
                glDisableVertexAttribArray(self.Vertex_normal_loc)
        finally:
            glUseProgram(0)

    def calc_normals(self):
        """
        normal vectors for each vertex
        :return:
        """
        surfs = self.surfaces
        verts = self.vertexes

        verts_count = len(self.vertexes)
        a = [np.array([])] * verts_count
        vert_norms = []

        for i in range(verts_count):

            vert_norm = []

            for surf in surfs:

                v1 = verts[surf[2]] - verts[surf[0]]
                v2 = verts[surf[1]] - verts[surf[0]]
                norm = np.cross(v1.to_list(), v2.to_list())
                norm = norm / np.linalg.norm(norm)  # normalized

                if i in surf:
                    vert_norm.append(norm)

            vert_norm = np.array(vert_norm)
            vert_norm = vert_norm.sum(axis=0)
            vert_norms.append(vert_norm)

        return np.array(vert_norms)

    @abstractmethod
    def set_edges(self):
        """
        edges indexes
        :return:
        """
        pass

    @abstractmethod
    def set_verts(self):
        """
        vertexes
        :return:
        """
        pass

    @abstractmethod
    def set_surfs(self):
        """
        surfaces indexes
        :return:
        """
        pass

    def draw(self, parent_transform=None, draw_warframe=False):

        self.apply_material()

        glBegin(GL_TRIANGLES)

        for i, surface in enumerate(self.surfaces):
            x = 0

            for vertex in surface:
                x += 1
                color = self.colors[vertex]
                glColor3fv(color)

                nx, ny, nz = self.normals[vertex]
                glNormal(nx, ny, nz)
                # point = self.pos + vertexes[vertex] * self.size
                v = self.vertexes[vertex].to_list()
                point = self.transform.local_to_global(v)
                if parent_transform:
                    point = parent_transform.local_to_global(point)
                # glVertex3fv(point.to_list())
                glVertex3fv(point)
        glEnd()

        if not draw_warframe:
            return

        glColor3fv(Color.WHITE)

        glBegin(GL_LINES)

        for edge in self.edges:
            for vertex in edge:
                # point = self.pos + vertexes[vertex] * self.size
                # point = vertexes[vertex]
                v = self.vertexes[vertex].to_list()
                point = self.transform.local_to_global(v)
                if parent_transform:
                    point = parent_transform.local_to_global(point)
                # glVertex3fv(point.to_list())
                glVertex3fv(point)

        # normals

        # for i, surface in enumerate(surfaces):
        #     nx, ny, nz = normals[i]
        #     center = vertexes[surfaces[i][0]].to_list()
        #     norm = center + Point(nx, ny, nz).to_list()
        #
        #     center = self.transform.local_to_global(center)
        #     norm = self.transform.local_to_global(norm)
        #
        #     glVertex3fv(center)
        #     glVertex3fv(norm)

        glEnd()

    pass


class Cube3D(Object3D):
    """
    Cube primitive object
    """

    def __init__(self):
        super(Cube3D, self).__init__()

    def set_edges(self):
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

    def set_surfs(self):
        surfaces = (
            (0, 1, 2),
            (2, 3, 0),

            (3, 2, 7),
            (7, 6, 3),

            (6, 7, 5),
            (5, 4, 6),

            (4, 5, 1),
            (1, 0, 4),

            (1, 5, 7),
            (7, 2, 1),

            (4, 0, 3),
            (3, 6, 4)
        )
        return surfaces

    def set_verts(self):
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


class Composed:

    def set_material_all(self):
        for o in self.objects:
            o.set_material()

    def __init__(self, objects: list[Object3D] | np.ndarray = []):
        self.transform = Transform()
        self.objects = objects

    def draw_all(self):
        for o in self.objects:
            o.draw(self.transform)
