from setuptools import find_packages
from setuptools import setup

setup(
    name='tts_ros',
    version='0.0.0',
    packages=find_packages(
        include=('tts_ros', 'tts_ros.*')),
)
