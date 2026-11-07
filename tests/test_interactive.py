import unittest
from typing import Any, cast

import numpy as np

from manimlib.constants import BLUE, PURPLE, RIGHT, UP
from manimlib.camera.camera_frame import CameraFrame
from manimlib.event_handler import EVENT_DISPATCHER
from manimlib.event_handler.event_dispatcher import EventDispatcher
from manimlib.event_keys import Mods
from manimlib.mobject.geometry import Circle, Rectangle
from manimlib.mobject.interactive import LinearNumberSlider, ParameterSlider
from manimlib.mobject.mobject import Group, Point
from manimlib.mobject.value_tracker import ValueTracker
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.scene.interactive_scene import InteractiveScene
from manimlib.scene.scene import Scene


class InteractiveHistoryTests(unittest.TestCase):
    def test_keyboard_redo_restores_clip_plane_edit(self):
        for command in (Mods.CTRL, Mods.CMD):
            with self.subTest(command=command):
                scene = Scene.__new__(Scene)
                scene.time = 0
                scene.num_plays = 0
                scene.undo_stack = []
                scene.redo_stack = []
                disk = Circle().set_fill(BLUE, 1).set_clip_plane(RIGHT, 0)
                scene.mobjects = [disk]
                scene.save_state()
                disk.set_fill(PURPLE, 1).set_clip_plane(UP, 0)
                edited = disk.copy()

                scene.on_key_press(ord("z"), command)
                np.testing.assert_array_equal(disk.uniforms["clip_plane0"], [1, 0, 0, 0])
                scene.on_key_press(ord("z"), command | Mods.SHIFT)
                self.assertTrue(disk.looks_identical(edited))

    def test_shift_z_without_command_does_not_touch_history(self):
        scene = Scene.__new__(Scene)
        scene.undo_stack = []
        scene.redo_stack = [object()]
        scene.on_key_press(ord("z"), Mods.SHIFT)
        self.assertEqual(len(scene.redo_stack), 1)

    def test_scene_state_does_not_reuse_changed_tracker_value(self):
        scene = Scene.__new__(Scene)
        scene.time = scene.num_plays = 0
        scene.undo_stack = []
        scene.redo_stack = []
        tracker = ValueTracker(1)
        scene.mobjects = [tracker]
        scene.save_state()
        tracker.set_value(2)
        scene.save_state()
        tracker.set_value(3)
        scene.undo()
        self.assertEqual(tracker.get_value(), 2)
        scene.undo()
        self.assertEqual(tracker.get_value(), 1)

    def test_grouped_tracker_snapshots_keep_distinct_values(self):
        scene = Scene.__new__(Scene)
        scene.time = scene.num_plays = 0
        scene.undo_stack = []
        scene.redo_stack = []
        tracker = ValueTracker(1)
        scene.mobjects = [Group(Group(tracker))]
        scene.save_state()
        tracker.set_value(2)
        scene.save_state()
        tracker.set_value(3)
        scene.undo()
        self.assertEqual(tracker.get_value(), 2)
        scene.undo()
        self.assertEqual(tracker.get_value(), 1)
        scene.redo()
        self.assertEqual(tracker.get_value(), 2)


