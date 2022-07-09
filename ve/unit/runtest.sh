#!/bin/sh

ROOTDIR=../..

PYTHON=${ROOTDIR}/packages/python/bin/python3

export PYTHONPATH=${ROOTDIR}/src

${PYTHON} -m unittest -v 

