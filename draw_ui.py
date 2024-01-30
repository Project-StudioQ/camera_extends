import bpy
import math
import mathutils
import bgl
import gpu
from gpu_extras.batch import batch_for_shader

from . import overScan
from . import tiltshift

# -----------------------------------------------------------------------------

TILT_SHIFT_CAMERA_LINE_COLOR = (0,1,0,1)
shader = None
try:
    shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
except:
    pass

# -----------------------------------------------------------------------------

class QANIM_PT_overscan(bpy.types.Panel):
    bl_label = "Camera Extends"
    bl_idname = "QANIM_PT_overscan"
    # bl_space_type = 'PROPERTIES'
    # bl_region_type = 'WINDOW'
    # bl_context = "data"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Q_ANIM"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        ''' 特定のオブジェクトタイプでのみUIを表示
        '''
        return (context.active_object) and (context.object) and (context.object.type == 'CAMERA')
        
    def draw(self, context):
        ''' UI設定
        '''

        scene = context.active_object.data

        layout = self.layout

        row = layout.row()

        # オーバースキャンの基点ボタン表示
        pivot_box = row.box()

        pivot_box_row = pivot_box.row()
        pivot_box_row.label(text='pivot:')
        
        pivot_box_row.column(align=True)
        pivot_box_row.grid_flow(columns=3).prop(scene, 'pivot_prop_enum', expand=True)

        # オーバースキャン比率か、オーバースキャン後の解像度のいずれかを表示
        input_box = row.box()
        input_box.alignment = 'CENTER'
        input_box_row = input_box.row()
        input_box_row.prop(scene, "pixOrPer_prop_enum", expand=True)

        # 解像度/比率の入力
        input_box_row = input_box.row()
        input_box_row_column = input_box_row.column(align=True)
        
        if scene.pixOrPer_prop_enum == 'percent':
            input_box_row_column.prop(scene, "magnification_prop_FloatX", text="scaleRateX")
            input_box_row_column.prop(scene, "magnification_prop_FloatY", text="scaleRateY")
            input_box_row.prop(scene, "temp_ratio_interlocked", icon='LOCKED' if scene.temp_ratio_interlocked else 'UNLOCKED', icon_only=True)

        elif scene.pixOrPer_prop_enum == 'pixcel':
            input_box_row_column.prop(scene, "magnification_prop_IntX", text="scalePixcelX")
            input_box_row_column.prop(scene, "magnification_prop_IntY", text="scalePixcelY")

        # オーバースキャン実行かリセットの表示
        layout.label(text="Overscan:")
        layout.prop( scene, "temp_camera_overscan_force_apply" )
        row = layout.row(align=False)
        row.operator(overScan.QANIM_OT_overscan_run.bl_idname, text="execute", icon='SHADING_BBOX')
        row.operator(overScan.QANIM_OT_overscan_reset.bl_idname, text="reset", icon='LOOP_BACK')

        # ティルトシフトのUI
        camera_object = context.active_object
        camera = camera_object.data

        layout.label(text="Tilt Shift:")
        row = layout.row( )
        input_box = row.box( )
        row = input_box.row( )
        row.prop( camera, "tilt_shift_vertical", text="Vertical" )
        row.operator( tiltshift.QANIM_OT_tiltshift_vertical_auto_detection.bl_idname, text="auto", icon="AUTO")

        row = input_box.row( )
        row.prop(camera, "tilt_shift_horizontal", text="Horizontal")
        row.operator( tiltshift.QANIM_OT_tiltshift_horizontal_auto_detection.bl_idname, text="auto", icon="AUTO")

        # オーバースキャンテスト表示
        layout.label(text="Overscan Test Display:")

        layout.prop( camera, 'temp_overscan_area_displaying_color', text='Area Color' )
        layout.prop( camera, 'overscan_area_transparent_percentage', text='Transparency' )
        layout.label( text= "Area Overscan Percentage:" )
        row = layout.row( )
        col = row.column( )
        col.prop( camera, 'temp_overscan_area_percentage_x', text='Area Percentage:X' )
        col = row.column( )
        col.prop( camera, 'temp_overscan_area_percentage_y', text='Area Percentage:Y' )

# -----------------------------------------------------------------------------

def _draw_line_for_tiltshift(  ):
    """
        オーバースキャン スキャンエリア描画
        ティルトシフト スクリーンガイド描画
    """

    if not bpy.context.space_data.overlay.show_overlays or not bpy.context.scene.temp_overscan_area_displaying:
        return

    global shader
    if shader is None:
        return

    currently_view_layer = bpy.context.view_layer

    bgl.glDisable( bgl.GL_DEPTH_TEST )
    bgl.glDisable( bgl.GL_CULL_FACE )
    bgl.glEnable( bgl.GL_BLEND )

    def is_hide_in_global( o ):
        if not o.visible_get( ) or o.hide_viewport:
            return True
        if o.parent is not None:
            return is_hide_in_global( o.parent )

        return False

    for o in bpy.data.objects:
        if o.type != "CAMERA":
            continue

        if is_hide_in_global( o ):
            continue

        _draw_line_on_camera( o, o.data )

def _draw_line_on_camera( camera_object, camera ):
    context = bpy.context

    tilt_shift_vertical_radian = math.radians( camera.tilt_shift_vertical )
    tilt_shift_horizontal_radian = math.radians( camera.tilt_shift_horizontal )

    # ガイドの位置を計算
    shift = mathutils.Vector((camera.shift_x, camera.shift_y, 0.0))
    if hasattr(camera, "temp_lens") and 0.0 < camera.temp_lens:
        shift.x = camera.temp_shift_x
        shift.y = camera.temp_shift_y
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
    lens = camera.temp_lens if hasattr( camera, "temp_lens" ) and 0.0 < camera.temp_lens else camera.lens
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
        sx = camera.temp_overscan_area_percentage_x / 100.0
        sy = camera.temp_overscan_area_percentage_y / 100.0
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
        c = camera.temp_overscan_area_displaying_color
        shader.uniform_float( "color", ( c.r, c.g, c.b, camera.overscan_area_transparent_percentage / 100.0 ) )
        batch = batch_for_shader( shader, 'TRIS', { "pos": coords } )
        batch.draw( shader )

# -----------------------------------------------------------------------------
_draw_line_for_tiltshift_handler = None

def _initialized( ):
    """
        初期化
    """

    bpy.types.Scene.temp_overscan_area_displaying = bpy.props.BoolProperty( name="Overscan Area Displaying", default= True )

    scene = bpy.types.Camera

    # オーバースキャンエリアパーセンテージ
    scene.temp_overscan_area_percentage_x = bpy.props.FloatProperty(
        name='X',
        description='Overscan Area Percentage X',
        subtype='PERCENTAGE',
        default=110.0,
        min=100.0,
        max=200.0,
    )
    scene.temp_overscan_area_percentage_y = bpy.props.FloatProperty(
        name='Y',
        description='Overscan Area Percentage Y',
        subtype='PERCENTAGE',
        default=110.0,
        min=100.0,
        max=200.0,
    )
    # オーバースキャンエリア表示色
    scene.temp_overscan_area_displaying_color = bpy.props.FloatVectorProperty(
        name='Overscan Area Displaying Color',
        description='Overscan Area Displaying Color',
        subtype='COLOR',
        default=(0.0,1.0,0.0),
    )
    # オーバースキャンエリア表示アルファ
    scene.overscan_area_transparent_percentage = bpy.props.FloatProperty(
        name='Overscan Area Transparent Percentage',
        description='Overscan Area Transparent Percentage',
        subtype='PERCENTAGE',
        default=40.0,
        min=0.0,
        max=100.0,
    )

    global _draw_line_for_tiltshift_handler
    _draw_line_for_tiltshift_handler = bpy.types.SpaceView3D.draw_handler_add( _draw_line_for_tiltshift, (), 'WINDOW', 'POST_VIEW' )

def _deinitialized( ):
    """
        後始末
    """
    global _draw_line_for_tiltshift_handler
    if _draw_line_for_tiltshift_handler is not None:
        bpy.types.SpaceView3D.draw_handler_remove( _draw_line_for_tiltshift_handler, 'WINDOW' )

    scene = bpy.types.Camera

    del scene.temp_overscan_area_percentage_x
    del scene.temp_overscan_area_percentage_y
    del scene.temp_overscan_area_displaying_color
    del scene.overscan_area_transparent_percentage
    del bpy.types.Scene.temp_overscan_area_displaying
