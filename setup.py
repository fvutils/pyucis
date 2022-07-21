
import os
from setuptools import setup, find_namespace_packages

version="0.1.2"

if "BUILD_NUM" in os.environ.keys():
    version = version + "." + os.environ["BUILD_NUM"]

setup(
  name = "pyucis",
  packages=find_namespace_packages(where='src'),
  package_dir = {'' : 'src'},
  package_data = {'' : ['*.xsd']},
  version=version,
  author = "Matthew Ballance",
  author_email = "matt.ballance@gmail.com",
  description = ("PyUCIS provides a Python API for manipulating UCIS coverage data."),
  long_description = """
  Python library for interacting with verification coverage data
  """,
  license = "Apache 2.0",
  keywords = ["SystemVerilog", "Verilog", "RTL", "Coverage"],
  url = "https://github.com/fvutils/pyucis",
  entry_points={
    'console_scripts': [
      'pyucis = ucis.__main__:main'
    ]
  },
  setup_requires=[
    'setuptools_scm',
    'ivpm'
  ],
  install_requires=[
    'lxml',
    'python-jsonschema-objects',
    'jsonschema',
    'pyyaml'
  ],
)

