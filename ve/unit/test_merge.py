'''
Created on Nov 10, 2021

@author: mballance
'''
import sys
from io import StringIO
from unittest.case import TestCase

from ucis.mem.mem_factory import MemFactory
from ucis.mem.mem_ucis import MemUCIS
from ucis.report.coverage_report_builder import CoverageReportBuilder
from ucis.report.text_coverage_report_formatter import TextCoverageReportFormatter
from ucis.yaml.yaml_reader import YamlReader
from ucis.xml.xml_reader import XmlReader
from ucis.merge.db_merger import DbMerger


class TestMerge(TestCase):

    def test_null_type_cg_1_cp(self):
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
        
        src_db = YamlReader().loads(text)
        rpt = CoverageReportBuilder.build(src_db)
        
        self.assertEqual(len(rpt.covergroups), 1)
        self.assertEqual(rpt.covergroups[0].name, "cvg")
        self.assertEqual(len(rpt.covergroups[0].coverpoints), 1)
        self.assertEqual(len(rpt.covergroups[0].coverpoints[0].bins), 2)
        self.assertEqual(rpt.covergroups[0].coverpoints[0].coverage, 50.0)
        
        dst_db = MemFactory.create()

        merger = DbMerger()
        merger.merge(dst_db, [src_db])
        
        rpt = CoverageReportBuilder.build(dst_db)
        
        self.assertEqual(len(rpt.covergroups), 1)
        self.assertEqual(rpt.covergroups[0].name, "cvg")
        self.assertEqual(len(rpt.covergroups[0].coverpoints), 1)
        self.assertEqual(len(rpt.covergroups[0].coverpoints[0].bins), 2)
        self.assertEqual(rpt.covergroups[0].coverpoints[0].coverage, 50.0)

    def test_null_inst_cg_1_cp(self):
        text = """
        coverage:
          covergroups:
          - name: cvg
            
            instances:   
            - name: inst1
                  
              coverpoints:
              - name: cp1
                bins:
                - name: b0
                  count: 0
                - name: b1
                  count: 1
                             
            - name: inst2
                   
              coverpoints:
              - name: cp1
                bins:
                - name: b0
                  count: 1
                - name: b1
                  count: 0
        """
        
        src_db = YamlReader().loads(text)
        rpt = CoverageReportBuilder.build(src_db)
        
        self.assertEqual(len(rpt.covergroups), 1)
        self.assertEqual(rpt.covergroups[0].name, "cvg")
        self.assertEqual(len(rpt.covergroups[0].coverpoints), 1)
        self.assertEqual(len(rpt.covergroups[0].coverpoints[0].bins), 2)
        self.assertEqual(rpt.covergroups[0].coverpoints[0].coverage, 100.0)
        
        self.assertEqual(len(rpt.covergroups[0].covergroups), 2)
#        self.assertEqual(rpt.covergroups[0].name, "cvg")
        self.assertEqual(len(rpt.covergroups[0].covergroups[0].coverpoints), 1)
        self.assertEqual(len(rpt.covergroups[0].covergroups[0].coverpoints[0].bins), 2)
        self.assertEqual(rpt.covergroups[0].covergroups[0].coverpoints[0].coverage, 50.0)
        
#        self.assertEqual(rpt.covergroups[0].name, "cvg")
        self.assertEqual(len(rpt.covergroups[0].covergroups[1].coverpoints), 1)
        self.assertEqual(len(rpt.covergroups[0].covergroups[1].coverpoints[0].bins), 2)
        self.assertEqual(rpt.covergroups[0].covergroups[1].coverpoints[0].coverage, 50.0)
        
        dst_db = MemFactory.create()

        merger = DbMerger()
        merger.merge(dst_db, [src_db])
        
        rpt = CoverageReportBuilder.build(dst_db)
        
        self.assertEqual(len(rpt.covergroups), 1)
        self.assertEqual(rpt.covergroups[0].name, "cvg")
        self.assertEqual(len(rpt.covergroups[0].coverpoints), 1)
        self.assertEqual(len(rpt.covergroups[0].coverpoints[0].bins), 2)
        self.assertEqual(rpt.covergroups[0].coverpoints[0].coverage, 100.0)
        self.assertEqual(len(rpt.covergroups[0].covergroups), 2)
