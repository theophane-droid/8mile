from distutils.core import setup
setup(
    name='hmile',
    version='0.4.2',
    author='theophanedroid',
    description='Python 3.x module to render financial results in tensorboard ',
    packages=['hmile',],
    license='MIT license',
    long_description=open('README.md').read(),
    install_requires=[
        "mplfinance",
        "ta",
        "pandas",
        "elasticsearch",
        "numpy",
        "yfinance",
        "multitasking",
        "IPython",
        "TA-Lib",
        "requests",
        "scikit-learn",
        "tqdm",
        "pytickersymbols"
    ],
    extras_require={
        'test': ['unittest2']
    },
)