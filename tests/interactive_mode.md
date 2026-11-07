# Native interactive checkpoints

Run `manimgl tests/interactive_mode.py InteractiveMode -l` from the repo root.
This opens a native GLFW preview and an embedded IPython terminal; no LaTeX is needed.
Use the same window size for before/after captures (e.g. `window.size: (1280, 720)`
in a local config file passed with `--config_file`). Do not use `-w`: these checks
exercise native pointer/key events, not just offline rendering.

## Drop-in scene parameter

`ParameterSlider` is a labelled `ValueTracker`. Add it to any `Scene` and read its
value in an updater; no subclass or separate control panel is required:

```python
cut = ParameterSlider("cut", min_value=-1.2, max_value=1.2, step=0.1, value=0)
cut.to_corner(DL)
disk.add_updater(lambda mob: mob.set_clip_plane(RIGHT, -cut.get_value()))
self.add(disk, cut)
self.embed()
```

Click the track or drag the knob. Values snap to the nearest step and clamp at
the endpoints; `step=None` gives continuous adjustment. Use `cut.set_value(0)`
from the terminal or animate it like any tracker. The readout follows restoration
and animation. A changed click/drag saves one undo state on release; unchanged
clicks preserve undo/redo history. A slider drag must not pan the camera. The control
stays fixed and clickable after orbit/pan/zoom. Removed controls must not capture input.

## Repeatable checkpoints

1. **Frontal baseline:** green full circle, blue right semicircle against the red
   guide, yellow right half-outline; `cut = 0.00`. Capture the preview.
2. **Live parameter:** click/drag the slider to both limits and back to zero.
   Only the yellow outline's clipping changes. Try Ctrl+Z / Ctrl+Shift+Z (Cmd on
   macOS) after a drag; both the value and displayed clip must follow history.
3. **Planar scene treated as 3D:** hold `d` and move the pointer; the scene orbits
   while the title/slider remain horizontal. Drag the slider again in this view;
   the knob should track the pointer, not move the camera. Hold `f` and move to
   pan, then wheel to zoom. Press `r` and set `cut.set_value(0)` in the terminal
   to recover the frontal baseline. Repeat once to catch cumulative drift.
4. **Checkpoint paste:** put the following block on the system clipboard and
   run `checkpoint_paste()` in the embedded terminal:

   ```python
   # disk edit
   disk.set_clip_plane(UP, 0)
   disk.set_fill(PURPLE, 1)
   ```

   Capture the purple upper semicircle. Change the disk in the terminal, then
   paste the same comment-keyed block again: it must recover exactly the same
   upper-half checkpoint rather than accumulating changes.
5. **Keyboard redo regression:** in the terminal run:

   ```python
   self.undo_stack.clear(); self.redo_stack.clear()
   disk.set_clip_plane(RIGHT, 0); disk.set_fill(BLUE, 1); save_state()
   disk.set_clip_plane(UP, 0); disk.set_fill(PURPLE, 1)
   ```

   Focus the preview. Ctrl+Z must show blue/right; Ctrl+Shift+Z must show
   purple/upper again. Repeat. On the old code the redo shortcut takes the undo
   branch and stays blue/right; direct `redo()` in the terminal isolates the
   problem to keyboard dispatch. Capture before/after GIFs of the same sequence.
6. **Grouped controls and history:** run `remove(cut); add(Group(Group(cut)))`
   in the terminal. Edit the slider, click empty space without dragging, then
   undo: it must restore the pre-edit value, knob, readout and yellow clipping
   immediately, not consume an unchanged snapshot. Click empty space again and
   redo: the edit must return. Repeat after clicking the unchanged knob instead
   of empty space. Repeat orbit/drag and checkpoint paste with the nested slider.

Automated, display-independent companion checks: `python -m pytest tests`.
Do not pass pytest flags: manimlib parses command-line arguments on import.
