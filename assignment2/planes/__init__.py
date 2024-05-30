import mathutils
import numpy

from .distance_to_planes import *
from .test import *

import random
import bpy
from bpy.app.handlers import persistent
import mathutils
from mathutils import Vector, Matrix, Quaternion


class PlanesPropertyGroup(bpy.types.PropertyGroup):
    point: bpy.props.FloatVectorProperty(
        name="Point",
        size=[3],
        subtype='TRANSLATION',
        default=[0, 0, 0]
    )
    normal: bpy.props.FloatVectorProperty(
        name="Normal",
        size=[3],
        subtype='DIRECTION',
        default=[0, 0, 1]
    )
    color: bpy.props.FloatVectorProperty(
        name="Color",
        size=[3],
        subtype='COLOR',
        default=[1, 0, 0]
    )


def add_plane(scene=None, point=None, normal=None, color=None):
    scene = scene if scene is not None else bpy.context.scene
    plane = scene.planes.add()
    plane.point = (Vector([random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)])
                   if point is None else point)
    plane.normal = (Vector([random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)]).normalized()
                    if normal is None else normal)
    random_color = numpy.random.uniform(0, 1, 3)
    random_color = random_color / numpy.linalg.norm(random_color)
    plane.color = random_color if color is None else color


class PlanesList(bpy.types.UIList):
    bl_idname = "UI_UL_PlanesList"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        col = layout.column(align=True)

        row = col.row(align=True).split(factor=0.75, align=True)
        row.label(text=f"Plane {index}:")
        row.prop(item, 'color', text="")

        row = col.row(align=True)
        row.prop(item, 'point', text="")

        row = col.row(align=True)
        row.prop(item, 'normal', text="")

        col.separator(factor=1.0)


class CreatePlaneOperator(bpy.types.Operator):
    bl_label = "Add a plane"
    bl_idname = "assignment2.create_plane_operator"

    @classmethod
    def poll(cls, context):
        return len(context.scene.planes) < 100

    def execute(self, context):
        add_plane(context.scene)
        # plane = context.scene.planes.add()
        # todo: set up the plane with random values
        return {'FINISHED'}


class RemovePlaneOperator(bpy.types.Operator):
    bl_label = "Add a plane"
    bl_idname = "assignment2.remove_plane_operator"

    @classmethod
    def poll(cls, context):
        return len(context.scene.planes) > 0

    def execute(self, context):
        context.scene.planes.remove(context.scene.selected_plane)
        context.scene.selected_plane = min(context.scene.selected_plane, len(context.scene.planes) - 1)
        return {'FINISHED'}


class CreateExamplePlanesOperator(bpy.types.Operator):
    bl_label = "Add a set of planes as a test case"
    bl_idname = "assignment2.create_example_planes_operator"

    def execute(self, context):
        rotation = Quaternion(numpy.random.uniform(0, 1, 4)).normalized()
        transform = Matrix.LocRotScale(
            Vector(numpy.random.uniform(-2, 2, 3)),
            rotation,
            Vector([random.random() * 4] * 3)
        ).normalized()
        add_plane(context.scene, point=transform @ Vector([0, 0, 0]), normal=rotation @ Vector([1, 0, 0]))
        add_plane(context.scene, point=transform @ Vector([2, 0, 0]), normal=rotation @ Vector([1, 0, 0]))
        add_plane(context.scene, point=transform @ Vector([1, -1, 0]), normal=rotation @ Vector([0, 1, 0]))
        add_plane(context.scene, point=transform @ Vector([1, 1, 0]), normal=rotation @ Vector([0, 1, 0]))
        add_plane(context.scene, point=transform @ Vector([1, 0, -1]), normal=rotation @ Vector([0, 0, 1]))
        add_plane(context.scene, point=transform @ Vector([1, 0, 1]), normal=rotation @ Vector([0, 0, 1]))
        return {'FINISHED'}


class MoveToOptimalPositionOperator(bpy.types.Operator):
    bl_label = "Move the cursor to the optimal position"
    bl_idname = "assignment2.move_to_optimal_position_operator"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return len(context.scene.planes) > 1

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        # context.scene.planes.remove(context.scene.selected_plane)
        # context.scene.selected_plane = min(context.scene.selected_plane, len(context.scene.planes) - 1)
        points_with_normals = [(Vector(p.point), Vector(p.normal)) for p in context.scene.planes]
        solver = SquaredDistanceToPlanesSolver(points_with_normals)
        context.scene.cursor.location = solver.optimal_point()
        return {'FINISHED'}


