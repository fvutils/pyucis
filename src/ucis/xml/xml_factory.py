
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

'''
Created on Jan 5, 2020

@author: ballance
'''
from ucis import UCIS
from ucis.xml.xml_writer import XmlWriter
from ucis.xml import validate_ucis_xml
from ucis.xml.xml_reader import XmlReader

class XmlFactory():
    
    @staticmethod
    def read(file_or_filename) -> UCIS:
        """Reads the specified XML file and returns a UCIS representation"""
        
        # First, validate the incoming XML
        if type(file_or_filename) == str:
            fp = open(file_or_filename)
        else:
            fp = file_or_filename

        try:            
            validate_ucis_xml(fp)
        except:
            if type(file_or_filename) == str:
                fp.close()
            

        fp.seek(0)
        
        reader = XmlReader()
        
        try:
            ret = reader.read(fp)
        finally:
            if type(file_or_filename) == str:
                fp.close()

        return ret
        
    @staticmethod
    def write(db : UCIS, file_or_filename):
        """Writes the specified database in XML format"""
        writer = XmlWriter()
        
        if type(file_or_filename) == str:
            fp = open(file_or_filename, "w")
        else:
            fp = file_or_filename
        
        writer.write(fp, db)
        
        if type(file_or_filename) == str:
            fp.close()
            
        pass