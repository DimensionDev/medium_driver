from setuptools import find_packages, setup

setup(
    name='mediumdb',
    version='0.0.2',
    description='Medium driver.',
    url='https://github.com/sujitech/medium_driver',
    author='Mindey',
    author_email='mindey@qq.com',
    license='ASK FOR PERMISSIONS',
    packages = find_packages(exclude=['docs', 'tests*']),
    install_requires=['metadrive'],
    extras_require = {
        'test': ['coverage', 'pytest', 'pytest-cov'],
    },
    zip_safe=False
)
