from distutils.core import setup
from pathlib import Path

from setuptools import find_packages

setup(
    name="dotstree",
    version="0.1.0",
    description="Flexible dotfile manager based on directory trees.",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://www.github.com/metov/dotstree",
    author="Azat Akhmetov",
    author_email="azatinfo@yandex.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "coloredlogs",
        "docopt",
        "PyYAML",
        "questionary",
        "tabulate",
        "tqdm",
    ],
    entry_points={
        "console_scripts": [
            "dots=dotstree.main:main",
        ],
    },
)
