import bpy

from . import overScan
from . import tiltshift
from . import draw_ui

# -----------------------------------------------------------------------------

# 登録クラス名のリスト
classes = (
    tiltshift.QANIM_OT_tiltshift_vertical_auto_detection,
    tiltshift.QANIM_OT_tiltshift_horizontal_auto_detection,

    overScan.QANIM_OT_overscan_reset,
    overScan.QANIM_OT_overscan_run,

    draw_ui.QANIM_PT_overscan,
)

def register():
    ''' クラス登録
    '''
    for i in classes:
        bpy.utils.register_class(i)
        
    overScan._initialized()
    tiltshift._initialized()
    draw_ui._initialized()

def unregister():
    ''' クラス登録解除
    '''
    for i in classes:
        bpy.utils.unregister_class(i)

    overScan._deinitialized( )
    tiltshift._deinitialized( )
    draw_ui._deinitialized()
