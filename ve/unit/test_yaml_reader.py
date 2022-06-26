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
                    count: 1
                  - name: b
                    count: 0
              - name: l2
                coverpoints:
                - name: CP1
                  atleast: 1
                  bins:
                  - name: a
                    count: 0
                  - name: b
                    count: 1
                
                    
        """
        db = YamlReader().loads(StringIO(text))
        rpt = CoverageReportBuilder.build(db)
        
        print("rpt=%s" % str(rpt))
        
        renderer = TextCoverageReportFormatter(rpt, sys.stdout)
        renderer.details = True
        renderer.report()
        
        self.assertEqual(round(rpt.covergroups[0].coverage, 2), 66.67)
        self.assertEqual(round(rpt.covergroups[0].covergroups[0].coverage, 2), 50.0)
        self.assertEqual(round(rpt.covergroups[0].covergroups[1].coverage, 2), 50.0)

    def test_cross_smoke(self):
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
                    count: 1
                  - name: b
                    count: 0
                - name: CP2
                  atleast: 1
                  bins:
                  - name: a
                    count: 0
                  - name: b
                    count: 1
                crosses:
                - name: CP1xCP2
                  coverpoints: [CP1, CP2]
                  bins:
                  - name: <a,a>
                    count: 0
                  - name: <a,b>
                    count: 1
                  - name: <b,a>
                    count: 0
                  - name: <b,b>
                    count: 0
        """
        db = YamlReader().loads(StringIO(text))
        rpt = CoverageReportBuilder.build(db)
        
        print("rpt=%s" % str(rpt))
        
        renderer = TextCoverageReportFormatter(rpt, sys.stdout)
        renderer.details = True
        renderer.report()
        
        self.assertEqual(round(rpt.covergroups[0].coverage, 2), 41.67)
        self.assertEqual(round(rpt.covergroups[0].covergroups[0].coverage, 2), 41.67)
        self.assertEqual(len(rpt.covergroups[0].coverpoints), 2)
        self.assertEqual(len(rpt.covergroups[0].crosses), 1)
        
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
        