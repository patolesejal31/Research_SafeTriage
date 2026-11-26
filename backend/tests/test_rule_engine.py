"""Comprehensive tests for the SafeTriage deterministic clinical rule engine."""

from pathlib import Path
import pytest

from app.core.urgency import Urgency
from app.triage.engine import RuleEngine
from app.triage.invariant import ComponentStatus
from app.triage.nlp_extractor import NLPExtractor


@pytest.fixture
def engine() -> RuleEngine:
    return RuleEngine()


@pytest.fixture
def extractor() -> NLPExtractor:
    return NLPExtractor()


class TestRuleGovernanceAndIntegrity:
    """Tests for rule uniqueness, source traceability, and review status governance."""

    def test_rule_ids_unique_across_all_files(self, engine: RuleEngine):
        """Every rule ID must be strictly unique across all specialty rule YAML files."""
        rule_ids = [r.id for r in engine.rules]
        assert len(rule_ids) >= 25, f"Expected at least 25 rules, found {len(rule_ids)}"
        assert len(rule_ids) == len(set(rule_ids)), f"Duplicate rule IDs found: {set([x for x in rule_ids if rule_ids.count(x) > 1])}"

    def test_every_rule_has_source_and_is_unverified(self, engine: RuleEngine):
        """Invariant: Every rule must have a valid source object and be marked UNVERIFIED with verified=false."""
        for rule in engine.rules:
            assert rule.review_status == "UNVERIFIED", f"Rule {rule.id} has invalid review status {rule.review_status}"
            assert rule.reviewer_initials is None, f"Rule {rule.id} must not have reviewer initials set"
            assert rule.source is not None, f"Rule {rule.id} missing source object"
            assert rule.source.body, f"Rule {rule.id} source missing body"
            assert rule.source.document_title, f"Rule {rule.id} source missing document title"
            assert rule.source.year > 2000, f"Rule {rule.id} source invalid year"
            assert rule.source.verified is False, f"Rule {rule.id} must not be marked verified without human signoff"

    def test_duplicate_rule_id_raises_valueerror(self, tmp_path: Path):
        """RuleEngine must reject duplicate rule IDs across files with ValueError."""
        r1 = tmp_path / "spec1.yaml"
        r2 = tmp_path / "spec2.yaml"
        content = """
rules:
  - id: "DUP-001"
    level: 1
    name: "Duplicate Rule"
    conditions:
      all_of:
        - concept: "fever"
"""
        r1.write_text(content, encoding="utf-8")
        r2.write_text(content, encoding="utf-8")
        with pytest.raises(ValueError, match="Duplicate Rule ID detected"):
            RuleEngine(rules_dir=tmp_path)

    def test_nonexistent_directories_handled_gracefully(self, tmp_path: Path):
        """RuleEngine handles non-existent paths without unhandled crashes."""
        eng = RuleEngine(rules_dir=tmp_path / "nonexistent", age_bands_path=tmp_path / "none.yaml")
        assert eng.rules == []
        assert eng.age_bands == {}

    def test_age_text_heuristics(self, engine: RuleEngine):
        """Verify fallback age text parsing into appropriate clinical bands."""
        assert engine.resolve_age_band(age_text="senior citizen") == "older_adult"
        assert engine.resolve_age_band(age_text="young adult") == "adult"
        assert engine.resolve_age_band(age_text="child") == "school_age_child"
        assert engine.resolve_age_band(age_text="toddler") == "toddler"
        assert engine.resolve_age_band(age_text="baby") == "young_infant"
        assert engine.resolve_age_band(age_text="unknown string") == "unknown"

    def test_coverage_report(self, engine: RuleEngine):
        """Verify engine coverage report outputs rules per level and per specialty."""
        report = engine.get_rule_coverage_report()
        assert report["total_rules"] >= 25
        assert report["rules_by_level"][1] >= 10, "Expected at least 10 Level 1 emergency rules"
        assert report["all_unverified"] is True
        assert len(report["rules_by_specialty"]) == 10, "Expected all 10 clinical specialties present"


class TestLevel1Precedence:
    """Requirement: Level 1 emergency rules are always evaluated first regardless of file order."""

    def test_rules_sorted_by_urgency_ascending(self, engine: RuleEngine):
        """Internal rule list must be strictly ordered with Level 1 first, then 2, 3, 4."""
        levels = [int(r.level) for r in engine.rules]
        assert levels == sorted(levels)

    def test_level_1_overrides_lower_urgency_in_same_presentation(self, engine: RuleEngine, extractor: NLPExtractor):
        """When presentation matches both a Level 1 rule and a Level 3 rule, Level 1 is returned."""
        # Patient with acute crushing chest pain (Level 1 CARD-001) and cough (Level 3 RESP-003)
        ext = extractor.extract("Patient has severe crushing chest pain and persistent cough.")
        res = engine.evaluate(ext, age_years=45)

        assert res.component_result.status == ComponentStatus.OK
        assert res.component_result.level == Urgency.EMERGENCY
        assert res.triggered_rule.id == "CARD-001"
        assert any(r.id == "RESP-003" for r in res.all_matched_rules)


