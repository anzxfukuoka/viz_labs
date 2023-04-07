from abc import ABC, abstractmethod

from OpenGL.GL import shaders
from OpenGL.GL import *

from misc import load_file

# default shaders
VERTEX_SHADER = load_file("vertex_shader.vsh")
FRAGMENT_SHADER = load_file("fragment_shader.fsh")


# colors enum
class Color:
    RED = (1, 0, 0)
    GREEN = (0, 1, 0)
    BLUE = (0, 1, 1)

    WHITE = (1, 1, 1)
    BLACK = (0, 0, 0)
    GRAY = (0.33, 0.33, 0.33)
    SILVER = (0.66, 0.66, 0.66)

    TWILIGHT = (0.26, 0.22, 0.8)
    MINT = (0.4, 1, 0.6)


class MaterialBase(ABC):

    @abstractmethod
    def __init__(self, vertex_shader, fragment_shader, color=Color.SILVER):
        self.color = color
        self.vertex_shader = vertex_shader
        self.fragment_shader = fragment_shader

        self.shader = self.compile_shader()
        self.define_attrs()

    def compile_shader(self):
        compiled_vertex_shader = shaders.compileShader(self.vertex_shader, GL_VERTEX_SHADER)
        compiled_fragment_shader = shaders.compileShader(self.fragment_shader, GL_FRAGMENT_SHADER)

        compiled_shader = shaders.compileProgram(compiled_vertex_shader, compiled_fragment_shader)

        return compiled_shader

    @abstractmethod
    def define_attrs(self):
        pass


class BRDF(MaterialBase):
    def __init__(self):
        vertex_sh = load_file("brdf.vsh")
        fragment_sh = load_file("brdf.fsh")

        super(BRDF, self).__init__(vertex_sh, fragment_sh, Color.MINT)

    def define_attrs(self):
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
            location = glGetUniformLocation(self.shader, uniform)
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
            location = glGetAttribLocation(self.shader, attribute)
            if location in (None, -1):
                print('Warning, no attribute {}'.format(attribute))
            else:
                set_attrib = attribute + '_loc'
                setattr(self, set_attrib, location)
