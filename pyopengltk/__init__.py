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
import sys

# Platform specific frames
if sys.platform.startswith('linux'):
    from pyopengltk.linux import OpenGLFrame

if sys.platform.startswith('win32'):
    from pyopengltk.win32 import OpenGLFrame

# if sys.platform.startswith('darwin'):
#     from pyopengltk.darwin import OpenGLFrame

# opengl
from pyopengltk.opengl import RawOpengl
from pyopengltk.opengl import Opengl
from pyopengltk.opengl import glTranslateScene
from pyopengltk.opengl import glRotateScene
from pyopengltk.opengl import v3distsq
