import mathutils

from .explicit_laplace_smoothing import *
from .test import *

import bpy
import bmesh


class ExplicitLaplaceSmoothing(bpy.types.Operator):
    bl_idname = "object.explicit_laplace_smoothing"
    bl_label = "Mesh Smoothing with Combinatorial Laplace Coordinates"
    bl_options = {'REGISTER', 'UNDO'}

    # Input parameters
    tau: bpy.props.FloatProperty(
        name="ε", description="Minimum distance, below which the mesh is considered converged",
        min=0.0, step=0.01, max=1.0, default=0.15
    )
    iterations: bpy.props.IntProperty(
        name="Iterations", description="Maximum number of iterations",
        min=1, max=200, default=5
    )

    # Output parameters
    status: bpy.props.StringProperty(
        name="Smoothing Status", default="Status not set"
    )

    @classmethod
    def poll(self, context):
        # Explicit Laplace Smoothing is only available when a mesh is selected
        return (
                context.view_layer.objects.active is not None
                and context.view_layer.objects.active.type == 'MESH'
        )

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):

        active_object = context.view_layer.objects.active

        # Produce BMesh types to work with
        active = bmesh.new()
        active.from_mesh(active_object.data)

        # Smooth active mesh
        try:
            smoothed_mesh = iterative_explicit_laplace_smooth(
                active,
                self.tau,
                self.iterations)
        except Exception as error:
            self.report({'WARNING'}, f"Explicit Laplace Smoothing failed with error '{error}'")
            return {'CANCELLED'}

        self.status = (f"Applied {self.iterations} iterations (ε={self.tau:.2f})")

        # Update mesh with smoothed data
        smoothed_mesh.to_mesh(active_object.data)
        active_object.data.update()


        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        # Object selection
        row = layout.row(align=True)
        row.label(text="Object to smooth: ")
        row.separator()
        row.prop(context.view_layer.objects, 'active', text="", expand=True, emboss=False)
        layout.separator()

        # Convergence parameters
        layout.prop(self, 'iterations')
        layout.prop(self, 'tau')

        layout.prop(self, 'status', text="Status", emboss=False)

    @staticmethod
    def menu_func(menu, context):
        menu.layout.operator(ExplicitLaplaceSmoothing.bl_idname)
