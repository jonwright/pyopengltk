
# An opengl frame for pyopengl-tkinter based on ctypes (no togl compilation)
#
# Collected together by Jon Wright, Jan 2018.
#
# Based on the work of others:
#
# C + Tcl/Tk
# http://github.com/codeplea/opengl-tcltk/
# (zlib license)
# Article at:
#   https://codeplea.com/opengl-with-c-and-tcl-tk
#
# Python + Tkinter (no pyopengl)
# http://github.com/arcanosam/pytkogl/
# (The Code Project Open License)
# Article at 
#  http://www.codeproject.com/Articles/1073475/OpenGL-in-Python-with-TKinter
#
# Large parts copied from pyopengl/Tk/__init__.py
#

from __future__ import print_function


__all__ = [  'OpenGLFrame', 'RawOpengl', 'Opengl', 
        'glTranslateScene','glRotateScene','v3distsq' ]


import sys, math, os, logging

_log = logging.getLogger( 'pyopengltk' )

from OpenGL import GL, GLU

if sys.version_info[0] < 3:
    import Tkinter as tk
    import Dialog as dialog
else:
    import tkinter as tk
    from tkinter import dialog as dialog



class baseOpenGLFrame(tk.Frame):
    """ Common code for windows/x11 """
    def __init__(self, *args, **kw):
        # Set background to empty string to avoid 
        # flickering overdraw by Tk
        kw['bg'] ="" 
        tk.Frame.__init__( self, *args, **kw )
        self.bind('<Map>', self.tkMap )
        self.bind('<Configure>', self.tkResize )
        self.bind('<Expose>', self.tkExpose )
        self.animate = 0
        self.cb = None

    def tkMap( self, evt ):
        """" Called when frame goes onto the screen """
        self._wid = self.winfo_id()
        self.tkCreateContext( )
        self.initgl()

    def printContext(self, extns=False):
        """ For debugging """
        exts = GL.glGetString(GL.GL_EXTENSIONS)
        if extns:
            print("Extension list:")        
            for e in sorted(exts.split()):
                print(  "\t", e )
        else:
            print("Number of extensions:",len(exts.split()))
        print( "GL_VENDOR  :",GL.glGetString(GL.GL_VENDOR))
        print( "GL_RENDERER:",GL.glGetString(GL.GL_RENDERER))
        print( "GL_VERSION :",GL.glGetString(GL.GL_VERSION))
        try:
            print(" GL_MAJOR_VERSION:", GL.glGetIntegerv( GL.GL_MAJOR_VERSION ))
            print(" GL_MINOR_VERSION:", GL.glGetIntegerv( GL.GL_MINOR_VERSION ))
            print(" GL_SHADING_LANGUAGE_VERSION :", 
                    GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION))
            msk = GL.glGetIntegerv(GL.GL_CONTEXT_PROFILE_MASK)
            print(" GL_CONTEXT_CORE_PROFILE_BIT :",
                   bool( msk & GL.GL_CONTEXT_CORE_PROFILE_BIT) )
            print(" GL_CONTEXT_COMPATIBILITY_PROFILE_BIT :",
                   bool( msk & GL.GL_CONTEXT_COMPATIBILITY_PROFILE_BIT) )
        except:
            print("Old context errors arose")
            # raise

    def tkCreateContext( self ):
        # Platform dependent part
        raise NotImplementedError

    def tkMakeCurrent( self ):
        # Platform dependent part
        raise NotImplementedError

    def tkSwapBuffers( self ): 
        # Platform dependent part
        raise NotImplementedError

    def tkExpose( self, evt):
        if self.cb:
            self.after_cancel(self.cb)
        self._display()

    def tkResize( self, evt ):
        """
        Things to do on window resize:
        Adjust viewport:
            glViewPort(0,0, width, height)
        Adjust projection matrix:
            glFrustum(left * ratio, right * ratio, bottom, top, nearClip,farClip)
        or
            glOrtho(left * ratio, right * ratio, bottom, top, nearClip,farClip)
        or
            gluOrtho2D(left * ratio, right * ratio, bottom, top)
        (assuming that left, right, bottom and top are all equal and
         ratio=width/height)
        """
        self.width, self.height = evt.width, evt.height
        if self.winfo_ismapped():
            GL.glViewport( 0, 0, self.width, self.height )
            self.initgl()
            
    def _display(self):
        self.update_idletasks()
        self.tkMakeCurrent()
        self.redraw()
        self.tkSwapBuffers( )
        if self.animate > 0:
            self.cb = self.after(self.animate, self._display )
        
    def initgl(self): 
        # For the user code
        raise NotImplementedError

    def redraw(self):
        # For the user code
        raise NotImplementedError

