

# Poke around to see about matching visuals...
# From https://github.com/garrybodsworth/pyxlib-ctypes

from ctypes import *
from ctypes import util
libX11 = CDLL( util.find_library( "X11" ))

XPointer = c_char_p
XID = c_ulong
VisualID = c_ulong
Window = XID
Bool = c_int
Colormap = XID
Status = c_int

class _XExtData(Structure):
    pass
_XExtData._fields_ = [
	('number', c_int),
	('next', POINTER(_XExtData)),
	('free_private', c_void_p),
	('private_data', XPointer),
]
XExtData = _XExtData

GContext = XID
class _XGC(Structure):
	_fields_ = [
		('ext_data', POINTER(XExtData)),
		('gid', GContext),
	]
GC = POINTER(_XGC)

class Visual(Structure):
	_fields_ = [
		('ext_data', POINTER(XExtData)),
		('visualid', VisualID),
		('c_class', c_int),
		('red_mask', c_ulong),
		('green_mask', c_ulong),
		('blue_mask', c_ulong),
		('bits_per_rgb', c_int),
		('map_entries', c_int),
	]

class Depth(Structure):
	_fields_ = [
		('depth', c_int),
		('nvisuals', c_int),
		('visuals', POINTER(Visual)),
	]
        
        
class ScreenFormat(Structure):
	_fields_ = [
		('ext_data', POINTER(XExtData)),
		('depth', c_int),
		('bits_per_pixel', c_int),
		('scanline_pad', c_int),
	]
        
class _XrmHashBucketRec(Structure): pass

class _XPrivate(Structure): pass

class _XDisplay(Structure): pass

class Screen(Structure):
	_fields_ = [
		('ext_data', POINTER(XExtData)),
		('display', POINTER(_XDisplay)),
		('root', Window),
		('width', c_int),
		('height', c_int),
		('mwidth', c_int),
		('mheight', c_int),
		('ndepths', c_int),
		('depths', POINTER(Depth)),
		('root_depth', c_int),
		('root_visual', POINTER(Visual)),
		('default_gc', GC),
		('cmap', Colormap),
		('white_pixel', c_ulong),
		('black_pixel', c_ulong),
		('max_maps', c_int),
		('min_maps', c_int),
		('backing_store', c_int),
		('save_unders', Bool),
		('root_input_mask', c_long),
	]
        class _XDisplay(Structure): pass

_XDisplay._fields_ = [
	('ext_data', POINTER(XExtData)),
	('private1', POINTER(_XPrivate)),
	('fd', c_int),
	('private2', c_int),
	('proto_major_version', c_int),
	('proto_minor_version', c_int),
	('vendor', c_char_p),
	('private3', XID),
	('private4', XID),
	('private5', XID),
	('private6', c_int),
	('resource_alloc', c_void_p),
	('byte_order', c_int),
	('bitmap_unit', c_int),
	('bitmap_pad', c_int),
	('bitmap_bit_order', c_int),
	('nformats', c_int),
	('pixmap_format', POINTER(ScreenFormat)),
	('private8', c_int),
	('release', c_int),
	('private9', POINTER(_XPrivate)),
	('private10', POINTER(_XPrivate)),
	('qlen', c_int),
	('last_request_read', c_ulong),
	('request', c_ulong),
	('private11', XPointer),
	('private12', XPointer),
	('private13', XPointer),
	('private14', XPointer),
	('max_request_size', c_uint),
	('db', POINTER(_XrmHashBucketRec)),
	('private15', c_void_p),
	('display_name', c_char_p),
	('default_screen', c_int),
	('nscreens', c_int),
	('screens', POINTER(Screen)),
	('motion_buffer', c_ulong),
	('private16', c_ulong),
	('min_keycode', c_int),
	('max_keycode', c_int),
	('private17', XPointer),
	('private18', XPointer),
	('private19', c_int),
	('xdefaults', c_char_p),
]
Display = _XDisplay


class XWindowAttributes(Structure):
	_fields_ = [
		('x', c_int),
		('y', c_int),
		('width', c_int),
		('height', c_int),
		('border_width', c_int),
		('depth', c_int),
		('visual', POINTER(Visual)),
		('root', Window),
		('c_class', c_int),
		('bit_gravity', c_int),
		('win_gravity', c_int),
		('backing_store', c_int),
		('backing_planes', c_ulong),
		('backing_pixel', c_ulong),
		('save_under', Bool),
		('colormap', Colormap),
		('map_installed', Bool),
		('map_state', c_int),
		('all_event_masks', c_long),
		('your_event_mask', c_long),
		('do_not_propagate_mask', c_long),
		('override_redirect', Bool),
		('screen', POINTER(Screen)),
	]

XGetWindowAttributes = libX11.XGetWindowAttributes
XGetWindowAttributes.restype = Status
XGetWindowAttributes.argtypes = [POINTER(Display), Window, POINTER(XWindowAttributes)]

XOpenDisplay = libX11.XOpenDisplay
XOpenDisplay.restype = POINTER(Display)
XOpenDisplay.argtypes = [c_char_p]

def getXWA( wid ):
    dpy = XOpenDisplay("")
    attrs = XWindowAttributes()
    status = XGetWindowAttributes( dpy, Window(wid), pointer(attrs) )
    return attrs

__all__ = [ getXWA ]

if __name__ == "__main__":
    import Tkinter
    root = Tkinter.Tk()
    frm = Tkinter.Frame(root, width=200, height=200, bg="" )
    frm.pack()

    def testframe():
        dpy = XOpenDisplay("")
        attrs = XWindowAttributes()
        print dpy
        print attrs
        status = XGetWindowAttributes( dpy, Window(frm.winfo_id()), pointer(attrs) )
        print status
        print attrs.visual.contents.bits_per_rgb
        print attrs.visual.contents.visualid
        
    frm.after(100, testframe)
    root.mainloop()

