"""
Tests for UCIS show summary command
"""
import json
import os
import tempfile
from unittest.case import TestCase
from io import StringIO
import sys

from db_creator import DbCreator
from ucis.cmd.show.show_summary import ShowSummary


class TestShowSummary(TestCase):
    """Test suite for show summary command."""
    
    def test_summary_basic_structure(self):
        """Test that summary produces expected data structure."""
        db_creator = DbCreator()
        
        # Create test data
        db_creator.dummy_test_data()
        inst = db_creator.dummy_instance()
        
        # Create a simple covergroup
        db_creator.create_covergroup(
            inst,
            "cg_test",
            dict(
                coverpoints=dict(
                    cp_a = dict(
                        bins=[
                            ("bin1", 10),
                            ("bin2", 5),
                            ("bin3", 0),
                        ]
                    )
                )
            )
        )
        
        # Mock args
        class Args:
            def __init__(self):
                self.db = None
                self.input_format = 'mem'
                self.output_format = 'json'
                self.out = None
        
        args = Args()
        
        # Create command and get data
        cmd = ShowSummary(args)
        cmd.db = db_creator.db
        data = cmd.get_data()
        
        # Verify structure
        self.assertIn('overall_coverage', data)
        self.assertIn('coverage_by_type', data)
        self.assertIn('statistics', data)
        self.assertIn('tests', data)
        
        # Verify coverage calculation
        self.assertIsInstance(data['overall_coverage'], (int, float))
        
        # Verify statistics
        stats = data['statistics']
        self.assertEqual(stats['total_covergroups'], 1)
        self.assertEqual(stats['total_coverpoints'], 1)
        self.assertEqual(stats['total_bins'], 3)
        self.assertEqual(stats['covered_bins'], 2)  # bin1 and bin2 are covered
        
    def test_summary_multiple_covergroups(self):
        """Test summary with multiple covergroups."""
        db_creator = DbCreator()
        
        db_creator.dummy_test_data()
        inst = db_creator.dummy_instance()
        
        # Create two covergroups
        db_creator.create_covergroup(
            inst,
            "cg_1",
            dict(
                coverpoints=dict(
                    cp_a = dict(
                        bins=[
                            ("bin1", 1),
                            ("bin2", 1),
                        ]
                    )
                )
            )
        )
        
        db_creator.create_covergroup(
            inst,
            "cg_2",
            dict(
                coverpoints=dict(
                    cp_a = dict(
                        bins=[
                            ("bin1", 1),
                            ("bin2", 0),
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
        
        args = Args()
        cmd = ShowSummary(args)
        cmd.db = db_creator.db
        data = cmd.get_data()
        
        # Verify we have 2 covergroups
        stats = data['statistics']
        self.assertEqual(stats['total_covergroups'], 2)
        self.assertEqual(stats['total_bins'], 4)
        self.assertEqual(stats['covered_bins'], 3)
        
    def test_summary_json_output(self):
        """Test that JSON output is valid."""
        db_creator = DbCreator()
        
        db_creator.dummy_test_data()
        inst = db_creator.dummy_instance()
        
        db_creator.create_covergroup(
            inst,
            "cg_test",
            dict(
                coverpoints=dict(
                    cp_a = dict(
                        bins=[
                            ("bin1", 1),
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
        
        args = Args()
        cmd = ShowSummary(args)
        cmd.db = db_creator.db
        data = cmd.get_data()
        
        # Capture output
        output = StringIO()
        cmd._write_json(data, output)
        
        # Verify valid JSON
        output_str = output.getvalue()
        parsed = json.loads(output_str)
        
        self.assertIn('overall_coverage', parsed)
        self.assertIn('statistics', parsed)
        
    def test_summary_text_output(self):
        """Test that text output is generated."""
        db_creator = DbCreator()
        
        db_creator.dummy_test_data()
        inst = db_creator.dummy_instance()
        
        db_creator.create_covergroup(
            inst,
            "cg_test",
            dict(
                coverpoints=dict(
                    cp_a = dict(
                        bins=[
                            ("bin1", 1),
                        ]
                    )
                )
            )
        )
        
        class Args:
            def __init__(self):
                self.db = None
                self.input_format = 'mem'
                self.output_format = 'text'
                self.out = None
        
        args = Args()
        cmd = ShowSummary(args)
        cmd.db = db_creator.db
        data = cmd.get_data()
        
        # Capture output
        output = StringIO()
        cmd._write_text(data, output)
        
        # Verify text output contains key fields
        output_str = output.getvalue()
        self.assertIn('overall_coverage', output_str)
        self.assertIn('statistics', output_str)
        self.assertIn('total_bins', output_str)
