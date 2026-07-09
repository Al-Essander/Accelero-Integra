# SPDX-License-Identifier: GPL-3.0-or-later
import bpy

from . import backup, math_models
from .properties import PROP_CHANNEL_MAP


def _duration_seconds(props, fps):
    return (props.frame_end - props.frame_start) / fps


def _evaluate_position(props, t, duration):
    model = props.model
    if model == 'CONSTANT':
        return math_models.constant_acceleration(t, props.x0, props.v0, props.accel)
    if model == 'TRAPEZOID':
        return math_models.trapezoidal(
            t, duration, props.x0, props.v0,
            props.v_target, props.v_end,
            props.accel_rate, props.decel_rate,
        )
    if model == 'SINE':
        return math_models.sine_ease(t, duration, props.x0, props.v0, props.v_target)
    if model == 'EXPONENTIAL':
        return math_models.exponential_approach(
            t, props.x0, props.v0, props.v_target, props.time_constant,
        )
    if model == 'CUSTOM_CURVE':
        t_norm = t / duration if duration else 0.0
        curve = props.custom_curve.curves[0]
        return math_models.custom_curve_position(t_norm, props.x0, props.custom_x_end, curve.evaluate)
    raise ValueError(f"Unknown model: {model}")


def _get_or_create_fcurve(obj, data_path, index):
    if obj.animation_data is None:
        obj.animation_data_create()
    if obj.animation_data.action is None:
        obj.animation_data.action = bpy.data.actions.new(name=f"{obj.name}Action")
    action = obj.animation_data.action

    fcurve = action.fcurves.find(data_path, index=index)
    if fcurve is None:
        fcurve = action.fcurves.new(data_path, index=index, action_group=obj.name)
    return fcurve


class ACCELERO_OT_generate(bpy.types.Operator):
    bl_idname = "accelero_integra.generate"
    bl_label = "Generate"
    bl_description = "Analytically compute the position for every frame and insert it as a linear keyframe"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.accelero_integra
        obj = props.target_object

        if obj is None:
            self.report({'ERROR'}, "Select an object first.")
            return {'CANCELLED'}

        if props.frame_end <= props.frame_start:
            self.report({'ERROR'}, "End frame must be greater than Start frame.")
            return {'CANCELLED'}

        if props.model == 'CUSTOM_CURVE':
            props.custom_curve.initialize()
            props.custom_curve.update()

        scene = context.scene
        fps = scene.render.fps / scene.render.fps_base
        duration = _duration_seconds(props, fps)

        data_path, index = PROP_CHANNEL_MAP[props.prop_channel]
        fcurve = _get_or_create_fcurve(obj, data_path, index)

        backup.store(obj, data_path, index, fcurve, props.frame_start, props.frame_end)

        for kp in [kp for kp in fcurve.keyframe_points
                   if props.frame_start <= kp.co.x <= props.frame_end]:
            fcurve.keyframe_points.remove(kp, fast=True)

        try:
            for frame in range(props.frame_start, props.frame_end + 1):
                t = (frame - props.frame_start) / fps
                value = _evaluate_position(props, t, duration)
                kp = fcurve.keyframe_points.insert(frame, value, options={'FAST'})
                kp.interpolation = 'LINEAR'
        except math_models.MotionRangeError as exc:
            self.report({'ERROR'}, str(exc))
            fcurve.update()
            return {'CANCELLED'}

        fcurve.update()
        count = props.frame_end - props.frame_start + 1
        self.report({'INFO'}, f"Generated {count} keyframes on {data_path}[{index}].")
        return {'FINISHED'}


class ACCELERO_OT_clear(bpy.types.Operator):
    bl_idname = "accelero_integra.clear"
    bl_label = "Clear / Revert"
    bl_description = "Remove the generated keyframes and restore whatever was there before Generate ran"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.accelero_integra
        obj = props.target_object

        if obj is None:
            self.report({'ERROR'}, "Select an object first.")
            return {'CANCELLED'}

        data_path, index = PROP_CHANNEL_MAP[props.prop_channel]
        action = obj.animation_data.action if obj.animation_data else None
        fcurve = action.fcurves.find(data_path, index=index) if action else None

        if fcurve is None:
            self.report({'WARNING'}, "Nothing to clear on this channel.")
            return {'CANCELLED'}

        restored = backup.restore(obj, data_path, index, fcurve, props.frame_start, props.frame_end)
        self.report({'INFO'}, "Restored previous keyframes." if restored else "Cleared the frame range.")
        return {'FINISHED'}


class ACCELERO_OT_edit_curve(bpy.types.Operator):
    bl_idname = "accelero_integra.edit_curve"
    bl_label = "Edit Progress Curve"
    bl_description = "Draw a custom 0-1 progress curve between Start and End value"
    bl_options = {'REGISTER'}

    def invoke(self, context, event):
        props = context.scene.accelero_integra
        props.custom_curve.initialize()
        return context.window_manager.invoke_props_dialog(self, width=420)

    def draw(self, context):
        props = context.scene.accelero_integra
        layout = self.layout
        layout.label(text="Progress over time (X: time, Y: 0=Start Value, 1=End Value)")
        layout.template_curve_mapping(props, "custom_curve")
        row = layout.row(align=True)
        row.prop(props, "x0", text="Start")
        row.prop(props, "custom_x_end", text="End")

    def execute(self, context):
        context.scene.accelero_integra.custom_curve.update()
        return {'FINISHED'}
