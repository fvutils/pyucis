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
Design Unit (DU) name parsing and composition utilities.

Provides helpers for working with fully-qualified UCIS DU names of the form
"<library>.<module>". Analogues of ucis_ParseDUName and ucis_ComposeDUName
from the UCIS 1.0 LRM.

Example::

    library, module = parseDUName("work.counter")
    # library == "work", module == "counter"

    library, module = parseDUName("counter")
    # library == "work", module == "counter"  (default library)

    full_name = composeDUName("mylib", "alu")
    # full_name == "mylib.alu"
"""

DEFAULT_LIBRARY = "work"


def parseDUName(name: str, default_library: str = DEFAULT_LIBRARY):
    """Parse a fully-qualified DU name into (library, module) components.

    If ``name`` contains a dot, it is split on the first dot.  Otherwise the
    ``default_library`` is used and the whole string is treated as the module
    name.

    Args:
        name: DU name string, e.g. ``"work.counter"`` or ``"counter"``.
        default_library: Library to use when ``name`` has no library prefix.
            Defaults to ``"work"``.

    Returns:
        A ``(library, module)`` tuple of strings.

    Raises:
        ValueError: If ``name`` is empty or ``None``.

    Examples:
        >>> parseDUName("work.counter")
        ('work', 'counter')
        >>> parseDUName("alu")
        ('work', 'alu')
        >>> parseDUName("mylib.adder", default_library="mylib")
        ('mylib', 'adder')

    See Also:
        composeDUName: Inverse operation
        UCIS LRM Section 8.5.6 "ucis_ParseDUName"
    """
    if not name:
        raise ValueError("DU name must not be empty")
    parts = name.split('.', 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return default_library, parts[0]


def composeDUName(library: str, module: str) -> str:
    """Compose a fully-qualified DU name from library and module components.

    Args:
        library: Library name (e.g. ``"work"``).
        module:  Module/entity name (e.g. ``"counter"``).

    Returns:
        A string of the form ``"<library>.<module>"``.

    Raises:
        ValueError: If either argument is empty or ``None``.

    Examples:
        >>> composeDUName("work", "counter")
        'work.counter'
        >>> composeDUName("mylib", "alu")
        'mylib.alu'

    See Also:
        parseDUName: Inverse operation
        UCIS LRM Section 8.5.7 "ucis_ComposeDUName"
    """
    if not library or not module:
        raise ValueError("library and module must not be empty")
    return f"{library}.{module}"