#        self.assertEqual(rpt.covergroups[0].name, "cvg")
        self.assertEqual(len(rpt.covergroups[0].covergroups[0].coverpoints), 1)
        self.assertEqual(len(rpt.covergroups[0].covergroups[0].coverpoints[0].bins), 2)
        self.assertEqual(rpt.covergroups[0].covergroups[0].coverpoints[0].coverage, 50.0)
        
        self.assertEqual(len(rpt.covergroups[0].covergroups[1].coverpoints), 1)
        self.assertEqual(len(rpt.covergroups[0].covergroups[1].coverpoints[0].bins), 2)
        self.assertEqual(rpt.covergroups[0].covergroups[1].coverpoints[0].coverage, 50.0)


    def test_2db_1t_2i(self):
        cvg1 = """
        coverage:
          covergroups:
          - name: cvg
            
            instances:   
            - name: inst1
              coverpoints:
              - name: cp1
                bins:
                - name: b0
                  count: 0
                - name: b1
                  count: 1
                             
        """
        
        cvg2 = """
        coverage:
          covergroups:
          - name: cvg
            
            instances:   
            - name: inst2
              coverpoints:
              - name: cp1
                bins:
                - name: b0
                  count: 1
                - name: b1
                  count: 0
        """
        
        src1_db = YamlReader().loads(cvg1)
        src2_db = YamlReader().loads(cvg2)
        
        dst_db = MemFactory.create()

        merger = DbMerger()
        merger.merge(dst_db, [src1_db, src2_db])
        
        rpt = CoverageReportBuilder.build(dst_db)
        
        self.assertEqual(len(rpt.covergroups), 1)
        self.assertEqual(rpt.covergroups[0].name, "cvg")
        self.assertEqual(len(rpt.covergroups[0].coverpoints), 1)
        self.assertEqual(len(rpt.covergroups[0].coverpoints[0].bins), 2)
        self.assertEqual(rpt.covergroups[0].coverpoints[0].coverage, 100.0)
        self.assertEqual(len(rpt.covergroups[0].covergroups), 2)
