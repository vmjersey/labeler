#!/usr/bin/env python3
'''
Headless regression tests for the bounding-box drawing handlers in img_label.

These tests instantiate ImageLabeler WITHOUT calling its wx __init__ (which
requires a display) and drive OnLeftDown / OnMotion / OnLeftUp directly
against a real matplotlib Figure using a non-wx canvas.  No display needed.

Run directly:   python tests/test_draw_rect.py
Or via pytest:  pytest tests/test_draw_rect.py
'''

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib
matplotlib.use("Agg")

from types import SimpleNamespace

import matplotlib
import img_label

# img_label forces the WXAgg backend at import; switch back to Agg so this
# test can build figures without a display.
matplotlib.use("Agg")

from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from img_label import ImageLabeler


class FakeCanvas(object):
    '''
    Records draw/draw_idle calls; nothing actually paints.
    '''
    def __init__(self):
        self.draw_calls = 0
        self.draw_idle_calls = 0

    def draw(self):
        self.draw_calls += 1

    def draw_idle(self):
        self.draw_idle_calls += 1


class FakeGrid(object):
    '''
    Minimal wx.grid.Grid stand-in implementing only what fill_grid and
    get_grid_list need.
    '''
    COL_LABELS = ["X1", "Y1", "X2", "Y2", "Label"]

    def __init__(self, rows=100, cols=5):
        self._rows = rows
        self._cols = cols
        self.cells = {}

    def GetNumberCols(self):
        return self._cols

    def GetNumberRows(self):
        return self._rows

    def GetColLabelValue(self, col):
        return self.COL_LABELS[col]

    def GetCellValue(self, row, col):
        return self.cells.get((row, col), "")

    def SetCellValue(self, row, col, value):
        self.cells[(row, col)] = value

    def DeleteRows(self, row):
        self.cells = {key: value for key, value in self.cells.items()
                      if key[0] != row}
        self._rows = max(self._rows - 1, 0)

    def ForceRefresh(self):
        pass


def make_app():
    app = ImageLabeler.__new__(ImageLabeler)
    app.frame = SimpleNamespace(pressed=False)
    app.figure = Figure()
    app.axes = app.figure.add_axes((0.0, 0.0, 1.0, 1.0))
    app.axes.set_axis_off()
    app.canvas = FakeCanvas()
    app.rect_obj_list = []
    app.rect_labels = []
    app.cursor_mode = "bb"
    app.is_moving = False
    app.BBGrid = FakeGrid()
    return app


def ev(xdata=None, ydata=None):
    return SimpleNamespace(xdata=xdata, ydata=ydata)


def test_drag_draws_rectangle_live():
    app = make_app()

    app.OnLeftDown(ev(50, 50))
    assert app.frame.pressed is True
    # Placeholder rectangle must be shown as soon as the drag starts.
    assert app.canvas.draw_idle_calls >= 1

    app.OnMotion(ev(150, 120))
    assert (app.rect.get_width(), app.rect.get_height()) == (100.0, 70.0)
    assert (app.rect.get_xy()) == (50.0, 50.0)
    # The live update also asks for a redraw.
    assert app.canvas.draw_idle_calls >= 2

    app.OnLeftUp(ev(150, 120))
    assert app.rect in app.rect_obj_list
    assert len(app.rect_labels) == 1
    assert app.frame.pressed is False
    # The box goes solid the moment the mouse is released.
    assert app.rect.get_linestyle() == 'solid'
    # The grid was populated from the finished rectangle.
    assert app.BBGrid.cells[(0, 0)] == "50"
    assert app.BBGrid.cells[(0, 2)] == "150"
    assert app.BBGrid.cells[(0, 3)] == "120"


def test_drag_past_image_edge_does_not_freeze():
    app = make_app()

    app.OnLeftDown(ev(50, 50))
    # Cursor leaves the image: xdata/ydata go None.  This used to raise
    # TypeError inside the handler and silently freeze the live draw.
    app.OnMotion(ev(None, None))
    # Back over the image: rectangle must track again.
    app.OnMotion(ev(150, 120))
    assert (app.rect.get_width(), app.rect.get_height()) == (100.0, 70.0)

    app.OnLeftUp(ev(150, 120))
    assert app.rect in app.rect_obj_list


def test_release_off_canvas_after_press_does_not_crash():
    app = make_app()

    app.OnLeftDown(ev(50, 50))
    # Release happens off the image, before any on-canvas motion: the box
    # never got sized, so it must be discarded, not kept as a 0px box.
    app.OnLeftUp(ev(None, None))
    assert app.frame.pressed is False
    assert app.rect_obj_list == []
    assert app.rect not in app.axes.patches


def test_press_off_canvas_is_ignored():
    app = make_app()

    app.OnLeftDown(ev(None, None))
    assert app.frame.pressed is False
    app.OnLeftUp(ev(None, None))
    assert app.rect_obj_list == []
    assert app.canvas.draw_idle_calls == 0


