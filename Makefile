
ROOTDIR:=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))


html : schema
	$(ROOTDIR)/packages/python/bin/sphinx-build \
		-M html $(ROOTDIR)/doc/source $(ROOTDIR)/doc/build
	cp $(ROOTDIR)/doc/schema/coverage.json $(ROOTDIR)/doc/build/html
	cp $(ROOTDIR)/doc/schema/coverage_report.json $(ROOTDIR)/doc/build/html
schema : 
	rm -rf $(ROOTDIR)/doc/schema
	cp -r $(ROOTDIR)/src/ucis/schema $(ROOTDIR)/doc/schema

clean :
	rm -rf $(ROOTDIR)/doc/build 
	rm -rf $(ROOTDIR)/doc/schema 
