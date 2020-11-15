
import os
from setuptools import setup, find_namespace_packages

def get_version():
    try:
        import ivpm
        return ivpm.get_pkg_version(__file__)
    except:
        return "0.0.0"


setup(
  name = "pyucis",
  packages=find_namespace_packages(where='src'),
  package_dir = {'' : 'src'},
  package_data = {'' : ['*.xsd']},
  version=get_version(),
  author = "Matthew Ballance",
  author_email = "matt.ballance@gmail.com",
  description = ("PyUCIS provides a Python API for manipulating UCIS coverage data."),
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
  ],
)

