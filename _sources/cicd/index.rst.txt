################
CI/CD Integration
################

PyUCIS integrates cleanly into continuous integration pipelines. The typical
pattern is:

1. Run tests — each test produces a coverage file
2. Merge coverage files into a single database
3. Export to the format your CI tool expects
4. Optionally gate the build on a coverage threshold

.. toctree::
   :maxdepth: 1

   github-actions
   gitlab-ci
   jenkins

For the available export formats see :doc:`../reporting/exporting`.
