# SPDX-License-Identifier: GPL-3.0-or-later
#
# Accelero Integra - analytically generated keyframes for acceleration/speed
# based animation (e.g. spinning up a fan), instead of hand-tuned Bezier
# handles in the Graph Editor.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version. See the LICENSE file for details.

bl_info = {
    "name": "Accelero Integra",
    "author": "Al-Essander",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Accelero Integra, Graph Editor > Sidebar > Accelero Integra",
    "description": (
        "Generates LINEAR keyframes from closed-form acceleration/speed models "
        "(constant, trapezoidal, sine, exponential, custom curve) instead of "
        "hand-tuned Bezier handles."
    ),
    "category": "Animation",
}

import bpy

from . import operators, panels, properties

_classes = (
    properties.AcceleroIntegraSettings,
    operators.ACCELERO_OT_generate,
    operators.ACCELERO_OT_clear,
    operators.ACCELERO_OT_edit_curve,
    panels.ACCELERO_PT_main,
    panels.ACCELERO_PT_graph_editor,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.accelero_integra = bpy.props.PointerProperty(type=properties.AcceleroIntegraSettings)


def unregister():
    del bpy.types.Scene.accelero_integra
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
