# SPDX-License-Identifier: GPL-3.0-or-later
import bpy


class ACCELERO_PT_main(bpy.types.Panel):
    bl_label = "Accelero Integra"
    bl_idname = "ACCELERO_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Accelero Integra"

    def draw(self, context):
        layout = self.layout
        props = context.scene.accelero_integra

        col = layout.column()
        col.prop(props, "target_object")
        col.prop(props, "prop_channel")

        row = col.row(align=True)
        row.prop(props, "frame_start")
        row.prop(props, "frame_end")

        col.separator()
        col.prop(props, "model")

        box = col.box()
        if props.model == 'CONSTANT':
            box.prop(props, "x0")
            box.prop(props, "v0")
            box.prop(props, "accel")
        elif props.model == 'TRAPEZOID':
            box.prop(props, "x0")
            box.prop(props, "v0")
            box.prop(props, "v_target")
            box.prop(props, "v_end")
            box.prop(props, "accel_rate")
            box.prop(props, "decel_rate")
        elif props.model == 'SINE':
            box.prop(props, "x0")
            box.prop(props, "v0")
            box.prop(props, "v_target")
        elif props.model == 'EXPONENTIAL':
            box.prop(props, "x0")
            box.prop(props, "v0")
            box.prop(props, "v_target")
            box.prop(props, "time_constant")
        elif props.model == 'CUSTOM_CURVE':
            box.prop(props, "x0", text="Start Value")
            box.prop(props, "custom_x_end", text="End Value")
            box.operator("accelero_integra.edit_curve", icon='FCURVE')

        col.separator()
        row = col.row(align=True)
        row.operator("accelero_integra.generate", icon='KEYFRAME_HLT')
        row.operator("accelero_integra.clear", icon='TRASH')


class ACCELERO_PT_graph_editor(ACCELERO_PT_main):
    bl_idname = "ACCELERO_PT_graph_editor"
    bl_space_type = 'GRAPH_EDITOR'
