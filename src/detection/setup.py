from setuptools import setup

package_name = 'detection'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    py_modules=[
        'detection.detection_node',
    ],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='your_name',
    maintainer_email='your_email@example.com',
    description='Description of your package',
    license='License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'detection_node = detection.detection_node:main'
        ],
    },
)

