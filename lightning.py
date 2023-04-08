from abc import ABC, abstractmethod

import numpy as np
import pygame as pg
import pyrr as pyrr
from OpenGL.GL import shaders
from OpenGL.GL import *
from PIL import Image

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

    def apply_transform(self, trans):
        self.model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
        """
            pitch: rotation around x axis
            roll:rotation around z axis
            yaw: rotation around y axis
        """
        self.model_transform = pyrr.matrix44.multiply(
            m1=self.model_transform,
            m2=pyrr.matrix44.create_from_eulers(
                eulers=np.radians(trans.rotation), dtype=np.float32
            )
        )
        self.model_transform = pyrr.matrix44.multiply(
            m1=self.model_transform,
            m2=pyrr.matrix44.create_from_translation(
                vec=np.array(trans.position), dtype=np.float32
            )
        )

        glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, self.model_transform)

    def __init__(self, color_main):
        vertex_sh = VERTEX_SHADER
        fragment_sh = FRAGMENT_SHADER

        self.color_main = color_main

        super(DefaultMaterial, self).__init__(vertex_sh, fragment_sh)


class Glass(MaterialBase):

    def __init__(self):
        vertex_sh = load_file("texsh.vsh")
        fragment_sh = load_file("texsh.fsh")

        self.wood_texture = Tex("tex.jpg")
        self.wood_texture.use()

        super(Glass, self).__init__(vertex_sh, fragment_sh)

    def apply_uniform(self):
        glUniform1i(glGetUniformLocation(self.shader, "imageTexture"), 0)

        # projection_transform = pyrr.matrix44.create_perspective_projection(
        #     fovy=90, aspect=800 / 600,
        #     near=0.001, far=100.0, dtype=np.float32
        # )
        #
        # glUniformMatrix4fv(
        #     glGetUniformLocation(self.shader, "projection"),
        #     1, GL_FALSE, projection_transform
        # )
        # self.modelMatrixLocation = glGetUniformLocation(self.shader, "model")
        pass

    def apply_attrs(self):

        # glEnableVertexAttribArray(self.Vertex_position_loc)
        # glEnableVertexAttribArray(self.Vertex_normal_loc)
        # glEnableVertexAttribArray(self.Tex_coord_loc)
        #
        # glVertexAttribPointer(self.Vertex_position_loc,
        #                       3, GL_FLOAT, GL_FALSE, 0, None)
        # glVertexAttribPointer(self.Vertex_normal_loc,
        #                       3, GL_FLOAT, GL_FALSE, 0, None)
        # glVertexAttribPointer(self.Tex_coord_loc,
        #                       2, GL_FLOAT, GL_FALSE, 0, None)

        # get the position from  shader
        glBindAttribLocation(self.shader, 0, 'position')
        #position = glGetAttribLocation(self.shader, 'position')
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 4 * 8, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        # get the color from  shader
        glBindAttribLocation(self.shader, 1, 'color')
        #color = glGetAttribLocation(self.shader, 'color')
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 4 * 8, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)

        glBindAttribLocation(self.shader, 2, 'InTexCoords')
        #texCoords = glGetAttribLocation(self.shader, "InTexCoords")
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 4 * 8, ctypes.c_void_p(24))
        glEnableVertexAttribArray(2)

        # VBO

        # glEnableVertexAttribArray(self.Vertex_position_loc)
        # glVertexAttribPointer(self.Vertex_position_loc,
        #                       3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        #
        # glEnableVertexAttribArray(self.Vertex_normal_loc)
        # glVertexAttribPointer(self.Vertex_normal_loc,
        #                       3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
        #
        # glEnableVertexAttribArray(self.Tex_coord_loc)
        # glVertexAttribPointer(self.Tex_coord_loc,
        #                       2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(24))



    def define_attrs(self):

        # self.Vertex_position_loc = 0
        # self.Vertex_normal_loc = 1
        # self.Tex_coord_loc = 2
        #
        # glBindAttribLocation(self.shader, self.Vertex_position_loc, "Vertex_position")
        # glBindAttribLocation(self.shader, self.Vertex_normal_loc, "Vertex_normal")
        # glBindAttribLocation(self.shader, self.Tex_coord_loc, "Tex_coord")
        pass


class BRDF(MaterialBase):
    def apply_attrs(self):

        # tex

        self.wood_texture.use()

        glEnableVertexAttribArray(self.Vertex_position_loc)
        glEnableVertexAttribArray(self.Vertex_normal_loc)

        glVertexAttribPointer(self.Vertex_position_loc,
                              3, GL_FLOAT, GL_FALSE, 0, None)
        glVertexAttribPointer(self.Vertex_normal_loc,
                              3, GL_FLOAT, GL_FALSE, 0, None)
        glVertexAttribPointer(4,
                              2, GL_FLOAT, GL_FALSE, 0, None)

    def __init__(self, light_pos, color_main):
        vertex_sh = load_file("brdf.vsh")
        fragment_sh = load_file("brdf.fsh")

        self.light_pos = light_pos
        self.color = color_main

        self.wood_texture = Tex("tex.jpg")

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
            ,'Vertex_normal'
        )
        for attribute in attribute_values:
            location = glGetAttribLocation(self.shader, attribute)
            if location in (None, -1):
                print('Warning, no attribute {}'.format(attribute))
            else:
                set_attrib = attribute + '_loc'
                setattr(self, set_attrib, location)

        self.vertexTexCoord_loc = 4

        glBindAttribLocation(self.shader, self.vertexTexCoord_loc, "vertexTexCoord")

class Tex:
    def __init__(self, filepath):
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        image = pg.image.load(filepath).convert_alpha()
        image_width,image_height = image.get_rect().size
        img_data = pg.image.tostring(image,'RGBA')
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

    def use(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D,self.texture)

    def destroy(self):
        glDeleteTextures(1, (self.texture,))