import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

from curves import *
from geometrix import Cube3D

qul = 10

# view 1
bz = BezierCurve([Point(0, 0, "xz", depth=8), Point(2, 0, "xz", depth=8), Point(3, 2, "xz", depth=8)], quality=qul)
bz2 = BezierCurve([Point(3, 2, "xz", depth=8), Point(4, 5, "xz", depth=8), Point(4, 8, "xz", depth=8)], quality=qul)

bz_mid = BezierCurve([Point(0, 1, "xz", depth=4), Point(2, 1, "xz", depth=4), Point(3, 3, "xz", depth=4)], quality=qul)

# view 2
bz3 = BezierCurve([Point(0, 1, "xz", depth=0), Point(6, 1, "xz", depth=0), Point(8, 0, "xz", depth=0)], quality=qul)
bz4 = BezierCurve([Point(8, 0, "xz", depth=0), Point(5, 2, "xz", depth=0), Point(5, 8, "xz", depth=0)], quality=qul)

bz_mid2 = BezierCurve([Point(2, 2, "xz", depth=4), Point(3, 5, "xz", depth=4), Point(3, 8, "xz", depth=4)], quality=qul)

# surf

bs1 = BezierSurface([bz, bz_mid, bz3], last=True, quality=qul)
bs2 = BezierSurface([bz2, bz_mid2, bz4], last=True, quality=qul)

bs3 = BezierSurface([bz, bz_mid, bz3], last=True, quality=qul)
bs3.size = Point(-1, 1, 1)
bs4 = BezierSurface([bz2, bz_mid2, bz4], last=True, quality=qul)
bs4.size = Point(-1, 1, 1)


def DrawBz(verts, edges):
    glBegin(GL_LINES)

    vertexes = tuple([(p.x, p.y, p.z) for p in verts])
    lines = tuple(edges)

    for line in lines:
        for vertex in line:
            glVertex3fv(vertexes[vertex])
            # glVertex3fv(np.array(vertexes[vertex]) * 0.8)
    glEnd()


def main():
    pygame.init()
    display = (800, 600)

    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    gluPerspective(90, (display[0] / display[1]), 0.001, 100.0)
    # gluOrtho2D(-100, 100, -100, 100)

    glTranslatef(0.0, -6, -20)

    glRotatef(-90, 1, 0, 0)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        glRotatef(1, 0, 0, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # Cube()

        bz.draw()
        bz2.draw()
        bz3.draw()
        bz4.draw()

        bs1.draw()
        bs2.draw()
        bs3.draw()
        bs4.draw()

        """for v in bs1.get_verts():
            cube = Cube3D(pos=v, size=Point(0.1, 0.1, 0.1))
            cube.draw()"""

        pygame.display.flip()
        pygame.time.wait(10)


main()
