import bpy

import math

from . import show_overscan
from . import calc_overscan
from . import tilt_shift

# -----------------------------------------------------------------------------

class QANIM_Props_camera_extends_Camera_overscan(bpy.types.PropertyGroup):
    ratio_interlocked: bpy.props.BoolProperty(
        name='Ratio Interlock',
        description='lock/unlock screen/pixel ratio',
        default=True,
    )

    magnification_scale_x: bpy.props.FloatProperty(
        precision= 2,
        default= 120.0,
        min= 1.0,
        max= 500.0,
        step= 0.5,
        name= 'X',
        description= 'Screen Scale X',
        subtype= 'PERCENTAGE',
    )
    magnification_scale_y: bpy.props.FloatProperty(
        precision= 2,
        default= 120.0,
        min= 1.0,
        max= 500.0,
        step= 0.5,
        name= 'Y',
        description= 'Screen Scale Y',
        subtype= 'PERCENTAGE',
    )

    magnification_resolution_x: bpy.props.IntProperty(
        default= 2304,
        subtype='PIXEL',
        name= 'X',
        description= 'Screen Pixel X'
    )
    magnification_resolution_y: bpy.props.IntProperty(
        default= 1296,
        subtype='PIXEL',
        name= 'Y',
        description= 'Screen Pixel Y'
    )

    overscan_type: bpy.props.EnumProperty(
        name= 'Pixel or Percent',
        description= 'Select Overscan Method',
        items= (
            ('PERCENT', 'Percent', 'Percent'),
            ('PIXEL', 'Pixel', 'Pixel'),
        ),
        default= 'PERCENT',
    )

    pivot: bpy.props.EnumProperty(
        name= 'Pivot',
        description= 'Select Overscan Pivot',
        items= (
            ('UL', '', 'Upper Left'),
            ('UM', '', 'Upper Middle'),
            ('UR', '', 'Upper Right'),
            ('ML', '', 'Left'),
            ('MM', '', 'Center'),
            ('MR', '', 'Right'),
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

    last_applied_magnification_scale_x: bpy.props.FloatProperty( subtype= 'PERCENTAGE' )
    last_applied_magnification_scale_y: bpy.props.FloatProperty( subtype= 'PERCENTAGE' )
    last_applied_magnification_resolution_x: bpy.props.IntProperty( )
    last_applied_magnification_resolution_y: bpy.props.IntProperty( )
    last_applied_sensor_width: bpy.props.FloatProperty( )
    last_applied_shift_x: bpy.props.FloatProperty( )
    last_applied_shift_y: bpy.props.FloatProperty( )
    last_applied_overscan_type: bpy.props.EnumProperty(
        name= 'Pixel or Percent',
        description= 'Select Method',
        items= (
            ('PERCENT', 'Percent', 'Percent'),
            ('PIXEL', 'Pixel', 'Pixel'),
        ),
        default= 'PERCENT',
    )
    last_applied_pivot: bpy.props.EnumProperty(
        name= 'Pivot',
        description= 'Overscan Pivot',
        items= (
            ('UL', '', 'Upper Left'),
            ('UM', '', 'Upper Middle'),
            ('UR', '', 'Upper Right'),
            ('ML', '', 'Left'),
            ('MM', '', 'Center'),
            ('MR', '', 'Right'),
            ('DL', '', 'Lower Left'),
            ('DM', '', 'Lower Middle'),
            ('DR', '', 'Lower Right'),
        ),
        default= 'MM',
    )

class QANIM_Props_camera_extends_Camera_overscan_area(bpy.types.PropertyGroup):
    overscan_display_mode: bpy.props.EnumProperty(
        name= 'Overscan Display Mode'
    ,   description= 'Display Mode'
    ,   default= 'PERCENTAGE'
    ,   items= (
            ('PERCENTAGE', 'Percent', 'Percent')
        ,   ('PIXEL', 'Pixel', 'Pixel')
        )
    )
    percentage_x: bpy.props.FloatProperty(
        name='X',
        description='Overscan Area Percent X',
        subtype='PERCENTAGE',
        default=110.0,
        min=100.0,
        max=200.0,
        options= {'HIDDEN'},
    )
    percentage_y: bpy.props.FloatProperty(
        name='Y',
        description='Overscan Area Percent Y',
        subtype='PERCENTAGE',
        default=110.0,
        min=100.0,
        max=200.0,
        options= {'HIDDEN'},
    )
    pixel_x: bpy.props.FloatProperty(
        name='X',
        description='Overscan Area Pixel X',
        subtype='PIXEL',
        default=110.0,
        min=0.0,
        max=4000.0,
        options= {'HIDDEN'},
    )
    pixel_y: bpy.props.FloatProperty(
        name='Y',
        description='Overscan Area Pixel Y',
        subtype='PIXEL',
        default=110.0,
        min=0.0,
        max=4000.0,
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
        name='Overscan Area Transparent Percent',
        description='Overscan Area Transparent Percentage',
        subtype='PERCENTAGE',
        default=40.0,
        min=0.0,
        max=100.0,
        options= {'HIDDEN'},
    )

class QANIM_Props_camera_extends_Camera_tilt_shift(bpy.types.PropertyGroup):
    vertical: bpy.props.FloatProperty(
        name= 'Vertical'
    ,   description= 'TiltShift Vertial Angle'
    ,   precision=4
    ,   default=0.0
    ,   step=10.0
    ,   min=-math.pi/2.0
    ,   max=math.pi/2.0
    ,   subtype= 'ANGLE'
    ,   update=tilt_shift.update
    ,   options= {'HIDDEN'}
    )
    horizontal: bpy.props.FloatProperty(
        name= 'Horizontal'
    ,   description= 'TiltShift Horizontal Angle'
    ,   precision=4
    ,   default=0.0
    ,   step=10.0
    ,   min=-math.pi/2.0
    ,   max=math.pi/2.0
    ,   subtype= 'ANGLE'
    ,   update=tilt_shift.update
    ,   options= {'HIDDEN'}
    )

    temp_lens: bpy.props.FloatProperty( )
    temp_shift_x: bpy.props.FloatProperty( )
    temp_shift_y: bpy.props.FloatProperty( )

class QANIM_Props_camera_extends_Camera(bpy.types.PropertyGroup):
    overscan: bpy.props.PointerProperty( type= QANIM_Props_camera_extends_Camera_overscan )
    overscan_area: bpy.props.PointerProperty( type= QANIM_Props_camera_extends_Camera_overscan_area )
    tilt_shift: bpy.props.PointerProperty( type= QANIM_Props_camera_extends_Camera_tilt_shift )

class QANIM_Props_camera_extends_Scene(bpy.types.PropertyGroup):
    overscan_is_display: bpy.props.BoolProperty( name="Overscan Area Showing", description= 'Overscan Area Showing', default= True, options= {'HIDDEN'} )

# -----------------------------------------------------------------------------

class QANIM_PT_camera_extends(bpy.types.Panel):
    bl_label = "Camera Extends"
    bl_idname = "QANIM_PT_overscan"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Camera Extends"
    bl_options = {'DEFAULT_CLOSED'}

    def draw( self, context ):
        if context.active_object and context.object and context.object.type == 'CAMERA':
            self._draw_overscan( )
            self._draw_tilt_shift( )
            self._draw_overscan_area( )
        else:
            self._draw_please_select( )
            self._draw_overscan_area( )

    def _draw_overscan( self ):
        layout = self.layout
        camera_object = bpy.context.active_object
        camera = camera_object.data
        props = camera.q_camera_extends.overscan

        row = layout.row( )

        # 基点
        box = row.box( )
        pivot_row = box.row( ).split( factor= 0.35 )
        pivot_column = pivot_row.column( )
        pivot_column.row( ).label( text= 'Pivot:' )
        grid = pivot_column.row( ).grid_flow( columns= 3, row_major= True )
        grid.scale_y = 0.8
        grid.prop( props, "pivot", expand= True )

        # オーバースキャン比率 or オーバースキャン後の解像度
        box = pivot_row.box( )
        pivot_column = box.column( align=True )
        row = pivot_column.row( )
        row.prop( props, "overscan_type", expand= True )
        pivot_column.separator( )

        # 解像度 / 比率入力
        row = pivot_column.row( )
        col = row.column( align= True )
        if props.overscan_type == 'PERCENT':
            col.prop( props, 'magnification_scale_x', text= "X" )
            if props.ratio_interlocked:
                col.prop( props, 'magnification_scale_x', text= "Y" )
            else:
                col.prop( props, 'magnification_scale_y', text= "Y" )
            row.prop( props, 'ratio_interlocked', icon='LOCKED' if props.ratio_interlocked else 'UNLOCKED', icon_only=True)
        elif props.overscan_type == 'PIXEL':
            col.prop( props, 'magnification_resolution_x', text= "X" )
            col.prop( props, 'magnification_resolution_y', text= "Y" )

        # オーバースキャン実行
        row = layout.row( )
        row.label( text= "Overscan:" )
        row = layout.row( align= False )
        row.operator( calc_overscan.QANIM_OT_camera_extends_overscan_execute.bl_idname, text= "Apply", icon= 'SHADING_BBOX' )
        row.operator( calc_overscan.QANIM_OT_camera_extends_overscan_reset.bl_idname, text= "Reset", icon= 'LOOP_BACK' )
        box = layout.box( )
        row = box.row( )
        sp = row.column( ).split( factor= 0.4 )
        if props.last_applied_overscan_type == "PERCENT":
            sp.label( text= "Total Scale")
            if props.applied:
                sp.label( text= "%s%% x %s%%" % (
                    ( "%-8.2f" % ( props.last_applied_magnification_scale_x * 100.0 ) ).replace( " ", "" )
                ,   ( "%-8.2f" % ( props.last_applied_magnification_scale_y * 100.0 ) ).replace( " ", "" )
                ))
            else:
                sp.label( text= "Not Applied" )
        elif props.last_applied_overscan_type == "PIXEL":
            sp.label( text= "Original Pixel")
            if props.applied:
                sp.label( text= "%d x %d" % (
                    props.last_applied_magnification_resolution_x
                ,   props.last_applied_magnification_resolution_y
                ))
            else:
                sp.label( text= "Not Applied" )
        row = box.row( )
        sp = row.column( ).split( factor= 0.4 )
        sp.label( text= "Pivot" )
        if props.applied:
            sp.label( text= "%s%s" % (
                {"U": "Upper ", "D": "Lower ", "M": ""}[props.last_applied_pivot[0]]
            ,   "Center" if props.last_applied_pivot == "MM" else {"L": "Left", "R": "Right", "M": "Middle"}[props.last_applied_pivot[1]]
            ))
        else:
            sp.label( text= "Not Applied" )

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
        camera_object = bpy.context.scene.camera
        if camera_object is None:
            return

        camera = camera_object.data
        props = camera.q_camera_extends.overscan_area

        row = layout.row( )
        row.label( text= "Overscan Test Display:" )
        row = layout.row( )
        row.prop( bpy.context.scene.q_camera_extends, 'overscan_is_display', text= 'Showing' )
        row = layout.row( )
        row.prop( props, 'displaying_color', text= 'Area Color' )
        row = layout.row( )
        row.prop( props, 'transparent_percentage', text= 'Transparency' )

        row = layout.row( )
        row.prop( props, 'overscan_display_mode', expand= True )
        if props.overscan_display_mode == 'PERCENTAGE':
            row = layout.row( align= True )
            col = row.column( )
            col.label( text= "Area Percent:" )
            col = row.column( )
            col.prop( props, 'percentage_x', text= "" )
            col = row.column( )
            col.prop( props, 'percentage_y', text= "" )
        elif props.overscan_display_mode == 'PIXEL':
            row = layout.row( align= True )
            col = row.column( )
            col.label( text= "Area Pixel:" )
            col = row.column( )
            col.prop( props, 'pixel_x', text= "" )
            col = row.column( )
            col.prop( props, 'pixel_y', text= "" )

    def _draw_please_select( self ):
        layout = self.layout
        layout.label( text= "Select the Camera.", icon= 'INFO' )

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
