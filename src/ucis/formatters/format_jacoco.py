"""
JaCoCo XML format exporter for UCIS coverage data.

JaCoCo is a widely-used Java code coverage library. This formatter
exports UCIS coverage data in JaCoCo XML format for integration with
Maven, Gradle, SonarQube, and other Java ecosystem tools.

JaCoCo XML Structure:
  <report name="...">
    <sessioninfo id="..." start="..." dump="..."/>
    <package name="...">
      <class name="..." sourcefilename="...">
        <method name="..." desc="..." line="...">
          <counter type="INSTRUCTION" missed="X" covered="Y"/>
          <counter type="BRANCH" missed="X" covered="Y"/>
          <counter type="LINE" missed="X" covered="Y"/>
        </method>
        <counter type="INSTRUCTION" missed="X" covered="Y"/>
        <counter type="BRANCH" missed="X" covered="Y"/>
        <counter type="LINE" missed="X" covered="Y"/>
        <counter type="METHOD" missed="X" covered="Y"/>
        <counter type="CLASS" missed="0" covered="1"/>
      </class>
      <sourcefile name="...">
        <line nr="1" mi="0" ci="10" mb="0" cb="2"/>
        <counter type="INSTRUCTION" missed="X" covered="Y"/>
        <counter type="BRANCH" missed="X" covered="Y"/>
        <counter type="LINE" missed="X" covered="Y"/>
      </sourcefile>
      <counter type="INSTRUCTION" missed="X" covered="Y"/>
      <counter type="BRANCH" missed="X" covered="Y"/>
      <counter type="LINE" missed="X" covered="Y"/>
      <counter type="METHOD" missed="X" covered="Y"/>
      <counter type="CLASS" missed="X" covered="Y"/>
    </package>
    <counter type="INSTRUCTION" missed="X" covered="Y"/>
    <counter type="BRANCH" missed="X" covered="Y"/>
    <counter type="LINE" missed="X" covered="Y"/>
    <counter type="METHOD" missed="X" covered="Y"/>
    <counter type="CLASS" missed="X" covered="Y"/>
  </report>
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
import time


class JacocoFormatter:
    """Format UCIS coverage data as JaCoCo XML."""
    
    def format(self, db, fp):
        """
        Convert UCIS coverage data to JaCoCo XML format.
        
        Args:
            db: UCIS database object
            fp: File pointer to write XML to
        """
        from ucis.report.coverage_report_builder import CoverageReportBuilder
        
        # Build coverage report
        coverage_report = CoverageReportBuilder.build(db)
        
        # Create root report element
        root = ET.Element('report', name='ucis_coverage')
        
        # Add session info
        session = ET.SubElement(root, 'sessioninfo',
                                id='ucis-session',
                                start=str(int(time.time() * 1000)),
                                dump=str(int(time.time() * 1000)))
        
        # Initialize counters
        total_instructions_covered = 0
        total_instructions_missed = 0
        total_branches_covered = 0
        total_branches_missed = 0
        total_lines_covered = 0
        total_lines_missed = 0
        total_methods = 0
        total_classes = 0
        
        # Process coverage data
        if coverage_report.covergroups:
            # Create package element (use "functional" for UCIS coverage)
            package = ET.SubElement(root, 'package', name='functional')
            
            package_inst_cov = 0
            package_inst_miss = 0
            package_branch_cov = 0
            package_branch_miss = 0
            package_line_cov = 0
            package_line_miss = 0
            package_methods = 0
            package_classes = 0
            
            for covergroup in coverage_report.covergroups:
                cg_name = covergroup.name
                cg_coverage = covergroup.coverage
                
                # Each covergroup becomes a class
                class_elem = ET.SubElement(package, 'class',
                                          name=cg_name,
                                          sourcefilename=f'functional/{cg_name}.sv')
                
                class_inst_cov = 0
                class_inst_miss = 0
                class_branch_cov = 0
                class_branch_miss = 0
                class_line_cov = 0
                class_line_miss = 0
                class_methods = 0
                
                # Process coverpoints as methods
                if covergroup.coverpoints:
                    for idx, coverpoint in enumerate(covergroup.coverpoints):
                        cp_name = coverpoint.name
                        cp_coverage = coverpoint.coverage
                        
                        # Method element
                        method = ET.SubElement(class_elem, 'method',
                                             name=cp_name,
                                             desc='()',
                                             line=str(idx + 1))
                        
                        # Calculate counters from bins
                        bins = coverpoint.bins
                        covered_bins = sum(1 for b in bins if b.count > 0)
                        missed_bins = len(bins) - covered_bins
                        
                        # Each bin is treated as an instruction and line
                        inst_covered = covered_bins
                        inst_missed = missed_bins
                        line_covered = covered_bins
                        line_missed = missed_bins
                        
                        # Branch coverage (bins can represent branches)
                        branch_covered = covered_bins
                        branch_missed = missed_bins
                        
                        # Add method counters
                        self._add_counter(method, 'INSTRUCTION', inst_missed, inst_covered)
                        self._add_counter(method, 'BRANCH', branch_missed, branch_covered)
                        self._add_counter(method, 'LINE', line_missed, line_covered)
                        
                        # Update class totals
                        class_inst_cov += inst_covered
                        class_inst_miss += inst_missed
                        class_branch_cov += branch_covered
                        class_branch_miss += branch_missed
                        class_line_cov += line_covered
                        class_line_miss += line_missed
                        class_methods += 1
                
                # Add class counters
                self._add_counter(class_elem, 'INSTRUCTION', class_inst_miss, class_inst_cov)
                self._add_counter(class_elem, 'BRANCH', class_branch_miss, class_branch_cov)
                self._add_counter(class_elem, 'LINE', class_line_miss, class_line_cov)
                self._add_counter(class_elem, 'METHOD', 0 if class_methods > 0 else 1,
                                class_methods if class_methods > 0 else 0)
                self._add_counter(class_elem, 'CLASS', 0, 1)
                
                # Update package totals
                package_inst_cov += class_inst_cov
                package_inst_miss += class_inst_miss
                package_branch_cov += class_branch_cov
                package_branch_miss += class_branch_miss
                package_line_cov += class_line_cov
                package_line_miss += class_line_miss
                package_methods += class_methods
                package_classes += 1
            
            # Add package counters
            self._add_counter(package, 'INSTRUCTION', package_inst_miss, package_inst_cov)
            self._add_counter(package, 'BRANCH', package_branch_miss, package_branch_cov)
            self._add_counter(package, 'LINE', package_line_miss, package_line_cov)
            self._add_counter(package, 'METHOD', 0 if package_methods > 0 else 0, package_methods)
            self._add_counter(package, 'CLASS', 0 if package_classes > 0 else 0, package_classes)
            
            # Update report totals
            total_instructions_covered = package_inst_cov
            total_instructions_missed = package_inst_miss
            total_branches_covered = package_branch_cov
            total_branches_missed = package_branch_miss
            total_lines_covered = package_line_cov
            total_lines_missed = package_line_miss
            total_methods = package_methods
            total_classes = package_classes
        
        # Add report-level counters
        self._add_counter(root, 'INSTRUCTION', total_instructions_missed, total_instructions_covered)
        self._add_counter(root, 'BRANCH', total_branches_missed, total_branches_covered)
        self._add_counter(root, 'LINE', total_lines_missed, total_lines_covered)
        self._add_counter(root, 'METHOD', 0 if total_methods > 0 else 0, total_methods)
        self._add_counter(root, 'CLASS', 0 if total_classes > 0 else 0, total_classes)
        
        # Convert to pretty-printed XML string and write to file
        xml_str = self._prettify(root)
        fp.write(xml_str)
    
    def _add_counter(self, parent, counter_type, missed, covered):
        """Add a counter element to parent."""
        ET.SubElement(parent, 'counter',
                     type=counter_type,
                     missed=str(missed),
                     covered=str(covered))
    
    def _prettify(self, elem):
        """Return a pretty-printed XML string."""
        rough_string = ET.tostring(elem, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
