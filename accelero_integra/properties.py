# SPDX-License-Identifier: GPL-3.0-or-later
import bpy

PROP_CHANNEL_MAP = {
    'LOC_X': ("location", 0),
    'LOC_Y': ("location", 1),
    'LOC_Z': ("location", 2),
    'ROT_X': ("rotation_euler", 0),
    'ROT_Y': ("rotation_euler", 1),
    'ROT_Z': ("rotation_euler", 2),
    'SCALE_X': ("scale", 0),
    'SCALE_Y': ("scale", 1),
    'SCALE_Z': ("scale", 2),
}

PROP_CHANNEL_ITEMS = (
    ('LOC_X', "Location X", ""),
    ('LOC_Y', "Location Y", ""),
    ('LOC_Z', "Location Z", ""),
    ('ROT_X', "Rotation X", ""),
    ('ROT_Y', "Rotation Y", ""),
    ('ROT_Z', "Rotation Z", ""),
    ('SCALE_X', "Scale X", ""),
    ('SCALE_Y', "Scale Y", ""),
    ('SCALE_Z', "Scale Z", ""),
)

MODEL_ITEMS = (
    ('CONSTANT', "Constant Acceleration", "Classic uniformly accelerated motion"),
    ('TRAPEZOID', "Trapezoidal", "Accelerate, cruise at a target speed, then decelerate"),
    ('SINE', "Sine (Ease)", "Smooth, jerk-free transition between two speeds"),
    ('EXPONENTIAL', "Exponential", "Asymptotic approach to a target speed"),
    ('CUSTOM_CURVE', "Custom Curve", "Hand-drawn progress curve from Start to End value"),
)


class AcceleroCurvePoint(bpy.types.PropertyGroup):
    position: bpy.props.FloatProperty(name="Time", min=0.0, max=1.0, default=0.5)
    value: bpy.props.FloatProperty(name="Progress", min=0.0, max=1.0, default=0.5)


class AcceleroIntegraSettings(bpy.types.PropertyGroup):
    target_object: bpy.props.PointerProperty(
        name="Object",
        type=bpy.types.Object,
        description="Object whose property will be keyframed",
    )
    prop_channel: bpy.props.EnumProperty(
        name="Property",
        items=PROP_CHANNEL_ITEMS,
        default='ROT_Z',
    )
    frame_start: bpy.props.IntProperty(name="Start", default=1)
    frame_end: bpy.props.IntProperty(name="End", default=100)

    model: bpy.props.EnumProperty(
        name="Model",
        items=MODEL_ITEMS,
        default='CONSTANT',
    )

    x0: bpy.props.FloatProperty(name="Start Value", default=0.0)
    v0: bpy.props.FloatProperty(name="Start Speed", default=0.0)

    accel: bpy.props.FloatProperty(name="Acceleration", default=1.0)

    v_target: bpy.props.FloatProperty(name="Target Speed", default=5.0)
    v_end: bpy.props.FloatProperty(name="End Speed", default=0.0)
    accel_rate: bpy.props.FloatProperty(name="Accel Rate", default=2.0, min=0.0001)
    decel_rate: bpy.props.FloatProperty(name="Decel Rate", default=2.0, min=0.0001)

    time_constant: bpy.props.FloatProperty(
        name="Time Constant (k)", default=2.0, min=0.0001,
        description="Higher values approach the target speed faster",
    )

    custom_x_end: bpy.props.FloatProperty(name="End Value", default=1.0)
    custom_curve_points: bpy.props.CollectionProperty(type=AcceleroCurvePoint)
    custom_curve_active_index: bpy.props.IntProperty()
