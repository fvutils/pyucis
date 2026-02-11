
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
Created on Dec 22, 2019

@author: ballance
'''

from ucis.history_node_kind import HistoryNodeKind
from typing import List, Iterator
from ucis.scope_type_t import ScopeTypeT
from ucis.unimpl_error import UnimplError
from ucis.scope import Scope
from ucis.history_node import HistoryNode
from ucis.source_file import SourceFile
from ucis.instance_coverage import InstanceCoverage
from ucis.statement_id import StatementId
from ucis.int_property import IntProperty
from ucis.file_handle import FileHandle

class UCIS(Scope):
    """Root database class for Unified Coverage Interoperability Standard.
    
    UCIS is the top-level container for all coverage data, representing the
    entire coverage database. It extends Scope to act as the root of the scope
    hierarchy and provides database-level operations for persistence, metadata
    management, and history tracking.
    
    A UCIS database can exist in two forms:
    - **In-memory**: Fast random access to all data, held in RAM
    - **Persistent**: Stored on disk in XML, SQLite, or other backend formats
    
    Key capabilities:
    - **Hierarchy Root**: Contains top-level scopes (design units, instances)
    - **Persistence**: Read from and write to files in various formats
    - **History Tracking**: Manage test history nodes for merge tracking
    - **Metadata**: Store database version, tool info, timestamps
    - **File Management**: Create and manage file handles for source references
    
    The database supports multiple backends (in-memory, SQLite, XML, YAML) with
    different trade-offs between performance, persistence, and file size.
    
    Example:
        >>> # Create in-memory database
        >>> from ucis.mem import MemFactory
        >>> db = MemFactory.create()
        >>> 
        >>> # Create design hierarchy
        >>> du = db.createScope("counter", None, 1, SourceT.SV,
        ...                     ScopeTypeT.DU_MODULE, 0)
        >>> inst = db.createInstance("top", None, 1, SourceT.SV,
        ...                          ScopeTypeT.INSTANCE, du, 0)
        >>> 
        >>> # Save to file
        >>> db.write("coverage.xml")
        >>> db.close()
        
    Note:
        UCIS objects should be created through backend-specific factory methods
        (MemFactory, SqliteUCIS, etc.) rather than direct instantiation.
        
    See Also:
        Scope: Base class for hierarchical containers
        HistoryNode: Test history and merge tracking
        UCIS LRM Section 8.1 "Database Creation and File Management"
        UCIS LRM Chapter 4 "Introduction to the UCIS Data Model"
    """
    
    def __init__(self):
        pass
    
    def getIntProperty(
            self, 
            coverindex : int,
            property : IntProperty
            )->int:
        """Get an integer property value from the database.
        
        Overrides Scope.getIntProperty() to provide database-specific properties
        including modification status and test counts.
        
        Args:
            coverindex: Index of cover item, or -1 for database-level properties.
            property: Integer property identifier (IntProperty enum).
            
        Returns:
            Integer value of the requested property.
            
        Raises:
            UnimplError: If property is not supported.
            
        See Also:
            Obj.getIntProperty(): Base implementation
            IntProperty: Database-specific properties include IS_MODIFIED,
                MODIFIED_SINCE_SIM, NUM_TESTS
        """
        if property == IntProperty.IS_MODIFIED:
            return 1 if self.isModified() else 0
        elif property == IntProperty.MODIFIED_SINCE_SIM:
            return 1 if self.modifiedSinceSim() else 0
        elif property == IntProperty.NUM_TESTS:
            return self.getNumTests()
        else:
            return super().getIntProperty(coverindex, property)
    
    def setIntProperty(
            self,
            coverindex : int,
            property : IntProperty,
            value : int):
        """Set an integer property value on the database.
        
        Overrides Scope.setIntProperty() for database-level property handling.
        
        Args:
            coverindex: Index of cover item, or -1 for database-level properties.
            property: Integer property identifier (IntProperty enum).
            value: New integer value for the property.
            
        Raises:
            UnimplError: If property is not supported or read-only.
            
        See Also:
            Obj.setIntProperty(): Base implementation
        """
        super().setIntProperty(coverindex, property, value)
        
    def isModified(self):
        """Check if the database has been modified since opening.
        
        Returns True if any changes have been made to the database since it was
        opened or created. This includes adding/removing scopes, modifying coverage
        data, or changing metadata. Read-only property.
        
        Returns:
            Boolean indicating whether database has been modified.
            
        Raises:
            UnimplError: If modification tracking is not supported.
            
        Example:
            >>> if db.isModified():
            ...     print("Database has unsaved changes")
            ...     db.write("coverage.xml")
            
        See Also:
            modifiedSinceSim(): Check if modified since simulation
            IntProperty.IS_MODIFIED: Property identifier
        """
        raise UnimplError()
    
    def modifiedSinceSim(self):
        """Check if the database has been modified since simulation.
        
        Returns True if any changes have been made to the database after the
        original simulation run completed. This tracks post-simulation modifications
        like merging or manual edits. Read-only property.
        
        Returns:
            Boolean indicating whether database was modified post-simulation.
            
        Raises:
            UnimplError: If modification tracking is not supported.
            
        See Also:
            isModified(): Check if modified since opening
            IntProperty.MODIFIED_SINCE_SIM: Property identifier
        """
        raise UnimplError()
    
    def getNumTests(self):
        """Get the number of test history nodes in the database.
        
        Returns the count of test history nodes (HistoryNodeKind.TEST) that
        represent individual test runs contributing to this database. This count
        is used for tracking test coverage and merge history. Read-only property.
        
        Returns:
            Integer count of test history nodes (>= 0).
            
        Raises:
            UnimplError: If test counting is not supported.
            
        Example:
            >>> num = db.getNumTests()
            >>> print(f"Database contains coverage from {num} tests")
            
        See Also:
            historyNodes(): Iterate test history nodes
            IntProperty.NUM_TESTS: Property identifier
        """
        raise UnimplError()
    
    def getAPIVersion(self) -> str:
        """Get the UCIS API version string.
        
        Returns the version of the UCIS API implementation. This typically follows
        the UCIS standard version (e.g., "1.0") but may include tool-specific
        version information.
        
        Returns:
            String containing API version identifier.
            
        Raises:
            UnimplError: If version information is not available.
            
        Example:
            >>> version = db.getAPIVersion()
            >>> print(f"UCIS API version: {version}")
            
        See Also:
            getDBVersion(): Get database format version
            UCIS LRM Section 8.18.1 "ucis_GetAPIVersion"
        """
        raise UnimplError()
    
    def getWrittenBy(self)->str:
        """Get the tool identifier that created this database.
        
        Returns a string identifying the tool that originally wrote/created this
        database. Typically includes vendor and tool name (e.g., "vendor:tool:version").
        
        Returns:
            String identifying the creating tool, or empty string if not set.
            
        Raises:
            UnimplError: If tool metadata is not supported.
            
        Example:
            >>> tool = db.getWrittenBy()
            >>> print(f"Database created by: {tool}")
            
        See Also:
            setWrittenBy(): Set tool identifier
        """
        raise UnimplError()
    
    def setWrittenBy(self, by : str):
        """Set the tool identifier for this database.
        
        Stores a string identifying the tool creating or modifying this database.
        Convention is "vendor:tool:version" format.
        
        Args:
            by: Tool identifier string (e.g., "Acme:Simulator:2.5").
            
        Raises:
            UnimplError: If tool metadata is not supported.
            
        Example:
            >>> db.setWrittenBy("MyCompany:CoverageTool:1.0")
            
        See Also:
            getWrittenBy(): Retrieve tool identifier
        """
        raise UnimplError()

    def getWrittenTime(self)->int:
        """Get the timestamp when the database was written.
        
        Returns the time (typically Unix epoch seconds) when the database was
        last written to persistent storage.
        
        Returns:
            Integer timestamp (seconds since epoch), or 0 if not set.
            
        Raises:
            UnimplError: If timestamp metadata is not supported.
            
        Example:
            >>> import time
            >>> ts = db.getWrittenTime()
            >>> print(f"Written: {time.ctime(ts)}")
            
        See Also:
            setWrittenTime(): Set database timestamp
        """
        raise UnimplError()
    
    def setWrittenTime(self, time : int):
        """Set the timestamp for this database.
        
        Stores the time when the database was written. Typically set automatically
        during write() operations.
        
        Args:
            time: Timestamp as seconds since Unix epoch.
            
        Raises:
            UnimplError: If timestamp metadata is not supported.
            
        Example:
            >>> import time
            >>> db.setWrittenTime(int(time.time()))
            
        See Also:
            getWrittenTime(): Retrieve database timestamp
        """
        raise UnimplError()
    
    def getDBVersion(self):
        """Get the database format version.
        
        Returns a version identifier for the database format/schema. This may
        differ from the API version if the file uses an older format.
        
        Returns:
            Version identifier (format depends on backend).
            
        Raises:
            UnimplError: If version information is not available.
            
        See Also:
            getAPIVersion(): Get API version
            UCIS LRM Section 8.18.2 "ucis_GetDBVersion"
        """
        raise UnimplError()
    
    def getPathSeparator(self):
        """Get the hierarchical path separator character.
        
        Returns the character used to separate components in hierarchical scope
        names. Default is typically '/' but can be customized per database.
        
        Returns:
            Single character string (e.g., '/', '.').
            
        Raises:
            UnimplError: If path separator is not supported.
            
        Example:
            >>> sep = db.getPathSeparator()
            >>> path = f"top{sep}dut{sep}counter"
            
        See Also:
            setPathSeparator(): Change path separator
            UCIS LRM Section 8.1.7 "ucis_GetPathSeparator"
        """
        raise UnimplError()

    def setPathSeparator(self, separator):
        """Set the hierarchical path separator character.
        
        Changes the character used for hierarchical scope name separation.
        This affects how full paths are constructed and interpreted.
        
        Args:
            separator: Single character to use as separator (typically '/' or '.').
            
        Raises:
            UnimplError: If path separator customization is not supported.
            ValueError: If separator is invalid (e.g., multi-character).
            
        Note:
            Changing the separator after scopes are created may cause path
            resolution issues. Set this before building the hierarchy.
            
        See Also:
            getPathSeparator(): Retrieve current separator
            UCIS LRM Section 8.1.8 "ucis_SetPathSeparator"
        """
        raise UnimplError()
    
    def createFileHandle(self, filename : str, workdir : str)->FileHandle:
        """Create a file handle for source file references.
        
        Creates a FileHandle object representing a source file. File handles enable
        efficient storage of file references - each unique filename is stored once
        and referenced by multiple objects through handles.
        
        Args:
            filename: Source file name or path. Can be absolute or relative to workdir.
            workdir: Working directory for resolving relative paths. If filename is
                absolute, workdir is ignored. Can be None for relative-to-current.
                
        Returns:
            FileHandle object referencing the specified file.
            
        Raises:
            UnimplError: If file handles are not supported.
            ValueError: If filename is empty or invalid.
            
        Example:
            >>> # Absolute path
            >>> fh1 = db.createFileHandle("/project/rtl/counter.sv", None)
            >>> # Relative path with workdir
            >>> fh2 = db.createFileHandle("alu.sv", "/project/rtl")
            >>> # Use in source location
            >>> src = SourceInfo(fh2, 42, 0)
            
        Note:
            The file need not exist at creation time. File handles store path
            information for later resolution.
            
        See Also:
            FileHandle: File handle operations
            SourceInfo: Source location using file handles
            UCIS LRM Section 8.12.2 "ucis_CreateFileHandle"
        """
        raise UnimplError()
    
    def createHistoryNode(self, 
                         parent : HistoryNode, 
                         logicalname : str, 
                         physicalname : str, 
                         kind : HistoryNodeKind)->HistoryNode:
        """Create a history node for test or merge tracking.
        
        Creates a HistoryNode to record information about test runs, merges, or
        other database operations. History nodes form a tree tracking how the
        database was constructed over time.
        
        Args:
            parent: Parent history node, or None for root-level nodes. Forms
                hierarchy for tracking merge operations.
            logicalname: Logical identifier (e.g., test name, merge operation name).
            physicalname: Physical identifier (e.g., test command, file path).
            kind: Type of history node (HistoryNodeKind: TEST, TESTPLAN, MERGE, etc.).
                
        Returns:
            Newly created HistoryNode object.
            
        Raises:
            UnimplError: If history tracking is not supported.
            ValueError: If parameters are invalid.
            
        Example:
            >>> # Create test history node
            >>> test = db.createHistoryNode(
            ...     None,
            ...     "test_basic",
            ...     "./run_sim.sh",
            ...     HistoryNodeKind.TEST)
            >>> # Set test data
            >>> from ucis.test_data import TestData
            >>> from ucis.test_status_t import TestStatusT
            >>> td = TestData(teststatus=TestStatusT.OK,
            ...               toolcategory="simulator",
            ...               date="2024-01-15")
            >>> test.setTestData(td)
            
        See Also:
            HistoryNode: History node operations
            HistoryNodeKind: Node type enumeration
            TestData: Test execution metadata
            UCIS LRM Section 8.13.1 "ucis_CreateHistoryNode"
        """
        raise UnimplError()
    
    def historyNodes(self, kind : HistoryNodeKind) -> Iterator[HistoryNode]:
        """Iterate over history nodes of a specific kind.
        
        Returns an iterator over history nodes, filtered by node kind. Enables
        traversal of test history for analysis and reporting.
        
        Args:
            kind: Type of history nodes to iterate (HistoryNodeKind enum).
                Use HistoryNodeKind.TEST for test runs, MERGE for merge operations.
                
        Yields:
            HistoryNode objects matching the specified kind.
            
        Raises:
            UnimplError: If history iteration is not supported.
            
        Example:
            >>> # Iterate all test nodes
            >>> for test in db.historyNodes(HistoryNodeKind.TEST):
            ...     td = test.getTestData()
            ...     print(f"Test: {test.getLogicalName()}, Status: {td.teststatus}")
            
        See Also:
            getHistoryNodes(): Get history nodes as a list
            createHistoryNode(): Create history nodes
            UCIS LRM Section 8.8.1 "ucis_HistoryIterate"
        """
        raise UnimplError()
    
    def getHistoryNodes(self, kind : HistoryNodeKind) -> List[HistoryNode]:
        """Get history nodes of a specific kind as a list.
        
        Convenience method that returns all matching history nodes as a list
        rather than an iterator. Useful when you need the full collection.
        
        Args:
            kind: Type of history nodes to retrieve (HistoryNodeKind enum).
            
        Returns:
            List of HistoryNode objects matching the specified kind.
            
        Example:
            >>> tests = db.getHistoryNodes(HistoryNodeKind.TEST)
            >>> print(f"Database contains {len(tests)} tests")
            
        See Also:
            historyNodes(): Iterator version
        """
        return list(self.historyNodes(kind))
    
    def getSourceFiles(self) -> [SourceFile]:
        """Get the list of source files referenced in the database.
        
        Returns all source files that are referenced by coverage objects through
        file handles. Useful for generating file-level coverage reports.
        
        Returns:
            List of SourceFile objects representing referenced files.
            
        Raises:
            UnimplError: If source file enumeration is not supported.
            
        Example:
            >>> for src_file in db.getSourceFiles():
            ...     print(f"File: {src_file.getName()}")
            
        See Also:
            createFileHandle(): Create file references
            SourceFile: Source file information
        """
        raise UnimplError()
    
    def getCoverInstances(self) -> [InstanceCoverage]:
        """Get per-instance coverage data.
        
        Returns coverage information organized by instance for covergroups that
        have per-instance coverage enabled. This allows analysis of coverage
        differences across multiple instances of the same module.
        
        Returns:
            List of InstanceCoverage objects.
            
        Raises:
            UnimplError: If instance coverage tracking is not supported.
            
        Example:
            >>> for inst_cov in db.getCoverInstances():
            ...     print(f"Instance: {inst_cov.getInstanceName()}")
            
        See Also:
            InstanceCoverage: Per-instance coverage data
            IntProperty.CVG_PERINSTANCE: Per-instance coverage flag
        """
        raise UnimplError()
    
    def write(self, file : str, scope=None, recurse : bool=True, covertype : int=-1):
        """Write the database to a persistent file.
        
        Serializes the coverage database to a file in the backend's native format
        (XML, SQLite, YAML, etc.). This operation commits the in-memory state to
        persistent storage.
        
        Args:
            file: Output file path. File extension may determine format (.xml, .ucis, etc.).
            scope: Starting scope for partial writes. If None, writes entire database.
                Allows exporting subtrees of the coverage hierarchy.
            recurse: If True (default), write scope and all descendants. If False,
                write only the specified scope level.
            covertype: Coverage type mask to filter which cover items are written.
                Use -1 (default) for all types, or CoverTypeT mask to filter.
                
        Raises:
            UnimplError: If write operation is not supported.
            IOError: If file cannot be written.
            ValueError: If parameters are invalid.
            
        Example:
            >>> # Write entire database
            >>> db.write("coverage.xml")
            >>> 
            >>> # Write subtree starting at specific scope
            >>> scope = db.getScopeByName("top/dut")
            >>> db.write("dut_coverage.xml", scope=scope)
            >>> 
            >>> # Write only functional coverage (no code coverage)
            >>> from ucis.cover_type_t import CoverTypeT
            >>> db.write("funcov.xml", covertype=CoverTypeT.CVGBIN)
            
        Note:
            The specific file format depends on the backend implementation.
            Some backends may support multiple formats based on file extension.
            
        See Also:
            close(): Close database and free resources
            UCIS LRM Section 8.1.3 "ucis_Write"
        """
        raise UnimplError()

    def close(self):
        """Close the database and commit changes to backing storage.
        
        Closes the database, frees all associated resources, and (for persistent
        backends) ensures changes are committed to storage. After closing, the
        database object should not be used.
        
        For backends with transaction support, this commits any pending
        transactions. For file-based backends, this may trigger an implicit
        write if not already saved.
        
        Raises:
            UnimplError: If close operation is not supported.
            IOError: If pending changes cannot be committed.
            
        Example:
            >>> db = MemFactory.create()
            >>> # ... populate database ...
            >>> db.write("coverage.xml")
            >>> db.close()
            >>> # db should not be used after this point
            
        Note:
            Best practice is to explicitly call close() when done with a database,
            even though Python garbage collection may eventually free resources.
            Use context managers (with statement) if available for automatic cleanup.
            
        See Also:
            write(): Save database before closing
            UCIS LRM Section 8.1.4 "ucis_Close"
        """
        raise UnimplError()
