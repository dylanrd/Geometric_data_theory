import mathutils

from .axis_of_rotation import *
from .test import *

import bpy
import mathutils


class AxisOfRotation(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_AxisOfRotationPanel"
    bl_label = "Mesh Rotation Matrix"

    bl_category = "Practical 2"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):

        if context.view_layer.objects.active:
            self.layout.prop(context.active_object, 'rotation_matrix')
            self.layout.label(text="Axis of Rotation")
            self.layout.prop(context.active_object, 'rotation_axis', text="")
        else:
            self.layout.label(text="Select a mesh")

        self.layout.prop(context.scene, 'show_axis_of_rotation')


class AxisOfRotationGizmo(bpy.types.GizmoGroup):
    bl_idname = "OBJECT_GGT_axis_of_rotation"
    bl_label = "Axis of Rotation Gizmo"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'PERSISTENT'}

    arrow_north, arrow_south = None, None
    dial = None

    @classmethod
    def poll(cls, context):
        return context.scene.show_axis_of_rotation and context.view_layer.objects.active

    def setup(self, context):
        self.arrow_north, self.arrow_south = self.gizmos.new("GIZMO_GT_arrow_3d"), self.gizmos.new("GIZMO_GT_arrow_3d")
        self.dial = self.gizmos.new("GIZMO_GT_dial_3d")

        self.arrow_north.color = (1.0, 0.1, 0.1)
        self.arrow_south.draw_style = 'BOX'
        self.dial.alpha = 0.4
        self.dial.line_width = 5

        self.arrow_south.target_set_handler('offset', get=lambda: 0.0, set=lambda v: None)
        self.arrow_north.target_set_handler('offset', get=lambda: 0.0, set=lambda v: None)

    def draw_prepare(self, context):
        active_object = context.view_layer.objects.active

        axis, angle = active_object.rotation_axis, active_object.rotation_angle

        self.arrow_north.matrix_basis = mathutils.Matrix.LocRotScale(
            active_object.matrix_world.translation,
            mathutils.Vector([0, 0, 1]).rotation_difference(axis),
            None
        )
        self.arrow_south.matrix_basis = mathutils.Matrix.LocRotScale(
            active_object.matrix_world.translation,
            mathutils.Vector([0, 0, -1]).rotation_difference(axis),
            None
        )
        self.dial.matrix_basis = active_object.matrix_world
        self.dial.matrix_basis = mathutils.Matrix.LocRotScale(
            active_object.matrix_world.translation,
            mathutils.Vector([0, 0, 1]).rotation_difference(axis) @ mathutils.Quaternion((0, 0, 1), angle / 2),
            mathutils.Vector([0.25, 0.25, 0.25])
        )
        self.dial.arc_partial_angle = math.tau - angle


def register():
    # Global property which enables the visualization
    bpy.types.Scene.show_axis_of_rotation = bpy.props.BoolProperty(
        name="Visualize Axis of Rotation",
        description="When enabled, the net axis of (world-space) rotion of the currently selected object is "
                    "visualized as an arrow.",
        default=True,
    )

    bpy.types.Object.rotation_matrix = bpy.props.FloatVectorProperty(
        name="Rotation Matrix",
        size=[3, 3],
        subtype='MATRIX',
        get=lambda obj: rotation_component(obj.matrix_world),
        # no `set` -- this property shouldn't be writeable
    )
    bpy.types.Object.rotation_axis = bpy.props.FloatVectorProperty(
        name="Rotation Axis",
        size=[3],
        precision=3,
        get=lambda obj: axis_of_rotation(obj.rotation_matrix),
        # no `set` -- this property shouldn't be writeable
    )
    bpy.types.Object.rotation_angle = bpy.props.FloatProperty(
        name="Rotation Angle",
        get=lambda obj: angle_of_rotation(obj.rotation_matrix),
        # no `set` -- this property shouldn't be writeable
    )
