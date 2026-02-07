'''
Created on Nov 10, 2021

@author: mballance
'''
from _io import StringIO
import sys


from ucis.report.coverage_report_builder import CoverageReportBuilder
from ucis.report.text_coverage_report_formatter import TextCoverageReportFormatter
from ucis.yaml.yaml_reader import YamlReader


class TestYamlReader:
    
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
              - name: I2
                coverpoints:
                - name: CP1
                  atleast: 1
                  bins:
                  - name: a
                    count: 0
                  - name: b
                    count: 1
                
                    
        """
        db = YamlReader().loads(text)
        rpt = CoverageReportBuilder.build(db)
        
        print("rpt=%s" % str(rpt))
        
        renderer = TextCoverageReportFormatter(rpt, sys.stdout)
        renderer.details = True
        renderer.report()
        
        assert round(rpt.covergroups[0].coverage, 2) == 100.0
        assert round(rpt.covergroups[0].covergroups[0].coverage, 2) == 50.0
        assert round(rpt.covergroups[0].covergroups[1].coverage, 2) == 50.0

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
        db = YamlReader().loads(text)
        rpt = CoverageReportBuilder.build(db)
        
        print("rpt=%s" % str(rpt))
        
        renderer = TextCoverageReportFormatter(rpt, sys.stdout)
        renderer.details = True
        renderer.report()
        
        assert round(rpt.covergroups[0].coverage, 2) == 41.67
        assert round(rpt.covergroups[0].covergroups[0].coverage, 2) == 41.67
        assert len(rpt.covergroups[0].coverpoints) == 2
        assert len(rpt.covergroups[0].crosses) == 1
        
    def test_type_cvg_cvp(self):
        text = """
        coverage:
          covergroups:
          - name: cvg
            instances:
            - name: i1
              coverpoints:
              - name: cp1
                bins:
                - name: b0
                  count: 1
                - name: b1
                  count: 0
        """
        
        db = YamlReader().loads(text)
        rpt = CoverageReportBuilder.build(db)
        
        assert len(rpt.covergroups) == 1
        assert rpt.covergroups[0].name == "cvg"
        assert len(rpt.covergroups[0].coverpoints) == 1
        assert len(rpt.covergroups[0].coverpoints[0].bins) == 2
        assert rpt.covergroups[0].coverpoints[0].coverage == 50.0

    def test_type_cvg_2_cvp(self):
        text = """
        coverage:
          covergroups:
          - name: cvg
            instances:
            - name: i1
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
        
        db = YamlReader().loads(text)
        rpt = CoverageReportBuilder.build(db)
        
        assert len(rpt.covergroups) == 1
        assert rpt.covergroups[0].name == "cvg"
        assert len(rpt.covergroups[0].coverpoints) == 2
        assert len(rpt.covergroups[0].coverpoints[0].bins) == 2
        assert len(rpt.covergroups[0].coverpoints[1].bins) == 2
        assert rpt.covergroups[0].coverage == 75.0
        