"""
Code copied from pyopengl/Tk/__init__.py for compatibility
Modified so it does not import *

A class that creates an opengl widget.
Mike Hartshorn
Department of Chemistry
University of York, UK
"""
import sys
import math
from OpenGL import GL, GLU
from pyopengltk import OpenGLFrame

if sys.version_info[0] < 3:
    import Tkinter as tk
    import Dialog as dialog
else:
    import tkinter as tk
    from tkinter import dialog as dialog


def glTranslateScene(s, x, y, mousex, mousey):
    GL.glMatrixMode(GL.GL_MODELVIEW)
    mat = GL.glGetDoublev(GL.GL_MODELVIEW_MATRIX)
    GL.glLoadIdentity()
    GL.glTranslatef(s * (x - mousex), s * (mousey - y), 0.0)
    GL.glMultMatrixd(mat)


def glRotateScene(s, xcenter, ycenter, zcenter, x, y, mousex, mousey):
    GL.glMatrixMode(GL.GL_MODELVIEW)
    mat = GL.glGetDoublev(GL.GL_MODELVIEW_MATRIX)
    GL.glLoadIdentity()
    GL.glTranslatef(xcenter, ycenter, zcenter)
    GL.glRotatef(s * (y - mousey), 1., 0., 0.)
    GL.glRotatef(s * (x - mousex), 0., 1., 0.)
    GL.glTranslatef(-xcenter, -ycenter, -zcenter)
    GL.glMultMatrixd(mat)


def v3distsq(a, b):
    d = (a[0] - b[0], a[1] - b[1], a[2] - b[2])
    return d[0] * d[0] + d[1] * d[1] + d[2] * d[2]


class RawOpengl(OpenGLFrame):
    """Widget without any sophisticated bindings\
    by Tom Schwaller"""
    def __init__(self, master=None, cnf={}, **kw):
        OpenGLFrame.__init__(*(self, master, cnf), **kw)

    # replaces our _display method
    def tkRedraw(self, *dummy):
        # This must be outside of a pushmatrix, since a resize event
        # will call redraw recursively.
        self.update_idletasks()
        self.tkMakeCurrent()
        _mode = GL.glGetDoublev(GL.GL_MATRIX_MODE)
        try:
            GL.glMatrixMode(GL.GL_PROJECTION)
            GL.glPushMatrix()
            try:
                self.redraw()
                GL.glFlush()
            finally:
                GL.glPopMatrix()
        finally:
            GL.glMatrixMode(_mode)
        self.tkSwapBuffers()


