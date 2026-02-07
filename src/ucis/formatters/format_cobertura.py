"""
Cobertura Format Exporter

Exports UCIS coverage data to Cobertura XML format.
Cobertura format is widely used in Java/Jenkins ecosystems.
"""
from typing import TextIO
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom


class CoberturaFormatter:
    """
    Format UCIS data as Cobertura XML.
    
    Cobertura XML structure:
    <coverage>
      <sources>
        <source>/path/to/source</source>
      </sources>
      <packages>
        <package name="..." line-rate="..." branch-rate="...">
          <classes>
            <class name="..." filename="..." line-rate="..." branch-rate="...">
              <methods>
                <method name="..." signature="..." line-rate="..." branch-rate="...">
                  <lines>
                    <line number="..." hits="..." branch="..."/>
                  </lines>
                </method>
              </methods>
              <lines>
                <line number="..." hits="..." branch="..."/>
              </lines>
            </class>
          </classes>
        </package>
      </packages>
    </coverage>
    """
    
    def __init__(self):
        pass
        
    def format(self, db, output: TextIO):
        """
        Format database as Cobertura XML.
        
        Args:
            db: UCIS database
            output: Output file/stream
        """
        from ucis.report.coverage_report_builder import CoverageReportBuilder
        
        # Build coverage report
        report = CoverageReportBuilder.build(db)
        
        # Create XML structure
        root = self._create_coverage_element(report)
        
        # Add sources
        sources = SubElement(root, 'sources')
        SubElement(sources, 'source').text = '/functional'
        
        # Add packages
        packages = SubElement(root, 'packages')
        self._add_packages(packages, report)
        
        # Pretty print and write
        xml_str = self._prettify(root)
        output.write(xml_str)
    
    def _create_coverage_element(self, report) -> Element:
        """Create root coverage element."""
        line_rate = report.coverage / 100.0
        branch_rate = report.coverage / 100.0
        
        coverage = Element('coverage', {
            'line-rate': f'{line_rate:.4f}',
            'branch-rate': f'{branch_rate:.4f}',
            'lines-covered': '0',
            'lines-valid': '0',
            'branches-covered': '0',
            'branches-valid': '0',
            'complexity': '0',
            'version': '1.0',
            'timestamp': str(int(__import__('time').time())),
        })
        
        return coverage
    
    def _add_packages(self, packages: Element, report):
        """Add package elements."""
        if not report.covergroups:
            return
        
        # Create one package for all covergroups
        pkg = SubElement(packages, 'package', {
            'name': 'functional',
            'line-rate': f'{report.coverage / 100.0:.4f}',
            'branch-rate': f'{report.coverage / 100.0:.4f}',
            'complexity': '0',
        })
        
        classes = SubElement(pkg, 'classes')
        
        for cg in report.covergroups:
            self._add_class(classes, cg)
    
    def _add_class(self, classes: Element, cg):
        """Add a class element for a covergroup."""
        cls = SubElement(classes, 'class', {
            'name': cg.name,
            'filename': f'functional/{cg.name}.sv',
            'line-rate': f'{cg.coverage / 100.0:.4f}',
            'branch-rate': f'{cg.coverage / 100.0:.4f}',
            'complexity': '0',
        })
        
        methods = SubElement(cls, 'methods')
        lines = SubElement(cls, 'lines')
        
        line_num = 1
        
        if hasattr(cg, 'coverpoints') and cg.coverpoints:
            for cp in cg.coverpoints:
                # Add method for coverpoint
                method = SubElement(methods, 'method', {
                    'name': cp.name,
                    'signature': '()',
                    'line-rate': f'{cp.coverage / 100.0:.4f}',
                    'branch-rate': f'{cp.coverage / 100.0:.4f}',
                })
                
                method_lines = SubElement(method, 'lines')
                
                # Add lines for bins
                if hasattr(cp, 'bins') and cp.bins:
                    for bin in cp.bins:
                        SubElement(method_lines, 'line', {
                            'number': str(line_num),
                            'hits': str(bin.count),
                            'branch': 'true',
                        })
                        
                        # Also add to class lines
                        SubElement(lines, 'line', {
                            'number': str(line_num),
                            'hits': str(bin.count),
                            'branch': 'true',
                        })
                        
                        line_num += 1
    
    def _prettify(self, elem: Element) -> str:
        """Return pretty-printed XML string."""
        rough_string = tostring(elem, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