#        self.assertEqual(rpt.covergroups[0].name, "cvg")
        self.assertEqual(len(rpt.covergroups[0].covergroups[0].coverpoints), 1)
        self.assertEqual(len(rpt.covergroups[0].covergroups[0].coverpoints[0].bins), 2)
        self.assertEqual(rpt.covergroups[0].covergroups[0].coverpoints[0].coverage, 50.0)
        
        self.assertEqual(len(rpt.covergroups[0].covergroups[1].coverpoints), 1)
        self.assertEqual(len(rpt.covergroups[0].covergroups[1].coverpoints[0].bins), 2)
        self.assertEqual(rpt.covergroups[0].covergroups[1].coverpoints[0].coverage, 50.0)

    def test_2db_1t_1i(self):
        cvg1 = """
        coverage:
          covergroups:
          - name: cvg
            
            instances:   
            - name: inst1
              coverpoints:
              - name: cp1
                bins:
                - name: b0
                  count: 0
                - name: b1
                  count: 1
                             
        """
        
        cvg2 = """
        coverage:
          covergroups:
          - name: cvg
            
            instances:   
            - name: inst1
              coverpoints:
              - name: cp1
                bins:
                - name: b0
                  count: 1
                - name: b1
                  count: 0
        """
        
        src1_db = YamlReader().loads(cvg1)
        src2_db = YamlReader().loads(cvg2)
        
        dst_db = MemFactory.create()

        merger = DbMerger()
        merger.merge(dst_db, [src1_db, src2_db])
        
        rpt = CoverageReportBuilder.build(dst_db)
        
        self.assertEqual(len(rpt.covergroups), 1)
        self.assertEqual(rpt.covergroups[0].name, "cvg")
        self.assertEqual(len(rpt.covergroups[0].coverpoints), 1)
        self.assertEqual(len(rpt.covergroups[0].coverpoints[0].bins), 2)
        self.assertEqual(rpt.covergroups[0].coverpoints[0].coverage, 100.0)
        self.assertEqual(len(rpt.covergroups[0].covergroups), 1)

        self.assertEqual(len(rpt.covergroups[0].covergroups[0].coverpoints), 1)
        self.assertEqual(len(rpt.covergroups[0].covergroups[0].coverpoints[0].bins), 2)
        self.assertEqual(rpt.covergroups[0].covergroups[0].coverpoints[0].coverage, 100.0)

    def test_3db_1t_2i(self):
        cvg1 = """
        coverage:
          covergroups:
          - name: cvg
            
            instances:   
            - name: inst1
              coverpoints:
              - name: cp1
                bins:
                - name: b0
                  count: 0
                - name: b1
                  count: 1
                             
        """
        
        cvg2 = """
        coverage:
          covergroups:
          - name: cvg
            
            instances:   
            - name: inst1
              coverpoints:
              - name: cp1
                bins:
                - name: b0
                  count: 1
                - name: b1
                  count: 0
        """
        
        cvg3 = """
        coverage:
          covergroups:
          - name: cvg
            
            instances:   
            - name: inst2
              coverpoints:
              - name: cp1
                bins:
                - name: b0
                  count: 1
                - name: b1
                  count: 0
        """
        
        src1_db = YamlReader().loads(cvg1)
        src2_db = YamlReader().loads(cvg2)
        src3_db = YamlReader().loads(cvg3)
        
        dst_db = MemFactory.create()

        merger = DbMerger()
        merger.merge(dst_db, [src1_db, src2_db, src3_db])
        
        rpt = CoverageReportBuilder.build(dst_db)
        
        self.assertEqual(len(rpt.covergroups), 1)
        self.assertEqual(rpt.covergroups[0].name, "cvg")
        self.assertEqual(len(rpt.covergroups[0].coverpoints), 1)
        self.assertEqual(len(rpt.covergroups[0].coverpoints[0].bins), 2)
        self.assertEqual(rpt.covergroups[0].coverpoints[0].coverage, 100.0)
        self.assertEqual(len(rpt.covergroups[0].covergroups), 2)

        self.assertEqual(len(rpt.covergroups[0].covergroups[0].coverpoints), 1)
        self.assertEqual(len(rpt.covergroups[0].covergroups[0].coverpoints[0].bins), 2)
        self.assertEqual(rpt.covergroups[0].covergroups[0].coverpoints[0].coverage, 100.0)        
        
        self.assertEqual(len(rpt.covergroups[0].covergroups[1].coverpoints), 1)
        self.assertEqual(len(rpt.covergroups[0].covergroups[1].coverpoints[0].bins), 2)
        self.assertEqual(rpt.covergroups[0].covergroups[1].coverpoints[0].coverage, 50.0)

    def test_3db_2t_1i(self):
        cvg1 = """
        coverage:
          covergroups:
          - name: cvg
            
            instances:   
            - name: inst1
              coverpoints:
              - name: cp1
                bins:
                - name: b0
                  count: 0
                - name: b1
                  count: 1
                             
        """
        
        cvg2 = """
        coverage:
          covergroups:
          - name: cvg
            
            instances:   
            - name: inst1
              coverpoints:
              - name: cp1
                bins:
                - name: b0
                  count: 1
                - name: b1
                  count: 0
        """
        
        cvg3 = """
        coverage:
          covergroups:
          - name: cvg2
            
            instances:   
            - name: inst1
              coverpoints:
              - name: cp1
                bins:
                - name: b0
                  count: 1
                - name: b1
                  count: 0
        """
        
        src1_db = YamlReader().loads(cvg1)
        src2_db = YamlReader().loads(cvg2)
        src3_db = YamlReader().loads(cvg3)
        
        dst_db = MemFactory.create()

        merger = DbMerger()
        merger.merge(dst_db, [src1_db, src2_db, src3_db])
        
        rpt = CoverageReportBuilder.build(dst_db)
        
        self.assertEqual(len(rpt.covergroups), 2)
        self.assertEqual(rpt.covergroups[0].name, "cvg")
        self.assertEqual(len(rpt.covergroups[0].coverpoints), 1)
        self.assertEqual(len(rpt.covergroups[0].coverpoints[0].bins), 2)
        self.assertEqual(rpt.covergroups[0].coverpoints[0].coverage, 100.0)
        self.assertEqual(len(rpt.covergroups[0].covergroups), 1)

        self.assertEqual(len(rpt.covergroups[0].covergroups[0].coverpoints), 1)
        self.assertEqual(len(rpt.covergroups[0].covergroups[0].coverpoints[0].bins), 2)
        self.assertEqual(rpt.covergroups[0].covergroups[0].coverpoints[0].coverage, 100.0)        
        
        self.assertEqual(rpt.covergroups[1].name, "cvg2")
        self.assertEqual(len(rpt.covergroups[1].covergroups), 1)
        self.assertEqual(len(rpt.covergroups[1].covergroups[0].coverpoints), 1)
        self.assertEqual(len(rpt.covergroups[1].covergroups[0].coverpoints[0].bins), 2)
        self.assertEqual(rpt.covergroups[1].covergroups[0].coverpoints[0].coverage, 50.0)

    def test_1db_2ci_2cp_1cr(self):
        text = """
        coverage:
          covergroups:
          - name: cvg
            
            instances:
            - name: inst1
              coverpoints:
              - name: cp1
                bins:
                - name: b0
                  count: 0
                - name: b1
                  count: 1
              - name: cp2
                bins:
                - name: b0
                  count: 0
                - name: b1
                  count: 1
              crosses:
              - name: cp1xc2
                coverpoints: ["cp1", "cp2"]
                bins:
                - name: "<b0,b0>"
                  count: 0
                - name: "<b0,b1>"
                  count: 0
                - name: "<b1,b0>"
                  count: 0
                - name: "<b1,b1>"
                  count: 1
                             
            - name: inst2
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
                  count: 0
              crosses:
              - name: cp1xc2
                coverpoints: ["cp1", "cp2"]
                bins:
                - name: "<b0,b0>"
                  count: 1
                - name: "<b0,b1>"
                  count: 0
                - name: "<b1,b0>"
                  count: 0
                - name: "<b1,b1>"
                  count: 0
        """
        
        src_db = YamlReader().loads(text)
        rpt = CoverageReportBuilder.build(src_db)
        
        self.assertEqual(len(rpt.covergroups), 1)
        self.assertEqual(rpt.covergroups[0].name, "cvg")
        self.assertEqual(len(rpt.covergroups[0].coverpoints), 2)
        self.assertEqual(len(rpt.covergroups[0].coverpoints[0].bins), 2)
        self.assertEqual(rpt.covergroups[0].coverpoints[0].coverage, 100.0)
        self.assertEqual(len(rpt.covergroups[0].crosses), 1)
        self.assertEqual(len(rpt.covergroups[0].crosses[0].bins), 4)
        self.assertEqual(rpt.covergroups[0].crosses[0].coverage, 50.0)
        
        self.assertEqual(len(rpt.covergroups[0].covergroups), 2)