class Opengl(RawOpengl):
    """
    Tkinter bindings for an Opengl widget.
    Mike Hartshorn
    Department of Chemistry
    University of York, UK
    http://www.yorvic.york.ac.uk/~mjh/
    """

    def __init__(self, master=None, cnf={}, **kw):
        """\
        Create an opengl widget.
        Arrange for redraws when the window is exposed or when
        it changes size."""

        # Widget.__init__(self, master, 'togl', cnf, kw)
        RawOpengl.__init__(*(self, master, cnf), **kw)
        self.initialised = 0

        # Current coordinates of the mouse.
        self.xmouse = 0
        self.ymouse = 0

        # Where we are centering.
        self.xcenter = 0.0
        self.ycenter = 0.0
        self.zcenter = 0.0

        # The _back color
        self.r_back = 1.
        self.g_back = 0.
        self.b_back = 1.

        # Where the eye is
        self.distance = 10.0

        # Field of view in y direction
        self.fovy = 30.0

        # Position of clipping planes.
        self.near = 0.1
        self.far = 1000.0

        # Is the widget allowed to autospin?
        self.autospin_allowed = 0

        # Is the widget currently autospinning?
        self.autospin = 0

        # Basic bindings for the virtual trackball
        self.bind('<Shift-Button-1>', self.tkHandlePick)
        # self.bind('<Button-1><ButtonRelease-1>', self.tkHandlePick)
        self.bind('<Button-1>', self.tkRecordMouse)
        self.bind('<B1-Motion>', self.tkTranslate)
        self.bind('<Button-2>', self.StartRotate)
        self.bind('<B2-Motion>', self.tkRotate)
        self.bind('<ButtonRelease-2>', self.tkAutoSpin)
        self.bind('<Button-3>', self.tkRecordMouse)
        self.bind('<B3-Motion>', self.tkScale)

    def help(self):
        """Help for the widget."""

        d = dialog.Dialog(None, {
            'title': 'Viewer help',
            'text': 'Button-1: Translate\n'
                    'Button-2: Rotate\n'
                    'Button-3: Zoom\n'
                    'Reset: Resets transformation to identity\n',
            'bitmap': 'questhead',
            'default': 0,
            'strings': ('Done', 'Ok')})
        assert d

    def activate(self):
        """Cause this Opengl widget to be the current destination for drawing."""
        self.tkMakeCurrent()

    # This should almost certainly be part of some derived class.
    # But I have put it here for convenience.
    def basic_lighting(self):
        """\
        Set up some basic lighting (single infinite light source).

        Also switch on the depth buffer."""

        self.activate()
        light_position = (1, 1, 1, 0)
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_POSITION, light_position)
        GL.glEnable(GL.GL_LIGHTING)
        GL.glEnable(GL.GL_LIGHT0)
        GL.glDepthFunc(GL.GL_LESS)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()

    def initgl(self):
        self.basic_lighting()

    def set_background(self, r, g, b):
        """Change the background colour of the widget."""

        self.r_back = r
        self.g_back = g
        self.b_back = b

        self.tkRedraw()

    def set_centerpoint(self, x, y, z):
        """Set the new center point for the model.
        This is where we are looking."""

        self.xcenter = x
        self.ycenter = y
        self.zcenter = z

        self.tkRedraw()

    def set_eyepoint(self, distance):
        """Set how far the eye is from the position we are looking."""

        self.distance = distance
        self.tkRedraw()

    def reset(self):
        """Reset rotation matrix for this widget."""

        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        self.tkRedraw()

    def tkHandlePick(self, event):
        """Handle a pick on the scene."""

        if hasattr(self, 'pick'):
            # here we need to use glu.UnProject

            # Tk and X have their origin top left, 
            # while Opengl has its origin bottom left.
            # So we need to subtract y from the window height to get
            # the proper pick position for Opengl

            realy = self.winfo_height() - event.y

            p1 = GLU.gluUnProject(event.x, realy, 0.)
            p2 = GLU.gluUnProject(event.x, realy, 1.)

            if self.pick(self, p1, p2):
                """If the pick method returns true we redraw the scene."""

                self.tkRedraw()

    def tkRecordMouse(self, event):
        """Record the current mouse position."""

        self.xmouse = event.x
        self.ymouse = event.y

    def StartRotate(self, event):
        # Switch off any autospinning if it was happening

        self.autospin = 0
        self.tkRecordMouse(event)

    def tkScale(self, event):
        """Scale the scene.  Achieved by moving the eye position.

        Dragging up zooms in, while dragging down zooms out
        """
        scale = 1 - 0.01 * (event.y - self.ymouse)
        # do some sanity checks, scale no more than
        # 1:1000 on any given click+drag
        if scale < 0.001:
            scale = 0.001
        elif scale > 1000:
            scale = 1000
        self.distance = self.distance * scale
        self.tkRedraw()
        self.tkRecordMouse(event)

    def do_AutoSpin(self):
        self.activate()

        glRotateScene(0.5, self.xcenter, self.ycenter, self.zcenter,
                      self.yspin, self.xspin, 0, 0)
        self.tkRedraw()

        if self.autospin:
            self.after(10, self.do_AutoSpin)

    def tkAutoSpin(self, event):
        """Perform autospin of scene."""

        self.after(4)
        self.update_idletasks()

        # This could be done with one call to pointerxy but I'm not sure
        # it would any quicker as we would have to split up the resulting
        # string and then conv

        x = self.tk.getint(self.tk.call('winfo', 'pointerx', self._w))
        y = self.tk.getint(self.tk.call('winfo', 'pointery', self._w))

        if self.autospin_allowed:
            if x != event.x_root and y != event.y_root:
                self.autospin = 1

        self.yspin = x - event.x_root
        self.xspin = y - event.y_root

        self.after(10, self.do_AutoSpin)

    def tkRotate(self, event):
        """Perform rotation of scene."""

        self.activate()
        glRotateScene(0.5, self.xcenter, self.ycenter, self.zcenter,
                      event.x, event.y, self.xmouse, self.ymouse)
        self.tkRedraw()
        self.tkRecordMouse(event)

    def tkTranslate(self, event):
        """Perform translation of scene."""

        self.activate()

        # Scale mouse translations to object viewplane so object
        # tracks with mouse

        win_height = max(1, self.winfo_height())
        obj_c = (self.xcenter, self.ycenter, self.zcenter)
        win = GLU.gluProject(obj_c[0], obj_c[1], obj_c[2])
        obj = GLU.gluUnProject(win[0], win[1] + 0.5 * win_height, win[2])
        dist = math.sqrt(v3distsq(obj, obj_c))
        scale = abs(dist / (0.5 * win_height))

        glTranslateScene(scale, event.x, event.y, self.xmouse, self.ymouse)
        self.tkRedraw()
        self.tkRecordMouse(event)

    def tkRedraw(self, *dummy):
        """Cause the opengl widget to redraw itself."""

        if not self.initialised:
            return

        self.activate()

        GL.glPushMatrix()        # Protect our matrix
        self.update_idletasks()
        self.activate()
        w = self.winfo_width()
        h = self.winfo_height()
        GL.glViewport(0, 0, w, h)

        # Clear the background and depth buffer.
        GL.glClearColor(self.r_back, self.g_back, self.b_back, 0.)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GLU.gluPerspective(self.fovy, float(w)/float(h), self.near, self.far)

        if 0:
            # Now translate the scene origin away from the world origin
            GL.glMatrixMode(GL.GL_MODELVIEW)
            mat = GL.glGetDoublev(GL.GL_MODELVIEW_MATRIX)
            GL.glLoadIdentity()
            GL.glTranslatef(-self.xcenter, -self.ycenter, -(
                self.zcenter+self.distance))
            GL.glMultMatrixd(mat)
        else:
            GLU.gluLookAt(self.xcenter, self.ycenter, self.zcenter + self.distance,
                          self.xcenter, self.ycenter, self.zcenter,
                          0., 1., 0.)
            GL.glMatrixMode(GL.GL_MODELVIEW)

        # Call objects redraw method.
        self.redraw(self)
        GL.glFlush()      # Tidy up
        GL.glPopMatrix()  # Restore the matrix

        self.tkSwapBuffers()

    def redraw(self, *args, **named):
        """Prevent access errors if user doesn't set redraw fast enough"""

    def tkExpose(self, *dummy):
        """Redraw the widget.
        Make it active, update tk events, call redraw procedure and
        swap the buffers.  Note: swapbuffers is clever enough to
        only swap double buffered visuals."""

        self.activate()
        if not self.initialised:
            self.basic_lighting()
            self.initialised = 1
        self.tkRedraw()

    def tkPrint(self, file):
        """Turn the current scene into PostScript via the feedback buffer."""
        self.activate()