def seed_rect(app, x0=50.0, y0=50.0, width=100.0, height=100.0):
    rect = Rectangle((x0, y0), width, height,
                     facecolor='None', edgecolor='green', linewidth='2')
    app.axes.add_patch(rect)
    app.rect_obj_list.append(rect)
    app.rect_labels.append("")
    return rect


def test_move_drags_rectangle():
    app = make_app()
    rect = seed_rect(app)

    # Press inside the box: starts a move (not a new box).
    app.OnLeftDown(ev(60, 60))
    assert app.is_moving is True

    # The box tracks the mouse delta from the press origin.
    app.OnMotion(ev(110, 110))
    assert rect.get_xy() == (100.0, 100.0)
    app.OnMotion(ev(160, 160))
    assert rect.get_xy() == (150.0, 150.0)
    # Live updates are requested with draw_idle (the same mechanism as
    # drawing a new box, which the gui relies on for responsive drags).
    assert app.canvas.draw_idle_calls >= 1

    app.OnLeftUp(ev(160, 160))
    assert app.is_moving is False
    assert app.press is None
    # Grid reflects the box's new position.
    assert app.BBGrid.cells.get((0, 0)) == "150"
    assert app.BBGrid.cells.get((0, 2)) == "250"


def test_click_outside_rect_starts_new_box():
    app = make_app()
    seed_rect(app)

    app.OnLeftDown(ev(10, 10))
    assert app.is_moving is False
    # A new (not moved) box started drawing.
    assert app.frame.pressed is True

    # Release far enough away for a real box (sub-10px drags are discarded).
    app.OnLeftUp(ev(50, 50))
    assert len(app.rect_obj_list) == 2


def test_single_click_does_not_create_box():
    app = make_app()

    app.OnLeftDown(ev(50, 50))
    # A click with no meaningful drag must not leave a 0px box.
    app.OnLeftUp(ev(51, 51))
    assert app.rect_obj_list == []
    assert app.rect_labels == []
    assert app.BBGrid.cells == {}
    assert app.rect not in app.axes.patches
    # Both the press and the discard repaint with draw_idle.
    assert app.canvas.draw_idle_calls >= 2


def test_exact_ten_pixel_drag_is_discarded():
    app = make_app()

    app.OnLeftDown(ev(0, 100))
    # 10px wide is exactly the threshold -> not a real box.
    app.OnLeftUp(ev(10, 110))
    assert app.rect_obj_list == []

    app.OnLeftDown(ev(0, 200))
    # One pixel past the threshold -> kept.
    app.OnLeftUp(ev(11, 211))
    assert len(app.rect_obj_list) == 1


def test_delete_removes_rect_and_repaints():
    app = make_app()
    rect = seed_rect(app)
    app.selected_rect = 0

    app.OnDelete()

    assert app.rect_obj_list == []
    assert app.rect_labels == []
    assert rect not in app.axes.patches
    assert not hasattr(app, 'selected_rect')
    # The delete requests a repaint with draw_idle (a synchronous draw from
    # a keyboard handler doesn't get painted until the next event).
    assert app.canvas.draw_idle_calls >= 1


def test_move_past_image_edge_keeps_position():
    app = make_app()
    rect = seed_rect(app)

    app.OnLeftDown(ev(60, 60))
    app.OnMotion(ev(110, 110))
    assert rect.get_xy() == (100.0, 100.0)

    # Cursor off the image: move is ignored, box doesn't distort.
    app.OnMotion(ev(None, None))
    assert rect.get_xy() == (100.0, 100.0)

    # Back on the image: keeps tracking from the press origin.
    app.OnMotion(ev(120, 120))
    assert rect.get_xy() == (110.0, 110.0)

    app.OnLeftUp(ev(120, 120))
    assert app.is_moving is False
    assert app.BBGrid.cells.get((0, 0)) == "110"


def run_all():
    tests = [test_drag_draws_rectangle_live,
             test_drag_past_image_edge_does_not_freeze,
             test_release_off_canvas_after_press_does_not_crash,
             test_press_off_canvas_is_ignored,
             test_move_drags_rectangle,
             test_click_outside_rect_starts_new_box,
             test_move_past_image_edge_keeps_position,
             test_single_click_does_not_create_box,
             test_exact_ten_pixel_drag_is_discarded,
             test_delete_removes_rect_and_repaints]

    failures = 0
    for test in tests:
        try:
            test()
            print("PASS", test.__name__)
        except AssertionError as error:
            failures += 1
            print("FAIL", test.__name__, "->", error)

    if failures:
        print(f"{failures}/{len(tests)} tests failed.")
        raise SystemExit(1)
    print(f"{len(tests)}/{len(tests)} tests passed.")


if __name__ == "__main__":
    run_all()