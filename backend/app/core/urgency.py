"""Urgency definitions and operations for SafeTriage.

Core clinical invariants:
1. Urgency levels: 1=Emergency, 2=Urgent, 3=Routine, 4=Self-care (lower number = more urgent).
2. UNCERTAIN is a DISTINCT STATE, not an integer level. It cannot be ordered or compared
   against Urgency levels (any comparison raises TypeError). It is never displayed as
   Level 3, Level 4, or 'self-care'.
3. Transitions to higher numbers (e.g., 2 -> 3) represent clinical DOWNGRADES.
   Transitions to lower numbers (e.g., 3 -> 1) represent ESCALATIONS.
"""

from enum import IntEnum
from typing import Any, Union


class Urgency(IntEnum):
    """Clinical urgency levels for symptom triage.
    
    Lower integer value = more urgent priority.
    """
    EMERGENCY = 1
    URGENT = 2
    ROUTINE = 3
    SELF_CARE = 4

    @property
    def display_name(self) -> str:
        return {
            Urgency.EMERGENCY: "Emergency",
            Urgency.URGENT: "Urgent",
            Urgency.ROUTINE: "Routine",
            Urgency.SELF_CARE: "Self-care",
        }[self]


class UncertainType:
    """Distinct non-integer sentinel state representing clinical uncertainty.
    
    UNCERTAIN is not an integer level and has no numeric value.
    Any comparison (<, <=, >, >=) with Urgency levels, integers, or floats
    MUST raise a TypeError.
    """
    _instance: "UncertainType | None" = None

    def __new__(cls) -> "UncertainType":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "UNCERTAIN"

    def __str__(self) -> str:
        return "UNCERTAIN"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, UncertainType)

    def __hash__(self) -> int:
        return hash("SAFETRIAGE_UNCERTAIN_STATE")

    def __bool__(self) -> bool:
        return True

    # Ordering comparisons against levels or numbers MUST raise TypeError
    def __lt__(self, other: object) -> bool:
        raise TypeError(f"UNCERTAIN cannot be ordered or compared with {type(other).__name__}")

    def __le__(self, other: object) -> bool:
        raise TypeError(f"UNCERTAIN cannot be ordered or compared with {type(other).__name__}")

    def __gt__(self, other: object) -> bool:
        raise TypeError(f"UNCERTAIN cannot be ordered or compared with {type(other).__name__}")

    def __ge__(self, other: object) -> bool:
        raise TypeError(f"UNCERTAIN cannot be ordered or compared with {type(other).__name__}")


UNCERTAIN = UncertainType()
UrgencyOrUncertain = Union[Urgency, UncertainType]


def is_downgrade(old: Urgency, new: Urgency) -> bool:
    """Determine if moving from 'old' to 'new' constitutes a clinical downgrade.
    
    In SafeTriage:
    - Lower integer = more urgent priority (1=Emergency, 4=Self-care).
    - If new > old, the assigned priority is less urgent (e.g., 2 Urgent -> 3 Routine).
      This is a downgrade and returns True.
    - If new < old, the assigned priority is more urgent (e.g., 3 Routine -> 1 Emergency).
      This is an escalation and returns False.
    - If new == old, no change, returns False.
    
    Both arguments must be Urgency instances. If either is UNCERTAIN or another type,
    a TypeError is raised.
    """
    if isinstance(old, UncertainType) or isinstance(new, UncertainType):
        raise TypeError("UNCERTAIN cannot be evaluated for urgency downgrade")
    if not isinstance(old, Urgency) or not isinstance(new, Urgency):
        raise TypeError(f"Arguments must be Urgency instances, got {type(old).__name__} and {type(new).__name__}")
    
    return int(new) > int(old)


def select_most_urgent(*levels: Urgency) -> Urgency:
    """Select the most urgent level (lowest integer) from the provided levels.
    
    Raises ValueError if no levels are provided.
    Raises TypeError if any argument is UNCERTAIN or not an Urgency instance.
    """
    if not levels:
        raise ValueError("At least one Urgency level must be provided")
    for lvl in levels:
        if isinstance(lvl, UncertainType):
            raise TypeError("UNCERTAIN cannot be compared in select_most_urgent")
        if not isinstance(lvl, Urgency):
            raise TypeError(f"Expected Urgency instance, got {type(lvl).__name__}")
    return min(levels)


def validate_urgency(value: Any) -> Urgency | None:
    """Validate whether a value represents a valid Urgency level (1, 2, 3, or 4).
    
    Out-of-range levels (0, 5, -1, etc.) or non-numeric types are REJECTED
    and return None. They are NEVER clamped.
    """
    if value is None or isinstance(value, UncertainType):
        return None
    if isinstance(value, Urgency):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        try:
            return Urgency(value)
        except ValueError:
            return None
    return None
