import numpy as np
import pytest

from manimlib.mobject.geometry import Arc
from manimlib.utils.space_ops import rotation_matrix


@pytest.mark.parametrize("angle,axis", [
    (0, [0, 0, 1]),
    (1.0, [1, 2, 0.5]),
    (np.pi / 2, [1, 0, 0]),
])
def test_arc_center_after_rotation(angle, axis):
    center = np.array([0.5, 0.2, 0.0])
    arc = Arc(start_angle=0.3, angle=2.0, radius=1.5, arc_center=center)
    matrix = rotation_matrix(angle, np.array(axis, dtype=float))
    arc.apply_matrix(matrix)

    np.testing.assert_allclose(arc.get_arc_center(), matrix @ center, atol=1e-5)
