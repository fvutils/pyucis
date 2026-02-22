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

"""In-memory toggle coverage scope."""

from ucis.mem.mem_scope import MemScope
from ucis.scope_type_t import ScopeTypeT
from ucis.source_t import SourceT
from ucis.flags_t import FlagsT
from ucis.toggle_dir_t import ToggleDirT
from ucis.toggle_metric_t import ToggleMetricT
from ucis.toggle_type_t import ToggleTypeT
from ucis.int_property import IntProperty
from ucis.str_property import StrProperty


class MemToggleScope(MemScope):
    """In-memory implementation of a toggle coverage scope.

    Represents a single signal with toggle coverage tracking.
    Bins are created via createNextCover() with TOGGLEBIN cover type.
    """

    def __init__(self, parent, name, srcinfo, weight, source, flags=0):
        super().__init__(parent, name, srcinfo, weight, source,
                         ScopeTypeT.TOGGLE, flags)
        self._canonical_name = name
        self._toggle_metric = ToggleMetricT._2STOGGLE
        self._toggle_type = ToggleTypeT.NET
        self._toggle_dir = ToggleDirT.INTERNAL
        self._num_bits = 1

    # --- Canonical name ---

    def getCanonicalName(self) -> str:
        return self._canonical_name

    def setCanonicalName(self, name: str):
        self._canonical_name = name

    # --- Toggle metric, type, direction ---

    def getToggleMetric(self) -> ToggleMetricT:
        return self._toggle_metric

    def setToggleMetric(self, metric: ToggleMetricT):
        self._toggle_metric = metric

    def getToggleType(self) -> ToggleTypeT:
        return self._toggle_type

    def setToggleType(self, t: ToggleTypeT):
        self._toggle_type = t

    def getToggleDir(self) -> ToggleDirT:
        return self._toggle_dir

    def setToggleDir(self, d: ToggleDirT):
        self._toggle_dir = d

    def getNumBits(self) -> int:
        return self._num_bits

    def setNumBits(self, n: int):
        self._num_bits = n

    # --- Aggregate counts from cover items ---

    def getTotalToggle01(self) -> int:
        """Sum of all 0->1 transition counts across bins."""
        from ucis.cover_type_t import CoverTypeT
        total = 0
        for item in self.m_cover_items:
            if item.m_data is not None and item.m_data.type == CoverTypeT.TOGGLEBIN:
                if '0->1' in item.m_name or '01' in item.m_name:
                    total += item.m_data.data
        return total

    def getTotalToggle10(self) -> int:
        """Sum of all 1->0 transition counts across bins."""
        from ucis.cover_type_t import CoverTypeT
        total = 0
        for item in self.m_cover_items:
            if item.m_data is not None and item.m_data.type == CoverTypeT.TOGGLEBIN:
                if '1->0' in item.m_name or '10' in item.m_name:
                    total += item.m_data.data
        return total

    # --- Property overrides ---

    def getIntProperty(self, coverindex, property):
        if property == IntProperty.TOGGLE_TYPE:
            return int(self._toggle_type)
        elif property == IntProperty.TOGGLE_DIR:
            return int(self._toggle_dir)
        elif property == IntProperty.TOGGLE_METRIC:
            return int(self._toggle_metric)
        elif property == IntProperty.TOGGLE_COVERED:
            # Covered if at least one bin of each transition direction has count > 0
            from ucis.cover_type_t import CoverTypeT
            has01 = any(
                item.m_data is not None
                and item.m_data.type == CoverTypeT.TOGGLEBIN
                and item.m_data.data > 0
                and ('0->1' in item.m_name or '01' in item.m_name)
                for item in self.m_cover_items
            )
            has10 = any(
                item.m_data is not None
                and item.m_data.type == CoverTypeT.TOGGLEBIN
                and item.m_data.data > 0
                and ('1->0' in item.m_name or '10' in item.m_name)
                for item in self.m_cover_items
            )
            return 1 if (has01 and has10) else 0
        return super().getIntProperty(coverindex, property)

    def setIntProperty(self, coverindex, property, value):
        if property == IntProperty.TOGGLE_TYPE:
            self._toggle_type = ToggleTypeT(value)
        elif property == IntProperty.TOGGLE_DIR:
            self._toggle_dir = ToggleDirT(value)
        elif property == IntProperty.TOGGLE_METRIC:
            self._toggle_metric = ToggleMetricT(value)
        else:
            super().setIntProperty(coverindex, property, value)

    def getStringProperty(self, coverindex, property):
        if property == StrProperty.TOGGLE_CANON_NAME:
            return self._canonical_name
        return super().getStringProperty(coverindex, property)

    def setStringProperty(self, coverindex, property, value):
        if property == StrProperty.TOGGLE_CANON_NAME:
            self._canonical_name = value
        else:
            super().setStringProperty(coverindex, property, value)
