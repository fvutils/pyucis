'''
Created on Mar 23, 2020

@author: ballance
'''
from ucis.cover_index import CoverIndex
from ucis.cover_data import CoverData
from ucis.source_info import SourceInfo

class MemCoverIndex(CoverIndex):
    
    def __init__(self, 
                 name : str,
                 data : CoverData,
                 srcinfo : SourceInfo):
        CoverIndex.__init__(self)
        self.name = name
        self.data = data
        self.srcinfo = srcinfo
        
    def getName(self)->str:
        return self.name
        
    def getCoverData(self)->CoverData:
        return self.data
    
    def getSourceInfo(self)->SourceInfo:
        return self.srcinfo
    
    def incrementCover(self, amt=1):
        self.data.data += amt

    def setCoverData(self, data: CoverData):
        """Replace the cover data for this item."""
        self.data = data

    def getCoverFlags(self) -> int:
        """Get cover flags (stored in data.flags)."""
        return self.data.flags if self.data else 0

    def setCoverFlags(self, flags: int):
        """Set cover flags."""
        if self.data:
            self.data.flags = flags

    def setAttribute(self, key: str, value: str):
        """Set a user-defined attribute on this coveritem."""
        if not hasattr(self, '_attributes'):
            self._attributes = {}
        self._attributes[key] = value

    def getAttribute(self, key: str):
        """Get a user-defined attribute by key."""
        if not hasattr(self, '_attributes'):
            return None
        return self._attributes.get(key)

    def getAttributes(self):
        """Get all user-defined attributes as a dict."""
        if not hasattr(self, '_attributes'):
            return {}
        return dict(self._attributes)
