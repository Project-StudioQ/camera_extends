import bpy

# -----------------------------------------------------------------------------

class QANIM_OT_overscan_reset(bpy.types.Operator):
    bl_label = "reset_overScan"
    bl_idname = "qanim.overscan_reset"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}   # undo効くようにする設定
    
    def resetOverScan(self, context):
        ''' オーバースキャンで設定したパラメータをリセット
        '''
        camera_object = context.active_object
        camera = camera_object.data

        bpy.context.scene.render.resolution_x = camera.oriResX
        bpy.context.scene.render.resolution_y = camera.oriResY
        camera.shift_x = camera.overscan_original_shift_x
        camera.shift_y = camera.overscan_original_shift_y
        camera.sensor_width = camera.sensorWidth

        camera_object.delta_rotation_euler.x = 0
        camera_object.delta_rotation_euler.z = 0

        del camera["oriResX"]
        del camera["oriResY"]
        del camera["sensorWidth"]

        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

    def execute(self, context):
        ''' メイン処理
        '''
        
        camera_object = context.active_object
        camera = camera_object.data

        if hasattr(camera, "oriResX") is False:    # 初回起動時はこちらでオーバースキャン実行
            self.resetOverScan( context )
        elif camera.oriResX > 0:                   # 2回目以降はこちら
            self.resetOverScan( context )

        return{'FINISHED'}

class QANIM_OT_overscan_run(bpy.types.Operator):
    bl_label = "run_overScan"
    bl_idname = "qanim.overscan_run"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}   # undo効くようにする設定
    
    def overScan(self, context):
        ''' オーバースキャン設定
        '''

        camera_object = context.active_object
        camera = camera_object.data
        pivot = camera.pivot_prop_enum
        scaleRatioX = camera.magnification_prop_FloatX
        scaleRatioY = camera.magnification_prop_FloatY

        # 解像度変更
        curResX = bpy.context.scene.render.resolution_x
        curResY = bpy.context.scene.render.resolution_y
        
        if camera.pixOrPer_prop_enum == 'percent':
            bpy.context.scene.render.resolution_x = int( curResX * scaleRatioX )
            bpy.context.scene.render.resolution_y = int( curResY * scaleRatioY )
        elif camera.pixOrPer_prop_enum == 'pixcel':
            bpy.context.scene.render.resolution_x = camera.magnification_prop_IntX
            bpy.context.scene.render.resolution_y = camera.magnification_prop_IntY

        resResult = bpy.context.scene.render.resolution_y / bpy.context.scene.render.resolution_x

        # センサーフィットが自動だったら水平に変換しセンサーの初期値確定
        curSensor = camera.sensor_width
        if camera.sensor_fit == 'AUTO':
            camera.sensor_fit = 'HORIZONTAL'
            if curResY > curResX:
                camera.sensor_width = (curResY / curResX * curSensor) / 2

        # 元のカメラ設定・解像度をカスタムプロパティに格納
        bpy.types.Camera.oriResX = bpy.props.IntProperty(name="oriResX")
        bpy.types.Camera.oriResY = bpy.props.IntProperty(name="oriResY")
        bpy.types.Camera.sensorWidth = bpy.props.IntProperty(name="sensor_width")
        camera.oriResX = curResX
        camera.oriResY = curResY
        camera.sensorWidth = int( camera.sensor_width )

        # センサーサイズ変更によるオーバースキャン
        sensorWidth = camera.sensor_width
        if camera.pixOrPer_prop_enum == 'percent':
            camera.sensor_width = int( sensorWidth * scaleRatioX )
        elif camera.pixOrPer_prop_enum == 'pixcel':
            camera.sensor_width = int( sensorWidth * (camera.magnification_prop_IntX / camera.oriResX) )
        
        # オーバースキャン基点設定
        if pivot[0] == 'U':
            LRPivot = 1
        elif pivot[0] == 'D':
            LRPivot = -1
        elif pivot[0] == 'M':
            LRPivot = 0

        if pivot[1] == 'L':
            UDPivot = -1
        elif pivot[1] == 'R':
            UDPivot = 1
        elif pivot[1] == 'M':
            UDPivot = 0
            
        if camera.pixOrPer_prop_enum == 'pixcel':
            scaleRatioX = camera.magnification_prop_IntX / camera.oriResX
            scaleRatioY = camera.magnification_prop_IntY / camera.oriResY

        camera.overscan_original_shift_x = camera.shift_x
        camera.overscan_original_shift_y = camera.shift_y
        camera.shift_x = camera.overscan_original_shift_x + (scaleRatioX - 1) / scaleRatioX / 2 * LRPivot
        camera.shift_y = camera.overscan_original_shift_y + (scaleRatioY - 1) / scaleRatioY / 2 * resResult * UDPivot
        camera.temp_camera_overscan_force_apply = False

    def execute(self, context):
        ''' メイン処理
        '''

        camera_object = context.active_object
        camera = camera_object.data

        # オーバースキャン実行
        if 'CAMERA' == camera_object.type:
            if hasattr(camera, "oriResX") is False:       # 初回起動時はこちらでオーバースキャン実行
                self.overScan( context )
            elif camera.oriResX == 0:                     # 2回目以降はこちら
                self.overScan( context )
            elif camera.temp_camera_overscan_force_apply: # 多重かけ防止だが、強制的にONにする
                self.overScan( context )

        return{'FINISHED'}

