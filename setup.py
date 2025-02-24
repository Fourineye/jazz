from setuptools import setup, find_packages
#from jazz import __version__

setup(
    name="jazz",
    version="1.0.0",
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
