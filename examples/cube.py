import tkinter
from pyopengltk import OpenGLFrame
from OpenGL import GL
from OpenGL import GLU

verticies = (    (1, -1, -1),    (1, 1, -1),    (-1, 1, -1),    (-1, -1, -1),
                 (1, -1, 1),    (1, 1, 1),    (-1, -1, 1),    (-1, 1, 1)    )

edges = (    (0,1),    (0,3),    (0,4),    (2,1),    (2,3),    (2,7),
    (6,3),    (6,4),    (6,7),    (5,1),    (5,4),    (5,7)    )

def Cube():
    GL.glBegin(GL.GL_LINES)
    for edge in edges:
        for vertex in edge:
            GL.glVertex3fv(verticies[vertex])
    GL.glEnd()

class CubeSpinner( OpenGLFrame ):
    def initgl(self):
        GL.glLoadIdentity()
        GLU.gluPerspective(45, (self.width/self.height), 0.1, 50.0)
        GL.glTranslatef(0.0,0.0, -5)
    def redraw(self):
        GL.glRotatef(1, 3, 1, 1)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT|GL.GL_DEPTH_BUFFER_BIT)
        Cube()

def main():
    frm = CubeSpinner( height = 600, width = 800 )
    frm.animate = 10
    frm.pack( fill = tkinter.BOTH, expand = 1)
    return frm.mainloop()

if __name__=="__main__":
    main()
