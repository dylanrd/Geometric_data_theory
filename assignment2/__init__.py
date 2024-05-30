import bpy

from .smoothing import *
from .rotation import *
from .planes import *

bl_info = {
    "name": "GDP Practical Assignment 2",
    "author": "Add your names here!",
    "description": "A student implementation of Geometric Data Processing practical assignment 2.",
    "blender": (4, 0, 2),
    "version": (0, 0, 1),
    "location": "View3D",
    "warning": "",
    "category": "Mesh"
}

classes = [
    AxisOfRotation,
    AxisOfRotationGizmo,

    PlanesPropertyGroup,
    PlanesList,
    CreatePlaneOperator,
    RemovePlaneOperator,
    CreateExamplePlanesOperator,
    DistanceToPlanes,
    MoveToOptimalPositionOperator,
    PlanesGizmo,
    VectorsToPlanesGizmo,

    ExplicitLaplaceSmoothing,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.VIEW3D_MT_object.append(ExplicitLaplaceSmoothing.menu_func)

    rotation.register()
    planes.register()


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
