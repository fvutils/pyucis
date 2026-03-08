'''
Test for file list feature with large number of databases

This test creates thousands of small coverage databases and merges them
using the --file-list feature to verify it works at scale.
'''
import os
import sys
import tempfile
import shutil
from unittest.case import TestCase
from ucis.xml.xml_reader import XmlReader
from ucis.mem.mem_factory import MemFactory
from ucis.report.coverage_report_builder import CoverageReportBuilder
from ucis.__main__ import get_parser


class TestFileList(TestCase):

    def setUp(self):
        """Create temporary directory for test databases"""
        self.test_dir = tempfile.mkdtemp(prefix="pyucis_test_")
        
    def tearDown(self):
        """Clean up temporary directory"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def _create_test_db(self, name, bin_values):
        """Create a simple test database with specified bin values using YAML"""
        yaml_text = f"""
        coverage:
          covergroups:
          - name: test_cg
            instances:
            - name: test_inst
              coverpoints:
              - name: test_cp
                bins:
"""
        for i, value in enumerate(bin_values):
            yaml_text += f"                - name: bin_{i}\n"
            yaml_text += f"                  count: {value}\n"
        
        # Create database from YAML
        from ucis.yaml.yaml_reader import YamlReader
        from ucis.xml.xml_writer import XmlWriter
        db = YamlReader().loads(yaml_text)
        
        # Write to XML file
        filepath = os.path.join(self.test_dir, name)
        writer = XmlWriter()
        with open(filepath, 'w') as f:
            writer.write(f, db)
        return filepath

    def test_file_list_basic(self):
        """Test basic file list functionality"""
        # Create a few test databases
        db1 = self._create_test_db("db1.xml", [1, 0])
        db2 = self._create_test_db("db2.xml", [0, 1])
        
        # Create file list
        file_list_path = os.path.join(self.test_dir, "merge.list")
        with open(file_list_path, 'w') as f:
            f.write("# Test file list\n")
            f.write(f"{db1}\n")
            f.write("\n")  # blank line
            f.write(f"# Comment\n")
            f.write(f"{db2}\n")
        
        # Merge using file list
        output_path = os.path.join(self.test_dir, "merged.xml")
        parser = get_parser()
        args = parser.parse_args([
            "merge",
            "-f", file_list_path,
            "-o", output_path
        ])
        
        args.func(args)
        
        # Verify output exists
        self.assertTrue(os.path.exists(output_path))
        
        # Verify merged content
        merged_db = XmlReader().read(output_path)
        rpt = CoverageReportBuilder.build(merged_db)
        
        self.assertEqual(len(rpt.covergroups), 1)
        self.assertEqual(len(rpt.covergroups[0].coverpoints), 1)
        self.assertEqual(len(rpt.covergroups[0].coverpoints[0].bins), 2)
        # Both bins should have count=1 after merge
        self.assertEqual(rpt.covergroups[0].coverpoints[0].coverage, 100.0)

    def test_file_list_with_direct_args(self):
        """Test combining file list with direct arguments"""
        db1 = self._create_test_db("db1.xml", [1, 0])
        db2 = self._create_test_db("db2.xml", [0, 1])
        db3 = self._create_test_db("db3.xml", [1, 1])
        
        # Create file list with only db1 and db2
        file_list_path = os.path.join(self.test_dir, "merge.list")
        with open(file_list_path, 'w') as f:
            f.write(f"{db1}\n")
            f.write(f"{db2}\n")
        
        # Merge using file list + direct argument (db3)
        output_path = os.path.join(self.test_dir, "merged.xml")
        parser = get_parser()
        args = parser.parse_args([
            "merge",
            "-f", file_list_path,
            db3,
            "-o", output_path
        ])
        
        args.func(args)
        
        # Verify output
        self.assertTrue(os.path.exists(output_path))
        merged_db = XmlReader().read(output_path)
        rpt = CoverageReportBuilder.build(merged_db)
        
        # Should have merged all 3 databases
        self.assertEqual(len(rpt.covergroups[0].coverpoints[0].bins), 2)

    def test_file_list_large_scale(self):
        """Test file list with thousands of databases"""
        num_databases = 1000  # Create 1000 databases
        print(f"\nCreating {num_databases} test databases...")
        
        # Create databases with different coverage patterns
        db_paths = []
        for i in range(num_databases):
            # Alternate bin coverage patterns
            bin_values = [1, 0] if i % 2 == 0 else [0, 1]
            db_path = self._create_test_db(f"db_{i:04d}.xml", bin_values)
            db_paths.append(db_path)
        
        print(f"Created {len(db_paths)} databases")
        
        # Create file list
        file_list_path = os.path.join(self.test_dir, "large_merge.list")
        with open(file_list_path, 'w') as f:
            f.write(f"# Large scale test with {num_databases} databases\n")
            for db_path in db_paths:
                f.write(f"{db_path}\n")
        
        print(f"Created file list with {num_databases} entries")
        
        # Merge using file list
        output_path = os.path.join(self.test_dir, "merged_large.xml")
        parser = get_parser()
        args = parser.parse_args([
            "merge",
            "-f", file_list_path,
            "-o", output_path
        ])
        
        print("Starting merge...")
        args.func(args)
        print("Merge completed")
        
        # Verify output
        self.assertTrue(os.path.exists(output_path))
        
        # Verify merged content
        merged_db = XmlReader().read(output_path)
        rpt = CoverageReportBuilder.build(merged_db)
        
        self.assertEqual(len(rpt.covergroups), 1)
        self.assertEqual(len(rpt.covergroups[0].coverpoints), 1)
        self.assertEqual(len(rpt.covergroups[0].coverpoints[0].bins), 2)
        
        # With 1000 databases alternating between [1,0] and [0,1],
        # both bins should be fully covered
        self.assertEqual(rpt.covergroups[0].coverpoints[0].coverage, 100.0)
        
        print(f"Successfully merged {num_databases} databases")
        print(f"Final coverage: {rpt.covergroups[0].coverpoints[0].coverage}%")

    def test_file_list_missing_file(self):
        """Test error handling for missing file list"""
        output_path = os.path.join(self.test_dir, "merged.xml")
        parser = get_parser()
        args = parser.parse_args([
            "merge",
            "-f", "nonexistent.list",
            "-o", output_path
        ])
        
        with self.assertRaises(Exception) as context:
            args.func(args)
        
        self.assertIn("File list not found", str(context.exception))

    def test_no_databases_specified(self):
        """Test error when no databases are specified"""
        output_path = os.path.join(self.test_dir, "merged.xml")
        parser = get_parser()
        args = parser.parse_args([
            "merge",
            "-o", output_path
        ])
        
        with self.assertRaises(Exception) as context:
            args.func(args)
        
        self.assertIn("No input databases specified", str(context.exception))