class TestAgeBandBoundariesAndUnknownHandling:
    """Requirement: Clinical age cutoffs referencing age_bands.yaml with boundary tests and unknown handling."""

    @pytest.mark.parametrize(
        ("age_days", "expected_band"),
        [
            (10, "neonate"),           # 10 days < 28 days
            (27, "neonate"),           # 27 days < 28 days
            (28, "young_infant"),      # 28 days boundary
            (35, "young_infant"),      # 35 days
        ],
    )
    def test_neonate_to_young_infant_boundary(self, engine: RuleEngine, age_days: int, expected_band: str):
        """Boundary test at 28 days (<28 days neonate, >=28 days young infant)."""
        band = engine.resolve_age_band(age_days=age_days)
        assert band == expected_band

    @pytest.mark.parametrize(
        ("age_months", "expected_band"),
        [
            (2.9, "young_infant"),     # < 3.0 months
            (3.0, "older_infant"),     # exactly 3.0 months boundary (NICE NG143 Amber)
            (5.9, "older_infant"),     # < 6.0 months
            (6.0, "toddler"),          # exactly 6.0 months boundary
            (23.9, "toddler"),
            (24.0, "preschool_child"), # 2 years
            (59.9, "preschool_child"),
            (60.0, "school_age_child"), # 5 years
        ],
    )
    def test_infant_and_child_boundaries(self, engine: RuleEngine, age_months: float, expected_band: str):
        """Boundary tests at 3 months, 6 months, 2 years, and 5 years."""
        band = engine.resolve_age_band(age_months=age_months)
        assert band == expected_band

    @pytest.mark.parametrize(
        ("age_years", "expected_band"),
        [
            (17.9, "adolescent"),
            (18.0, "adult"),           # 18 years adult boundary
            (64.9, "adult"),
            (65.0, "older_adult"),     # 65 years older adult boundary
            (80.0, "older_adult"),
        ],
    )
    def test_adult_and_older_adult_boundaries(self, engine: RuleEngine, age_years: float, expected_band: str):
        """Boundary tests at 18 years and 65 years."""
        band = engine.resolve_age_band(age_years=age_years)
        assert band == expected_band

    def test_unknown_age_flags_followup_and_does_not_assume_adult(self, engine: RuleEngine, extractor: NLPExtractor):
        """Unknown or 'prefer not to say' age flags requires_age_followup and evaluates pediatric safety."""
        ext = extractor.extract("High fever since yesterday and lethargy.")
        res = engine.evaluate(ext, age_years=None)

        assert res.resolved_age_band == "unknown"
        assert res.requires_age_followup is True


class TestEngineExceptionHandling:
    """Requirement: Engine exceptions caught and surfaced as ComponentStatus.ERROR (UNCERTAIN)."""

    def test_engine_crash_surfaces_as_error_uncertain(self, engine: RuleEngine):
        """When an unhandled exception occurs inside evaluation, engine surfaces ERROR status."""
        # Pass an object that causes an exception during condition access
        res = engine.evaluate(None)  # type: ignore

        assert res.component_result.status == ComponentStatus.ERROR
        assert res.component_result.level is None
        assert res.triggered_rule is None


class TestNegationPreventsRuleActivation:
    """Requirement: Negated entities do not trigger clinical rules."""

    def test_negated_chest_pain_does_not_trigger_card_001(self, engine: RuleEngine, extractor: NLPExtractor):
        """'No chest pain' must NOT trigger CARD-001."""
        ext = extractor.extract("Patient has no chest pain, mild cough.")
        res = engine.evaluate(ext, age_years=40)

        # CARD-001 must not trigger
        assert not any(r.id == "CARD-001" for r in res.all_matched_rules)


