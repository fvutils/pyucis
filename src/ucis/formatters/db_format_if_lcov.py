"""FormatIfDb implementation for LCOV format."""
from ucis.rgy.format_if_db import FormatIfDb, FormatDescDb, FormatDbFlags, FormatCapabilities


class DbFormatIfLcov(FormatIfDb):
    """LCOV format: write-only (LCOV is a write-only report format)."""

    def create(self, filename=None):
        from ucis.mem import MemUCIS
        return MemUCIS()

    def read(self, file_or_filename):
        raise NotImplementedError(
            "LCOV is a write-only report format; reading LCOV is not supported"
        )

    def write(self, db, file_or_filename, ctx=None):
        from ucis.formatters.format_lcov import LcovFormatter
        formatter = LcovFormatter()
        with open(file_or_filename, "w") as fp:
            formatter.format(db, fp)
        if ctx:
            # LCOV cannot fully represent functional coverage; warn if the DB
            # contains any covergroups
            from ucis.report.coverage_report_builder import CoverageReportBuilder
            rpt = CoverageReportBuilder.build(db)
            if rpt and rpt.covergroups:
                ctx.warn(
                    "LCOV format maps functional coverage to pseudo-files; "
                    "data may not be tool-compatible"
                )

    @staticmethod
    def register(rgy):
        rgy.addDatabaseFormat(FormatDescDb(
            DbFormatIfLcov,
            name="lcov",
            description="Exports UCIS coverage data to LCOV .info format (write-only)",
            flags=FormatDbFlags.Write,
            capabilities=FormatCapabilities(
                can_read=False, can_write=True,
                functional_coverage=True,   # mapped to pseudo-files
                code_coverage=True,         # statement/line counts
                toggle_coverage=False,
                fsm_coverage=False,
                cross_coverage=False,
                assertions=False,
                history_nodes=True,         # test name from history
                design_hierarchy=False,
                ignore_illegal_bins=False,
                lossless=False,
            )))