class ParameterSliderTests(unittest.TestCase):
    def setUp(self):
        self.listeners = {key: list(value) for key, value in EVENT_DISPATCHER.event_listners.items()}

    def tearDown(self):
        EVENT_DISPATCHER.event_listners = self.listeners
        EVENT_DISPATCHER.draggable_object_listners = []

    def test_initial_thumb_and_programmatic_value(self):
        slider = ParameterSlider("cut", min_value=-1, max_value=1, value=-1, step=0.1)
        np.testing.assert_allclose(slider.slider.get_center(), slider.slider_axis.get_start())
        slider.set_value(0.5)
        self.assertEqual(slider.readout.get_value(), 0.5)
        np.testing.assert_allclose(slider.slider.get_center(), slider.slider_axis.point_from_proportion(0.75))
        self.assertTrue(all(mob.is_fixed_in_frame() for mob in slider.get_family()))

    def test_nearest_step_clamping_continuous_and_nondivisible_endpoint(self):
        slider = LinearNumberSlider(min_value=-1, max_value=1.1, step=0.3)
        point = slider.slider_axis.point_from_proportion(0.4)
        self.assertAlmostEqual(slider.get_value_from_point(point), -0.1)
        self.assertEqual(slider.get_value_from_point(np.array([10, 0, 0])), 1.1)
        self.assertEqual(slider.get_value_from_point(np.array([-10, 0, 0])), -1)
        slider.step = None
        self.assertAlmostEqual(slider.get_value_from_point(point), -0.16)

    def test_invalid_ranges_steps_and_values(self):
        kwargs: dict[str, Any]
        for kwargs in ({"min_value": 1, "max_value": 1}, {"step": 0}, {"step": -1},
                       {"step": np.nan}, {"max_value": np.inf}, {"value": np.nan}, {"value": 100}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                LinearNumberSlider(**kwargs)

    def make_scene(self, slider, scene_type=Scene):
        scene = scene_type.__new__(scene_type)
        scene.frame = CameraFrame().scale(0.8).reorient(25, 40).shift(RIGHT)
        scene.mobjects = [scene.frame, slider]
        scene.mouse_drag_point = Point()
        scene.time = scene.num_plays = 0
        scene.undo_stack = []
        scene.redo_stack = []
        return scene

    def test_fixed_slider_click_and_drag_after_orbit_does_not_pan(self):
        slider = ParameterSlider("cut", min_value=-1, max_value=1, value=0, step=0.1)
        scene = self.make_scene(slider)
        start = scene.frame.from_fixed_frame_point(slider.slider_axis.get_start())
        end = scene.frame.from_fixed_frame_point(slider.slider_axis.get_end())
        before = scene.frame.copy()
        # No prior motion event: the click itself must supply the hit-test point.
        scene.on_mouse_press(start, 1, 0)
        self.assertEqual(slider.get_value(), -1)
        scene.on_mouse_drag(end, end - start, [1], 0)
        self.assertAlmostEqual(slider.get_value(), 1)
        self.assertTrue(before.looks_identical(scene.frame))
        scene.on_mouse_release(end, 1, 0)
        scene.undo()
        slider.update()
        self.assertEqual(slider.get_value(), 0)
        self.assertEqual(slider.readout.get_value(), 0)
        scene.redo()
        slider.update()
        self.assertEqual(slider.readout.get_value(), 1)

    def test_removed_slider_does_not_intercept_input(self):
        slider = ParameterSlider("cut", min_value=-1, max_value=1, value=0)
        scene = self.make_scene(slider)
        point = scene.frame.from_fixed_frame_point(slider.slider_axis.get_end())
        scene.remove(slider)
        scene.on_mouse_press(point, 1, 0)
        self.assertEqual(slider.get_value(), 0)
        self.assertEqual(EVENT_DISPATCHER.draggable_object_listners, [])

    def test_grouped_slider_undo_restores_value_and_display(self):
        slider = ParameterSlider("cut", min_value=-1, max_value=1, value=0, step=0.1)
        scene = self.make_scene(slider)
        scene.mobjects = [scene.frame, Group(Group(slider))]
        point = scene.frame.from_fixed_frame_point(slider.slider_axis.get_end())
        scene.on_mouse_press(point, 1, 0)
        scene.on_mouse_release(point, 1, 0)
        self.assertEqual(slider.get_value(), 1)
        scene.undo()
        slider.update()
        self.assertEqual(slider.get_value(), 0)
        self.assertEqual(slider.readout.get_value(), 0)
        np.testing.assert_allclose(slider.slider.get_center(), slider.slider_axis.get_center())
        scene.redo()
        slider.update()
        self.assertEqual(slider.get_value(), 1)
        self.assertEqual(slider.readout.get_value(), 1)

    def test_empty_click_does_not_consume_undo_or_redo(self):
        slider = ParameterSlider("cut", min_value=-1, max_value=1, value=0)
        scene = self.make_scene(slider)
        end = scene.frame.from_fixed_frame_point(slider.slider_axis.get_end())
        empty = scene.frame.from_fixed_frame_point(UP)
        scene.on_mouse_press(end, 1, 0)
        scene.on_mouse_release(end, 1, 0)
        scene.on_mouse_press(empty, 1, 0)
        scene.on_mouse_release(empty, 1, 0)
        scene.undo()
        slider.update()
        self.assertEqual(slider.get_value(), 0)
        scene.on_mouse_press(empty, 1, 0)
        scene.on_mouse_release(empty, 1, 0)
        scene.redo()
        slider.update()
        self.assertEqual(slider.get_value(), 1)

    def test_no_op_slider_click_preserves_redo(self):
        slider = ParameterSlider("cut", min_value=-1, max_value=1, value=0)
        scene = self.make_scene(slider)
        end = scene.frame.from_fixed_frame_point(slider.slider_axis.get_end())
        middle = scene.frame.from_fixed_frame_point(slider.slider_axis.get_center())
        scene.on_mouse_press(end, 1, 0)
        scene.on_mouse_release(end, 1, 0)
        scene.undo()
        slider.update()
        scene.on_mouse_press(middle, 1, 0)
        scene.on_mouse_release(middle, 1, 0)
        scene.redo()
        slider.update()
        self.assertEqual(slider.get_value(), 1)

    def test_ignored_interactive_overlays_do_not_clear_redo(self):
        slider = ParameterSlider("cut", min_value=-1, max_value=1, value=0)
        scene = cast(InteractiveScene, self.make_scene(slider, InteractiveScene))
        scene.selection_highlight = Group()
        scene.selection_rectangle = Rectangle()
        scene.crosshair = VGroup()
        scene.mobjects.insert(0, scene.selection_highlight)
        end = scene.frame.from_fixed_frame_point(slider.slider_axis.get_end())
        empty = scene.frame.from_fixed_frame_point(UP)
        Scene.on_mouse_press(scene, end, 1, 0)
        Scene.on_mouse_release(scene, end, 1, 0)
        scene.undo()
        slider.update()
        self.assertEqual(slider.get_value(), 0)
        self.assertTrue(scene.get_state().matches_scene(scene))
        Scene.on_mouse_press(scene, empty, 1, 0)
        Scene.on_mouse_release(scene, empty, 1, 0)
        scene.redo()
        slider.update()
        self.assertEqual(slider.get_value(), 1)

    def test_world_space_listener_is_not_transformed(self):
        dispatcher = EventDispatcher()
        mob = Circle().shift(RIGHT)
        observed = []
        from manimlib.event_handler.event_listner import EventListener
        from manimlib.event_handler.event_type import EventType
        dispatcher.add_listner(EventListener(mob, EventType.MousePressEvent, lambda m, e: observed.append(e["point"])))
        dispatcher.dispatch(EventType.MousePressEvent, frame=CameraFrame().scale(2), point=RIGHT)
        np.testing.assert_array_equal(observed, [RIGHT])


if __name__ == "__main__":
    unittest.main()
