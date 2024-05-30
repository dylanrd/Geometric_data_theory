import math
from typing import Optional

import numpy
from mathutils import Matrix, Vector


# !!! This function will be used for automatic grading, don't edit the signature !!!
def rotation_component(transformation: Matrix) -> Matrix:
    """
    Finds the rotation component of an affine transformation matrix.

    The input matrix may contain translation and scaling components, but will not contain shear.

    :param transformation: A 4x4 affine transformation matrix.
    :return: The 3x3 rotation matrix implied by this transformation.
    """

    # Converting to numpy may make some of your math more convenient!
    transformation = numpy.array(transformation)

    # HINT: The translation is contained entirely in the 4th column, so it will be dropped when you make the matrix 3x3

    # TODO: This should extract the 3x3 rotation matrix from the 4x4 input
    return Matrix(transformation[:3, :3])


# !!! This function will be used for automatic grading, don't edit the signature !!!
def axis_of_rotation(transformation: Matrix) -> Vector:
    """
    Finds the axis of rotation for a transformation matrix.

    NOTE: the use of `transformation.to_quaternion().axis` or equivalent functionality is not permitted!
          This task is intended to be completed manually, using techniques discussed in class.

    :param transformation: The 3x3 transformation matrix for which to find the axis of rotation.
    """
    # TODO: This should return the axis of rotation
    return Vector([0, 0, 1])


# !!! This function will be used for automatic grading, don't edit the signature !!!
def angle_of_rotation(transformation: Matrix) -> float:
    """
    Finds the angle of rotation for a transformation matrix.

    NOTE: the use of `transformation.to_quaternion().angle` or equivalent functionality is not permitted!
          This task is intended to be completed manually, using techniques discussed in class.

    :param transformation: The 3x3 transformation matrix for which to find the angle of rotation.
    :return: The angle of rotation in radians.
    """
    # TODO: This should return the angle of rotation
    return math.pi
