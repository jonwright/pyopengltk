from __future__ import print_function
import sys
from OpenGL import GL

if sys.version_info[0] < 3:
    import Tkinter as tk
    import Dialog as dialog
else:
    import tkinter as tk
    from tkinter import dialog as dialog


class BaseOpenGLFrame(tk.Frame):
    """ Common code for windows/x11 """
    def __init__(self, *args, **kw):
        # Set background to empty string to avoid
        # flickering overdraw by Tk
        kw['bg'] = ""
        tk.Frame.__init__(self, *args, **kw)
        self.bind('<Map>', self.tkMap)
        self.bind('<Configure>', self.tkResize)
        self.bind('<Expose>', self.tkExpose)
        self.animate = 0
        self.cb = None

    def tkMap(self, evt):
        """" Called when frame goes onto the screen """
        self._wid = self.winfo_id()
        self.tkCreateContext()
        self.initgl()

    def printContext(self, extns=False):
        """ For debugging """
        exts = GL.glGetString(GL.GL_EXTENSIONS)
        if extns:
            print("Extension list:")
            for e in sorted(exts.split()):
                print("\t", e)
        else:
            print("Number of extensions:", len(exts.split()))

        print("GL_VENDOR  :", GL.glGetString(GL.GL_VENDOR))
        print("GL_RENDERER:", GL.glGetString(GL.GL_RENDERER))
        print("GL_VERSION :", GL.glGetString(GL.GL_VERSION))
        try:
            print(" GL_MAJOR_VERSION:", GL.glGetIntegerv(GL.GL_MAJOR_VERSION))
            print(" GL_MINOR_VERSION:", GL.glGetIntegerv(GL.GL_MINOR_VERSION))
            print(" GL_SHADING_LANGUAGE_VERSION :",
                  GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION))
            msk = GL.glGetIntegerv(GL.GL_CONTEXT_PROFILE_MASK)
            print(" GL_CONTEXT_CORE_PROFILE_BIT :",
                  bool(msk & GL.GL_CONTEXT_CORE_PROFILE_BIT))
            print(" GL_CONTEXT_COMPATIBILITY_PROFILE_BIT :",
                  bool(msk & GL.GL_CONTEXT_COMPATIBILITY_PROFILE_BIT))
        except:
            print("Old context errors arose")
            # raise

    def tkCreateContext(self):
        # Platform dependent part
        raise NotImplementedError

    def tkMakeCurrent(self):
        # Platform dependent part
        raise NotImplementedError

    def tkSwapBuffers(self):
        # Platform dependent part
        raise NotImplementedError

    def tkExpose(self, evt):
        if self.cb:
            self.after_cancel(self.cb)
        self._display()

    def tkResize(self, evt):
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
            GL.glViewport(0, 0, self.width, self.height)
            self.initgl()

    def _display(self):
        self.update_idletasks()
        self.tkMakeCurrent()
        self.redraw()
        self.tkSwapBuffers()
        if self.animate > 0:
            self.cb = self.after(self.animate, self._display)

    def initgl(self):
        # For the user code
        raise NotImplementedError

    def redraw(self):
        # For the user code
        raise NotImplementedError
