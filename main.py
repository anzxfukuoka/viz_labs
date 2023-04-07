import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

from curves import *
from geometrix import Cube3D, Composed

# surface quality
qul = 10

# view 1 (Y = 8)
bz = BezierCurve([Point(0, 0, "xz", depth=8), Point(2, 0, "xz", depth=8), Point(3, 2, "xz", depth=8)], quality=qul)
bz2 = BezierCurve([Point(3, 2, "xz", depth=8), Point(4, 5, "xz", depth=8), Point(4, 8, "xz", depth=8)], quality=qul)

# view 2 (Y = 0)
bz3 = BezierCurve([Point(0, 1, "xz", depth=0), Point(6, 1, "xz", depth=0), Point(8, 0, "xz", depth=0)], quality=qul)
bz4 = BezierCurve([Point(8, 0, "xz", depth=0), Point(5, 2, "xz", depth=0), Point(5, 8, "xz", depth=0)], quality=qul)

# middle (Y = 4)
bz_mid = BezierCurve([Point(0, 1, "xz", depth=4), Point(2, 1, "xz", depth=4), Point(3, 3, "xz", depth=4)], quality=qul)
bz_mid2 = BezierCurve([Point(2, 2, "xz", depth=4), Point(3, 5, "xz", depth=4), Point(6, 8, "xz", depth=4)], quality=qul)

# surfaces
bs1 = BezierSurface([bz, bz_mid, bz3], last=True, quality=qul)
bs2 = BezierSurface([bz2, bz_mid2, bz4], last=True, quality=qul)

# mirrored
bs3 = BezierSurface([bz, bz_mid, bz3], last=True, quality=qul)
bs3.size = Point(-1, 1, 1)
bs4 = BezierSurface([bz2, bz_mid2, bz4], last=True, quality=qul)
bs4.size = Point(-1, 1, 1)

# composed objects
bsCurves = Composed([bz, bz2, bz3, bz4])
bsSurface = Composed([bs1, bs2, bs3, bs4])


def main():
    pygame.init()
    display = (800, 600)

    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)

    gluPerspective(90, (display[0] / display[1]), 0.001, 100.0)
    # gluOrtho2D(-100, 100, -100, 100)

    glTranslatef(0.0, -6, -20)

    glRotatef(-90, 1, 0, 0)

    x_axis = 0
    y_axis = 0
    speed = 2

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        keys = pygame.key.get_pressed()
        x_axis = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * speed
        y_axis = (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * speed

        glRotatef(x_axis, 0, 0, 1)
        glRotatef(y_axis, 1, 0, 0)

        # draw

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # Cube()

        bsCurves.drawAll()
        bsSurface.drawAll()

        pygame.display.flip()
        pygame.time.wait(10)


if __name__ == "__main__":
    main()
