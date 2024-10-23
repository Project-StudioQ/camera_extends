import bpy

# -----------------------------------------------------------------------------

class QANIM_OT_camera_extends_overscan_reset(bpy.types.Operator):
    bl_label = "Reset Overscan"
    bl_idname = "qanim.camera_extends_overscan_reset"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}

    def execute( self, context ):
        camera_object = context.active_object
        camera = camera_object.data
        props = camera.q_camera_extends.overscan

        if not props.applied:
            self.report({'WARNING'}, "適応されていません。")
            return {'CANCELLED'}

        bpy.context.scene.render.resolution_x = props.saved_resolution_x
        bpy.context.scene.render.resolution_y = props.saved_resolution_y
        camera.shift_x = props.saved_shift_x
        camera.shift_y = props.saved_shift_y
        camera.sensor_width = props.saved_sensor_width

        camera_object.delta_rotation_euler.x = 0
        camera_object.delta_rotation_euler.z = 0

        props.applied = False

        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

        return {'FINISHED'}

class QANIM_OT_camera_extends_overscan_execute(bpy.types.Operator):
    bl_label = "Execute Overscan"
    bl_idname = "qanim.overscan_execute"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}

    def execute( self, context ):
        camera_object = context.active_object
        camera = camera_object.data
        props = camera.q_camera_extends.overscan

        if props.applied:
            self.report({'WARNING'}, "既に適応済みです。")
            return {'CANCELLED'}

        # 解像度を計算
        scale_ratio_x = props.magnification_scale_x
        if props.ratio_interlocked:
            scale_ratio_y = scale_ratio_x
        else:
            scale_ratio_y = props.magnification_scale_y

        currently_resolution_x = bpy.context.scene.render.resolution_x
        currently_resolution_y = bpy.context.scene.render.resolution_y

        if props.overscan_type == 'PERCENT':
            bpy.context.scene.render.resolution_x = int( currently_resolution_x * scale_ratio_x )
            bpy.context.scene.render.resolution_y = int( currently_resolution_y * scale_ratio_y )
        elif props.overscan_type == 'PIXEL':
            bpy.context.scene.render.resolution_x = props.magnification_resolution_x
            bpy.context.scene.render.resolution_y = props.magnification_resolution_y

        resolution_ratio = bpy.context.scene.render.resolution_y / bpy.context.scene.render.resolution_x

        # センサーフィットが自動だったら水平に変換しセンサーの初期値確定
        currently_sensor_width = camera.sensor_width
        if camera.sensor_fit == 'AUTO':
            camera.sensor_fit = 'HORIZONTAL'
            if currently_resolution_x < currently_resolution_y:
                camera.sensor_width = (currently_resolution_y / currently_resolution_x * currently_sensor_width) / 2.0

        # 元のカメラ設定・解像度をカスタムプロパティに格納
        props.saved_resolution_x = currently_resolution_x
        props.saved_resolution_y = currently_resolution_y
        props.saved_sensor_width = currently_sensor_width
        props.saved_shift_x = camera.shift_x
        props.saved_shift_y = camera.shift_y
        props.applied = True

        # センサーサイズ変更によるオーバースキャン
        if props.overscan_type == 'PERCENT':
            camera.sensor_width = currently_sensor_width * scale_ratio_x
        elif props.overscan_type == 'PIXEL':
            camera.sensor_width = currently_sensor_width * (props.magnification_resolution_x / currently_resolution_x)

        # オーバースキャン基点設定
        lr_pivot = {'U': 1, 'D': -1, 'M': 0}[props.pivot[0]]
        ud_pivot = {'L': -1, 'R': 1, 'M': 0}[props.pivot[1]]

        if props.overscan_type == 'PIXEL':
            scale_ratio_x = props.magnification_resolution_x / currently_resolution_x
            scale_ratio_y = props.magnification_resolution_y / currently_resolution_y

        camera.shift_x = props.saved_shift_x + (scale_ratio_x - 1) / scale_ratio_x / 2.0 * lr_pivot
        camera.shift_y = props.saved_shift_y + (scale_ratio_y - 1) / scale_ratio_y / 2.0 * resolution_ratio * ud_pivot

        return {'FINISHED'}
