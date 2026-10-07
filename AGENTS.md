# AGENTS.md

wxPython + matplotlib GUI for drawing bounding-box labels on images. Old, minimal project — assume nothing is automated.

## Run / install

- GUI app, needs a display/X server. There is **no headless operation and no automated test suite**; `tests/test_wx.py` is a manual smoke test for the wx install (launches a frame), not something pytest can run headless.
- Entry point is `img_label.py` at repo root (installed as the `img_label` console script via the `[project.scripts]` entry in `pyproject.toml`). Run directly: `python img_label.py` or after `pip install -e .`.
- Install deps from `pyproject.toml` `project.dependencies` (wxpython, opencv-python>=4.4, shapely, scipy, matplotlib, scikit-learn). Do NOT trust `README.md`'s Python/Dependency list — it also mentions Keras/Tensorflow/ImageAI, which are **not** in `dependencies`.
- CLI args (argparse): `--file PATH`, `--imagedir DIR`, `--confdir DIR`.
- First run auto-creates `~/.labeler/main.conf` (configparser). Pass `--confdir` to relocate. If `main.conf` is missing/corrupt the app prints a warning but continues.

## env / system quirks

- wx/GTK may fail without `export XKB_CONFIG_ROOT=/usr/share/X11/xkb` (see README).
- `container/Containerfile` (fedora:39 + miniconda + wxGTK-devel) is the intended way to run in a headless machine with an X/X11 setup.

## Architecture

- `img_label.py` — the whole app: `ImageLabeler(wx.App)`, all panels/menus, mouse/keyboard handlers, zoom, bounding-box lifecycle.
- `labeler/` package:
  - `imaging.py` — OpenCV image ops (filters, morphology, canny, watershed); `image.jpg` and `icons/` are shipped package data.
  - `grid.py` — bounding-box grid ↔ CSV (`import_grid_csv`, `write_grid_csv`, `fill_grid`). CSV export defaults to same basename as the image (e.g. `img.jpg` → `img.csv`); imports skip the header row.
  - `utils.py` — `get_list_files` scans a dir recursively for PNG/JPG; an image counts as already labeled if a sibling `.csv` exists.
  - `trans.py` / `segment.py` — tool frames wired into the main app.
  - `configfile.py` — config dir/`main.conf` handling.
  - `models/yolo.py` — the only model; requires `imageai` + a `yolov3.h5` weights file that is **not shipped or installed**. Importing `labeler.models` fails unless you install ImageAI yourself. Treat as dormant/optional.