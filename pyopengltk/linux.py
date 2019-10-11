"""
Linux implementation of the opengl frame
"""
from __future__ import print_function
import logging
from ctypes import c_int, c_char_p, c_void_p, cdll, POINTER, util, \
    pointer, CFUNCTYPE, c_bool
from OpenGL import GL, GLX
from pyopengltk.base import BaseOpenGLFrame

try:
    from OpenGL.raw._GLX import Display
except:
    from OpenGL.raw.GLX._types import Display

_log = logging.getLogger(__name__)


_x11lib = cdll.LoadLibrary(util.find_library("X11"))
XOpenDisplay = _x11lib.XOpenDisplay
XOpenDisplay.argtypes = [c_char_p]
XOpenDisplay.restype = POINTER(Display)

Colormap = c_void_p
# Attributes for old style creation
att = [
    GLX.GLX_RGBA, GLX.GLX_DOUBLEBUFFER,
    GLX.GLX_RED_SIZE,   4,
    GLX.GLX_GREEN_SIZE, 4,
    GLX.GLX_BLUE_SIZE,  4,
    GLX.GLX_DEPTH_SIZE, 16,
    0,
]
# Attributes for newer style creations
fbatt = [
    GLX.GLX_X_RENDERABLE,    1,
    GLX.GLX_DRAWABLE_TYPE,   GLX.GLX_WINDOW_BIT,
    GLX.GLX_RENDER_TYPE,     GLX.GLX_RGBA_BIT,
    GLX.GLX_RED_SIZE,        1,
    GLX.GLX_GREEN_SIZE,      1,
    GLX.GLX_BLUE_SIZE,       1,
    GLX.GLX_DOUBLEBUFFER,    1,
    0,
]


# Inherits the base and fills in the 3 platform dependent functions
class OpenGLFrame(BaseOpenGLFrame):

    def tkCreateContext(self):
        self.__window = XOpenDisplay(self.winfo_screen().encode('utf-8'))
        # Check glx version:
        major = c_int(0)
        minor = c_int(0)
        GLX.glXQueryVersion(self.__window, major, minor)
        print("GLX version: %d.%d" % (major.value, minor.value))
        if major.value == 1 and minor.value < 3:  # e.g. 1.2 and down
            visual = GLX.glXChooseVisual(self.__window, 0, (GL.GLint * len(att))(* att))
            if not visual:
                _log.error("glXChooseVisual call failed")
            self.__context = GLX.glXCreateContext(self.__window,
                                                  visual,
                                                  None,
                                                  GL.GL_TRUE)
            GLX.glXMakeCurrent(self.__window, self._wid, self.__context)
            return  # OUT HERE FOR 1.2 and less
        else:
            # 1.3 or higher
            # which screen - should it be winfo_screen instead ??
            XDefaultScreen = _x11lib.XDefaultScreen
            XDefaultScreen.argtypes = [POINTER(Display)]
            XDefaultScreen.restype = c_int
            screen = XDefaultScreen(self.__window)
            print("Screen is ", screen)
            # Look at framebuffer configs
            ncfg = GL.GLint(0)
            cfgs = GLX.glXChooseFBConfig(
                self.__window,
                screen,
                (GL.GLint * len(fbatt))(* fbatt),
                ncfg,
            )
            print("Number of FBconfigs", ncfg.value)
            #
            # Try to match to the current window
            # ... might also be possible to set this for the frame
            # ... but for now we just take what Tk gave us
            ideal = int(self.winfo_visualid(), 16)  # convert from hex
            best = -1
            for i in range(ncfg.value):
                vis = GLX.glXGetVisualFromFBConfig(self.__window,  cfgs[i])
                if ideal == vis.contents.visualid:
                    best = i
                    print("Got a matching visual: index %d %d xid %s" % (
                        best, vis.contents.visualid, hex(ideal)))
            if best < 0:
                print("oh dear - visual does not match")
                # Take the first in the list (should be another I guess)
                best = 0
            # Here we insist on RGBA - but didn't check earlier
            self.__context = GLX.glXCreateNewContext(
                self.__window,
                cfgs[best],
                GLX.GLX_RGBA_TYPE,
                None,  # share list
                GL.GL_TRUE,  # direct
            )
            print("Is Direct?: ", GLX.glXIsDirect(self.__window, self.__context))
            # Not creating another window ... some tutorials do
            # print("wid: ", self._wid)
            # self._wid = GLX.glXCreateWindow(self.__window, cfgs[best], self._wid, None)
            # print("wid: ", self._wid)
            GLX.glXMakeContextCurrent(self.__window, self._wid, self._wid, self.__context)
            print("Done making a first context")
            extensions = GLX.glXQueryExtensionsString(self.__window, screen)
            # Here we quit - getting a modern context needs further work below
            return
            if "GLX_ARB_create_context" in extensions:
                # We can try to upgrade it ??
                print("Trying to upgrade context")
                s = "glXCreateContextAttribsARB"
                p = GLX.glXGetProcAddress(c_char_p(s))

                print(p)
                if not p:
                    p = GLX.glXGetProcAddressARB((GL.GLubyte * len(s)).from_buffer_copy(s))
                print(p)
                if p:
                    print(" p is true")
                p.restype = GLX.GLXContext
                p.argtypes = [
                    POINTER(Display),
                    GLX.GLXFBConfig,
                    GLX.GLXContext,
                    c_bool,
                    POINTER(c_int),
                ]
                arb_attrs = fbatt[:-1] + []

                #    GLX.GLX_CONTEXT_MAJOR_VERSION_ARB , 3
                #    GLX.GLX_CONTEXT_MINOR_VERSION_ARB , 1,
                #    0 ]
                #
                #    GLX.GLX_CONTEXT_FLAGS_ARB
                #    GLX.GLX_CONTEXT_PROFILE_MASK_ARB
                # ]
#                    import pdb
#                    pdb.set_trace()
                self.__context = p(
                    self.__window, cfgs[best], None, GL.GL_TRUE,
                    (GL.GLint * len(arb_attrs))(* arb_attrs),
                )

    def tkMakeCurrent(self):
        if self.winfo_ismapped():
            GLX.glXMakeCurrent(self.__window, self._wid, self.__context)

    def tkSwapBuffers(self):
        if self.winfo_ismapped():
            GLX.glXSwapBuffers(self.__window, self._wid)
