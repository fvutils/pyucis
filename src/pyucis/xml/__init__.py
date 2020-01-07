import os
from lxml import etree
from lxml.etree import tounicode


def validate_ucis_xml(file_or_filename):
    
    xml_pkg_dir = os.path.dirname(os.path.abspath(__file__))
    schema_dir = os.path.join(xml_pkg_dir, "schema")
    ucis_xsd = os.path.join(schema_dir, "ucis-1.0.xsd")
    
    with open(ucis_xsd, "r") as xsd_fp:
        ucis_xsd_doc = etree.parse(xsd_fp)
        
#    print("schema_doc: " + tounicode(ucis_xsd_doc, pretty_print=True))
    
    ucis_schema = etree.XMLSchema(ucis_xsd_doc)
    
#    print("schema: " + str(ucis_schema))
    
    if type(file_or_filename) == str:
        print("open file")
        fp = open(file_or_filename, "r")
    else:
        fp = file_or_filename
        
    ret = False

    try:
        doc = etree.parse(fp)
        
        root = doc.getroot()

        # There is some inconsistency in whether
        # elements should be namespace-qualified or not.
        # The official schema indicates that they should be,
        # while the examples indicate they shouldn't be. The
        # (apparently) simplest way around this is to remove 
        # namespace qualification entirely.
        for elem in root.getiterator():
            if not hasattr(elem.tag, 'find'): continue  # (1)
            i = elem.tag.find('}')
            if i >= 0:
                elem.tag = elem.tag[i+1:]        
                
        ret = ucis_schema.assertValid(doc)
    finally:
        if type(file_or_filename) == str:
            fp.close()

    return ret
