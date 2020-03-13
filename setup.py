
import os
from setuptools import setup

setup(
  name = "pyucis",
  packages=['pyucis'],
  package_dir = {'' : 'src'},
  author = "Matthew Ballance",
  author_email = "matt.ballance@gmail.com",
  description = ("pyucis is a Python API for manipulating UCIS XML files."),
  license = "Apache 2.0",
  keywords = ["SystemVerilog", "Verilog", "RTL", "Coverage"],
  url = "https://github.com/fvutils/pyucis",
  entry_points={
    'console_scripts': [
      'pyucis = pyucis.__main__:main'
    ]
  },
  setup_requires=[
    'setuptools_scm',
  ],
  install_requires=[
    'lxml',
  ],
)

