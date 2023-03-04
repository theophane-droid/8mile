from distutils.core import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='hmile',
    version='0.4.2',
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