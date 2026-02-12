"""
Format interface for HTML reports
"""
from ucis.rgy.format_if_rpt import FormatIfRpt, FormatDescRpt, FormatRptOutFlags
from ucis.ucis import UCIS
from ucis.formatters.format_html import HtmlFormatter


class FormatRptHtml(FormatIfRpt):
    """HTML report formatter interface for registry."""
    
    def __init__(self):
        self.include_source = True
        self.compress = True
        self.theme = 'light'
    
    @classmethod
    def register(cls, rgy):
        """Register HTML format with the format registry."""
        desc = FormatDescRpt(
            cls,
            name="html",
            out_flags=FormatRptOutFlags.Stream,
            description="Produces an interactive single-file HTML coverage report")
        rgy.addReportFormat(desc)
    
    def report(self, 
               db: UCIS,
               out,
               args):
        """Generate HTML report.
        
        Args:
            db: UCIS database
            out: Output file handle
            args: Additional arguments (unused)
        """
        formatter = HtmlFormatter(
            include_source=self.include_source,
            compress=self.compress,
            theme=self.theme
        )
        formatter.format(db, out)
