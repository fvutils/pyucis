
from ucis.mem.mem_factory import MemFactory
from . import example_create_ucis
from ucis.xml.xml_factory import XmlFactory
from _io import StringIO


class TestXmlExamples:
    
    def test_create_ucis(self):
        db = MemFactory.create()
        example_create_ucis.create_ucis(db)
        out = StringIO()
        XmlFactory.write(db, out)
        print("output:\n" + out.getvalue())