###############################################################################
# Windows specific code here:
if sys.platform.startswith( 'win32' ):

    from ctypes import WinDLL, c_void_p, sizeof
    from ctypes.wintypes import HDC, BOOL
    from OpenGL.WGL import PIXELFORMATDESCRIPTOR, ChoosePixelFormat, \
            SetPixelFormat, SwapBuffers, wglCreateContext, wglMakeCurrent

    _user32 = WinDLL('user32')
    GetDC = _user32.GetDC
    GetDC.restype = HDC
    GetDC.argtypes = [c_void_p]

    pfd = PIXELFORMATDESCRIPTOR()
    PFD_TYPE_RGBA =         0
    PFD_MAIN_PLANE =        0
    PFD_DOUBLEBUFFER =      0x00000001
    PFD_DRAW_TO_WINDOW =    0x00000004
    PFD_SUPPORT_OPENGL =    0x00000020
    pfd.dwFlags = PFD_DRAW_TO_WINDOW | PFD_SUPPORT_OPENGL | PFD_DOUBLEBUFFER
    pfd.iPixelType = PFD_TYPE_RGBA
    pfd.cColorBits = 24
    pfd.cDepthBits = 16
    pfd.iLayerType = PFD_MAIN_PLANE

    # Inherits the base and fills in the 3 platform dependent functions
    class OpenGLFrame( baseOpenGLFrame ):
        
        def tkCreateContext( self ):
            self.__window = GetDC(self.winfo_id())
            pixelformat = ChoosePixelFormat(self.__window, pfd)
            SetPixelFormat(self.__window, pixelformat, pfd)
            self.__context = wglCreateContext(self.__window)
            wglMakeCurrent(self.__window, self.__context)

        def tkMakeCurrent( self ):
            if self.winfo_ismapped():
                wglMakeCurrent( self.__window, self.__context)
    
        def tkSwapBuffers( self ):
            if self.winfo_ismapped():
                SwapBuffers(self.__window) 

# END Windows specific code
###############################################################################
# Linux/X11 specific code here:  

if sys.platform.startswith( 'linux' ):

    from ctypes import c_int, c_char_p, c_void_p, cdll, POINTER, util, \
        pointer, CFUNCTYPE, c_bool
    from OpenGL import GLX
    try:
        from OpenGL.raw._GLX import Display
    except:
        from OpenGL.raw.GLX._types import Display
    
    _x11lib = cdll.LoadLibrary(util.find_library( "X11" ) )
    XOpenDisplay = _x11lib.XOpenDisplay
    XOpenDisplay.argtypes = [c_char_p]
    XOpenDisplay.restype = POINTER(Display)
    
    Colormap = c_void_p
    # Attributes for old style creation
    att = [     GLX.GLX_RGBA, GLX.GLX_DOUBLEBUFFER,
                GLX.GLX_RED_SIZE,   4,
                GLX.GLX_GREEN_SIZE, 4,
                GLX.GLX_BLUE_SIZE,  4,
                GLX.GLX_DEPTH_SIZE, 16,
                0,
            ]
    # Attributes for newer style creations
    fbatt = [     GLX.GLX_X_RENDERABLE     , 1,
                  GLX.GLX_DRAWABLE_TYPE    , GLX.GLX_WINDOW_BIT,
                  GLX.GLX_RENDER_TYPE      , GLX.GLX_RGBA_BIT,
                  GLX.GLX_RED_SIZE         , 1,
                  GLX.GLX_GREEN_SIZE       , 1,
                  GLX.GLX_BLUE_SIZE        , 1,
                  GLX.GLX_DOUBLEBUFFER     , 1,
                  0,
            ]

    # Inherits the base and fills in the 3 platform dependent functions
    class OpenGLFrame( baseOpenGLFrame ):

        def tkCreateContext( self ):
            self.__window = XOpenDisplay( self.winfo_screen().encode('utf-8'))
            # Check glx version:
            major = c_int(0)
            minor = c_int(0)
            GLX.glXQueryVersion( self.__window, major, minor )
            print("GLX version: %d.%d"%(major.value,minor.value))
            if major.value == 1 and minor.value < 3: # e.g. 1.2 and down
                visual = GLX.glXChooseVisual( self.__window, 0, 
                                              (GL.GLint * len(att))(* att) )
                if not visual:
                    _log.error("glXChooseVisual call failed" )
                self.__context = GLX.glXCreateContext(self.__window,
                                                      visual,
                                                      None,
                                                      GL.GL_TRUE)
                GLX.glXMakeCurrent(self.__window, self._wid, self.__context)
                return # OUT HERE FOR 1.2 and less
            else:
                # 1.3 or higher
                # which screen - should it be winfo_screen instead ??
                XDefaultScreen = _x11lib.XDefaultScreen
                XDefaultScreen.argtypes = [POINTER(Display)]
                XDefaultScreen.restype = c_int
                screen = XDefaultScreen( self.__window )
                print("Screen is ",screen)
                # Look at framebuffer configs 
                ncfg  = GL.GLint(0)
                cfgs = GLX.glXChooseFBConfig( self.__window,
                                             screen,
                                             (GL.GLint * len(fbatt))(* fbatt),
                                             ncfg )
                print( "Number of FBconfigs",ncfg.value )
                #
                # Try to match to the current window
                # ... might also be possible to set this for the frame
                # ... but for now we just take what Tk gave us
                ideal = int(self.winfo_visualid(), 16) # convert from hex
                best = -1
                for i in range(ncfg.value):
                    vis = GLX.glXGetVisualFromFBConfig(self.__window,  cfgs[i])
                    if ideal == vis.contents.visualid:
                        best = i
                        print("Got a matching visual: index %d %d xid %s"%(
                            best,vis.contents.visualid,hex(ideal) ))
                if best < 0:
                    print("oh dear - visual does not match" )
                    # Take the first in the list (should be another I guess)
                    best=0
                # Here we insist on RGBA - but didn't check earlier
                self.__context = GLX.glXCreateNewContext(self.__window,
                                                         cfgs[best],
                                                         GLX.GLX_RGBA_TYPE,
                                                         None, # share list
                                                         GL.GL_TRUE) # direct
                print("Is Direct?: ", GLX.glXIsDirect( self.__window, self.__context ))
                # Not creating another window ... some tutorials do
