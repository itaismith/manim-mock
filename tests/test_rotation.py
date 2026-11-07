import numpy as np

from manimlib.animation.rotation import Rotate
from manimlib.animation.rotation import Rotating
from manimlib.constants import BLUE, LEFT, ORIGIN, PI, RED, RIGHT
from manimlib.mobject.geometry import Arrow
from manimlib.mobject.geometry import Square


def play_through(animation, read_box_between_frames: bool) -> None:
    animation.begin()
    for alpha in np.linspace(0, 1, 9):
        animation.interpolate(alpha)
        if read_box_between_frames:
            # As an updater tracking the mobject's center would
            animation.mobject.get_center()
    animation.finish()


def test_rotate_about_edge_ignores_box_read_between_frames():
    for read in (False, True):
        arrow = Arrow(ORIGIN, 2 * RIGHT, buff=0)
        expected = arrow.copy().rotate(PI / 2, about_edge=LEFT)
        play_through(Rotate(arrow, PI / 2, about_edge=LEFT), read)
        np.testing.assert_allclose(arrow.get_points(), expected.get_points(), atol=1e-6)
        np.testing.assert_allclose(arrow.get_center(), expected.get_center(), atol=1e-6)


def test_rotating_does_not_compound_gradient_rotation():
    square = Square().set_color([BLUE, RED])
    expected = square.copy().rotate(PI / 2, about_point=ORIGIN)
    play_through(Rotating(square, PI / 2, about_point=ORIGIN, run_time=1), False)
    for key in square.pointlike_uniform_keys:
        np.testing.assert_allclose(square.uniforms[key], expected.uniforms[key], atol=1e-6)


def test_rotating_survives_removing_an_empty_child():
    from manimlib.mobject.types.vectorized_mobject import VGroup
    empty = VGroup()
    group = VGroup(empty, Square(), Square().shift(RIGHT))
    animation = Rotating(group, PI / 2, about_point=ORIGIN, run_time=1)
    animation.begin()
    animation.interpolate(0.25)
    group.remove(empty)
    animation.interpolate(0.5)


def test_rotating_does_not_compound_group_gradient_rotation():
    from manimlib.mobject.types.vectorized_mobject import VGroup
    group = VGroup(Square(), Square().shift(2 * RIGHT)).set_color([BLUE, RED])
    expected = group.copy().rotate(PI / 2, about_point=ORIGIN)
    play_through(Rotating(group, PI / 2, about_point=ORIGIN, run_time=1), False)
    for key in group.pointlike_uniform_keys:
        np.testing.assert_allclose(group.uniforms[key], expected.uniforms[key], atol=1e-6)
