from distutils.core import setup
setup(
    name='hmilerender',
    version='0.1.0',
    author='theophanedroid',
    description='Python 3.x module to render financial results in tensorboard ',
    packages=['Hmilerender',],
    license='MIT license',
    long_description=open('README.md').read(),
    install_requires=[
        "mplfinance",
        "numpy",
        "tensorflow",
        "jupyterlab",
        "tensorboard",
        "yfinance"
    ]
)