class DistanceToPlanes(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_DistanceToPlanes"
    bl_label = "Distance to Planes"

    bl_category = "Practical 2"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        box = self.layout.box()
        box.label(text="3d Cursor")
        box.row().prop(context.scene.cursor, 'location', text="")
        box.prop(context.scene, 'show_vectors_to_planes')
        box.prop(context.scene, 'cursor_distance_to_planes', text="Cursor Squared Distance")
        box.operator(MoveToOptimalPositionOperator.bl_idname)

        row = self.layout.row()
        row.operator(CreatePlaneOperator.bl_idname, text="", icon='ADD')
        row.operator(RemovePlaneOperator.bl_idname, text="", icon='REMOVE')
        row.operator(CreateExamplePlanesOperator.bl_idname, text="Example")
        row.prop(context.scene, 'show_planes', text="Visible")
        self.layout.template_list('UI_UL_PlanesList', '', context.scene, 'planes', context.scene, 'selected_plane')


class PlanesGizmo(bpy.types.GizmoGroup):
    bl_idname = "OBJECT_GGT_planes"
    bl_label = "Planes Gizmo"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'PERSISTENT'}

    gizmos_for_planes = dict()

    @classmethod
    def poll(cls, context):
        return context.scene.show_planes

    def setup(self, context):
        pass

    def draw_prepare(self, context):

        # Remove gizmos for planes which no longer exist
        for plane in list(self.gizmos_for_planes.keys()):
            if plane not in list(context.scene.planes):
                self.gizmos.remove(self.gizmos_for_planes.pop(plane))

        # Draw all the planes
        for plane in context.scene.planes:

            # Add a gizmo for any plane which doesn't already have one
            if plane not in self.gizmos_for_planes.keys():
                self.gizmos_for_planes[plane] = self.gizmos.new("GIZMO_GT_primitive_3d")

            # Style the gizmo to match the plane
            gizmo = self.gizmos_for_planes[plane]
            gizmo.alpha = 0.8
            gizmo.color = plane.color

            # Move the gizmo to match the plane
            self.gizmos_for_planes[plane].matrix_basis = mathutils.Matrix.LocRotScale(
                plane.point,
                mathutils.Vector([0, 0, 1]).rotation_difference(plane.normal),
                None
            )


class VectorsToPlanesGizmo(bpy.types.GizmoGroup):
    bl_idname = "OBJECT_GGT_vectors_to_planes"
    bl_label = "Vectors to Planes Gizmo"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'PERSISTENT'}

    arrows = dict()
    crosses = dict()

    @classmethod
    def poll(cls, context):
        return context.scene.show_vectors_to_planes

    def setup(self, context):
        pass

    def draw_prepare(self, context):

        # Remove gizmos for planes which no longer exist
        for plane in list(self.arrows.keys()):
            if plane not in list(context.scene.planes):
                self.gizmos.remove(self.arrows.pop(plane))
                self.gizmos.remove(self.crosses.pop(plane))

        # Draw all the vectors
        for plane in context.scene.planes:

            # Add a gizmo for any plane which doesn't already have one
            if plane not in self.arrows.keys():
                self.arrows[plane] = self.gizmos.new("GIZMO_GT_arrow_3d")
                self.crosses[plane] = self.gizmos.new("GIZMO_GT_arrow_3d")

            # Style the arrow to match the plane
            arrow = self.arrows[plane]
            arrow.alpha = 0.4
            arrow.color = plane.color
            arrow.use_draw_offset_scale = True
            arrow.use_draw_scale = False
            arrow.target_set_handler('offset', get=lambda: 0.0, set=lambda v: None)

            cross = self.crosses[plane]
            cross.draw_style = 'CROSS'
            cross.alpha = 0.4
            cross.color = plane.color

            # Move the arrow and cross to connect the 3d cursor to the plane
            cursor_position = context.scene.cursor.location
            vector_to_plane = (plane.point - cursor_position).dot(plane.normal) * plane.normal
            nearest_point_on_plane = cursor_position + vector_to_plane
            arrow.matrix_basis = mathutils.Matrix.LocRotScale(
                nearest_point_on_plane,  # cursor_position,
                mathutils.Vector([0, 0, 1]).rotation_difference(-vector_to_plane.normalized()),
                mathutils.Vector([0.5, 0.5, vector_to_plane.magnitude * 0.8]),
            )
            cross.matrix_basis = mathutils.Matrix.LocRotScale(
                nearest_point_on_plane,
                mathutils.Vector([0, 0, 1]).rotation_difference(-vector_to_plane.normalized()),
                None
            )


def distance_to_planes(pos: mathutils.Vector, planes: list[PlanesPropertyGroup]) -> float:
    points_with_normals = [(Vector(p.point), Vector(p.normal)) for p in planes]
    solver = SquaredDistanceToPlanesSolver(points_with_normals)
    return solver.sum_of_squared_distances(pos)


def register():
    # Global property which enables the visualization
    bpy.types.Scene.show_planes = bpy.props.BoolProperty(
        name="Show planes",
        description="Shows the planes used for task 2",
        default=True,
    )
    bpy.types.Scene.planes = bpy.props.CollectionProperty(
        name="Planes",
        type=PlanesPropertyGroup,
        description="The list of planes used in task 2, defined as points with normals",
    )
    bpy.types.Scene.selected_plane = bpy.props.IntProperty(
        name="Selected Plane",
        description="Index of the currently selected plane"
    )

    bpy.types.Scene.cursor_distance_to_planes = bpy.props.FloatProperty(
        name="Distance Squared to Planes",
        get=lambda scene: distance_to_planes(scene.cursor.location, scene.planes),
        # no `set` -- this property shouldn't be writeable
    )
    bpy.types.Scene.show_vectors_to_planes = bpy.props.BoolProperty(
        name="Show vectors to planes",
        description="Shows the shortest vectors that connect each plane to the 3d cursor",
        default=True,
    )
