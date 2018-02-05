
from __future__ import print_function

"""
Demo entry point for Tkinter Window with OpenGL
"""

import sys, math, time
if sys.version_info[0] < 3 :
    from Tkinter import Tk, YES, BOTH
else:
    from tkinter import Tk, YES, BOTH
from OpenGL import GL, GLU
from pyopengltk import OpenGLFrame

class AppOgl(OpenGLFrame):

    def initgl(self):
        GL.glViewport( 0, 0, self.width, self.height)
        GL.glClearColor(1.0,1.0,1.0,0.0)
        GL.glColor3f(0.0,0.0, 0.0)
        GL.glPointSize(4.0)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GLU.gluOrtho2D(-5,5,-5,5)
        self.start = time.time()
        self.nframes = 0
    

    def redraw(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        GL.glBegin(GL.GL_POINTS)
        npt = 100
        for i in range(npt):
            x = -5.0 + i*10.0/npt 
            y = math.sin(x+ time.time())*5/2
            GL.glVertex2f( x, y )
        GL.glEnd()
        GL.glFlush()
        self.nframes+=1
        tm = time.time() - self.start
        print("fps",self.nframes / tm, end="\r" )

if __name__ == '__main__':
    root = Tk()
    app = AppOgl(root, width=320, height=200)
    app.pack(fill=BOTH, expand=YES)
    app.animate=1
    app.after(100, app.printContext)
    app.mainloop()
