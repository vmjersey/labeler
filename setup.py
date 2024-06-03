import setuptools
from glob import glob

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="labeler", 
    version="0.0.1",
    author="James L. Barker",
    author_email="vmjersey@hotmail.com",
    description="Image labeler for machine learning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="<https://github.com/vmjersey/labeler.git>",
    packages=["labeler","labeler.models"],
    include_package_data=True,
    package_data={
            # If any package contains *.txt or *.rst files, include them:
            "": ["*.jpg","icons/*.png"]
                },
    #data_files=[('share/',  glob('icons/*'))],
    scripts=['img_label.py'],
    python_requires='>=3.6',
	install_requires=[
        "wxpython",
        "opencv-python",
        "shapely",
	"scipy",
	"matplotlib",
	"scikit-learn",
        ],
)

