import bpy

from . import show_overscan
from . import calc_overscan
from . import tilt_shift

# -----------------------------------------------------------------------------

class QANIM_Props_camera_extends_Camera_overscan(bpy.types.PropertyGroup):
    ratio_interlocked: bpy.props.BoolProperty(
        name='temp_ratio_interlocked',
        description='lock/unlock screen/pixel ratio',
        default=True,
    )

    magnification_scale_x: bpy.props.FloatProperty(
        precision= 1,
        default= 1.2,
        step= 10.0,
    )
    magnification_scale_y: bpy.props.FloatProperty(
        precision= 1,
        default= 1.2,
        step= 10.0,
    )

    magnification_resolution_x: bpy.props.IntProperty( default= 2304 )
    magnification_resolution_y: bpy.props.IntProperty( default= 1296 )

    overscan_type: bpy.props.EnumProperty(
        name= 'Pixel or Percentage',
        description= 'Select Method',
        items= (
            ('PERCENT', 'Percent', 'Percent'),
            ('PIXEL', 'Pixel', 'Pixel'),
        ),
        default= 'PERCENT',
    )

    pivot: bpy.props.EnumProperty(
        name= 'Pivot',
        description= 'Overscan Pivot',
        items= (
            ('UL', '', 'Upper Left'),
            ('UM', '', 'Upper Middle'),
            ('UR', '', 'Upper Right'),
            ('ML', '', 'Middle Left'),
            ('MM', '', 'Middle Middle'),
            ('MR', '', 'Middle Right'),
            ('DL', '', 'Lower Left'),
            ('DM', '', 'Lower Middle'),
            ('DR', '', 'Lower Right'),
        ),
        default= 'MM',
    )

    applied: bpy.props.BoolProperty( default= False )
    saved_resolution_x: bpy.props.IntProperty( )
    saved_resolution_y: bpy.props.IntProperty( )
    saved_sensor_width: bpy.props.FloatProperty( )
    saved_shift_x: bpy.props.FloatProperty( )
    saved_shift_y: bpy.props.FloatProperty( )

class QANIM_Props_camera_extends_Camera_overscan_area(bpy.types.PropertyGroup):
    percentage_x: bpy.props.FloatProperty(
        name='X',
        description='Overscan Area Percentage X',
        subtype='PERCENTAGE',
        default=110.0,
        min=100.0,
        max=200.0,
        options= {'HIDDEN'},
    )
    percentage_y: bpy.props.FloatProperty(
        name='Y',
        description='Overscan Area Percentage Y',
        subtype='PERCENTAGE',
        default=110.0,
        min=100.0,
        max=200.0,
        options= {'HIDDEN'},
    )
    displaying_color: bpy.props.FloatVectorProperty(
        name='Overscan Area Displaying Color',
        description='Overscan Area Displaying Color',
        subtype='COLOR',
        default=(0.0,1.0,0.0),
        options= {'HIDDEN'},
    )
    transparent_percentage: bpy.props.FloatProperty(
        name='Overscan Area Transparent Percentage',
        description='Overscan Area Transparent Percentage',
        subtype='PERCENTAGE',
        default=40.0,
        min=0.0,
        max=100.0,
        options= {'HIDDEN'},
    )

class QANIM_Props_camera_extends_Camera_tilt_shift(bpy.types.PropertyGroup):
    vertical: bpy.props.FloatProperty( precision=2, default=0.0, step=1.0, min=-90.0, max=90.0, update=tilt_shift.update, options= {'HIDDEN'} )
    horizontal: bpy.props.FloatProperty( precision=2, default=0.0, step=1.0, min=-90.0, max=90.0, update=tilt_shift.update, options= {'HIDDEN'} )

    temp_lens: bpy.props.FloatProperty( )
    temp_shift_x: bpy.props.FloatProperty( )
    temp_shift_y: bpy.props.FloatProperty( )

class QANIM_Props_camera_extends_Camera(bpy.types.PropertyGroup):
    overscan: bpy.props.PointerProperty( type= QANIM_Props_camera_extends_Camera_overscan )
    overscan_area: bpy.props.PointerProperty( type= QANIM_Props_camera_extends_Camera_overscan_area )
    tilt_shift: bpy.props.PointerProperty( type= QANIM_Props_camera_extends_Camera_tilt_shift )

class QANIM_Props_camera_extends_Scene(bpy.types.PropertyGroup):
    overscan_is_display: bpy.props.BoolProperty( name="Overscan Area Displaying", default= True, options= {'HIDDEN'} )

# -----------------------------------------------------------------------------

