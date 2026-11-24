"""Comprehensive unit tests for urgency definitions, UNCERTAIN state, and ordering invariants."""

import pytest
from app.core.urgency import (
    UNCERTAIN,
    UncertainType,
    Urgency,
    is_downgrade,
    select_most_urgent,
    validate_urgency,
)


class TestUrgencyEnum:
    """Tests for the Urgency IntEnum."""

    def test_urgency_values(self):
        """Urgency levels must strictly match 1=Emergency, 2=Urgent, 3=Routine, 4=Self-care."""
        assert Urgency.EMERGENCY == 1
        assert Urgency.URGENT == 2
        assert Urgency.ROUTINE == 3
        assert Urgency.SELF_CARE == 4

    def test_urgency_ordering(self):
        """Lower integer value must denote more urgent clinical priority."""
        assert Urgency.EMERGENCY < Urgency.URGENT
        assert Urgency.URGENT < Urgency.ROUTINE
        assert Urgency.ROUTINE < Urgency.SELF_CARE

    def test_urgency_display_names(self):
        """Verify clinical display names."""
        assert Urgency.EMERGENCY.display_name == "Emergency"
        assert Urgency.URGENT.display_name == "Urgent"
        assert Urgency.ROUTINE.display_name == "Routine"
        assert Urgency.SELF_CARE.display_name == "Self-care"


class TestUncertainState:
    """Tests for the distinct UNCERTAIN state sentinel."""

    def test_uncertain_is_not_an_int(self):
        """UNCERTAIN must NOT inherit from int or float."""
        assert not isinstance(UNCERTAIN, int)
        assert not isinstance(UNCERTAIN, float)
        assert type(UNCERTAIN) is UncertainType

    def test_uncertain_singleton_identity_and_representation(self):
        """UNCERTAIN is a singleton with clear string representations."""
        another = UncertainType()
        assert another is UNCERTAIN
        assert repr(UNCERTAIN) == "UNCERTAIN"
        assert str(UNCERTAIN) == "UNCERTAIN"
        assert bool(UNCERTAIN) is True
        assert hash(UNCERTAIN) == hash("SAFETRIAGE_UNCERTAIN_STATE")

    def test_uncertain_equality(self):
        """UNCERTAIN equals another UNCERTAIN, but never an int or string."""
        assert UNCERTAIN == UncertainType()
        assert UNCERTAIN != 1
        assert UNCERTAIN != 2
        assert UNCERTAIN != 3
        assert UNCERTAIN != 4
        assert UNCERTAIN != "UNCERTAIN"
        assert UNCERTAIN != None  # noqa: E711

    def test_uncertain_ordering_with_levels_raises_typeerror(self):
        """Any comparison (<, <=, >, >=) between UNCERTAIN and Urgency levels MUST raise TypeError."""
        for level in Urgency:
            # UNCERTAIN on left
            with pytest.raises(TypeError, match="UNCERTAIN cannot be ordered"):
                _ = UNCERTAIN < level
            with pytest.raises(TypeError, match="UNCERTAIN cannot be ordered"):
                _ = UNCERTAIN <= level
            with pytest.raises(TypeError, match="UNCERTAIN cannot be ordered"):
                _ = UNCERTAIN > level
            with pytest.raises(TypeError, match="UNCERTAIN cannot be ordered"):
                _ = UNCERTAIN >= level

            # UNCERTAIN on right
            with pytest.raises(TypeError, match="UNCERTAIN cannot be ordered"):
                _ = level < UNCERTAIN
            with pytest.raises(TypeError, match="UNCERTAIN cannot be ordered"):
                _ = level <= UNCERTAIN
            with pytest.raises(TypeError, match="UNCERTAIN cannot be ordered"):
                _ = level > UNCERTAIN
            with pytest.raises(TypeError, match="UNCERTAIN cannot be ordered"):
                _ = level >= UNCERTAIN

    def test_uncertain_ordering_with_raw_integers_raises_typeerror(self):
        """Any comparison (<, <=, >, >=) between UNCERTAIN and raw integers MUST raise TypeError."""
        for val in (-1, 0, 1, 2, 3, 4, 5):
            with pytest.raises(TypeError, match="UNCERTAIN cannot be ordered"):
                _ = UNCERTAIN < val
            with pytest.raises(TypeError, match="UNCERTAIN cannot be ordered"):
                _ = UNCERTAIN <= val
            with pytest.raises(TypeError, match="UNCERTAIN cannot be ordered"):
                _ = UNCERTAIN > val
            with pytest.raises(TypeError, match="UNCERTAIN cannot be ordered"):
                _ = UNCERTAIN >= val

            with pytest.raises(TypeError, match="UNCERTAIN cannot be ordered"):
                _ = val < UNCERTAIN
            with pytest.raises(TypeError, match="UNCERTAIN cannot be ordered"):
                _ = val <= UNCERTAIN
            with pytest.raises(TypeError, match="UNCERTAIN cannot be ordered"):
                _ = val > UNCERTAIN
            with pytest.raises(TypeError, match="UNCERTAIN cannot be ordered"):
                _ = val >= UNCERTAIN


