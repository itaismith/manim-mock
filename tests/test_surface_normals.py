import numpy as np
import pytest

from manimlib.constants import OUT
from manimlib.constants import PI
from manimlib.mobject.three_dimensions import Cone
from manimlib.mobject.three_dimensions import Disk3D
from manimlib.mobject.three_dimensions import Sphere


# Each of these has a row or column of its grid collapsed to a single point: the center of a
# disk, the poles of a sphere, the tip of a cone. That is where a normal worked out from the
# step to a neighbor along that row came out as zero, and the surface was drawn black there.
SINGULAR_SURFACES = {
    "quarter disk": lambda: Disk3D(v_range=(PI, 1.5 * PI), radius=0.3),
    "disk": lambda: Disk3D(),
    "disk, finer radially": lambda: Disk3D(resolution=(10, 100)),
    "sphere": lambda: Sphere(),
    "coarse sphere": lambda: Sphere(resolution=(4, 4)),
    "cone": lambda: Cone(),
}


@pytest.mark.parametrize("make_surface", SINGULAR_SURFACES.values(), ids=SINGULAR_SURFACES.keys())
def test_unit_normals_are_unit_at_singular_points(make_surface):
    normals = make_surface().get_unit_normals()

    assert np.isfinite(normals).all()
    np.testing.assert_allclose(np.linalg.norm(normals, axis=1), 1.0, atol=1e-6)


def test_disk_faces_out_at_its_center():
    disk = Disk3D(v_range=(PI, 1.5 * PI))
    nu, nv = disk.get_resolution()
    normals = disk.get_unit_normals().reshape((nu, nv, 3))

    np.testing.assert_allclose(normals[0], np.tile(OUT, (nv, 1)), atol=1e-6)
    np.testing.assert_allclose(normals, np.tile(OUT, (nu, nv, 1)), atol=1e-6)


def test_sphere_faces_away_from_its_center_at_the_poles():
    sphere = Sphere(resolution=(11, 11))
    nu, nv = sphere.get_resolution()
    points = sphere.get_points().reshape((nu, nv, 3))
    normals = sphere.get_unit_normals().reshape((nu, nv, 3))

    radial = points / np.linalg.norm(points, axis=-1, keepdims=True)
    alignment = (normals * radial).sum(axis=-1)
    assert (alignment[:, [0, -1]] > 0.9).all()
