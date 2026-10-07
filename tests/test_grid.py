#!/usr/bin/env python3
'''
Pure-Python tests for the labeler grid <-> CSV round trip.

These tests do NOT require a display or wx: they exercise labeler.grid
against a tiny fake of the wx grid API surface that labeler.grid uses.

Running them still needs the labeler install_requires (importing
labeler.grid transitively imports labeler.utils, which imports scikit-learn).

Run directly:        python tests/test_grid.py
Or via pytest:       pytest tests/test_grid.py
'''

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from labeler.grid import import_grid_csv, write_grid_csv


class FakeGrid(object):
    '''
    Minimal stand-in for wx.grid.Grid, implementing only the methods that
    labeler.grid calls.
    '''
    def __init__(self, rows=100, cols=5):
        self._cols = cols
        self._col_labels = ["X1", "Y1", "X2", "Y2", "Label"]
        self._cells = [[""] * cols for _ in range(rows)]

    def GetNumberCols(self):
        return self._cols

    def GetNumberRows(self):
        return len(self._cells)

    def GetColLabelValue(self, col):
        return self._col_labels[col]

    def GetCellValue(self, row, col):
        return self._cells[row][col]

    def SetCellValue(self, row, col, value):
        self._cells[row][col] = value

    def ForceRefresh(self):
        pass


class FakeMaster(object):
    def __init__(self, image_path):
        self.imagepath = image_path
        self.BBGrid = FakeGrid()

    def user_info(self, message):
        pass


def fill_rect(master, row, x0, y0, x1, y1, label):
    grid = master.BBGrid
    grid.SetCellValue(row, 0, str(x0))
    grid.SetCellValue(row, 1, str(y0))
    grid.SetCellValue(row, 2, str(x1))
    grid.SetCellValue(row, 3, str(y1))
    grid.SetCellValue(row, 4, label)


def test_round_trip():
    master = FakeMaster("/tmp/nonexistent.jpg")
    fill_rect(master, 0, 10, 20, 30, 40, "car")
    fill_rect(master, 1, 100, 200, 300, 400, "person")

    with tempfile.TemporaryDirectory() as tmp:
        csv_path = os.path.join(tmp, "boxes.csv")
        master.imagepath = os.path.join(tmp, "boxes.jpg")
        write_grid_csv(master, csv_path)

        rows = import_grid_csv(master, csv_path)

    assert rows == [["10", "20", "30", "40", "car"],
                    ["100", "200", "300", "400", "person"]], rows


def test_header_row_is_skipped():
    master = FakeMaster("/tmp/nonexistent.jpg")

    with tempfile.TemporaryDirectory() as tmp:
        csv_path = os.path.join(tmp, "labeled.csv")
        with open(csv_path, "w") as fh:
            fh.write("X1,Y1,X2,Y2,Label\n")
            fh.write("1,2,3,4,cat\n")
            fh.write("5,6,7,8,dog\n")

        rows = import_grid_csv(master, csv_path)

    assert rows == [["1", "2", "3", "4", "cat"],
                    ["5", "6", "7", "8", "dog"]], rows


def test_first_row_is_always_treated_as_header():
    # Labeler CSVs always start with a header row, and import_grid_csv
    # unconditionally drops the first row.  A header-less file therefore
    # loses its first data row - this documents that contract.
    master = FakeMaster("/tmp/nonexistent.jpg")

    with tempfile.TemporaryDirectory() as tmp:
        csv_path = os.path.join(tmp, "naked.csv")
        with open(csv_path, "w") as fh:
            fh.write("1,2,3,4,cat\n")
            fh.write("5,6,7,8,dog\n")

        rows = import_grid_csv(master, csv_path)

    assert rows == [["5", "6", "7", "8", "dog"]], rows


def test_default_csv_written_beside_image():
    with tempfile.TemporaryDirectory() as tmp:
        image_path = os.path.join(tmp, "photo.jpg")
        master = FakeMaster(image_path)
        fill_rect(master, 0, 10, 20, 30, 40, "car")

        write_grid_csv(master)

        expected = os.path.join(tmp, "photo.csv")
        assert os.path.exists(expected)
        with open(expected) as fh:
            content = fh.read()
        assert content.splitlines()[0] == "X1,Y1,X2,Y2,Label"
        assert content.splitlines()[1] == "10,20,30,40,car"


def run_all():
    tests = [test_round_trip,
             test_header_row_is_skipped,
             test_first_row_is_always_treated_as_header,
             test_default_csv_written_beside_image]

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