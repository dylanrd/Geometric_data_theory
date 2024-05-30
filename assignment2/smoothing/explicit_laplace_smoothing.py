import numpy
import numpy as np
from scipy.sparse import coo_array, eye_array, sparray

import bpy
import bmesh


def numpy_verts(mesh: bmesh.types.BMesh) -> np.ndarray:
    """
    Extracts a numpy array of (x, y, z) vertices from a blender mesh

    :param mesh: The BMesh to extract the vertices of.
    :return: A numpy array of shape [n, 3], where array[i, :] is the x, y, z coordinate of vertex i.
    """
    data = bpy.data.meshes.new('tmp')
    mesh.to_mesh(data)
    # Explained here:
    # https://blog.michelanders.nl/2016/02/copying-vertices-to-numpy-arrays-in_4.html
    vertices = np.zeros(len(mesh.verts) * 3, dtype=np.float64)
    data.vertices.foreach_get('co', vertices)
    return vertices.reshape([len(mesh.verts), 3])


def set_verts(mesh: bmesh.types.BMesh, verts: np.ndarray) -> bmesh.types.BMesh:
    data = bpy.data.meshes.new('tmp1')  # temp Blender Mesh to perform fast setting
    mesh.to_mesh(data)
    data.vertices.foreach_set('co', verts.ravel())
    mesh.clear()
    mesh.from_mesh(data)
    return mesh


# HINT: This is a helper method which you can change (for example, if you want to try different sparse formats)
def adjacency_matrix(mesh: bmesh.types.BMesh) -> coo_array:
    """
    Computes the adjacency matrix of a mesh.

    Computes the adjacency matrix of the given mesh.
    Uses a sparse data structure to represent the matrix,
    which is more efficient for operations like matrix multiplication.

    :param mesh: Mesh to compute the adjacency matrix of.
    :return: A sparse matrix representing the mesh adjacency matrix.
    """
    # HINT: Iterating over mesh.edges is significantly faster than iterating over mesh.verts and getting neighbors!
    #       Building a sparse matrix from a set of I, J, V triplets is also faster than adding elements sequentially.
    # TODO: Create a sparse adjacency matrix using one of the types from scipy.sparse
    num_verts = len(mesh.verts)
    return coo_array(([], ([], [])), shape=(num_verts, num_verts))


# !!! This function will be used for automatic grading, don't edit the signature !!!
def build_combinatorial_laplacian(mesh: bmesh.types.BMesh) -> sparray:
    """
    Computes the normalized combinatorial Laplacian the given mesh.

    First, the adjacency matrix is computed efficiently using the edge_matrix function.
    Then the normalized Laplacian is calculated using the sparse operations: L = I-A/D
    where I is the identity and D the degree matrix.
    The resulting mesh should have the following properties:
        - L_ii = 1
        - L_ij = 1 / deg_i (if an edge exists between i and j)
        - L_ij = 0 (if such an edge does not exist)
    Where deg_i is the degree of node i (its number of edges).

    :param mesh: Mesh to compute the normalized combinatorial Laplacian matrix of.
    :return: A sparse array representing the mesh Laplacian matrix.
    """
    # TODO: Build the combinatorial laplacian matrix
    num_verts = len(mesh.verts)
    return eye_array(num_verts)


# !!! This function will be used for automatic grading, don't edit the signature !!!
def explicit_laplace_smooth(
        vertices: np.ndarray,
        L: coo_array,
        tau: float,
) -> np.ndarray:
    """
    Performs smoothing of a list of vertices given a combinatorial Laplace matrix and a weight Tau.

    Updates are computed using the laplacian matrix and then weighted by Tau before subtracting from the vertices.

        x = x + tau * L @ x

    :param vertices: Vertices to apply offsets to as an Nx3 numpy array.
    :param L: The NxN sparse laplacian matrix
    :param tau: Update weight, tau=0 leaves the vertices unchanged, and tau=1 applies the full update.
    :return: The new positions of the vertices as an Nx3 numpy array.
    """
    # TODO: Update the vertices using the combinatorial laplacian matrix L

    return vertices


# !!! This function will be used for automatic grading, don't edit the signature !!!
def iterative_explicit_laplace_smooth(
        mesh: bmesh.types.BMesh,
        tau: float,
        iterations: int
) -> bmesh.types.BMesh:
    """
    Performs smoothing of a given mesh using the iterative explicit Laplace smoothing.

    First, we define the coordinate vectors and the combinatorial Laplace matrix as numpy arrays.
    Then, we apply the smoothing operation as many times as iterations. 
    We weight the updating vector in each iteration by tau.

    :param mesh: Mesh to smooth.
    :param tau: Update weight.
    :param iterations: Number of smoothing iterations to perform.
    :return: A mesh with the updated coordinates after smoothing.
    """

    # Get coordinate vectors as numpy arrays
    X = numpy_verts(mesh)

    # Compute combinatorial Laplace matrix
    L = build_combinatorial_laplacian(mesh)

    # Perform smoothing operations
    for _ in range(iterations):
        X = explicit_laplace_smooth(X, L, tau)

    # Write smoothed vertices back to output mesh
    set_verts(mesh, X)

    return mesh
