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

"""
User attributes and tags support for SQLite UCIS
"""

from typing import Dict, List


# Object kind enumeration for attributes/tags
class ObjectKind:
    SCOPE = 1
    COVERITEM = 2
    HISTORYNODE = 3


class AttributeManager:
    """Manages user-defined attributes on UCIS objects"""
    
    def __init__(self, ucis_db):
        self.ucis_db = ucis_db
    
    def setAttribute(self, obj_kind: int, obj_id: int, key: str, value: str):
        """Set an attribute on an object"""
        self.ucis_db.conn.execute(
            """INSERT OR REPLACE INTO attributes (obj_kind, obj_id, attr_key, attr_value)
               VALUES (?, ?, ?, ?)""",
            (obj_kind, obj_id, key, value)
        )
    
    def getAttribute(self, obj_kind: int, obj_id: int, key: str) -> str:
        """Get an attribute value"""
        cursor = self.ucis_db.conn.execute(
            """SELECT attr_value FROM attributes 
               WHERE obj_kind = ? AND obj_id = ? AND attr_key = ?""",
            (obj_kind, obj_id, key)
        )
        row = cursor.fetchone()
        return row[0] if row else None
    
    def getAttributes(self, obj_kind: int, obj_id: int) -> Dict[str, str]:
        """Get all attributes for an object"""
        cursor = self.ucis_db.conn.execute(
            """SELECT attr_key, attr_value FROM attributes 
               WHERE obj_kind = ? AND obj_id = ?""",
            (obj_kind, obj_id)
        )
        return {row[0]: row[1] for row in cursor}
    
    def deleteAttribute(self, obj_kind: int, obj_id: int, key: str):
        """Delete an attribute"""
        self.ucis_db.conn.execute(
            """DELETE FROM attributes 
               WHERE obj_kind = ? AND obj_id = ? AND attr_key = ?""",
            (obj_kind, obj_id, key)
        )
    
    def findByAttribute(self, obj_kind: int, key: str, value: str = None) -> List[int]:
        """Find objects by attribute key (and optionally value)"""
        if value is None:
            cursor = self.ucis_db.conn.execute(
                """SELECT obj_id FROM attributes 
                   WHERE obj_kind = ? AND attr_key = ?""",
                (obj_kind, key)
            )
        else:
            cursor = self.ucis_db.conn.execute(
                """SELECT obj_id FROM attributes 
                   WHERE obj_kind = ? AND attr_key = ? AND attr_value = ?""",
                (obj_kind, key, value)
            )
        
        return [row[0] for row in cursor]


