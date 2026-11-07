"""Run: manimgl tests/interactive_mode.py InteractiveMode -l

See interactive_mode.md for repeatable native visual checkpoints.
"""
from manimlib import *


class InteractiveMode(Scene):
    def construct(self):
        self.set_background_color("#14171f")
        plane = NumberPlane(
            x_range=(-7, 7, 1), y_range=(-4, 4, 1),
            background_line_style={"stroke_color": GREY_D, "stroke_width": 1},
        )
        tiles = VGroup(*(
            Square(side_length=0.22).set_fill(
                BLUE_D if (i + j) % 2 else TEAL_D, 0.65
            ).set_stroke(width=0).move_to([i * 0.38, j * 0.38 + 2.25, 0])
            for i in range(-6, 6) for j in range(-2, 4)
        ))
        reference = Circle(radius=1.2).set_fill(GREEN, 0.8).set_stroke(WHITE, 4).shift(3.2 * LEFT)
        disk = Circle(radius=1.2).set_fill(BLUE, 1).set_stroke(WHITE, 4)
        disk.set_clip_plane(RIGHT, 0)
        outline = Circle(radius=1.2).set_fill(opacity=0).set_stroke(YELLOW, 8).shift(3.2 * RIGHT)
        cut = ParameterSlider("cut", min_value=-1.2, max_value=1.2, step=0.1, value=0)
        cut.to_corner(DL, buff=0.3)
        outline.add_updater(lambda mob: mob.set_clip_plane(RIGHT, -3.2 - cut.get_value()))
        guide = Line(1.5 * DOWN, 1.5 * UP, color=RED, stroke_width=2)
        title = Text("INTERACTIVE CHECKPOINTS", font_size=28).to_edge(UP).fix_in_frame()
        labels = VGroup(*(
            Text(text, font_size=22).move_to([x, -1.7, 0])
            for text, x in (("reference", -3.2), ("clip / undo / redo", 0), ("live cut", 3.2))
        ))
        hint = Text("d + move: orbit   f + move: pan   wheel: zoom   r: reset", font_size=18)
        hint.to_corner(DR, buff=0.3).fix_in_frame()
        self.add(plane, tiles, reference, disk, outline, guide, labels, title, hint, cut)
        self.embed()
