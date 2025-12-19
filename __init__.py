bl_info = {
    "name": "Tools:Q Camera Extends",
    "author": "Studio Q",
    "version": (1, 0, 0),
    "blender": (4, 3, 0),
    "description": "Extension features for camera",
    "location": "",
    "doc_url": "",
    "tracker_url": "",
    "warning": "",
    "support": "COMMUNITY",
    "category": "Animation"
}

if "bpy" in locals( ):
    import imp
    imp.reload( camera_extends )
else:
    from . import camera_extends

import bpy


def register():
    camera_extends.register( )

def unregister():
    camera_extends.unregister( )