#        self.assertEqual(rpt.covergroups[0].name, "cvg")
        self.assertEqual(len(rpt.covergroups[0].covergroups[0].coverpoints), 2)
        self.assertEqual(len(rpt.covergroups[0].covergroups[0].coverpoints[0].bins), 2)
        self.assertEqual(rpt.covergroups[0].covergroups[0].coverpoints[0].coverage, 50.0)
        self.assertEqual(len(rpt.covergroups[0].covergroups[0].coverpoints[1].bins), 2)
        self.assertEqual(rpt.covergroups[0].covergroups[0].coverpoints[1].coverage, 50.0)
        self.assertEqual(len(rpt.covergroups[0].covergroups[0].crosses), 1)
        self.assertEqual(len(rpt.covergroups[0].covergroups[0].crosses[0].bins), 4)
        self.assertEqual(round(rpt.covergroups[0].covergroups[0].crosses[0].coverage,2), 25.0)
        
#        self.assertEqual(rpt.covergroups[0].name, "cvg")
        self.assertEqual(len(rpt.covergroups[0].covergroups[1].coverpoints), 2)
        self.assertEqual(len(rpt.covergroups[0].covergroups[1].coverpoints[0].bins), 2)
        self.assertEqual(rpt.covergroups[0].covergroups[1].coverpoints[0].coverage, 50.0)
        
        dst_db = MemFactory.create()

        from ucis.xml.xml_writer import XmlWriter
        from ucis.xml.xml_reader import XmlReader
        from io import StringIO


        merger = DbMerger()
        merger.merge(dst_db, [src_db])

        # writer = XmlWriter()
        # cov = StringIO()
        # writer.write(cov, dst_db)        
        # print("Result:\n%s\n" % cov.getvalue())
        # reader = XmlReader()
        # dst_db_p = reader.read(StringIO(cov.getvalue()))

        # from ucis.report.text_coverage_report_formatter import TextCoverageReportFormatter

        # rpt_p = CoverageReportBuilder.build(dst_db_p)
        # rpt_s_p = StringIO()
        # rpt_fmt = TextCoverageReportFormatter(rpt_p, rpt_s_p)
        # rpt_fmt.report()
        # print("Final report:\n%s\n" % rpt_s_p.getvalue())
        
        rpt = CoverageReportBuilder.build(dst_db)
        
        self.assertEqual(len(rpt.covergroups), 1)
        self.assertEqual(rpt.covergroups[0].name, "cvg")
        self.assertEqual(len(rpt.covergroups[0].coverpoints), 2)
        self.assertEqual(len(rpt.covergroups[0].coverpoints[0].bins), 2)
        self.assertEqual(rpt.covergroups[0].coverpoints[0].coverage, 100.0)
        self.assertEqual(len(rpt.covergroups[0].covergroups), 2)
