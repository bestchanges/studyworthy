"""Lambda-commont module setup description."""

import setuptools

setuptools.setup(
    name='wlms-cli',
    version='0.0.1',
    author='Egor Fedorov',
    author_email='egor.fedorov@gmail.com',
    description='CLI client for WorthStydy LMS',
    packages=setuptools.find_packages(),
    py_modules=['wlms'],
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    entry_points = {
        'console_scripts': ['wlms=wlms:cli'],
    },
    install_requires=[
        'Click'
    ],
    extras_require={
        'dev': [
        ],
    },
    python_requires='>=3.6',
)
