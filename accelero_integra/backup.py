# SPDX-License-Identifier: GPL-3.0-or-later
"""Stores/restores whatever keyframes were on a channel before Generate ran,
so Clear acts as an undo-safe toggle even after a file save/reload.
"""

BACKUP_ID_PROPERTY = "accelero_integra_backup"


def _slot_key(data_path, index):
    return f"{data_path}[{index}]"


def store(obj, data_path, index, fcurve, frame_start, frame_end):
    data = dict(obj.get(BACKUP_ID_PROPERTY, {}))
    data[_slot_key(data_path, index)] = [
        {"frame": kp.co.x, "value": kp.co.y, "interpolation": kp.interpolation}
        for kp in fcurve.keyframe_points
        if frame_start <= kp.co.x <= frame_end
    ]
    obj[BACKUP_ID_PROPERTY] = data


def restore(obj, data_path, index, fcurve, frame_start, frame_end):
    """Removes keys in range and restores the pre-Generate snapshot, if any.
    Returns True if a snapshot was restored, False if the range was just cleared.
    """
    data = obj.get(BACKUP_ID_PROPERTY, {})
    keys = data.get(_slot_key(data_path, index)) if data else None

    for kp in [kp for kp in fcurve.keyframe_points if frame_start <= kp.co.x <= frame_end]:
        fcurve.keyframe_points.remove(kp, fast=True)

    if keys:
        for k in keys:
            kp = fcurve.keyframe_points.insert(k["frame"], k["value"], options={'FAST'})
            kp.interpolation = k["interpolation"]

    fcurve.update()
    return bool(keys)
