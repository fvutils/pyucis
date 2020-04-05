'''
Created on Apr 5, 2020

@author: ballance
'''
from unittest.case import TestCase
from ucis.report.coverage_report_builder import CoverageReportBuilder
from db_creator import DbCreator

class TestReport(TestCase):
    
    def test_type_covergroup_single_coverpoint(self):
        db_creator = DbCreator()
        
        db_creator.dummy_test_data()
        inst = db_creator.dummy_instance()
        
        db_creator.create_covergroup(
            inst,
            "cg_t",
            dict(
                coverpoints=dict(
                    a_cp = dict(
                        bins=[
                            ("b1", 1),
                            ("b2", 1),
                            ("b3", 0),
                            ("b4", 0),
                        ]
                    )
                )
            )
        )
            
        report = CoverageReportBuilder.build(db_creator.db)
        
        self.assertEqual(1, len(report.covergroups))
        self.assertEqual(1, len(report.covergroups[0].coverpoints))
        self.assertEqual(50.0, report.covergroups[0].coverpoints[0].coverage)
        self.assertEqual(50.0, report.covergroups[0].coverage)

    def test_type_covergroup_two_coverpoints(self):
        db_creator = DbCreator()
        
        db_creator.dummy_test_data()
        inst = db_creator.dummy_instance()
                
        db_creator.create_covergroup(
            inst,
            "cp_t",
            dict(
                coverpoints=dict(
                    a_cp = dict(
                        bins=[
                            ("b1", 1),
                            ("b2", 1),
                            ("b3", 0),
                            ("b4", 0),
                        ]
                    ),
                    b_cp = dict(
                        bins=[
                            ("b1", 0),
                            ("b2", 0),
                            ("b3", 0),
                            ("b4", 0),
                        ]
                    ),
                )
            )
        )
            
        report = CoverageReportBuilder.build(db_creator.db)
        
        self.assertEqual(1, len(report.covergroups))
        self.assertEqual(2, len(report.covergroups[0].coverpoints))
        self.assertEqual(50.0, report.covergroups[0].coverpoints[0].coverage)
        self.assertEqual(0.0, report.covergroups[0].coverpoints[1].coverage)
        self.assertEqual(25.0, report.covergroups[0].coverage)        

        
    def test_type_covergroup_two_coverpoints_weights(self):
        db_creator = DbCreator()
        
        db_creator.dummy_test_data()
        inst = db_creator.dummy_instance()

        db_creator.create_covergroup(
            inst,
            "cg_t",
            dict(
                coverpoints=dict(
                    a_cp = dict(
                        options=dict(weight=4),
                        bins=[
                            ("b1", 1),
                            ("b2", 1),
                            ("b3", 0),
                            ("b4", 0),
                        ]
                    ),
                    b_cp = dict(
                        options=dict(weight=8),
                        bins=[
                            ("b1", 0),
                            ("b2", 0),
                            ("b3", 0),
                            ("b4", 0),
                            ("b5", 0),
                            ("b6", 0),
                            ("b7", 1),
                            ("b8", 1),
                        ]
                    ),
                )
            )
        )
            
        report = CoverageReportBuilder.build(db_creator.db)
        
        self.assertEqual(1, len(report.covergroups))
        self.assertEqual(2, len(report.covergroups[0].coverpoints))
        self.assertEqual(50.0, report.covergroups[0].coverpoints[0].coverage)
        self.assertEqual(25.0, report.covergroups[0].coverpoints[1].coverage)
        self.assertEqual(round((100*4/12), 2), report.covergroups[0].coverage)

    def test_type_covergroup_two_coverpoints_weights_options(self):
        db_creator = DbCreator()
        
        db_creator.dummy_test_data()
        inst = db_creator.dummy_instance()
        
        type_cg_1 = db_creator.create_covergroup(
            inst,
            "cg_t",
            dict(
                options=dict(weight=1),
                coverpoints=dict(
                    a_cp = dict(
                        bins=[
                            ("b1", 1),
                            ("b2", 1),
                            ("b3", 0),
                            ("b4", 0),
                            ]
                    ),
                    b_cp = dict(
                        bins=[
                            ("b1", 0),
                            ("b2", 0),
                            ("b3", 0),
                            ("b4", 0),
                            ("b5", 1),
                            ("b6", 1),
                            ("b7", 1),
                            ("b8", 1),
                        ]
                    )
                )
            )
        )

        type_cg_2 = db_creator.create_covergroup(
            inst,
            "cg_t",
            dict(
                options=dict(weight=1),
                coverpoints=dict(
                    a_cp = dict(
                        bins=[
                            ("b1", 1),
                            ("b2", 1),
                            ("b3", 1),
                            ("b4", 1),
                            ]
                    ),
                    b_cp = dict(
                        bins=[
                            ("b1", 1),
                            ("b2", 1),
                            ("b3", 1),
                            ("b4", 1),
                            ("b5", 1),
                            ("b6", 1),
                            ("b7", 1),
                            ("b8", 1),
                        ]
                    )
                )
            )
        )        
            
        report = CoverageReportBuilder.build(db_creator.db)
        
        self.assertEqual(2, len(report.covergroups))
        self.assertEqual(2, len(report.covergroups[0].coverpoints))
        self.assertEqual(2, len(report.covergroups[1].coverpoints))
        self.assertEqual(75.0, report.coverage)
        