"""Formal verification status enumeration (UCIS §8.19.3)."""

from enum import IntEnum


class FormalStatusT(IntEnum):
    NONE         = 0  # No formal info (default)
    FAILURE      = 1  # Assertion fails
    PROOF        = 2  # Proven to never fail
    VACUOUS      = 3  # Assertion is vacuous
    INCONCLUSIVE = 4  # Proof failed to complete
    ASSUMPTION   = 5  # Assertion is an assume
    CONFLICT     = 6  # Data merge conflict
