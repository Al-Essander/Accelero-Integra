# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure-Python analytical motion models.

No bpy imports here on purpose: every model below computes position as a
closed-form function of time, so a single call replaces per-frame numeric
integration (and the rounding error it would accumulate). Keeping this
module bpy-free also makes it runnable and testable outside Blender.
"""

import math


class MotionRangeError(ValueError):
    """Raised when the given parameters cannot fit inside the requested duration."""


def constant_acceleration(t, x0, v0, accel):
    return x0 + v0 * t + 0.5 * accel * t * t


def trapezoidal(t, duration, x0, v0, v_target, v_end, accel, decel):
    if accel <= 0 or decel <= 0:
        raise MotionRangeError("Acceleration and deceleration must be positive.")
    if v_target < v0 or v_target < v_end:
        raise MotionRangeError(
            "Target speed must be the highest of the three speeds: "
            "it is reached by accelerating up from the start speed, "
            "then left by decelerating down to the end speed."
        )

    t1 = (v_target - v0) / accel
    t3 = (v_target - v_end) / decel
    t2 = duration - t1 - t3

    if t2 < -1e-6:
        raise MotionRangeError(
            "Accel/decel rates are too gentle for the given frame range: "
            "the ramp-up and ramp-down phases alone need more time than "
            "Start-End provides."
        )
    t2 = max(t2, 0.0)

    x1 = x0 + v0 * t1 + 0.5 * accel * t1 * t1
    x2 = x1 + v_target * t2

    if t <= t1:
        return x0 + v0 * t + 0.5 * accel * t * t
    if t <= t1 + t2:
        return x1 + v_target * (t - t1)
    dt = min(t - t1 - t2, t3)
    return x2 + v_target * dt - 0.5 * decel * dt * dt


def sine_ease(t, duration, x0, v0, v_target):
    """Smooth (jerk-free at both ends) transition from v0 to v_target."""
    if duration <= 0:
        return x0
    dv = v_target - v0
    omega = math.pi / duration
    return x0 + v0 * t + dv * 0.5 * (t - math.sin(omega * t) / omega)


def exponential_approach(t, x0, v0, v_target, k):
    """Asymptotic approach to v_target: dv/dt = k * (v_target - v)."""
    if k <= 0:
        raise MotionRangeError("Time constant (k) must be positive.")
    dv = v0 - v_target
    return x0 + v_target * t + dv / k * (1.0 - math.exp(-k * t))


def custom_curve_position(t_norm, x0, x1, evaluate):
    """Map a normalized 0..1 progress curve onto the x0..x1 range."""
    t_norm = min(max(t_norm, 0.0), 1.0)
    y = evaluate(t_norm)
    return x0 + y * (x1 - x0)
