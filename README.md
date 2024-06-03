# labeler
Python Image Labeler


## Install labeler

   * Using a Python virtual environment
```bash
    git clone https://github.com/vmjersey/labeler
    python -m venv image_labeler
    cd image_labeler
    source bin/activate
    pip install ../labeler
```

   * wxpython can take a while to compile and install.
   * Sometimes, you have to specify the XKB_CONFIG_ROOT

```bash
    export XKB_CONFIG_ROOT=/usr/share/X11/xkb
```
 ### Python Dependencies
```
    Python      3.6+
    Keras       2.3+
    Tensorflow  1.14+
    wxpython    4.2+
    ImageAI     2.1+
    Numpy       1.17+
    Matplotlib  3.1+
    OpenCV      3.4+
```


Wishlist:

   * Add ability to resize rectangles.
   * Add ability to draw free hand for semantic segmentation?
   * Add ability to load model in Keras for bounding boxes suggestions.
   * Add ability to have script generate image.

Bugs:
   * Bounding boxes move when trying to zoom inside bounding box.
