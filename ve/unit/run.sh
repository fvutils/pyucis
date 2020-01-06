#!/bin/bash

script_dir=`dirname $0`
script_dir=`cd $script_dir; pwd`
pyucis_dir=$script_dir

for i in 1 2; do
  pyucis_dir=`dirname $pyucis_dir`
done

export PYTHONPATH=${pyucis_dir}/src:/project/fun/portaskela/boolector/inst/lib

# valgrind --tool=memcheck --suppressions=./valgrind-python.supp ${pyucis_dir}/packages/python/bin/python3 -m unittest ${@:1}
# valgrind --tool=memcheck python3 -m unittest ${@:1}
# gdb --args python3 -m unittest ${@:1}
${pyucis_dir}/packages/python/bin/python3 -m unittest ${@:1}

