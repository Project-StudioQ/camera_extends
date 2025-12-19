import bpy
import math
import mathutils

# -----------------------------------------------------------------------------

DEBUG_MODE = False

# -----------------------------------------------------------------------------

class QANIM_OT_camera_extends_tilt_shift_vertical_auto_detection(bpy.types.Operator):
    bl_label = "Tilt Shift Vertical Auto Detection"
    bl_idname = "qanim.camera_extends_tilt_shift_v_auto_detection"
    bl_description = "Tilt Shift Vertical Auto Detection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        camera_object = context.active_object
        camera = camera_object.data
        props = camera.q_camera_extends.tilt_shift

        camera_object.rotation_mode = 'QUATERNION'
        camera_object.delta_rotation_quaternion = mathutils.Quaternion()
        bpy.context.view_layer.update( )
        matrix = camera_object.matrix_world.to_3x3( )
        props.vertical = math.asin( matrix[2].yz.normalized( ).cross( mathutils.Vector(( -1.0, 0.0 )) ) )

        return {'FINISHED'}

class QANIM_OT_camera_extends_tilt_shift_horizontal_auto_detection(bpy.types.Operator):
    bl_label = "Tilt Shift Horizontal Auto Detection"
    bl_idname = "qanim.camera_extends_tilt_shift_h_auto_detection"
    bl_description = "Tilt Shift Horizontal Auto Detection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        camera_object = context.active_object
        camera = camera_object.data
        props = camera.q_camera_extends.tilt_shift

        camera_object.rotation_mode = 'QUATERNION'
        camera_object.delta_rotation_quaternion = mathutils.Quaternion()
        bpy.context.view_layer.update( )
        matrix = camera_object.matrix_world.to_3x3( )
        props.horizontal = math.asin( matrix[0].xz.normalized( ).cross( mathutils.Vector(( 1.0, 0.0 )) ) )

        return {'FINISHED'}

# -----------------------------------------------------------------------------

def update( self, context ):
    camera_object = context.active_object
    camera = camera_object.data
    props = camera.q_camera_extends.tilt_shift

    if props.temp_lens == 0.0 :
        props.temp_lens = camera.lens
        props.temp_shift_x = camera.shift_x
        props.temp_shift_y = camera.shift_y
    else:
        camera.lens = props.temp_lens
        camera.shift_x = props.temp_shift_x
        camera.shift_y = props.temp_shift_y

    tilt_shift_vertical_radian = props.vertical
    tilt_shift_horizontal_radian = props.horizontal

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
    camera.shift_y = props.temp_shift_y + math.sin( - tilt_shift_vertical_radian ) * d + props.temp_shift_x * math.sin( tilt_shift_vertical_radian ) * 0.1
    camera.shift_x = props.temp_shift_x + math.sin( tilt_shift_horizontal_radian ) * d + props.temp_shift_y * math.sin( tilt_shift_horizontal_radian ) * 0.1
    # 焦点距離調整
    d = math.cos( - tilt_shift_vertical_radian - tilt_shift_horizontal_radian )
    camera.lens = props.temp_lens * d

    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
