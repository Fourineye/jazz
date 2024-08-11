from setuptools import setup, find_packages

setup(
    name='jazz',
    version='0.1.1',
    description='A example Python package',
    url='https://github.com/Fourineye/jazz',
    author='Paul Smith',
    author_email='',
    license='',
    packages=find_packages(),
    package_data={"jazz": ["./resources/*"]},
    include_package_data=True,
    install_requires=['pygame-ce'],
)
