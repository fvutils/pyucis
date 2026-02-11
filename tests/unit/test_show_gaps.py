"""
Tests for UCIS show gaps command
"""
import json
import pytest

from .db_creator import DbCreator
from ucis.cmd.show.show_gaps import ShowGaps


class TestShowGaps:
    """Test suite for show gaps command."""
    
    def test_gaps_basic_structure(self):
        """Test that gaps produces expected data structure."""
        db_creator = DbCreator()
        
        db_creator.dummy_test_data()
        inst = db_creator.dummy_instance()
        
        # Create covergroup with some gaps
        db_creator.create_covergroup(
            inst,
            "cg_test",
            dict(
                coverpoints=dict(
                    cp_a = dict(
                        bins=[
                            ("bin1", 10),  # covered
                            ("bin2", 0),   # gap
                            ("bin3", 5),   # covered
                        ]
                    )
                )
            )
        )
        
        class Args:
            def __init__(self):
                self.db = None
                self.input_format = 'mem'
                self.output_format = 'json'
                self.out = None
                self.threshold = None
        
        args = Args()
        cmd = ShowGaps(args)
        cmd.db = db_creator.db
        data = cmd.get_data()
        
        # Verify structure
        assert 'summary' in data
        assert 'uncovered_bins' in data
        
        # Verify summary
        summary = data['summary']
        assert summary['total_bins'] == 3
        assert summary['covered_bins'] == 2
        assert summary['uncovered_bins'] == 1
        
        # Verify uncovered bins list
        uncovered = data['uncovered_bins']
        assert len(uncovered) == 1
        assert uncovered[0]['bin'] == 'bin2'
        assert uncovered[0]['count'] == 0
        
    def test_gaps_multiple_covergroups(self):
        """Test gaps with multiple covergroups."""
        db_creator = DbCreator()
        
        db_creator.dummy_test_data()
        inst = db_creator.dummy_instance()
        
        # First covergroup with gaps
        db_creator.create_covergroup(
            inst,
            "cg_1",
            dict(
                coverpoints=dict(
                    cp_a = dict(
                        bins=[
                            ("bin1", 1),
                            ("bin2", 0),  # gap
                        ]
                    )
                )
            )
        )
        
        # Second covergroup with gaps
        db_creator.create_covergroup(
            inst,
            "cg_2",
            dict(
                coverpoints=dict(
                    cp_b = dict(
                        bins=[
                            ("bin1", 0),  # gap
                            ("bin2", 0),  # gap
                            ("bin3", 1),
                        ]
                    )
                )
            )
        )
        
        class Args:
            def __init__(self):
                self.db = None
                self.input_format = 'mem'
                self.output_format = 'json'
                self.out = None
                self.threshold = None
        
        args = Args()
        cmd = ShowGaps(args)
        cmd.db = db_creator.db
        data = cmd.get_data()
        
        # Should find 3 gaps total
        assert len(data['uncovered_bins']) == 3
        assert data['summary']['uncovered_bins'] == 3
        assert data['summary']['total_bins'] == 5
        
    def test_gaps_fully_covered(self):
        """Test gaps when everything is covered."""
        db_creator = DbCreator()
        
        db_creator.dummy_test_data()
        inst = db_creator.dummy_instance()
        
        # All bins covered
        db_creator.create_covergroup(
            inst,
            "cg_full",
            dict(
                coverpoints=dict(
                    cp_a = dict(
                        bins=[
                            ("bin1", 10),
                            ("bin2", 5),
                            ("bin3", 1),
                        ]
                    )
                )
            )
        )
        
        class Args:
            def __init__(self):
                self.db = None
                self.input_format = 'mem'
                self.output_format = 'json'
                self.out = None
                self.threshold = None
        
        args = Args()
        cmd = ShowGaps(args)
        cmd.db = db_creator.db
        data = cmd.get_data()
        
        # No gaps
        assert len(data['uncovered_bins']) == 0
        assert data['summary']['uncovered_bins'] == 0
        assert data['summary']['overall_coverage'] == 100.0
        
    def test_gaps_threshold_filter(self):
        """Test threshold filtering."""
        db_creator = DbCreator()
        
        db_creator.dummy_test_data()
        inst = db_creator.dummy_instance()
        
        # Covergroup with partial coverage (50%)
        db_creator.create_covergroup(
            inst,
            "cg_partial",
            dict(
                coverpoints=dict(
                    cp_a = dict(
                        bins=[
                            ("bin1", 1),
                            ("bin2", 0),  # gap
                        ]
                    )
                )
            )
        )
        
        # Covergroup with full coverage (100%)
        db_creator.create_covergroup(
            inst,
            "cg_full",
            dict(
                coverpoints=dict(
                    cp_b = dict(
                        bins=[
                            ("bin1", 1),
                            ("bin2", 1),
                        ]
                    )
                )
            )
        )
        
        class Args:
            def __init__(self):
                self.db = None
                self.input_format = 'mem'
                self.output_format = 'json'
                self.out = None
                self.threshold = 75.0  # Only show coverpoints < 75%
        
        args = Args()
        cmd = ShowGaps(args)
        cmd.db = db_creator.db
        data = cmd.get_data()
        
        # Should only show gap from partial coverpoint (50% < 75%)
        assert len(data['uncovered_bins']) == 1
        assert data['uncovered_bins'][0]['coverpoint'] == 'cp_a'
        
        # Verify filter metadata
        assert 'filter' in data
        assert data['filter']['threshold'] == 75.0