#        self.assertEqual(rpt.covergroups[0].name, "cvg")
        self.assertEqual(len(rpt.covergroups[0].covergroups[0].coverpoints), 2)
        self.assertEqual(len(rpt.covergroups[0].covergroups[0].coverpoints[0].bins), 2)
        self.assertEqual(rpt.covergroups[0].covergroups[0].coverpoints[0].coverage, 50.0)
        
        self.assertEqual(len(rpt.covergroups[0].covergroups[1].coverpoints), 2)
        self.assertEqual(len(rpt.covergroups[0].covergroups[1].coverpoints[0].bins), 2)
        self.assertEqual(rpt.covergroups[0].covergroups[1].coverpoints[0].coverage, 50.0)


    def test_2db_2ci_2cp_1cr_xml(self):
        db1_src = """
<UCIS xmlns:ucis="http://www.w3.org/2001/XMLSchema-instance" writtenBy="apaiva" writtenTime="2024-09-20T00:00:00" ucisVersion="1.0">
  <sourceFiles fileName="__null__file__" id="1"/>
  <sourceFiles fileName="&lt;unknown&gt;" id="2"/>
  <sourceFiles fileName="/xxx/agents/l1_client_fcov.py" id="3"/>
  <sourceFiles fileName="/xxx/agents/fpu/fpu_fcov.py" id="4"/>
  <sourceFiles fileName="/xxx/instrn/instrn_fcov/instrn_fcov.py" id="5"/>
  <sourceFiles fileName="/xxx/agents/unpack/unpack_fcov.py" id="6"/>
  <sourceFiles fileName="/xxx/agents/pack/pack_fcov.py" id="7"/>
  <historyNodes historyNodeId="0" logicalName="logicalName" physicalName="foo.ucis" kind="HistoryNodeKind.TEST" testStatus="true" simtime="0.0" timeunit="ns" runCwd="." cpuTime="0.0" seed="0" cmd="" args="" compulsory="0" date="2024-09-20T22:19:22" userName="user" cost="0.0" toolCategory="UCIS:simulator" ucisVersion="1.0" vendorId="unknown" vendorTool="unknown" vendorToolVersion="unknown"/>
  <instanceCoverages name="cg_inst" key="0">
    <id file="1" line="1" inlineCount="1"/>
    <covergroupCoverage>
      <cgInstance name="L1ClientOp" key="0">
        <options/>
        <coverpoint name="cp_101_in_fmt" key="0">
          <options/>
          <coverpointBin name="T6TensorStorageType.Float32" type="bins" key="0">
            <range from="-1" to="-1">
              <contents coverageCount="0"/>
            </range>
          </coverpointBin>
        </coverpoint>
        <coverpoint name="cp_blk_id" key="0">
          <options/>
          <coverpointBin name="cp_blk_id[0]" type="bins" key="0">
            <range from="-1" to="-1">
              <contents coverageCount="5"/>
            </range>
          </coverpointBin>
        </coverpoint>
        <cross name="cc_101_in_fmt_X_upk_id" key="0">
          <options/>
          <crossExpr>cp_101_in_fmt</crossExpr>
          <crossExpr>cp_blk_id</crossExpr>
          <crossBin name="&lt;T6TensorStorageType.Float32,cp_blk_id[0]&gt;" key="0" type="default">
            <index>-1</index>
            <contents coverageCount="0"/>
          </crossBin>
          <crossBin name="&lt;T6TensorStorageType.Float32,cp_blk_id[1]&gt;" key="0" type="default">
            <index>-1</index>
            <contents coverageCount="0"/>
          </crossBin>
        </cross>
      </cgInstance>
    </covergroupCoverage>
  </instanceCoverages>
</UCIS>
        """
        db2_src = """
<UCIS xmlns:ucis="http://www.w3.org/2001/XMLSchema-instance" writtenBy="apaiva" writtenTime="2024-09-20T00:00:00" ucisVersion="1.0">
  <sourceFiles fileName="__null__file__" id="1"/>
  <sourceFiles fileName="&lt;unknown&gt;" id="2"/>
  <sourceFiles fileName="/xxx/agents/l1_client_fcov.py" id="3"/>
  <sourceFiles fileName="/xxx/agents/fpu/fpu_fcov.py" id="4"/>
  <sourceFiles fileName="/xxx/instrn/instrn_fcov/instrn_fcov.py" id="5"/>
  <sourceFiles fileName="/xxx/agents/unpack/unpack_fcov.py" id="6"/>
  <sourceFiles fileName="/xxx/agents/pack/pack_fcov.py" id="7"/>
  <historyNodes historyNodeId="0" logicalName="logicalName" physicalName="foo.ucis" kind="HistoryNodeKind.TEST" testStatus="true" simtime="0.0" timeunit="ns" runCwd="." cpuTime="0.0" seed="0" cmd="" args="" compulsory="0" date="2024-09-20T22:19:22" userName="user" cost="0.0" toolCategory="UCIS:simulator" ucisVersion="1.0" vendorId="unknown" vendorTool="unknown" vendorToolVersion="unknown"/>
  <instanceCoverages name="cg_inst" key="0">
    <id file="1" line="1" inlineCount="1"/>
    <covergroupCoverage>
      <cgInstance name="L1ClientOp" key="0">
        <options/>
        <coverpoint name="cp_101_in_fmt" key="0">
          <options/>
          <coverpointBin name="T6TensorStorageType.Float32" type="bins" key="0">
            <range from="-1" to="-1">
              <contents coverageCount="0"/>
            </range>
          </coverpointBin>
        </coverpoint>
        <coverpoint name="cp_blk_id" key="0">
          <options/>
          <coverpointBin name="cp_blk_id[0]" type="bins" key="0">
            <range from="-1" to="-1">
              <contents coverageCount="5"/>
            </range>
          </coverpointBin>
          <coverpointBin name="cp_blk_id[1]" type="bins" key="0">
            <range from="-1" to="-1">
              <contents coverageCount="5"/>
            </range>
          </coverpointBin>
        </coverpoint>
        <cross name="cc_101_in_fmt_X_upk_id" key="0">
          <options/>
          <crossExpr>cp_101_in_fmt</crossExpr>
          <crossExpr>cp_blk_id</crossExpr>
          <crossBin name="&lt;T6TensorStorageType.Float32,cp_blk_id[0]&gt;" key="0" type="default">
            <index>-1</index>
            <contents coverageCount="0"/>
          </crossBin>
          <crossBin name="&lt;T6TensorStorageType.Float32,cp_blk_id[1]&gt;" key="0" type="default">
            <index>-1</index>
            <contents coverageCount="0"/>
          </crossBin>
        </cross>
      </cgInstance>
    </covergroupCoverage>
  </instanceCoverages>
</UCIS>
        """

        src_db = []
        src_db.append(XmlReader().loads(db1_src))
        src_db.append(XmlReader().loads(db2_src))

        rpt = CoverageReportBuilder.build(src_db[0])

        dst_db = MemFactory.create()

        merger = DbMerger()
        merger.merge(dst_db, src_db)

        self.assertEqual(len(dst_db.m_children), 2)
        self.assertEqual(len(dst_db.m_children[1].m_children[0].m_children), 4)
        self.assertEqual(len(dst_db.m_children[1].m_children[0].m_children[2].coverpoints), 2)
        self.assertEqual(len(dst_db.m_children[1].m_children[0].m_children[3].m_children[2].coverpoints), 2)

    def test_2db_2ci_2cp_1cr(self):
        db1_src = """
        coverage:
          covergroups:
          - name: cvg
            instances:
            - name: inst1
              coverpoints:
              - name: cp1
                bins:
                - { name: b0, count: 1 }
                - { name: b1, count: 0 }
              - name: cp2
                bins:
                - { name: b0, count: 1 }
                - { name: b1, count: 0 }
              crosses:
              - name: cp1xc2
                coverpoints: ["cp1", "cp2"]
                bins:
                - { name: "<b0,b0>", count: 1 }
                - { name: "<b0,b1>", count: 0 }
                - { name: "<b1,b0>", count: 0 }
                - { name: "<b1,b1>", count: 0 }
                             
            - name: inst2
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
                  count: 0
                - name: b1
                  count: 1
              crosses:
              - name: cp1xc2
                coverpoints: ["cp1", "cp2"]
                bins:
                - { name: "<b0,b0>", count: 0 }
                - { name: "<b0,b1>", count: 1 }
                - { name: "<b1,b0>", count: 0 }
                - { name: "<b1,b1>", count: 0 }
        """

        db2_src = """
        coverage:
          covergroups:
          - name: cvg
            instances:
            - name: inst1
              coverpoints:
              - name: cp1
                bins:
                - { name: b0, count: 0 }
                - { name: b1, count: 1 }
              - name: cp2
                bins:
                - { name: b0, count: 1 }
                - { name: b1, count: 0 }
              crosses:
              - name: cp1xc2
                coverpoints: ["cp1", "cp2"]
                bins:
                - { name: "<b0,b0>", count: 0 }
                - { name: "<b0,b1>", count: 0 }
                - { name: "<b1,b0>", count: 1 }
                - { name: "<b1,b1>", count: 0 }
                             
            - name: inst2
              coverpoints:
              - name: cp1
                bins:
                - { name: b0, count: 0 }
                - { name: b1, count: 1 }
              - name: cp2
                bins:
                - { name: b0, count: 0 }
                - { name: b1, count: 1 }
              crosses:
              - name: cp1xc2
                coverpoints: ["cp1", "cp2"]
                bins:
                - { name: "<b0,b0>", count: 0 }
                - { name: "<b0,b1>", count: 0 }
                - { name: "<b1,b0>", count: 0 }
                - { name: "<b1,b1>", count: 1 }
        """

        src_db = []
        src_db.append(YamlReader().loads(db1_src))
        src_db.append(YamlReader().loads(db2_src))

        rpt = CoverageReportBuilder.build(src_db[0])
        self.assertEqual(len(rpt.covergroups), 1)
        self.assertEqual(rpt.covergroups[0].name, "cvg")
        self.assertEqual(len(rpt.covergroups[0].coverpoints), 2)
        self.assertEqual(len(rpt.covergroups[0].coverpoints[0].bins), 2)
        self.assertEqual(rpt.covergroups[0].coverpoints[0].coverage, 50.0)
        self.assertEqual(len(rpt.covergroups[0].crosses), 1)
        
        dst_db = MemFactory.create()

        merger = DbMerger()
        merger.merge(dst_db, src_db)
        
        rpt = CoverageReportBuilder.build(dst_db)