class TestEveryRulePositiveAndNegative:
    """Requirement: For EVERY rule, at least one positive and one negative test."""

    ALL_RULES_CASES = [
        # (rule_id, positive_text, positive_age_kwargs, negative_text, negative_age_kwargs)
        ("CARD-001", "Severe crushing chest pain", {"age_years": 50}, "Mild headache", {"age_years": 50}),
        ("CARD-002", "Chest pain for 2 days", {"age_years": 70}, "Chest pain for 2 days", {"age_years": 30}),
        ("CARD-003", "Mild chest pain", {"age_years": 25}, "Severe crushing chest pain", {"age_years": 25}),
        ("NEUR-001", "Sudden facial droop and slurred speech", {"age_years": 60}, "Mild runny nose", {"age_years": 60}),
        ("NEUR-002", "Sudden worst headache of life thunderclap", {"age_years": 40}, "Mild cough", {"age_years": 40}),
        ("NEUR-003", "Patient having active seizure", {"age_years": 20}, "Mild rash", {"age_years": 20}),
        ("NEUR-004", "Patient is confused and unconscious", {"age_years": 45}, "Alert with mild cough", {"age_years": 45}),
        ("NEUR-005", "Throbbing migraine headache without fever", {"age_years": 30}, "Sudden worst headache of life", {"age_years": 30}),
        ("RESP-001", "Severe difficulty breathing can't breathe", {"age_years": 35}, "Mild cough", {"age_years": 35}),
        ("RESP-002", "Shortness of breath wheezing", {"age_years": 25}, "Severe can't breathe gasping", {"age_years": 25}),
        ("RESP-003", "Persistent dry cough", {"age_years": 40}, "Cough with severe difficulty breathing", {"age_years": 40}),
        ("ALLG-001", "Severe allergic reaction with throat swelling and tongue swelling", {"age_years": 20}, "Mild itching", {"age_years": 20}),
        ("ALLG-002", "Sudden acute widespread rash and hives", {"age_years": 25}, "Mild rash for several days", {"age_years": 25}),
        ("GAST-001", "Sudden severe abdominal pain with vomiting blood", {"age_years": 50}, "Mild loose stools", {"age_years": 50}),
        ("GAST-002", "Diarrhea and vomiting for 2 days", {"age_years": 30}, "Diarrhea alone without vomiting", {"age_years": 30}),
        ("GAST-003", "Watery diarrhea loose stools", {"age_years": 28}, "Diarrhea with vomiting", {"age_years": 28}),
        ("INFN-001", "High fever with severe confusion and unconsciousness", {"age_years": 40}, "Mild headache", {"age_years": 40}),
        ("INFN-002", "Fever and severe abdominal pain", {"age_years": 35}, "Fever alone without abdominal pain", {"age_years": 35}),
        ("INFN-003", "Mild fever", {"age_years": 30}, "Fever with confusion", {"age_years": 30}),
        ("PED-001", "Toddler with seizure and altered sensorium", {"age_months": 18}, "Toddler with mild cough", {"age_months": 18}),
        ("PED-002", "Baby 2 months old with high fever", {"age_months": 2.0}, "Child 4 years old with fever", {"age_years": 4}),
        ("PED-003", "Infant 4 months old with fever", {"age_months": 4.0}, "Infant 1 month old with fever", {"age_months": 1.0}),
        ("PED-004", "Toddler has diarrhea and vomiting", {"age_months": 14}, "Adult has diarrhea and vomiting", {"age_years": 35}),
        ("TRAU-001", "Patient has snakebite on leg", {"age_years": 40}, "Mild headache", {"age_years": 40}),
        ("TRAU-002", "Heavy bleeding and coughing blood", {"age_years": 45}, "Minor paper cut", {"age_years": 45}),
        ("TRAU-003", "High fever and unconsciousness after heat exposure", {"age_years": 30}, "Mild sunburn", {"age_years": 30}),
        ("GENU-001", "Swollen calf with deep vein thrombosis symptoms", {"age_years": 55}, "Mild dysuria", {"age_years": 55}),
        ("GENU-002", "Burning urination dysuria without fever", {"age_years": 30}, "Dysuria with high fever and abdominal pain", {"age_years": 30}),
        ("SELF-001", "Mild cough without fever", {"age_years": 30}, "Severe difficulty breathing", {"age_years": 30}),
        ("SELF-002", "Mild localized itching rash", {"age_years": 25}, "Sudden widespread rash with throat swelling", {"age_years": 25}),
        ("SELF-003", "Mild tension headache", {"age_years": 28}, "Sudden thunderclap worst headache of life", {"age_years": 28}),
    ]

    @pytest.mark.parametrize(("rule_id", "pos_text", "pos_age", "neg_text", "neg_age"), ALL_RULES_CASES)
    def test_positive_and_negative_case_for_rule(
        self,
        engine: RuleEngine,
        extractor: NLPExtractor,
        rule_id: str,
        pos_text: str,
        pos_age: dict,
        neg_text: str,
        neg_age: dict,
    ):
        """Each individual clinical rule matches its positive vignette and rejects its negative vignette."""
        # 1. Test positive trigger
        pos_ext = extractor.extract(pos_text)
        pos_res = engine.evaluate(pos_ext, **pos_age)
        assert any(r.id == rule_id for r in pos_res.all_matched_rules), (
            f"Rule {rule_id} failed to trigger on positive case: '{pos_text}' with {pos_age}. "
            f"Matched: {[r.id for r in pos_res.all_matched_rules]}, Entities: {pos_ext.entities}"
        )

        # 2. Test negative trigger
        neg_ext = extractor.extract(neg_text)
        neg_res = engine.evaluate(neg_ext, **neg_age)
        assert not any(r.id == rule_id for r in neg_res.all_matched_rules), (
            f"Rule {rule_id} improperly triggered on negative case: '{neg_text}' with {neg_age}."
        )
