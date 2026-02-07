"""
Clover XML format exporter for UCIS coverage data.

Clover is a coverage tool by Atlassian used for Java, PHP, and JavaScript.
This formatter exports UCIS coverage data in Clover XML format for integration
with Bamboo, Jenkins, and other CI/CD tools that support Clover.

Clover XML Structure:
  <coverage generated="..." clover="4.4.1">
    <project timestamp="..." name="...">
      <metrics statements="X" coveredstatements="Y"
               conditionals="X" coveredconditionals="Y"
               methods="X" coveredmethods="Y"
               elements="X" coveredelements="Y"
               complexity="X" loc="X" ncloc="X"/>
      <package name="...">
        <metrics statements="X" coveredstatements="Y"
                 conditionals="X" coveredconditionals="Y"
                 methods="X" coveredmethods="Y"
                 elements="X" coveredelements="Y"/>
        <file name="..." path="...">
          <metrics statements="X" coveredstatements="Y"
                   conditionals="X" coveredconditionals="Y"
                   methods="X" coveredmethods="Y"
                   elements="X" coveredelements="Y"/>
          <class name="...">
            <metrics statements="X" coveredstatements="Y"
                     conditionals="X" coveredconditionals="Y"
                     methods="X" coveredmethods="Y"
                     elements="X" coveredelements="Y"/>
            <line num="1" count="10" type="stmt" truecount="0" falsecount="0"/>
            <line num="2" count="5" type="cond" truecount="1" falsecount="1"/>
          </class>
        </file>
      </package>
    </project>
  </coverage>
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
import time


class CloverFormatter:
    """Format UCIS coverage data as Clover XML."""
    
    def format(self, db, fp):
        """
        Convert UCIS coverage data to Clover XML format.
        
        Args:
            db: UCIS database object
            fp: File pointer to write XML to
        """
        from ucis.report.coverage_report_builder import CoverageReportBuilder
        
        # Build coverage report
        coverage_report = CoverageReportBuilder.build(db)
        
        # Create root coverage element
        root = ET.Element('coverage',
                          generated=str(int(time.time())),
                          clover='4.4.1')
        
        # Create project element
        project = ET.SubElement(root, 'project',
                                timestamp=str(int(time.time())),
                                name='ucis_coverage')
        
        # Initialize project-level metrics
        proj_statements = 0
        proj_covered_statements = 0
        proj_conditionals = 0
        proj_covered_conditionals = 0
        proj_methods = 0
        proj_covered_methods = 0
        proj_complexity = 0
        proj_loc = 0
        
        # Process coverage data
        if coverage_report.covergroups:
            # Create package for functional coverage
            package = ET.SubElement(project, 'package', name='functional')
            
            pkg_statements = 0
            pkg_covered_statements = 0
            pkg_conditionals = 0
            pkg_covered_conditionals = 0
            pkg_methods = 0
            pkg_covered_methods = 0
            
            for covergroup in coverage_report.covergroups:
                cg_name = covergroup.name
                
                # Each covergroup becomes a file
                file_elem = ET.SubElement(package, 'file',
                                          name=f'{cg_name}.sv',
                                          path=f'functional/{cg_name}.sv')
                
                file_statements = 0
                file_covered_statements = 0
                file_conditionals = 0
                file_covered_conditionals = 0
                file_methods = 0
                file_covered_methods = 0
                
                # Each covergroup is also a class within the file
                class_elem = ET.SubElement(file_elem, 'class', name=cg_name)
                
                class_statements = 0
                class_covered_statements = 0
                class_conditionals = 0
                class_covered_conditionals = 0
                class_methods = 0
                class_covered_methods = 0
                
                line_num = 1
                
                # Process coverpoints
                if covergroup.coverpoints:
                    for coverpoint in covergroup.coverpoints:
                        class_methods += 1
                        if coverpoint.coverage > 0:
                            class_covered_methods += 1
                        
                        # Each bin becomes a line
                        for bin_item in coverpoint.bins:
                            count = bin_item.count
                            
                            # Treat bin as statement
                            class_statements += 1
                            if count > 0:
                                class_covered_statements += 1
                            
                            # Add line element (statement type)
                            line = ET.SubElement(class_elem, 'line',
                                                num=str(line_num),
                                                count=str(count),
                                                type='stmt',
                                                truecount='0',
                                                falsecount='0')
                            line_num += 1
                            
                            # Also count as conditional if bin represents a condition
                            class_conditionals += 1
                            if count > 0:
                                class_covered_conditionals += 1
                
                # Add class metrics
                class_elements = class_statements + class_conditionals + class_methods
                class_covered_elements = class_covered_statements + class_covered_conditionals + class_covered_methods
                
                self._add_metrics(class_elem,
                                 statements=class_statements,
                                 covered_statements=class_covered_statements,
                                 conditionals=class_conditionals,
                                 covered_conditionals=class_covered_conditionals,
                                 methods=class_methods,
                                 covered_methods=class_covered_methods,
                                 elements=class_elements,
                                 covered_elements=class_covered_elements)
                
                # Update file metrics (same as class in this case)
                file_statements = class_statements
                file_covered_statements = class_covered_statements
                file_conditionals = class_conditionals
                file_covered_conditionals = class_covered_conditionals
                file_methods = class_methods
                file_covered_methods = class_covered_methods
                
                # Add file metrics
                file_elements = file_statements + file_conditionals + file_methods
                file_covered_elements = file_covered_statements + file_covered_conditionals + file_covered_methods
                
                self._add_metrics(file_elem,
                                 statements=file_statements,
                                 covered_statements=file_covered_statements,
                                 conditionals=file_conditionals,
                                 covered_conditionals=file_covered_conditionals,
                                 methods=file_methods,
                                 covered_methods=file_covered_methods,
                                 elements=file_elements,
                                 covered_elements=file_covered_elements)
                
                # Update package totals
                pkg_statements += file_statements
                pkg_covered_statements += file_covered_statements
                pkg_conditionals += file_conditionals
                pkg_covered_conditionals += file_covered_conditionals
                pkg_methods += file_methods
                pkg_covered_methods += file_covered_methods
            
            # Add package metrics
            pkg_elements = pkg_statements + pkg_conditionals + pkg_methods
            pkg_covered_elements = pkg_covered_statements + pkg_covered_conditionals + pkg_covered_methods
            
            self._add_metrics(package,
                             statements=pkg_statements,
                             covered_statements=pkg_covered_statements,
                             conditionals=pkg_conditionals,
                             covered_conditionals=pkg_covered_conditionals,
                             methods=pkg_methods,
                             covered_methods=pkg_covered_methods,
                             elements=pkg_elements,
                             covered_elements=pkg_covered_elements)
            
            # Update project totals
            proj_statements = pkg_statements
            proj_covered_statements = pkg_covered_statements
            proj_conditionals = pkg_conditionals
            proj_covered_conditionals = pkg_covered_conditionals
            proj_methods = pkg_methods
            proj_covered_methods = pkg_covered_methods
            proj_loc = line_num - 1
        
        # Add project metrics
        proj_elements = proj_statements + proj_conditionals + proj_methods
        proj_covered_elements = proj_covered_statements + proj_covered_conditionals + proj_covered_methods
        
        self._add_metrics(project,
                         statements=proj_statements,
                         covered_statements=proj_covered_statements,
                         conditionals=proj_conditionals,
                         covered_conditionals=proj_covered_conditionals,
                         methods=proj_methods,
                         covered_methods=proj_covered_methods,
                         elements=proj_elements,
                         covered_elements=proj_covered_elements,
                         complexity=proj_complexity,
                         loc=proj_loc,
                         ncloc=proj_loc)
        
        # Convert to pretty-printed XML string and write to file
        xml_str = self._prettify(root)
        fp.write(xml_str)
    
    def _add_metrics(self, parent, statements=0, covered_statements=0,
                     conditionals=0, covered_conditionals=0,
                     methods=0, covered_methods=0,
                     elements=0, covered_elements=0,
                     complexity=None, loc=None, ncloc=None):
        """Add a metrics element to parent."""
        attrs = {
            'statements': str(statements),
            'coveredstatements': str(covered_statements),
            'conditionals': str(conditionals),
            'coveredconditionals': str(covered_conditionals),
            'methods': str(methods),
            'coveredmethods': str(covered_methods),
            'elements': str(elements),
            'coveredelements': str(covered_elements),
        }
        
        # Add optional attributes
        if complexity is not None:
            attrs['complexity'] = str(complexity)
        if loc is not None:
            attrs['loc'] = str(loc)
        if ncloc is not None:
            attrs['ncloc'] = str(ncloc)
        
        ET.SubElement(parent, 'metrics', **attrs)
    
    def _prettify(self, elem):
        """Return a pretty-printed XML string."""
        rough_string = ET.tostring(elem, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