class TestDowngradeDetection:
    """Exhaustive tests for is_downgrade."""

    @pytest.mark.parametrize(
        ("old", "new", "expected"),
        [
            # From Level 1 (Emergency)
            (Urgency.EMERGENCY, Urgency.EMERGENCY, False),
            (Urgency.EMERGENCY, Urgency.URGENT, True),     # Downgrade
            (Urgency.EMERGENCY, Urgency.ROUTINE, True),    # Downgrade
            (Urgency.EMERGENCY, Urgency.SELF_CARE, True),  # Downgrade
            # From Level 2 (Urgent)
            (Urgency.URGENT, Urgency.EMERGENCY, False),    # Escalation
            (Urgency.URGENT, Urgency.URGENT, False),
            (Urgency.URGENT, Urgency.ROUTINE, True),       # Downgrade
            (Urgency.URGENT, Urgency.SELF_CARE, True),     # Downgrade
            # From Level 3 (Routine)
            (Urgency.ROUTINE, Urgency.EMERGENCY, False),   # Escalation
            (Urgency.ROUTINE, Urgency.URGENT, False),      # Escalation
            (Urgency.ROUTINE, Urgency.ROUTINE, False),
            (Urgency.ROUTINE, Urgency.SELF_CARE, True),    # Downgrade
            # From Level 4 (Self-care)
            (Urgency.SELF_CARE, Urgency.EMERGENCY, False), # Escalation
            (Urgency.SELF_CARE, Urgency.URGENT, False),    # Escalation
            (Urgency.SELF_CARE, Urgency.ROUTINE, False),   # Escalation
            (Urgency.SELF_CARE, Urgency.SELF_CARE, False),
        ],
    )
    def test_all_sixteen_pairwise_downgrade_combinations(self, old, new, expected):
        """Every possible transition between Urgency levels correctly evaluated."""
        assert is_downgrade(old, new) is expected

    def test_is_downgrade_with_uncertain_raises_typeerror(self):
        """UNCERTAIN cannot be passed to is_downgrade."""
        with pytest.raises(TypeError, match="UNCERTAIN cannot be evaluated for urgency downgrade"):
            is_downgrade(UNCERTAIN, Urgency.ROUTINE)  # type: ignore

        with pytest.raises(TypeError, match="UNCERTAIN cannot be evaluated for urgency downgrade"):
            is_downgrade(Urgency.ROUTINE, UNCERTAIN)  # type: ignore

    def test_is_downgrade_with_invalid_types_raises_typeerror(self):
        """Non-urgency types must raise TypeError."""
        with pytest.raises(TypeError, match="Arguments must be Urgency instances"):
            is_downgrade(1, Urgency.ROUTINE)  # type: ignore

        with pytest.raises(TypeError, match="Arguments must be Urgency instances"):
            is_downgrade(Urgency.ROUTINE, 3)  # type: ignore


class TestSelectMostUrgent:
    """Tests for select_most_urgent helper."""

    def test_select_most_urgent_varied_order(self):
        """select_most_urgent picks the lowest integer priority regardless of order."""
        assert select_most_urgent(Urgency.ROUTINE, Urgency.EMERGENCY, Urgency.SELF_CARE) == Urgency.EMERGENCY
        assert select_most_urgent(Urgency.SELF_CARE, Urgency.URGENT) == Urgency.URGENT
        assert select_most_urgent(Urgency.SELF_CARE) == Urgency.SELF_CARE

    def test_select_most_urgent_empty_raises_valueerror(self):
        """Calling with no arguments raises ValueError."""
        with pytest.raises(ValueError, match="At least one Urgency level must be provided"):
            select_most_urgent()

    def test_select_most_urgent_with_uncertain_raises_typeerror(self):
        """UNCERTAIN cannot be included in select_most_urgent."""
        with pytest.raises(TypeError, match="UNCERTAIN cannot be compared"):
            select_most_urgent(Urgency.ROUTINE, UNCERTAIN)  # type: ignore

    def test_select_most_urgent_with_non_urgency_raises_typeerror(self):
        """Non-urgency arguments raise TypeError."""
        with pytest.raises(TypeError, match="Expected Urgency instance"):
            select_most_urgent(Urgency.ROUTINE, 1)  # type: ignore


class TestValidateUrgency:
    """Tests for validate_urgency and strict rejection of out-of-range levels."""

    def test_valid_levels_accepted(self):
        """Valid integer levels 1..4 and Urgency enums must be accepted."""
        for lvl in (1, 2, 3, 4):
            validated = validate_urgency(lvl)
            assert validated == Urgency(lvl)
            assert isinstance(validated, Urgency)

        for lvl in Urgency:
            assert validate_urgency(lvl) is lvl

    def test_out_of_range_levels_rejected_never_clamped(self):
        """Out-of-range levels (0, 5, -1, 99) must be rejected with None, NEVER clamped."""
        assert validate_urgency(0) is None
        assert validate_urgency(5) is None
        assert validate_urgency(-1) is None
        assert validate_urgency(99) is None
        assert validate_urgency(-99) is None

    def test_non_integers_and_uncertain_rejected(self):
        """UNCERTAIN, strings, floats, booleans, and None must return None."""
        assert validate_urgency(UNCERTAIN) is None
        assert validate_urgency("1") is None
        assert validate_urgency(1.0) is None
        assert validate_urgency(True) is None   # bool is subclass of int in Python
        assert validate_urgency(False) is None
        assert validate_urgency(None) is None
