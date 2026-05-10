from setuptools import setup

package_name = 'turtle_chain'

setup(
    name=package_name,
    version='0.0.1',

    packages=[package_name],

    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),

        ('share/' + package_name, ['package.xml']),
    ],

    install_requires=['setuptools'],
    zip_safe=True,

    maintainer='student',
    maintainer_email='student@example.com',

    description='ROS2 turtle chain following system',
    license='Apache License 2.0',

    tests_require=['pytest'],

    entry_points={
        'console_scripts': [
            'chain_manager = turtle_chain.chain_manager:main',
        ],
    },
)