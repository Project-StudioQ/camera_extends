import bpy
import math
import mathutils
import gpu
from gpu_extras.batch import batch_for_shader

# -----------------------------------------------------------------------------

TILT_SHIFT_CAMERA_LINE_COLOR = (0,1,0,1)
shader = None
try:
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
except:
    pass

# -----------------------------------------------------------------------------

def draw_line_for_tilt_shift( ):
    """
        オーバースキャン スキャンエリア描画
        ティルトシフト スクリーンガイド描画
    """

    if not bpy.context.space_data.overlay.show_overlays or not bpy.context.scene.q_camera_extends.overscan_is_display:
        return

    global shader
    if shader is None:
        return

    gpu.state.depth_test_set('NONE')
    gpu.state.depth_mask_set( False )
    gpu.state.face_culling_set( 'NONE' )
    gpu.state.blend_set( 'ALPHA' )

    def is_hide_in_global( o ):
        if o is None:
            return True

        if not o.visible_get( ) or o.hide_viewport:
            return True
        if o.parent is not None:
            return is_hide_in_global( o.parent )

        return False

    cam_obj = bpy.context.scene.camera
    if not is_hide_in_global( cam_obj ):
        _draw_line_on_camera( cam_obj, cam_obj.data )

    #for o in bpy.data.objects:
    #    if o.type != "CAMERA":
    #        continue

    #    if is_hide_in_global( o ):
    #        continue

    #    _draw_line_on_camera( o, o.data )

def _draw_line_on_camera( camera_object, camera ):
    context = bpy.context
    props = camera.q_camera_extends

    tilt_shift_vertical_radian = math.radians( props.tilt_shift.vertical )
    tilt_shift_horizontal_radian = math.radians( props.tilt_shift.horizontal )

    # ガイドの位置を計算
    shift = mathutils.Vector((camera.shift_x, camera.shift_y, 0.0))
    if 0.0 < props.tilt_shift.temp_lens:
        shift.x = props.tilt_shift.temp_shift_x
        shift.y = props.tilt_shift.temp_shift_y

    if camera.type == 'ORTHO':
        # 平行
        rotate_matrix = mathutils.Matrix.Rotation( tilt_shift_vertical_radian, 4, mathutils.Vector((1,0,0)) )
        rotate_matrix @= mathutils.Matrix.Rotation( -tilt_shift_horizontal_radian, 4, mathutils.Vector((0,1,0)) )
    else:
        # 透視
        rotate_matrix = mathutils.Matrix.Rotation( tilt_shift_vertical_radian, 4, mathutils.Vector((1,0,0)) ) * camera.display_size
        rotate_matrix @= mathutils.Matrix.Rotation( -tilt_shift_horizontal_radian, 4, mathutils.Vector((0,1,0)) )

    camera_scale = max( camera_object.scale.x, camera_object.scale.y, camera_object.scale.z )

    # ガイド4点の計算と中心点の計算
    quad = [ t for t in camera.view_frame( scene=context.scene ) ]
    center = mathutils.Vector((0,0,0))
    for t in quad:
        center += t / 4.0

    # スクリーンまでの距離を計算
    half_sensor = 0.5 * ( camera.sensor_height if camera.sensor_fit == 'VERTICAL' else camera.sensor_width )
    lens = props.tilt_shift.temp_lens if 0.0 < props.tilt_shift.temp_lens else camera.lens
    drawsize = 0.5 / camera_scale
    if camera.type == 'ORTHO':
        # 平行
        depth = -camera.display_size
    else:
        # 透視
        depth = ( drawsize * lens / (-half_sensor) ) * camera.display_size
    depth *= camera_scale

    # ティルトシフト回転 -> カメラ自体の行列計算
    for i in range( len( quad ) ):
        quad[i] = camera_object.matrix_world @ quad[i]
    coords = [
        quad[0], quad[1],
        quad[1], quad[2],
        quad[2], quad[3],
        quad[3], quad[0],
    ]
    quad_center = ( quad[0] + quad[1] + quad[2] + quad[3] ) / 4.0

    with gpu.matrix.push_pop_projection( ):
        # カメラのnearよりも前で映らない？
        if -depth < camera.clip_start:
            if camera.type != 'ORTHO':
                # 透視変換行列のクリッピングをいじる
                proj_matr = gpu.matrix.get_projection_matrix( )
                temp_far = camera.clip_end
                temp_near = -depth / 2.0
                proj_matr[2][2] = - (temp_far + temp_near) / (temp_far - temp_near)
                proj_matr[2][3] = - (2 * temp_far * temp_near) / (temp_far - temp_near)
                gpu.matrix.load_projection_matrix( proj_matr )

        # ティルトシフトガイド描画
        shader.bind( )
        shader.uniform_float( "color", TILT_SHIFT_CAMERA_LINE_COLOR )
        batch = batch_for_shader( shader, 'LINES', { "pos": coords } )
        batch.draw( shader )

        # オーバースキャンエリア
        sx = props.overscan_area.percentage_x / 100.0
        sy = props.overscan_area.percentage_y / 100.0
        inner_quad = [
            quad_center - ( ( ( quad[3] - quad[0] ) * 0.5 ) / sx ) - ( ( ( quad[1] - quad[0] ) * 0.5 ) / sy ),
            quad_center - ( ( ( quad[3] - quad[0] ) * 0.5 ) / sx ) + ( ( ( quad[1] - quad[0] ) * 0.5 ) / sy ),
            quad_center + ( ( ( quad[3] - quad[0] ) * 0.5 ) / sx ) + ( ( ( quad[1] - quad[0] ) * 0.5 ) / sy ),
            quad_center + ( ( ( quad[3] - quad[0] ) * 0.5 ) / sx ) - ( ( ( quad[1] - quad[0] ) * 0.5 ) / sy ),
        ]
        coords = [
            # 上
            quad[0], quad[3], inner_quad[0],
            quad[3], inner_quad[0], inner_quad[3],
            # 下
            quad[1], quad[2], inner_quad[1],
            quad[2], inner_quad[1], inner_quad[2],
            # 右
            quad[0], quad[1], inner_quad[0],
            quad[1], inner_quad[0], inner_quad[1],
            # 左
            quad[2], quad[3], inner_quad[3],
            quad[2], inner_quad[2], inner_quad[3],
        ]
        c = props.overscan_area.displaying_color
        shader.uniform_float( "color", ( c.r, c.g, c.b, props.overscan_area.transparent_percentage / 100.0 ) )
        batch = batch_for_shader( shader, 'TRIS', { "pos": coords } )
        batch.draw( shader )
