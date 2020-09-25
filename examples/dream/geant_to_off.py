import pandas as pd
import numpy as np
from typing import Dict


def g4trap(
    dz: float,
    theta: float,
    phi: float,
    dy1: float,
    dx1: float,
    dx2: float,
    alp1: float,
    dy2: float,
    dx3: float,
    dx4: float,
    alp2: float,
) -> (float, float, float, float, float, float, float, float):
    """
    Ported from GEANT4
    http://www.apc.univ-paris7.fr/~franco/g4doxy/html/G4Trap_8cc-source.html
    http://geant4-userdoc.web.cern.ch/geant4-userdoc/UsersGuides/ForApplicationDeveloper/html/Detector/Geometry/geomSolids.html
    """
    ttheta_cphi = np.tan(theta) * np.cos(phi)
    ttheta_sphi = np.tan(theta) * np.sin(phi)
    talpha1 = np.tan(alp1)
    talpha2 = np.tan(alp2)

    pt_0 = np.array(
        (-dz * ttheta_cphi - dy1 * talpha1 - dx1, -dz * ttheta_sphi - dy1, -dz,)
    )
    pt_1 = np.array(
        (-dz * ttheta_cphi - dy1 * talpha1 + dx1, -dz * ttheta_sphi - dy1, -dz,)
    )
    pt_2 = np.array(
        (-dz * ttheta_cphi + dy1 * talpha1 - dx2, -dz * ttheta_sphi + dy1, -dz,)
    )
    pt_3 = np.array(
        (-dz * ttheta_cphi + dy1 * talpha1 + dx2, -dz * ttheta_sphi + dy1, -dz,)
    )
    pt_4 = np.array(
        (+dz * ttheta_cphi - dy2 * talpha2 - dx3, +dz * ttheta_sphi - dy2, +dz,)
    )
    pt_5 = np.array(
        (+dz * ttheta_cphi - dy2 * talpha2 + dx3, +dz * ttheta_sphi - dy2, +dz,)
    )
    pt_6 = np.array(
        (+dz * ttheta_cphi + dy2 * talpha2 - dx4, +dz * ttheta_sphi + dy2, +dz,)
    )
    pt_7 = np.array(
        (+dz * ttheta_cphi + dy2 * talpha2 + dx4, +dz * ttheta_sphi + dy2, +dz,)
    )
    return pt_0, pt_1, pt_2, pt_3, pt_4, pt_5, pt_6, pt_7


def create_winding_order(
    number_of_voxels: int, vertices_in_voxel: int, vertices_in_each_face: int
) -> pd.DataFrame:
    index_0 = []
    index_1 = []
    index_2 = []
    index_3 = []
    for voxel in range(number_of_voxels):
        start_index = voxel * vertices_in_voxel
        index_0.extend(
            [
                start_index,
                start_index,
                start_index,
                start_index + 1,
                start_index + 2,
                start_index + 4,
            ]
        )
        index_1.extend(
            [
                start_index + 2,
                start_index + 4,
                start_index + 1,
                start_index + 3,
                start_index + 6,
                start_index + 5,
            ]
        )
        index_2.extend(
            [
                start_index + 3,
                start_index + 6,
                start_index + 5,
                start_index + 7,
                start_index + 7,
                start_index + 7,
            ]
        )
        index_3.extend(
            [
                start_index + 1,
                start_index + 2,
                start_index + 4,
                start_index + 5,
                start_index + 3,
                start_index + 6,
            ]
        )

    data = np.column_stack(
        (vertices_in_each_face, index_0, index_1, index_2, index_3,)
    ).astype(np.int32)
    return pd.DataFrame(data)


def write_to_file(
    filename: str,
    number_of_vertices: int,
    number_of_faces: int,
    vertices: pd.DataFrame,
    voxels: pd.DataFrame,
):
    with open(filename, "w") as f:
        f.writelines(
            (
                "OFF\n",
                "# DREAM End-Cap Sector 3\n",
                f"{number_of_vertices} {number_of_faces} 0\n",
            )
        )
    with open(filename, "a") as f:
        vertices.to_csv(f, sep=" ", header=None, index=False)
    with open(filename, "a") as f:
        voxels.to_csv(f, sep=" ", header=None, index=False)


