'''
Created on Nov 10, 2021

@author: mballance
'''
from _io import StringIO
import sys
from unittest.case import TestCase

from ucis.report.coverage_report_builder import CoverageReportBuilder
from ucis.report.text_coverage_report_formatter import TextCoverageReportFormatter
from ucis.yaml.yaml_reader import YamlReader


class TestYamlReader(TestCase):
    
    def test_smoke(self):
        text = """
        coverage:
            covergroups:
            - name: ABC
              weight: 1 
              instances:
              - name: I1
                coverpoints:
                - name: CP1
                  atleast: 1
                  bins:
                  - name: a
                    hits: 1
                  - name: b
                    hits: 0
              - name: l2
                coverpoints:
                - name: CP1
                  atleast: 1
                  bins:
                  - name: a
                    hits: 0
                  - name: b
                    hits: 1
                    
        """
        db = YamlReader().loads(StringIO(text))
        rpt = CoverageReportBuilder.build(db)
        
        TextCoverageReportFormatter(rpt, sys.stdout)
    
    def test_type_cvg_cvp(self):
        text = """
        coverage:
            covergroups:
                - type-name: cvg
                
                  coverpoints:
                    - name: cp1
                      bins:
                        - name: b0
                          count: 1
                        - name: b1
                          count: 0
        """
        
        db = YamlReader().loads(StringIO(text))
        rpt = CoverageReportBuilder.build(db)
        
        self.assertEqual(len(rpt.covergroups), 1)
        self.assertEqual(rpt.covergroups[0].name, "cvg")
        self.assertEqual(len(rpt.covergroups[0].coverpoints), 1)
        self.assertEqual(len(rpt.covergroups[0].coverpoints[0].bins), 2)
        self.assertEqual(rpt.covergroups[0].coverpoints[0].coverage, 50.0)

    def test_type_cvg_2_cvp(self):
        text = """
        coverage:
            covergroups:
                - type-name: cvg
                
                  coverpoints:
                    - name: cp1
                      bins:
                        - name: b0
                          count: 1
                        - name: b1
                          count: 0
                    - name: cp2
                      bins:
                        - name: b0
                          count: 1
                        - name: b1
                          count: 1
        """
        
        db = YamlReader().loads(StringIO(text))
        rpt = CoverageReportBuilder.build(db)
        
        self.assertEqual(len(rpt.covergroups), 1)
        self.assertEqual(rpt.covergroups[0].name, "cvg")
        self.assertEqual(len(rpt.covergroups[0].coverpoints), 2)
        self.assertEqual(len(rpt.covergroups[0].coverpoints[0].bins), 2)
        self.assertEqual(len(rpt.covergroups[0].coverpoints[1].bins), 2)
        self.assertEqual(rpt.covergroups[0].coverage, 75.0)
        