# -----------------------------------------------------------------------------

def _initialized():
    ''' プロパティの初期化
    '''

    scene = bpy.types.Camera
    # scene = bpy.types.Scene
    
    # 比を固定して変更するようにするか
    scene.temp_ratio_interlocked = bpy.props.BoolProperty(
        name='temp_ratio_interlocked',
        description='lock/unlock screen/pixel ratio',
        default=True,
    )
    
    # 更新中に追加更新しないように(無限ループになる)
    scene.temp_updating_locked = bpy.props.BoolProperty(
        name='temp_updating_locked',
        description='block infinity loop for update value',
        default=False,
    )
    scene.temp_camera_overscan_force_apply = bpy.props.BoolProperty(
        name='Force applies overscan',
        description='Force applies overscan',
        default=False,
    )
    
    # オーバースキャン比率プロパティ
    scene.magnification_prop_FloatX = bpy.props.FloatProperty(precision=1, default=1.2, step=10.0, update=_update_magnification_prop_FloatX)
    scene.magnification_prop_FloatY = bpy.props.FloatProperty(precision=1, default=1.2, step=10.0, update=_update_magnification_prop_FloatY)
    
    # オーバースキャン後解像度プロパティ
    scene.magnification_prop_IntX = bpy.props.IntProperty(default=2304)
    scene.magnification_prop_IntY = bpy.props.IntProperty(default=1296)

    # オリジナルシフト値を保存
    scene.overscan_original_shift_x = bpy.props.FloatProperty(name="Original Camera Shift X")
    scene.overscan_original_shift_y = bpy.props.FloatProperty(name="Original Camera Shift Y")

    # オーバースキャン比率か解像度のいずれをえらぶかのプロパティ
    scene.pixOrPer_prop_enum = bpy.props.EnumProperty(
        name='pixOrPer',
        description='select method',
        items=[
            ('percent', 'percent', 'percent'),
            ('pixcel', 'pixcel', 'pixcel'),
        ],
        default='percent'
    )

    # オーバースキャンpivot
    scene.pivot_prop_enum = bpy.props.EnumProperty(
        name='pivot',
        description='overscan pivot',
        items=[
            ('UL', '', 'up_left'),
            ('UM', '', 'up_mid'),
            ('UR', '', 'up_right'),
            ('ML', '', 'mid_left'),
            ('MM', '', 'mid_mid'),
            ('MR', '', 'mid_right'),
            ('DL', '', 'down_left'),
            ('DM', '', 'down_mid'),
            ('DR', '', 'down_right'),
        ],
        default='MM'
    )

def _deinitialized( ):
    """
        後始末
    """
    scene = bpy.types.Camera
    
    del scene.pixOrPer_prop_enum
    del scene.temp_ratio_interlocked
    del scene.temp_updating_locked
    del scene.temp_camera_overscan_force_apply
    del scene.magnification_prop_FloatX
    del scene.magnification_prop_FloatY
    del scene.magnification_prop_IntX
    del scene.magnification_prop_IntY

    del scene.overscan_original_shift_x
    del scene.overscan_original_shift_y
    del scene.pivot_prop_enum

def _update_magnification_prop_FloatX( self, context ):
    scene = context.active_object.data
    if scene.temp_updating_locked:
        return
    scene.temp_updating_locked = True
    if scene.temp_ratio_interlocked:
        scene.magnification_prop_FloatY = scene.magnification_prop_FloatX
    scene.temp_updating_locked = False

def _update_magnification_prop_FloatY( self, context ):
    scene = context.active_object.data
    if scene.temp_updating_locked:
        return
    scene.temp_updating_locked = True
    if scene.temp_ratio_interlocked:
        scene.magnification_prop_FloatX = scene.magnification_prop_FloatY
    scene.temp_updating_locked = False
