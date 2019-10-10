# pyopengltk

Tkinter - OpenGL Frame using ctypes

* [pyopengltk on Github](https://github.com/jonwright/pyopengltk)
* [pyopengltk on PyPI](https://pypi.org/project/pyopengltk/)

An opengl frame for pyopengl-tkinter based on ctypes (no togl compilation)

Collected together by Jon Wright, Jan 2018.

## Basic Example

This example creates a window containing an `OpenGLFrame`
filling the entire window. We configure it to animate
(constantly redraw) clearing the screen using a green color.
A simple framerate counter is included.
The context information is printed to the terminal.

```python
import time
import tkinter
from OpenGL import GL
from pyopengltk import OpenGLFrame

class AppOgl(OpenGLFrame):

    def initgl(self):
        """Initalize gl states when the frame is created"""
        GL.glViewport(0, 0, self.width, self.height)
        GL.glClearColor(0.0, 1.0, 0.0, 0.0)    
        self.start = time.time()
        self.nframes = 0

    def redraw(self):
        """Render a single frame"""
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        tm = time.time() - self.start
        self.nframes += 1
        print("fps",self.nframes / tm, end="\r" )


if __name__ == '__main__':
    root = tkinter.Tk()
    app = AppOgl(root, width=320, height=200)
    app.pack(fill=tkinter.BOTH, expand=tkinter.YES)
    app.animate = 1
    app.after(100, app.printContext)
    app.mainloop()
```

The repository on Github also contains more examples.

## Install

From PyPI:

```
pip install pyopengltk
```

From source:

```
git clone https://github.com/jonwright/pyopengltk
cd pyopengltk
pip install .
```

## Attributions

Based on the work of others.

### C + Tcl/Tk example:

* Project URL : http://github.com/codeplea/opengl-tcltk/ (zlib license)
* Article at : https://codeplea.com/opengl-with-c-and-tcl-tk

### Python + Tkinter (no pyopengl) example:

* Project URL : http://github.com/arcanosam/pytkogl/ (The Code Project Open License)
* Article at: http://www.codeproject.com/Articles/1073475/OpenGL-in-Python-with-TKinter

### pyopengl

* Large regions of code copied from `pyopengl/Tk/__init__.py`.
