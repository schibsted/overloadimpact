from setuptools import setup

setup(name='overloadimpact',
      version='0.0.5',
      description='CLI tool and framework for writing and running tests suites for loadimpact.com, with support for custom lua libraries.',
      url='https://github.com/schibsted/overloadimpact',
      author='Schibsted Products and Technology',
      author_email='someemail@example.com',
      license='MIT',
      packages=['overloadimpact'],
      zip_safe=False,
      keywords='loadtest loadimpact testing',
      # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'oimp=overloadimpact:main',
        ],
    },
)