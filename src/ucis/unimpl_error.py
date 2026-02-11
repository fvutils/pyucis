
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

class UnimplError(Exception):
    """Exception for unimplemented functionality.
    
    Raised when a method or feature is not implemented in the current backend
    or base class. This distinguishes unimplemented methods from other errors.
    
    PyUCIS uses an interface-based design where base classes define the API
    but specific backends (XML, SQLite, in-memory, etc.) provide the actual
    implementation. UnimplError is raised when:
    
    - A base class method is called directly without backend implementation
    - A specific backend doesn't support a particular feature
    - A method is intentionally left unimplemented
    
    Example:
        >>> # Calling unimplemented method raises UnimplError
        >>> try:
        ...     scope.getIthCoverItem(0)
        ... except UnimplError:
        ...     print("Method not implemented in this backend")
        >>>
        >>> # Use with specific backend that implements the method
        >>> from ucis.mem import UCIS_mem
        >>> db = UCIS_mem("coverage.ucis")
        >>> # Now methods are implemented
        
    See Also:
        NotImplementedError: Python's built-in for similar purpose
    """
    
    def __init__(self, msg=""):
        """Create UnimplError with optional message.
        
        Args:
            msg: Optional error message describing what is unimplemented.
        """
        super().__init__(msg)