def rotate_around_x(angle_degrees: float, vertex: np.ndarray) -> np.ndarray:
    angle = np.deg2rad(angle_degrees)
    rotation_matrix = np.array(
        [
            [1, 0, 0],
            [0, np.cos(angle), -np.sin(angle)],
            [0, np.sin(angle), np.cos(angle)],
        ]
    )
    return rotation_matrix.dot(vertex)


def rotate_around_y(angle_degrees: float, vertex: np.ndarray) -> np.ndarray:
    angle = np.deg2rad(angle_degrees)
    rotation_matrix = np.array(
        [
            [np.cos(angle), 0, np.sin(angle)],
            [0, 1, 0],
            [-np.sin(angle), 0, np.cos(angle)],
        ]
    )
    return rotation_matrix.dot(vertex)


def rotate_around_z(angle_degrees: float, vertex: np.ndarray) -> np.ndarray:
    angle = np.deg2rad(angle_degrees)
    rotation_matrix = np.array(
        [
            [np.cos(angle), -np.sin(angle), 0],
            [np.sin(angle), np.cos(angle), 0],
            [0, 0, 1],
        ]
    )
    return rotation_matrix.dot(vertex)


# TODO these numbers are approximate, check with Irina what they should be
sumo_number_to_angle: Dict[int, float] = {3: 10.0, 4: 17.0, 5: 23.0, 6: 29.0}
sumo_number_to_translation: Dict[int, np.ndarray] = {
    3: np.array([0, 410, -1300.0]),
    4: np.array([0, 590, -1310.0]),
    5: np.array([0, 780, -1325.0]),
    6: np.array([0, 1000, -1350.0]),
}


if __name__ == "__main__":
    df = pd.read_csv(
        "LookupTableDreamEndCap_noRRT.txt", delim_whitespace=True, header=None
    )
    df.columns = [
        "sumo",
        "sect-seg",
        "strip",
        "wire",
        "counter",
        "x_centre",
        "y_centre",
        "z_centre",
        "x1",
        "x2",
        "y1",
        "y2",
        "z",
    ]

    print(df)

    number_of_voxels = len(df.index)
    vertices_in_voxel = 8
    faces_in_voxel = 6
    number_of_vertices = vertices_in_voxel * number_of_voxels
    number_of_faces = faces_in_voxel * number_of_voxels

    x_coords = np.zeros(number_of_vertices)
    y_coords = np.zeros(number_of_vertices)
    z_coords = np.zeros(number_of_vertices)

    for voxel in range(number_of_voxels):
        sector_number = np.floor(df["sect-seg"][voxel] / 100)
        segment_number = df["sect-seg"][voxel] % 100

        voxel_vertices = g4trap(
            df["z"][voxel] / 2,
            0.0,
            0.0,
            df["y2"][voxel] / 2,
            df["x1"][voxel] / 2,
            df["x1"][voxel] / 2,
            0.0,
            df["y1"][voxel] / 2,
            df["x2"][voxel] / 2,
            df["x2"][voxel] / 2,
            0.0,
        )

        # Translate to centre
        voxel_position = np.array(
            [df["x_centre"][voxel], df["y_centre"][voxel], df["z_centre"][voxel]]
        )

        for vert_number, vertex in enumerate(voxel_vertices):
            # Translate voxel to position in SUMO
            vertex += voxel_position

            # Rotate 10 degrees around y
            # This means the SUMO doesn't face the sample, and is done to
            # increase efficiency of the detector
            vertex = rotate_around_y(-10, vertex)

            sumo_number = df["sumo"][voxel]
            vertex = rotate_around_x(sumo_number_to_angle[sumo_number], vertex)
            vertex += sumo_number_to_translation[sumo_number]

            x_coords[voxel * vertices_in_voxel + vert_number] = vertex[0]
            y_coords[voxel * vertices_in_voxel + vert_number] = vertex[1]
            z_coords[voxel * vertices_in_voxel + vert_number] = vertex[2]

    coords = np.column_stack((x_coords, y_coords, z_coords))
    vertices = pd.DataFrame(coords)

    # Vertices making up each face of each voxel
    number_of_faces = faces_in_voxel * number_of_voxels
    vertices_in_each_face = 4 * np.ones(number_of_faces)
    vertex_indices = np.arange(0, number_of_voxels * 8, 8)

    voxels = create_winding_order(
        number_of_voxels, vertices_in_voxel, vertices_in_each_face
    )

    write_to_file(
        "DREAM_endCap_sector.off",
        number_of_vertices,
        number_of_faces,
        vertices,
        voxels,
    )