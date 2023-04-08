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

    def __init__(self, vertex_shader, fragment_shader):
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
    def apply_uniform(self):
        pass

    @abstractmethod
    def apply_attrs(self):
        pass

    @abstractmethod
    def define_attrs(self):
        pass


class DefaultMaterial(MaterialBase):
    def apply_attrs(self):
        pass

    def apply_uniform(self):
        glUniform4f(self.Color_Main_loc, self.color_main[0], self.color_main[1], self.color_main[2], self.color_main[3])

    def define_attrs(self):
        # shader uniform
        self.Color_Main_loc = glGetUniformLocation(self.shader, "Color_Main")

    def __init__(self, color_main):
        vertex_sh = VERTEX_SHADER
        fragment_sh = FRAGMENT_SHADER

        self.color_main = color_main

        super(DefaultMaterial, self).__init__(vertex_sh, fragment_sh)


class BRDF(MaterialBase):
    def apply_attrs(self):
        glEnableVertexAttribArray(self.Vertex_position_loc)
        glEnableVertexAttribArray(self.Vertex_normal_loc)

        glVertexAttribPointer(self.Vertex_position_loc,
                              3, GL_FLOAT, GL_FALSE, 0, None)
        glVertexAttribPointer(self.Vertex_normal_loc,
                              3, GL_FLOAT, GL_FALSE, 0, None)

    def __init__(self, light_pos, color_main):
        vertex_sh = load_file("brdf.vsh")
        fragment_sh = load_file("brdf.fsh")

        self.light_pos = light_pos
        self.color = color_main

        super(BRDF, self).__init__(vertex_sh, fragment_sh)

    def apply_uniform(self):
        glUniform4f(self.Global_ambient_loc, .0, .6, .6, .1)
        glUniform4f(self.Light_ambient_loc, .2, .2, .2, 1.0)
        glUniform4f(self.Light_diffuse_loc, 1, 0.8, 0.9, 1)
        glUniform3f(self.Light_location_loc, self.light_pos[0], self.light_pos[1], self.light_pos[2])
        glUniform4f(self.Material_ambient_loc, .2, .2, .2, 1.0)
        glUniform4f(self.Material_diffuse_loc, self.color[0], self.color[1], self.color[2], self.color[3])

    def define_attrs(self):
        # get memory locations for
        # shader uniform variables
        uniform_values = (
            "Global_ambient",
            "Light_ambient",
            "Light_diffuse",
            "Light_location",
            "Material_ambient",
            "Material_diffuse",
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