class QANIM_PT_camera_extends(bpy.types.Panel):
    bl_label = "Camera Extends"
    bl_idname = "QANIM_PT_overscan"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Q_ANIM"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll( self, context ):
        return context.active_object and context.object and context.object.type == 'CAMERA'

    def draw( self, context ):
        self._draw_overscan( )
        self._draw_tilt_shift( )
        self._draw_overscan_area( )

    def _draw_overscan( self ):
        layout = self.layout
        camera_object = bpy.context.active_object
        camera = camera_object.data
        props = camera.q_camera_extends.overscan

        row = layout.row( )

        # 基点
        box = row.box( )
        row = box.row( )
        row.label( text= 'Pivot:' )
        row.column( align= True )
        row.grid_flow( columns= 3 ).prop( props, "pivot", expand= True )

        # オーバースキャン比率 or オーバースキャン後の解像度
        box = row.box( )
        box.alignment = 'CENTER'
        row = box.row( )
        row.prop( props, "overscan_type", expand= True )

        # 解像度 / 比率入力
        row = box.row( )
        col = row.column( align= True )
        if props.overscan_type == 'PERCENT':
            col.prop( props, 'magnification_scale_x', text= "Scale Rate X" )
            if props.ratio_interlocked:
                col.prop( props, 'magnification_scale_x', text= "Scale Rate Y" )
            else:
                col.prop( props, 'magnification_scale_y', text= "Scale Rate Y" )
            row.prop( props, 'ratio_interlocked', icon='LOCKED' if props.ratio_interlocked else 'UNLOCKED', icon_only=True)
        elif props.overscan_type == 'PIXEL':
            col.prop( props, 'magnification_resolution_x', text= "Scale Pixel X" )
            col.prop( props, 'magnification_resolution_y', text= "Scale Pixel Y" )

        # オーバースキャン実行
        row = layout.row( )
        row.label( text= "Overscan:" )
        row = layout.row( align= False )
        row.operator( calc_overscan.QANIM_OT_camera_extends_overscan_execute.bl_idname, text= "Execute", icon= 'SHADING_BBOX' )
        row.operator( calc_overscan.QANIM_OT_camera_extends_overscan_reset.bl_idname, text= "Reset", icon= 'LOOP_BACK' )

    def _draw_tilt_shift( self ):
        layout = self.layout
        camera_object = bpy.context.active_object
        camera = camera_object.data
        props = camera.q_camera_extends.tilt_shift

        row = layout.row( )
        row.label( text= "Tilt Shift:" )

        row = layout.row( )
        box = row.box( )
        row = box.row( align= True )
        row.prop( props, "vertical", text= "Vertical" )
        row.operator( tilt_shift.QANIM_OT_camera_extends_tilt_shift_vertical_auto_detection.bl_idname, text= "", icon= "AUTO" )

        row = box.row( align= True )
        row.prop( props, "horizontal", text= "Horizontal" )
        row.operator( tilt_shift.QANIM_OT_camera_extends_tilt_shift_horizontal_auto_detection.bl_idname, text= "", icon= "AUTO" )

    def _draw_overscan_area( self ):
        layout = self.layout
        camera_object = bpy.context.active_object
        camera = camera_object.data
        props = camera.q_camera_extends.overscan_area

        row = layout.row( )
        row.label( text= "Overscan Test Display:" )
        row = layout.row( )
        row.prop( props, 'displaying_color', text= 'Area Color' )
        row = layout.row( )
        row.prop( props, 'transparent_percentage', text= 'Transparency' )
        row = layout.row( align= True )
        col = row.column( )
        col.label( text= "Area Percentage:" )
        col = row.column( )
        col.prop( props, 'percentage_x', text= "" )
        col = row.column( )
        col.prop( props, 'percentage_y', text= "" )

# -----------------------------------------------------------------------------

_draw_line_for_tilt_shift_handler = None

classes = (
    QANIM_Props_camera_extends_Camera_overscan,
    QANIM_Props_camera_extends_Camera_overscan_area,
    QANIM_Props_camera_extends_Camera_tilt_shift,
    QANIM_Props_camera_extends_Camera,

    QANIM_Props_camera_extends_Scene,

    calc_overscan.QANIM_OT_camera_extends_overscan_reset,
    calc_overscan.QANIM_OT_camera_extends_overscan_execute,
    tilt_shift.QANIM_OT_camera_extends_tilt_shift_vertical_auto_detection,
    tilt_shift.QANIM_OT_camera_extends_tilt_shift_horizontal_auto_detection,

    QANIM_PT_camera_extends,
)

def register():
    """
        クラス登録
    """
    for i in classes:
        bpy.utils.register_class(i)

    bpy.types.Scene.q_camera_extends = bpy.props.PointerProperty( type= QANIM_Props_camera_extends_Scene )
    bpy.types.Camera.q_camera_extends = bpy.props.PointerProperty( type= QANIM_Props_camera_extends_Camera )

    global _draw_line_for_tilt_shift_handler
    _draw_line_for_tilt_shift_handler = bpy.types.SpaceView3D.draw_handler_add( show_overscan.draw_line_for_tilt_shift, (), 'WINDOW', 'POST_VIEW' )

def unregister():
    """
        クラス登録解除
    """
    global _draw_line_for_tilt_shift_handler
    if _draw_line_for_tilt_shift_handler is not None:
        bpy.types.SpaceView3D.draw_handler_remove( _draw_line_for_tilt_shift_handler, 'WINDOW' )

    del bpy.types.Scene.q_camera_extends
    del bpy.types.Camera.q_camera_extends

    for i in classes:
        bpy.utils.unregister_class(i)
