from setuptools import find_packages
from setuptools import setup

setup(
    name='audio_common_msgs',
    version='0.0.0',
    packages=find_packages(
        include=('audio_common_msgs', 'audio_common_msgs.*')),
)
