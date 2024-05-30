import unittest
import numpy as np
import numpy.random
from mathutils import Matrix, Vector
from .distance_to_planes import SquaredDistanceToPlanesSolver


class TestDistanceToPlanes(unittest.TestCase):

    # HINT: Add your own unit tests here

    # HINT: CreateExamplePlanesOperator in __init__.py contains code which creates a 'cube' of planes,
    #       This could be adapted into a nice test case, because the optimal point will always be in the middle.

    def test_one_plane(self):
        # Create a horizontal plane which is the same as the XY plane
        plane = (Vector([0, 0, 0]), Vector([0, 0, 1]))

        # Create a solver for distances from this plane
        solver = SquaredDistanceToPlanesSolver([plane])

        # Any point's distance to the plane should be equal to its height squared
        for _ in range(100):
            point = Vector(numpy.random.uniform(-100, 100, 3))

            self.assertEqual(
                solver.sum_of_squared_distances(point), point.z ** 2,
                "Distance squared from the XY plane should be equal to z^2"
            )

        # The optimal point should lie somewhere on this plane (z=0)
        # TODO: For a single plane, solving occasionally encounters singular matrices and fails
        #       If you implement tests with more planes, you can check your implementation like this:
        # self.assertEqual(
        #     solver.optimal_point().z, 0,
        #     "The optimal point for the XY plane should lie somewhere on that plane"
        # )
