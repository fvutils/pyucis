'''
Created on Jan 5, 2020

@author: ballance
'''

from lxml import etree as et
from pyucis.ucis import UCIS
from lxml.etree import QName, tounicode, SubElement

class XmlWriter():
    
    UCIS = "http://www.w3.org/2001/XMLSchema-instance"
    
    def __init__(self):
        self.db = None
        self.root = None
        pass
    
    def write(self, file, db : UCIS):
        self.db = db
        self.root = et.Element(QName(XmlWriter.UCIS, "UCIS"), nsmap={
            "ucis" : XmlWriter.UCIS
            })
        
        self.setAttr(self.root, "ucisVersion", db.getAPIVersion())

        self.write_source_files()
        self.write_history_nodes()
        
        file.write(tounicode(self.root, pretty_print=True))
        
    def write_source_files(self):
        
        for i,f in enumerate(self.db.getSourceFiles()):
            fileN = SubElement(self.root, "sourceFiles")
            fileN.set("fileName", f.getFilename())
            fileN.set("id", str(i))
        
    def write_history_nodes(self):
        
#        histNodes = self.root.SubElement(self.root, "historyNodes")
        
        for i,h in enumerate(self.db.getHistoryNodes()):
            histN = self.mkElem(self.root, "historyNodes")
            histN.set("historyNodeId", str(i))
            
            # TODO: parent
            histN.set("logicalName", h.getLogicalName())
            self.setIfNonNull(histN, "physicalName", h.getPhysicalName())
            self.setIfNonNull(histN, "kind", h.getKind())
            histN.set("testStatus", str(h.getTestStatus()))
            self.setIfNonNeg(histN, "simtime", h.getSimTime())
            self.setIfNonNull(histN, "timeunit", h.getTimeUnit())
            self.setIfNonNull(histN, "runCwd", h.getRunCwd())
            self.setIfNonNeg(histN, "cpuTime", h.getCpuTime())
            self.setIfNonNull(histN, "seed", h.getSeed())
            self.setIfNonNull(histN, "cmd", h.getCmd())
            self.setIfNonNull(histN, "args", h.getArgs())
            self.setIfNonNull(histN, "compulsory", h.getCompulsory())
            # TODO: date
            self.setIfNonNull(histN, "userName", h.getUserName())
            
            # TODO: userAttr
            
    def mkElem(self, p, name):
        # Creates a UCIS-qualified node
        return SubElement(p, QName(XmlWriter.UCIS, name))
        
    def setAttr(self, e, name, val):
        e.set(QName(XmlWriter.UCIS, name), val)
            
    def setIfNonNull(self, n, attr, val):
        if val is not None:
            self.setAttr(n, attr, str(val))
            
    def setIfNonNeg(self, n, attr, val):
        if val >= 0:
            self.setAttr(n, attr, str(val))
        
        