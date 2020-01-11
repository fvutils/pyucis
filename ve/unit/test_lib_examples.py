
import os
from unittest.case import TestCase
from pyucis.mem.mem_factory import MemFactory
from pyucis.source_info import SourceInfo
from pyucis.scope import Scope
from pyucis.test_data import TestData
from pyucis import *
from pyucis.lib.LibFactory import LibFactory
import example_create_ucis

class TestUcisExamples(TestCase):

    def setUp(self):
        LibFactory.load_ucis_library("libucis.so")
    
    def test_create_ucis(self):
        db = LibFactory.create()
        example_create_ucis.create_ucis(db)