#                print("wid: ",self._wid)
#                self._wid = GLX.glXCreateWindow( self.__window, cfgs[best], self._wid, None)
#                print("wid: ",self._wid)
                GLX.glXMakeContextCurrent( self.__window, self._wid, self._wid,
                                           self.__context )
                print("Done making a first context")
                extensions = GLX.glXQueryExtensionsString(self.__window, screen)
                # Here we quit - getting a modern context needs further work below
                return
                if "GLX_ARB_create_context" in extensions:
                    # We can try to upgrade it ??
                    print("Trying to upgrade context")
                    s =  "glXCreateContextAttribsARB"
                    p = GLX.glXGetProcAddress( c_char_p( s ) )
                    
                    print(p)
                    if not p:
                        p = GLX.glXGetProcAddressARB( ( GL.GLubyte * len(s)).from_buffer_copy(s) )
                    print(p)
                    if p:
                        print(" p is true")
                    p.restype = GLX.GLXContext
                    p.argtypes = [POINTER(Display),
                                  GLX.GLXFBConfig,
                                  GLX.GLXContext,
                                  c_bool,
                                  POINTER(c_int)]
                    arb_attrs =   fbatt[:-1] + [ ]

                    #    GLX.GLX_CONTEXT_MAJOR_VERSION_ARB , 3  
                    #    GLX.GLX_CONTEXT_MINOR_VERSION_ARB , 1,
                    #    0 ]
                    #
                    #    GLX.GLX_CONTEXT_FLAGS_ARB
                    #    GLX.GLX_CONTEXT_PROFILE_MASK_ARB
                    #]
#                    import pdb
#                    pdb.set_trace()
                    self.__context = p( self.__window, cfgs[best], None, GL.GL_TRUE,
                                        (GL.GLint * len(arb_attrs))(* arb_attrs) )
                

        def tkMakeCurrent( self ):
            if self.winfo_ismapped():
                GLX.glXMakeCurrent(self.__window, self._wid, self.__context)

        def tkSwapBuffers( self ):
            if self.winfo_ismapped():
                GLX.glXSwapBuffers( self.__window, self._wid)

# Linux/X11 specific code ends  
###############################################################################


# Code copied from pyopengl/Tk/__init__.py for compatibility
# Modified so it does not import *
#
#
# A class that creates an opengl widget.
# Mike Hartshorn
# Department of Chemistry
# University of York, UK

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


def v3distsq(a,b):
    d = ( a[0] - b[0], a[1] - b[1], a[2] - b[2] )
    return d[0]*d[0] + d[1]*d[1] + d[2]*d[2]


class RawOpengl( OpenGLFrame ):
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

        #Widget.__init__(self, master, 'togl', cnf, kw)
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
        #self.bind('<Button-1><ButtonRelease-1>', self.tkHandlePick)
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

        # Scale mouse translations to object viewplane so object tracks with mouse

        win_height = max( 1,self.winfo_height() )
        obj_c = ( self.xcenter, self.ycenter, self.zcenter )
        win = GLU.gluProject( obj_c[0], obj_c[1], obj_c[2])
        obj = GLU.gluUnProject( win[0], win[1] + 0.5 * win_height, win[2])
        dist = math.sqrt( v3distsq( obj, obj_c ) )
        scale = abs( dist / ( 0.5 * win_height ) )

        glTranslateScene(scale, event.x, event.y, self.xmouse, self.ymouse)
        self.tkRedraw()
        self.tkRecordMouse(event)


    def tkRedraw(self, *dummy):
        """Cause the opengl widget to redraw itself."""

        if not self.initialised: return
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
            glMatrixMode(GL_MODELVIEW)
            mat = glGetDoublev(GL_MODELVIEW_MATRIX)
            glLoadIdentity()
            glTranslatef(-self.xcenter, -self.ycenter, -(
                self.zcenter+self.distance))
            glMultMatrixd(mat)
        else:
            GLU.gluLookAt(self.xcenter, self.ycenter, self.zcenter+self.distance,
                self.xcenter, self.ycenter, self.zcenter,
                0., 1., 0.)
            GL.glMatrixMode(GL.GL_MODELVIEW)
    
        # Call objects redraw method.
        self.redraw(self)
        GL.glFlush()      # Tidy up
        GL.glPopMatrix()  # Restore the matrix

        self.tkSwapBuffers()


    def redraw( self, *args, **named ):
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

