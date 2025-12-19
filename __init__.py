bl_info = {
    "name": "Tools:Q Camera Extends",
    "author": "Studio Q",
    "version": (1, 0, 0),
    "blender": (4, 2, 0),
    "description": "Extension features for camera",
    "location": "",
    "doc_url": "",
    "tracker_url": "",
    "warning": "",
    "support": "COMMUNITY",
    "category": "Animation"
}

from . import camera_extends

def register():
    camera_extends.register( )

def unregister():
    camera_extends.unregister( )
