import unittest

import numpy as np

from manimlib.mobject.coordinate_systems import Axes
from manimlib.mobject.coordinate_systems import CoordinateSystem
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.simple_functions import binary_search


class StubCoordinateSystem(CoordinateSystem):
    def coords_to_point(self, *coords):
        return np.array([coords[0], coords[1], 0.0])

    def point_to_coords(self, point):
        return tuple(point[:2])

    def get_axes(self):
        return []

    def get_all_ranges(self):
        return []


class LineGraph:
    def quick_point_from_proportion(self, alpha):
        return np.array([2.0 + 4.0 * alpha, 3.0, 0.0])


class CoordinateSystemTests(unittest.TestCase):
    def test_binary_search_returns_input_at_endpoints(self):
        def function(value):
            return 2.0 + 4.0 * value

        self.assertEqual(binary_search(function, 2.0, 0.0, 1.0), 0.0)
        self.assertEqual(binary_search(function, 6.0, 0.0, 1.0), 1.0)

    def test_input_to_graph_point_searches_curve_proportion(self):
        axes = StubCoordinateSystem(x_range=(2.0, 6.0, 1.0), y_range=(0.0, 5.0, 1.0))
        graph = LineGraph()

        np.testing.assert_allclose(
            axes.input_to_graph_point(2.0, graph), [2.0, 3.0, 0.0]
        )
        np.testing.assert_allclose(
            axes.input_to_graph_point(4.0, graph), [4.0, 3.0, 0.0]
        )
        np.testing.assert_allclose(
            axes.input_to_graph_point(6.0, graph), [6.0, 3.0, 0.0]
        )

    def _bound_step_graph(self, get_discontinuities, func=np.sign):
        axes = Axes(x_range=(-4.0, 4.0, 1.0), y_range=(-2.0, 2.0, 1.0))
        graph = axes.get_graph(func)
        axes.bind_graph_to_func(graph, func, get_discontinuities=get_discontinuities)
        return axes, graph

    def test_bound_graph_with_discontinuities_keeps_its_x_range(self):
        axes, graph = self._bound_step_graph(lambda: [0.0])
        for _ in range(10):
            graph.update(1 / 30)
            xs = axes.x_axis.p2n(graph.get_points())
            np.testing.assert_allclose([xs.min(), xs.max()], [-4.0, 4.0], atol=1e-5)

    def test_bound_graph_updates_are_idempotent(self):
        axes, graph = self._bound_step_graph(lambda: [0.0])
        points = graph.get_points().copy()
        for _ in range(3):
            graph.update(1 / 30)
            np.testing.assert_allclose(graph.get_points(), points)

    def test_bound_graph_draws_the_jump_at_the_discontinuity(self):
        axes, graph = self._bound_step_graph(lambda: [0.33], lambda x: np.sign(x - 0.33))
        xs, ys = axes.p2c(graph.get_anchors())
        jump = np.argmax(np.abs(np.diff(ys)))
        self.assertAlmostEqual(xs[jump], 0.33, places=5)
        self.assertAlmostEqual(xs[jump + 1], 0.33, places=5)

    def test_bound_graph_point_count_is_independent_of_discontinuities(self):
        jumps = []
        axes, graph = self._bound_step_graph(lambda: jumps)
        num_points = graph.get_num_points()
        for new_jumps in [[], [0.0], [-1.0, 1.0], [6.0], [-6.0, 0.5, 2.5], [-4.0, 4.0], []]:
            jumps[:] = new_jumps
            graph.update()
            self.assertEqual(graph.get_num_points(), num_points)
            xs = axes.x_axis.p2n(graph.get_points())
            np.testing.assert_allclose([xs.min(), xs.max()], [-4.0, 4.0], atol=1e-5)

    def test_binding_an_empty_graph(self):
        graph = Axes().bind_graph_to_func(VMobject(), np.sin, get_discontinuities=lambda: [0.0])
        graph.update()
        self.assertEqual(graph.get_num_points(), 0)


if __name__ == "__main__":
    unittest.main()
