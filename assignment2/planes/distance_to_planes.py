from functools import cache
import numpy as np
import numpy.random
from mathutils import Vector, Matrix


class SquaredDistanceToPlanesSolver(object):
    """
    A solver type for computing and minimizing the sum of squared distances to a set of planes.
    """

    # !!! This function will be used for automatic grading, don't edit the signature !!!
    def __init__(self, planes: list[tuple[Vector, Vector]]):
        """
        Prepares the solver to perform squared-distances-to-planes calculations for a given set of planes.

        In order for the distance() and optimal_point() methods to run in constant time,
        pre-processing must be done in __init__()!

        :param planes: The set of planes to use in future calculations.
                       Each plane is represented as a tuple of a point and a normal.
                       The input for a trio of planes would be:
                       ```
                          [(q_0, n_0), (q_1, n_1), (q_2, n_2)]
                       ```
                       Where `q_i` and `n_i` are the point and the normal for plane_i, respectively.
        """

        # HINT: You'll want to save some precomputed results for best performance.
        #       Saving the list of planes directly and iterating over them in your distance() method will work,
        #       but it won't get full points.
        # print(planes[0])
        self.A = np.array(np.zeros((3, 3)))
        self.b = np.array(np.zeros((3, 1)))
        self.c = 0.0
        for i in range(len(planes)):
            curr_plane = planes[i]
            n = np.array([curr_plane[1]])
            q = np.array([curr_plane[0]])

            self.A += n.T @ n

            self.b += -(n.T @ n @ q.T)
            # print("N = ", q.T, q.T ** 2)
            self.c += (n @ q.T) ** 2

        self.planes = planes

    # !!! This function will be used for automatic grading, don't edit the signature !!!
    def sum_of_squared_distances(self, point: Vector) -> float:
        """
        Computes the sum of squared distances between a given point and each plane.

        If `distance(point, plane_i)` gives the distance between the point and the nearest point on plane_i,
        then this function should be equivalent to:
        ```
            sum(distance(point, plane)**2 for plane in planes)
        ```

        :param point: The point to find distance for.
        :return: The sum of squared distances between the point and all planes, as a float.
        """

        # numpy isn't strictly necessary here, but its features can make things easier.
        p = numpy.array([point])
        sum = 0
        for plane in self.planes:
            q = np.array([plane[0]])
            n = np.array([plane[1]])
            # print((n @ (p - q).T), (n @ (p - q).T)**2)
            sum += (n @ (p - q).T) ** 2
        # HINT: Consider the equation for the squared distance between a point and a plane.
        #       Can you identify the parts which depend on the point and the parts which depend on each plane?
        print("SUMMMMM", sum)
        # print("PPP", p)
        # print("AAAAAAAA", self.A)
        # print("BBBBBB", self.b.T)
        #
        # print("CCCCCC", self.c)

        quadratic = 0.5 * (p @ self.A @ p.T) + p @ self.b + self.c

        print("QUADRATIC", quadratic)
        return sum

    # !!! This function will be used for automatic grading, don't edit the signature !!!
    def optimal_point(self) -> Vector:
        """
        Finds a point which minimizes the sum of squared distances to all planes.

        This function is not always deterministic!
        For example, with two (non-parallel) planes any point along the line defined by their intersection is optimal.
        The important thing is that the point returned corresponds to the smallest possible sum of squared distances.
        i.e. `solver.distance(solver.optimal_point())` <= `solver.distance({any other point})`.

        :return: A point which minimizes the sum of squared distances.
        """

        # HINT: numpy.linalg.solve() will come in handy here!

        res = np.linalg.solve(self.A, -self.b)
        return Vector(res)
