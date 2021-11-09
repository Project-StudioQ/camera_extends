import bpy
import math
import mathutils

# -----------------------------------------------------------------------------

DEBUG_MODE = False

# -----------------------------------------------------------------------------

def _update( self, context ):
    camera_object = context.active_object
    camera = camera_object.data

    if not hasattr(camera, "temp_lens") :
        camera.temp_lens = camera.lens
        camera.temp_shift_x = camera.shift_x
        camera.temp_shift_y = camera.shift_y
    elif camera.temp_lens == 0.0 :
        camera.temp_lens = camera.lens
        camera.temp_shift_x = camera.shift_x
        camera.temp_shift_y = camera.shift_y
    else:
        camera.lens = camera.temp_lens
        camera.shift_x = camera.temp_shift_x
        camera.shift_y = camera.temp_shift_y

    tilt_shift_vertical_radian = math.radians( camera.tilt_shift_vertical )
    tilt_shift_horizontal_radian = math.radians( camera.tilt_shift_horizontal )

    # カメラ回転をQuaternionに変更する
    camera_object.rotation_mode = 'QUATERNION'
    camera_object.delta_rotation_quaternion = mathutils.Quaternion()
    # 再計算してview_frustrumに反映させる
    bpy.context.view_layer.update( )

    # rotation_quaternionで回転している状態から、さらに回転させるように計算
    # Blenderのmatrix_localは逆行列状態で返ってくる
    matrix = camera_object.matrix_local.inverted( )
    vertical_q = mathutils.Quaternion( matrix[0].xyz.normalized(), tilt_shift_vertical_radian )
    horizontal_q = mathutils.Quaternion( matrix[1].xyz.normalized(), tilt_shift_horizontal_radian )
    camera_object.delta_rotation_quaternion = vertical_q @ horizontal_q

    if DEBUG_MODE:
        print( matrix[0].xyz )
        print( camera_object.delta_rotation_quaternion.to_matrix( ) )

    # 再計算してview_frustrumに反映させる
    bpy.context.view_layer.update( )
    # Shiftの計算
    center = mathutils.Vector((0,0,0))
    for t in camera.view_frame( scene=bpy.context.scene ):
        center += t
    center /= 4.0
    d = center.length
    camera.shift_y = camera.temp_shift_y + math.sin( - tilt_shift_vertical_radian ) * d + camera.temp_shift_x * math.sin( tilt_shift_vertical_radian ) * 0.1
    camera.shift_x = camera.temp_shift_x + math.sin( tilt_shift_horizontal_radian ) * d + camera.temp_shift_y * math.sin( tilt_shift_horizontal_radian ) * 0.1
    # 焦点距離調整
    d = math.cos( - tilt_shift_vertical_radian - tilt_shift_horizontal_radian )
    camera.lens = camera.temp_lens * d

    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

# -----------------------------------------------------------------------------

class QANIM_OT_tiltshift_vertical_auto_detection(bpy.types.Operator):
    bl_label = "Tilt Shift Vertical Auto Detection"
    bl_idname = "qanim.ot_tiltshift_v_auto_detection"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}   # undo効くようにする設定

    def execute(self, context):
        camera_object = context.active_object
        camera = camera_object.data

        camera_object.rotation_mode = 'QUATERNION'
        camera_object.delta_rotation_quaternion = mathutils.Quaternion()
        bpy.context.view_layer.update( )
        matrix = camera_object.matrix_world.to_3x3( )
        camera.tilt_shift_vertical = math.degrees( math.asin( matrix[2].yz.normalized( ).cross( mathutils.Vector(( -1.0, 0.0 )) ) ) )

        #_update( None, context )
        return {'FINISHED'}

class QANIM_OT_tiltshift_horizontal_auto_detection(bpy.types.Operator):
    bl_label = "Tilt Shift Horizontal Auto Detection"
    bl_idname = "qanim.ot_tiltshift_h_auto_detection"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}   # undo効くようにする設定

    def execute(self, context):
        camera_object = context.active_object
        camera = camera_object.data

        camera_object.rotation_mode = 'QUATERNION'
        camera_object.delta_rotation_quaternion = mathutils.Quaternion()
        bpy.context.view_layer.update( )
        matrix = camera_object.matrix_world.to_3x3( )
        camera.tilt_shift_horizontal = math.degrees( math.asin( matrix[0].xz.normalized( ).cross( mathutils.Vector(( 1.0, 0.0 )) ) ) )

        #_update( None, context )
        return {'FINISHED'}

# -----------------------------------------------------------------------------

def _initialized( ):
    """
        初期化
    """
    camera_object = bpy.types.Object

    camera = bpy.types.Camera
    camera.tilt_shift_vertical = bpy.props.FloatProperty( precision=2, default=0.0, step=1.0, min=-90.0, max=90.0, update=_update )
    camera.tilt_shift_horizontal = bpy.props.FloatProperty( precision=2, default=0.0, step=1.0, min=-90.0, max=90.0, update=_update )

    camera.temp_lens = bpy.props.FloatProperty( )
    camera.temp_shift_x = bpy.props.FloatProperty( )
    camera.temp_shift_y = bpy.props.FloatProperty( )

def _deinitialized( ):
    """
        後始末
    """
    camera = bpy.types.Camera
    del camera.tilt_shift_vertical
    del camera.tilt_shift_horizontal

    del camera.temp_lens
    del camera.temp_shift_x
    del camera.temp_shift_y
