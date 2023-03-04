from distutils.core import setup

requirements = [
    'ta>=0.10.2',
    'pandas~=1.5.3',
    'elasticsearch>=8.6.2',
    'numpy>=1.24.2',
    'yfinance>=0.1.74',
    'ta-lib>=0.4.25',
    'pandas-ta>=0.3.14b0',
    'requests>=2.28.1',
    'pyyaml>=6.0',
    'scipy>=1.10.1'
]


setup(
    name='hmile',
    version='0.5.1',
    author='theophanedroid',
    description='Python 3.x module to render financial results in tensorboard ',
    packages=['hmile',],
    license='MIT license',
    long_description=open('README.md').read(),
    install_requires=requirements,
    extras_require={
        'test': ['unittest2']
    },
)