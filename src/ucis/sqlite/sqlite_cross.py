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
SQLite-backed Cross Coverage implementation with coverpoint linkage
"""

from typing import List
from ucis.sqlite.sqlite_coverpoint import SqliteCoverpoint
from ucis.cross import Cross
from ucis.cover_data import CoverData
# Import SqliteScope for type hints
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ucis.sqlite.sqlite_scope import SqliteScope


class SqliteCross(SqliteCoverpoint, Cross):
    """Cross coverage scope linking multiple coverpoints"""
    
    def __init__(self, ucis_db, scope_id: int):
        # Must set ucis_db FIRST for getattr check in setGoal
        self.ucis_db = ucis_db
        self._initializing = True
        
        # Initialize cached state
        self._coverpoints_cache = None
        
        # Initialize parent classes
        SqliteCoverpoint.__init__(self, ucis_db, scope_id)
        
        # Reset initialization flag before calling Cross.__init__
        self._initializing = True
        Cross.__init__(self)
        
        # Clear initialization flag NOW
        self._initializing = False
    
    # UCIS standard Cross interface methods
    def getNumCrossedCoverpoints(self) -> int:
        """Get number of coverpoints in cross (UCIS standard method)"""
        return self.getNumCoverpoints()
    
    def getIthCrossedCoverpoint(self, index: int):
        """Get the i-th coverpoint in cross (UCIS standard method)"""
        coverpoints = self.getCoverpoints()
        if 0 <= index < len(coverpoints):
            return coverpoints[index]
        return None
    
    def addCoverpoint(self, coverpoint: 'SqliteScope', index: int = None):
        """Add a coverpoint to this cross"""
        # Auto-assign index if not provided
        if index is None:
            cursor = self.ucis_db.conn.execute(
                "SELECT MAX(cvp_index) FROM cross_coverpoints WHERE cross_scope_id = ?",
                (self.scope_id,)
            )
            row = cursor.fetchone()
            index = (row[0] + 1) if (row[0] is not None) else 0
        
        # Insert linkage
        self.ucis_db.conn.execute(
            """INSERT OR IGNORE INTO cross_coverpoints 
               (cross_scope_id, coverpoint_scope_id, cvp_index)
               VALUES (?, ?, ?)""",
            (self.scope_id, coverpoint.scope_id, index)
        )
        
        # Invalidate cache
        self._coverpoints_cache = None
    
    def getCoverpoints(self) -> List['SqliteScope']:
        """Get list of linked coverpoints in order"""
        if self._coverpoints_cache is not None:
            return self._coverpoints_cache
        
        cursor = self.ucis_db.conn.execute(
            """SELECT coverpoint_scope_id FROM cross_coverpoints 
               WHERE cross_scope_id = ?
               ORDER BY cvp_index""",
            (self.scope_id,)
        )
        
        self._coverpoints_cache = []
        for row in cursor:
            from ucis.sqlite.sqlite_scope import SqliteScope
            cvp = SqliteScope(self.ucis_db, row[0])
            self._coverpoints_cache.append(cvp)
        
        return self._coverpoints_cache
    
    def getNumCoverpoints(self) -> int:
        """Get number of coverpoints in cross"""
        cursor = self.ucis_db.conn.execute(
            "SELECT COUNT(*) FROM cross_coverpoints WHERE cross_scope_id = ?",
            (self.scope_id,)
        )
        row = cursor.fetchone()
        return row[0] if row else 0
    
    def createCrossBin(self, bin_name: str, coverpoint_bins: List[str]) -> 'CoverIndex':
        """
        Create a cross bin representing specific combination of coverpoint bins
        
        Args:
            bin_name: Name for the cross bin (e.g., "<low,high>")
            coverpoint_bins: List of bin names, one per coverpoint
        """
        cover_data = CoverData(0x01, 0)  # CVGBIN type for cross bins
        cover_data.data = 0
        
        cross_bin = self.createNextCover(bin_name, cover_data, None)
        
        # Could store bin combination in properties if needed
        # For now, the name encodes the combination
        
        return cross_bin
    
    def generateCartesianProduct(self):
        """
        Generate all cross bins from Cartesian product of coverpoint bins
        
        Returns the number of bins created
        """
        coverpoints = self.getCoverpoints()
        if len(coverpoints) == 0:
            return 0
        
        # Get all bins from each coverpoint
        coverpoint_bins = []
        for cvp in coverpoints:
            bins = []
            for cover in cvp.coverItems(-1):
                bins.append(cover.getName())
            coverpoint_bins.append(bins)
        
        # Generate Cartesian product
        def cartesian_helper(lists, current=[]):
            if not lists:
                return [current]
            
            result = []
            for item in lists[0]:
                result.extend(cartesian_helper(lists[1:], current + [item]))
            return result
        
        combinations = cartesian_helper(coverpoint_bins)
        
        # Create cross bins
        created = 0
        for combo in combinations:
            bin_name = "<" + ",".join(combo) + ">"
            
            # Check if bin already exists
            existing = False
            for cover in self.coverItems(-1):
                if cover.getName() == bin_name:
                    existing = True
                    break
            
            if not existing:
                self.createCrossBin(bin_name, combo)
                created += 1
        
        return created
    
    def getCrossBinByCombo(self, coverpoint_bins: List[str]) -> 'CoverIndex':
        """Get cross bin for specific coverpoint bin combination"""
        bin_name = "<" + ",".join(coverpoint_bins) + ">"
        
        # Search for matching bin
        for cover in self.coverItems(-1):
            if cover.getName() == bin_name:
                return cover
        
        return None
    
    def incrementCrossBin(self, coverpoint_bins: List[str], amt: int = 1):
        """Increment count for specific cross bin combination"""
        cross_bin = self.getCrossBinByCombo(coverpoint_bins)
        if cross_bin:
            cross_bin.incrementCover(amt)
            return True
        return False
    
    def getCoveragePercent(self) -> float:
        """Calculate cross coverage percentage"""
        total = 0
        covered = 0
        
        for cover in self.coverItems(-1):
            total += 1
            if cover.getCoverData().data > 0:
                covered += 1
        
        return (100.0 * covered / total) if total > 0 else 0.0
    
    def getCoverageMatrix(self):
        """
        Get coverage matrix for 2-way cross (useful for reporting)
        
        Returns dict of {(bin1, bin2): count} for 2-coverpoint crosses
        """
        coverpoints = self.getCoverpoints()
        if len(coverpoints) != 2:
            return None  # Only works for 2-way crosses
        
        matrix = {}
        
        for cover in self.coverItems(-1):
            name = cover.getName()
            # Parse bin name: "<bin1,bin2>"
            if name.startswith("<") and name.endswith(">"):
                bins = name[1:-1].split(",")
                if len(bins) == 2:
                    matrix[(bins[0], bins[1])] = cover.getCoverData().data
        
        return matrix
    
    def printCoverageMatrix(self):
        """
        Print coverage matrix for 2-way cross (debugging/reporting)
        """
        matrix = self.getCoverageMatrix()
        if matrix is None:
            print("Coverage matrix only available for 2-way crosses")
            return
        
        # Get unique bin names for each dimension
        bins1 = sorted(set(k[0] for k in matrix.keys()))
        bins2 = sorted(set(k[1] for k in matrix.keys()))
        
        # Print header
        print(f"\nCross Coverage Matrix: {self.getScopeName()}")
        print("=" * 60)
        print(f"{'Bin1/Bin2':<15}", end="")
        for b2 in bins2:
            print(f"{b2:>10}", end="")
        print()
        print("-" * 60)
        
        # Print rows
        for b1 in bins1:
            print(f"{b1:<15}", end="")
            for b2 in bins2:
                count = matrix.get((b1, b2), 0)
                print(f"{count:>10}", end="")
            print()
        print()
