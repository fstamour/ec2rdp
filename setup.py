import os

from setuptools import find_packages, setup

base_dir = os.path.dirname(__file__)

with open(os.path.join(base_dir, 'version.txt')) as f:
    version = str(f.readline().strip())

with open(os.path.join(base_dir, 'README.rst')) as f:
    long_description = str(f.read())

with open(os.path.join(base_dir, 'requirements', 'setup.txt')) as f:
    requirements = f.read().splitlines()

setup(
    name='ec2rdp',
    description='Command line tool to quickly access AWS EC2 Windows instance through rdp.',
    long_description=long_description,
    version=version,
    author='JTV Softwares',
    author_email='jtvsoftwares@gmail.com',
    license='MIT',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'ec2rdp = ec2rdp.ec2rdp:main'
        ],
    },
    install_requires=requirements,
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Utilities',
        'Development Status :: 5 - Production/Stable'
    ]
)
