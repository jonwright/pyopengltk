"""
OS X implementation of the opengl frame

Resources:
https://github.com/apitrace/apitrace/blob/master/specs/cglapi.py
http://mirror.informatimago.com/next/developer.apple.com/documentation/GraphicsImaging/Conceptual/OpenGL/chap5/chapter_5_section_41.html#//apple_ref/doc/uid/TP30000136/BDJHHIDE
https://stackoverflow.com/questions/5523777/opengl-on-mac-operation

https://stackoverflow.com/questions/11402472/is-there-a-way-to-iterate-over-all-open-windows-in-mac-os-x
https://chromium.googlesource.com/external/p3/regal/+/b79468111af42248fdb0e5684820e39bba2bef7a/src/apitrace/specs/cglapi.py
"""
from __future__ import print_function

import sys, time
from ctypes import c_int, c_char_p, c_void_p, cdll, POINTER, util, \
    pointer, CFUNCTYPE, c_bool, byref

from pyopengltk.base import BaseOpenGLFrame

CGL_RESULT = {
    10000: 'Invalid pixel format attribute',
    10001: 'Invalid renderer property',
    10002: 'Invalid pixel format object',
    10003: 'Invalid renderer information object',
    10004: 'Invalid context object',
    10005: 'Invalid drawable',
    10006: 'Invalid display',
    10007: 'Invalid context state',
    10008: 'Invalid numerical value',
    10009: 'Invalid share context',
    10010: 'Invalid enumerant',
    10011: 'Invalid off-screen drawable',
    10012: 'Invalid full-screen drawable',
    10013: 'Invalid window',
    10014: 'Invalid memory address',
    10015: 'Invalid code module',
    10016: 'Invalid memory allocation',
    10017: 'Invalid Core Graphics connection',
}

class CGLPixelFormatAttribute(object):
    """
    The following constants are used by CGLChoosePixelFormat and CGLDescribePixelFormat.
    The existence of a Boolean attribute in the attribute array of CGLChoosePixelFormat
    implies a true value. Integer attribute constants must be followed by a value.
    """
    kCGLPFAAllRenderers       =   1
    kCGLPFADoubleBuffer       =   5
    kCGLPFAStereo             =   6
    kCGLPFAAuxBuffers         =   7
    kCGLPFAColorSize          =   8
    kCGLPFAAlphaSize          =  11
    kCGLPFADepthSize          =  12
    kCGLPFAStencilSize        =  13
    kCGLPFAAccumSize          =  14
    kCGLPFAMinimumPolicy      =  51
    kCGLPFAMaximumPolicy      =  52
    kCGLPFAOffScreen          =  53
    kCGLPFAFullScreen         =  54
    kCGLPFARendererID         =  70
    kCGLPFASingleRenderer     =  71
    kCGLPFANoRecovery         =  72
    kCGLPFAAccelerated        =  73
    kCGLPFAClosestPolicy      =  74
    kCGLPFARobust             =  75
    kCGLPFABackingStore       =  76
    kCGLPFAMPSafe             =  78
    kCGLPFAWindow             =  80
    kCGLPFAMultiScreen        =  81
    kCGLPFACompliant          =  83
    kCGLPFADisplayMask        =  84
    kCGLPFAOpenGLProfile      =  99
    kCGLPFAVirtualScreenCount = 128

kCGLOGLPVersion_Legacy   = 0x1000   # choose a renderer compatible with GL1.0
kCGLOGLPVersion_3_2_Core = 0x3200  # choose a renderer capable of GL3.2 or later
kCGLOGLPVersion_GL3_Core = 0x3200  # choose a renderer capable of GL3.2 or later
kCGLOGLPVersion_GL4_Core = 0x410   # choose a renderer capable of GL4.1 or later


_gllib = cdll.LoadLibrary(util.find_library("OpenGL"))
CGLGetCurrentContext = _gllib.CGLGetCurrentContext  # returns CGLContextObj
# CGLChoosePixelFormat (attribs, &pixelFormat, &numPixelFormats);
CGLChoosePixelFormat = _gllib.CGLChoosePixelFormat
# CGLCreateContext(pixelFormat, NULL, &cglContext1);
CGLCreateContext = _gllib.CGLCreateContext
CGLSetCurrentContext = _gllib.CGLSetCurrentContext
CGLSetSurface = _gllib.CGLSetSurface
CGSMainConnectionID = _gllib.CGSMainConnectionID


class OpenGLFrame(BaseOpenGLFrame):

    def tkCreateContext(self):
        print('winfo_id', self.winfo_id())
        try:
            attribs = c_int * 9
            pfo = attribs(
                CGLPixelFormatAttribute.kCGLPFAOpenGLProfile, kCGLOGLPVersion_Legacy,
                CGLPixelFormatAttribute.kCGLPFAWindow, 1,
                CGLPixelFormatAttribute.kCGLPFAColorSize, 24,
                CGLPixelFormatAttribute.kCGLPFADepthSize, 16,
                # CGLPixelFormatAttribute.kCGLPFAAccelerated,
                # CGLPixelFormatAttribute.kCGLPFAFullScreen,
                # CGLPixelFormatAttribute.kCGLPFADoubleBuffer,
                0,
            )
            pixel_format_obj = c_void_p()
            num_pixel_formats = c_int(0)
            CGLChoosePixelFormat(pfo, byref(pixel_format_obj), byref(num_pixel_formats))
            if num_pixel_formats.value == 0:
                raise ValueError("No pixel formats detected")

            print('num_pixel_formats', num_pixel_formats.value)
            print('pixel_format_obj', pixel_format_obj)

            self.__context = c_void_p()
            result = CGLCreateContext(pixel_format_obj, None, byref(self.__context))
            print('result', type(result), result)
            print('contect', type(self.__context), self.__context.value)
            err = CGL_RESULT.get(result)
            if err:
                raise ValueError('Error while creating context: %s' % err)

            test = CGSMainConnectionID()
            print("CGSMainConnectionID", test)
            # # Somehow we need to find the window and surface_id
            # CGSWindow = c_int(self.winfo_id())
            # CGLSetSurface(cgl_context, connection_id, window, surface_id)

            print('context', type(self.__context), self.__context)
            CGLSetCurrentContext(self.__context)
        except Exception as ex:
            print(ex)
            exit(-1)

    def tkMakeCurrent(self):
        if self.winfo_ismapped():
            CGLSetCurrentContext(self.__context)

    def tkSwapBuffers(self):
        pass
