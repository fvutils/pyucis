from unittest.case import TestCase
from pyucis.mem.mem_factory import MemFactory
from pyucis.xml.xml_writer import XmlWriter
import io
from pyucis.xml.xml_factory import XmlFactory

class TestSmoke(TestCase):
    
    def test_smoke(self):
        db = MemFactory.create()
        
        histN = db.createHistoryNode(None, "abc")
        out = io.StringIO()
        XmlFactory.write(db, out)
        
        print("output:\n" + out.getvalue())