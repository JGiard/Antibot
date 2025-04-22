import re

from setuptools import setup, find_packages

with open('src/antibot/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE).group(1)
    assert version is not None

setup(name='antibot',
      version=version,
      author='Jean Giard',
      license='LGPL',
      classifier=[
          'Programming Language :: Python :: 3'
      ],
      entry_points={
          'console_scripts': ['antibot=antibot.main:run'],
          'antibot': [
              'antibot=antibot.provided:BasePlugin',
              'dismiss=antibot.provided:DismissActionPlugin',
              'debug=antibot.provided:DebuggerPlugin',
          ]
      },
      packages=find_packages(where='src'),
      package_dir={'': 'src'},
      install_requires=[
          'pymongo',
          'requests',
          'injector',
          'pyckson',
          'pytz',
          'schedule',
          'slack_sdk',
          'arrow',
          'bottle'
      ],
      )
