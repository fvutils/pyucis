#######
Jenkins
#######

The declarative pipeline below merges coverage, publishes a Cobertura report
via the Jenkins Cobertura plugin, and generates an HTML report artifact.

Prerequisites
=============

Install the `Cobertura Plugin <https://plugins.jenkins.io/cobertura/>`_
(or `JaCoCo Plugin <https://plugins.jenkins.io/jacoco/>`_) in Jenkins.

Full Pipeline Example
=====================

.. code-block:: groovy

    pipeline {
        agent any

        stages {
            stage('Test') {
                steps {
                    sh 'make run_all_tests'  // produces test_*.xml
                }
            }

            stage('Coverage') {
                steps {
                    sh 'pip install pyucis'

                    // Merge all test coverage files
                    sh 'ucis merge -o merged.xml test_*.xml'

                    // Coverage gate
                    sh '''
                        COV=$(ucis show summary merged.xml -of json | jq -r '.overall_coverage')
                        echo "Coverage: ${COV}%"
                        python3 -c "import sys; sys.exit(0 if float('$COV') >= 80 else 1)" \
                            || { echo "Coverage below 80%"; exit 1; }
                    '''

                    // Export Cobertura for Jenkins plugin
                    sh 'ucis show code-coverage merged.xml --output-format cobertura > coverage.xml'

                    // Export JaCoCo (alternative)
                    // sh 'ucis show code-coverage merged.xml --output-format jacoco > jacoco.xml'

                    // Generate HTML report
                    sh 'ucis report merged.xml -of html -o coverage_report.html'
                }

                post {
                    always {
                        // Publish Cobertura coverage
                        cobertura coberturaReportFile: 'coverage.xml',
                                  failUnhealthy: false,
                                  failUnstable: false

                        // Archive HTML report
                        archiveArtifacts artifacts: 'coverage_report.html'
                    }
                }
            }
        }
    }

JaCoCo Variant
==============

Replace the Cobertura steps with:

.. code-block:: groovy

    sh 'ucis show code-coverage merged.xml --output-format jacoco > jacoco.xml'

    post {
        always {
            jacoco execPattern: 'jacoco.xml'
        }
    }

Verilator Projects
==================

.. code-block:: groovy

    sh 'ucis merge --input-format vltcov -o merged.xml tests/*/coverage.dat'