#        formatter = TextCoverageReportFormatter(rpt, sys.stdout)
#        formatter.details = True
#        formatter.report()
        
        self.assertEqual(len(rpt.covergroups), 1)
        self.assertEqual(rpt.covergroups[0].name, "cvg")
        self.assertEqual(len(rpt.covergroups[0].coverpoints), 2)
        self.assertEqual(len(rpt.covergroups[0].coverpoints[0].bins), 2)
        self.assertEqual(rpt.covergroups[0].coverpoints[0].coverage, 100.0)
        self.assertEqual(len(rpt.covergroups[0].crosses), 1)
        self.assertEqual(rpt.covergroups[0].crosses[0].coverage, 100.0)

        # inst1
        self.assertEqual(len(rpt.covergroups[0].covergroups), 2)
        self.assertEqual(rpt.covergroups[0].covergroups[0].name, "inst1")
        self.assertEqual(len(rpt.covergroups[0].covergroups[0].coverpoints), 2)
        self.assertEqual(len(rpt.covergroups[0].covergroups[0].coverpoints[0].bins), 2)
        self.assertEqual(rpt.covergroups[0].covergroups[0].coverpoints[0].coverage, 100.0)
        self.assertEqual(rpt.covergroups[0].covergroups[0].coverpoints[1].coverage, 50.0)
        self.assertEqual(len(rpt.covergroups[0].covergroups[0].crosses), 1)
        self.assertEqual(rpt.covergroups[0].covergroups[0].crosses[0].coverage, 50.0)
        
        self.assertEqual(len(rpt.covergroups[0].covergroups[1].coverpoints), 2)
        self.assertEqual(len(rpt.covergroups[0].covergroups[1].coverpoints[0].bins), 2)
        self.assertEqual(rpt.covergroups[0].covergroups[1].coverpoints[0].coverage, 100.0)

