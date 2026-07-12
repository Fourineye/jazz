import os
import re
from setuptools import setup, find_packages

def get_version():
    init_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jazz", "__init__.py")
    with open(init_path, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r'^__version__\s*=\s*[\'"]([^\'"]+)[\'"]', content, re.M)
    if match:
        return match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(
    name="jazz",
    version=get_version(),
    description="A pygame wrapper that provides tools to quickly build games.",
    url="https://github.com/Fourineye/jazz",
    author="Paul Smith",
    author_email="paulsmith8812@gmail.com",
    license="GPLv3",
    packages=find_packages(),
    package_data={"jazz": ["./resources/*"]},
    include_package_data=True,
    install_requires=["pygame-ce"],
)
