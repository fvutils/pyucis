
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from unittest.case import TestCase
from ucis.mem.mem_factory import MemFactory
from ucis.xml.xml_writer import XmlWriter
import io
from ucis.xml.xml_factory import XmlFactory
from ucis.statement_id import StatementId
from ucis.xml import validate_ucis_xml, xml_reader
from ucis.xml.xml_reader import XmlReader

class TestSmoke(TestCase):
    
    def disabled_test_smoke(self):
        db = MemFactory.create()

        srcF = db.createFileHandle("/home/foobar", None)        
        histN = db.createHistoryNode(None, "abc")
        coverI = db.createCoverInstance("my_cg", StatementId(srcF, 1, 1))
        out = io.StringIO()
        XmlFactory.write(db, out)
      
        print("output:\n" + out.getvalue())
        
        xml_in = io.StringIO(out.getvalue())
        validate_ucis_xml(xml_in)
        
        xml_in = io.StringIO(out.getvalue())
        db2 = XmlFactory.read(xml_in)
        
        out2 = io.StringIO()
        XmlFactory.write(db2, out2)
        print("output2:\n" + out2.getvalue())
        

    def disabled_test_validate(self):
        document = """
<ucis:UCIS xmlns:ucis="UCIS" ucisVersion="1.0"  writtenBy="$USER"
 writtenTime="2008-09-29T03:49:45">
<ucis:sourceFiles  fileName="string" id="201" />
</ucis:UCIS>        
        """
#        document = """
#<ucis:UCIS xmlns:ucis="UCIS" ucisVersion="1.0" writtenBy="foo" writtenTime="20200101">
#  <ucis:sourceFiles fileName="/home/foobar" id="0"/>
#  <ucis:historyNodes historyNodeId="0" logicalName="abc" testStatus="False"/>
#  <ucis:instanceCoverages name="my_cg" key="0">
#    <ucis:id file="0" line="1" inlineCount="1"/>
#  </ucis:instanceCoverages>
#</ucis:UCIS>
#        """
        
        
        file_i = io.StringIO(document)
        
        print("Document: " + file_i.getvalue())
        
        validate_ucis_xml(file_i)
        