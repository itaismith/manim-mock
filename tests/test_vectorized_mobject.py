import numpy as np

from manimlib.constants import OUT, PI
from manimlib.mobject.geometry import Square
from manimlib.mobject.types.vectorized_mobject import DashedVMobject


def test_subcurve_starting_with_null_curves_faces_out():
    # Past the first side, get_subcurve pads the start with repeated points
    subcurve = Square().get_subcurve(0.25, 0.5)

    np.testing.assert_allclose(subcurve.get_unit_normal(refresh=True), OUT)


def test_dashes_keep_facing_out_after_rotation():
    dashed = DashedVMobject(Square()).rotate(PI / 4)

    for dash in dashed:
        np.testing.assert_allclose(dash.get_unit_normal(), OUT, atol=1e-6)