class TagManager:
    """Manages tags on UCIS objects"""
    
    def __init__(self, ucis_db):
        self.ucis_db = ucis_db
        self._tag_cache = {}  # tag_name -> tag_id
    
    def createTag(self, tag_name: str) -> int:
        """Create or get a tag by name"""
        if tag_name in self._tag_cache:
            return self._tag_cache[tag_name]
        
        # Check if tag exists
        cursor = self.ucis_db.conn.execute(
            "SELECT tag_id FROM tags WHERE tag_name = ?",
            (tag_name,)
        )
        row = cursor.fetchone()
        
        if row:
            tag_id = row[0]
        else:
            # Create new tag
            cursor = self.ucis_db.conn.execute(
                "INSERT INTO tags (tag_name) VALUES (?)",
                (tag_name,)
            )
            tag_id = cursor.lastrowid
        
        self._tag_cache[tag_name] = tag_id
        return tag_id
    
    def addTag(self, obj_kind: int, obj_id: int, tag_name: str):
        """Add a tag to an object"""
        tag_id = self.createTag(tag_name)
        
        self.ucis_db.conn.execute(
            """INSERT OR IGNORE INTO object_tags (obj_kind, obj_id, tag_id)
               VALUES (?, ?, ?)""",
            (obj_kind, obj_id, tag_id)
        )
    
    def removeTag(self, obj_kind: int, obj_id: int, tag_name: str):
        """Remove a tag from an object"""
        cursor = self.ucis_db.conn.execute(
            "SELECT tag_id FROM tags WHERE tag_name = ?",
            (tag_name,)
        )
        row = cursor.fetchone()
        
        if row:
            tag_id = row[0]
            self.ucis_db.conn.execute(
                """DELETE FROM object_tags 
                   WHERE obj_kind = ? AND obj_id = ? AND tag_id = ?""",
                (obj_kind, obj_id, tag_id)
            )
    
    def getTags(self, obj_kind: int, obj_id: int) -> List[str]:
        """Get all tags for an object"""
        cursor = self.ucis_db.conn.execute(
            """SELECT t.tag_name FROM tags t
               JOIN object_tags ot ON t.tag_id = ot.tag_id
               WHERE ot.obj_kind = ? AND ot.obj_id = ?""",
            (obj_kind, obj_id)
        )
        return [row[0] for row in cursor]
    
    def hasTag(self, obj_kind: int, obj_id: int, tag_name: str) -> bool:
        """Check if object has a specific tag"""
        cursor = self.ucis_db.conn.execute(
            """SELECT 1 FROM object_tags ot
               JOIN tags t ON ot.tag_id = t.tag_id
               WHERE ot.obj_kind = ? AND ot.obj_id = ? AND t.tag_name = ?""",
            (obj_kind, obj_id, tag_name)
        )
        return cursor.fetchone() is not None
    
    def findByTag(self, obj_kind: int, tag_name: str) -> List[int]:
        """Find all objects with a specific tag"""
        cursor = self.ucis_db.conn.execute(
            """SELECT ot.obj_id FROM object_tags ot
               JOIN tags t ON ot.tag_id = t.tag_id
               WHERE ot.obj_kind = ? AND t.tag_name = ?""",
            (obj_kind, tag_name)
        )
        return [row[0] for row in cursor]
    
    def getAllTags(self) -> List[str]:
        """Get list of all tag names in database"""
        cursor = self.ucis_db.conn.execute(
            "SELECT tag_name FROM tags ORDER BY tag_name"
        )
        return [row[0] for row in cursor]
    
    def getTagUsageCount(self, tag_name: str) -> int:
        """Get number of objects with this tag"""
        cursor = self.ucis_db.conn.execute(
            """SELECT COUNT(*) FROM object_tags ot
               JOIN tags t ON ot.tag_id = t.tag_id
               WHERE t.tag_name = ?""",
            (tag_name,)
        )
        row = cursor.fetchone()
        return row[0] if row else 0


# Mixin class to add attribute/tag support to objects
class AttributeTagMixin:
    """Mixin to add attribute and tag methods to objects"""
    
    def _get_obj_kind(self):
        """Get the object kind for attributes/tags"""
        raise NotImplementedError("Subclasses must implement _get_obj_kind")
    
    def setAttribute(self, key: str, value: str):
        """Set a user attribute"""
        attr_mgr = AttributeManager(self.ucis_db)
        attr_mgr.setAttribute(self._get_obj_kind(), self._get_obj_id(), key, value)
    
    def getAttribute(self, key: str) -> str:
        """Get a user attribute"""
        attr_mgr = AttributeManager(self.ucis_db)
        return attr_mgr.getAttribute(self._get_obj_kind(), self._get_obj_id(), key)
    
    def getAttributes(self) -> Dict[str, str]:
        """Get all user attributes"""
        attr_mgr = AttributeManager(self.ucis_db)
        return attr_mgr.getAttributes(self._get_obj_kind(), self._get_obj_id())
    
    def deleteAttribute(self, key: str):
        """Delete a user attribute"""
        attr_mgr = AttributeManager(self.ucis_db)
        attr_mgr.deleteAttribute(self._get_obj_kind(), self._get_obj_id(), key)
    
    def addTag(self, tag_name: str):
        """Add a tag to this object"""
        tag_mgr = TagManager(self.ucis_db)
        tag_mgr.addTag(self._get_obj_kind(), self._get_obj_id(), tag_name)
    
    def removeTag(self, tag_name: str):
        """Remove a tag from this object"""
        tag_mgr = TagManager(self.ucis_db)
        tag_mgr.removeTag(self._get_obj_kind(), self._get_obj_id(), tag_name)
    
    def getTags(self) -> List[str]:
        """Get all tags for this object"""
        tag_mgr = TagManager(self.ucis_db)
        return tag_mgr.getTags(self._get_obj_kind(), self._get_obj_id())
    
    def hasTag(self, tag_name: str) -> bool:
        """Check if object has a specific tag"""
        tag_mgr = TagManager(self.ucis_db)
        return tag_mgr.hasTag(self._get_obj_kind(), self._get_obj_id(), tag_name)
