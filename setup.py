from distutils.core import setup
setup(
    name='hmile',
    version='0.3.0',
    author='theophanedroid',
    description='Python 3.x module to render financial results in tensorboard ',
    packages=['Hmile',],
    license='MIT license',
    long_description=open('README.md').read(),
    install_requires=[
        "mplfinance",
        "ta",
        "pandas",
        "elasticsearch",
        "torch",
        "numpy",
        "tensorflow",
        "tensorboard",
        "yfinance",
        "multitasking",
        "IPython",
        "TA-Lib",
        "requests",
        "scikit-learn",
        "matplotlib",
        "tqdm"
    ],
    extras_require={
        'test': ['unittest2']
    },
)