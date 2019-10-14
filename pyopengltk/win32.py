"""
Windows implementation of the opengl frame
"""
from ctypes import WinDLL, c_void_p
from ctypes.wintypes import HDC
from OpenGL.WGL import PIXELFORMATDESCRIPTOR, ChoosePixelFormat, \
    SetPixelFormat, SwapBuffers, wglCreateContext, wglMakeCurrent

from pyopengltk.base import BaseOpenGLFrame

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
class OpenGLFrame(BaseOpenGLFrame):

    def tkCreateContext(self):
        self.__window = GetDC(self.winfo_id())
        pixelformat = ChoosePixelFormat(self.__window, pfd)
        SetPixelFormat(self.__window, pixelformat, pfd)
        self.__context = wglCreateContext(self.__window)
        wglMakeCurrent(self.__window, self.__context)

    def tkMakeCurrent(self):
        if self.winfo_ismapped():
            wglMakeCurrent(self.__window, self.__context)

    def tkSwapBuffers(self):
        if self.winfo_ismapped():
            SwapBuffers(self.__window)
