
ROOTDIR:=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))

html :
	$(ROOTDIR)/packages/python/bin/sphinx-build \
		-M html $(ROOTDIR)/doc/source $(ROOTDIR)/doc/build

