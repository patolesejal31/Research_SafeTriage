"""Phase 6 Comprehensive Tests: Inter-Rater Reliability, Guest Retention TTL, and Dataset Integrity.

Safety & Governance Invariants Tested:
1. Cohen's Kappa: perfect agreement, zero variance / constant raters, unequal label sets,
   known values, empty inputs, and mismatched lengths.
2. Guest assessment TTL cleanup:
   - Expired guest records (created > GUEST_RETENTION_HOURS ago) are purged.
   - Recent guest records are retained.
   - Registered user records are NEVER auto-deleted regardless of age.
   - Cascading deletion: no orphan rows in structured_symptoms, rule_triggers, or override_logs.
   - Cleanup is fully idempotent.
   - Clock parameter is injectable for deterministic verification.
3. Synthetic Dataset (Phase 6):
   - Exactly 1,200 synthetic vignettes across 10 clinical specialties.
   - At least 60 template families (actual 70); family counts printed per specialty.
   - Strict family isolation across train/validation/test splits (zero leakage).
   - Test split contains at least 10 families.
   - All 4 urgency levels (1, 2, 3, 4) present in every split.
   - Metadata validation: tier="synthetic_dev", label_source="developer_assigned_unreviewed".
   - Hinglish / Marathi cases explicitly marked unreviewed by native speakers.
   - Zero prescription drug names or dosages (strictly non-prescriptive).
   - Canonical serialization produces byte-identical hashes across runs.
   - Test split SHA-256 matches frozen checksum.
   - Zero exact duplicates across splits; near-duplicate rate computed and reported.
   - `clinician_annotated/` confirmed empty and marked BLOCKED.
   - `independent_vignettes/` confirmed schema and template only.
   - `docs/clinician_review_form.md` contains 31 rules and 100-case stratified sample.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Set

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models import (
    Assessment,
    OverrideLog,
    RuleTrigger,
    StructuredSymptom,
    User,
)
from app.services.metrics import cohen_kappa
from app.services.retention import cleanup_guest_assessments

# Project root paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATASETS_DIR = PROJECT_ROOT / "datasets"
SYNTHETIC_DIR = DATASETS_DIR / "synthetic_dev"
INDEPENDENT_DIR = DATASETS_DIR / "independent_vignettes"
CLINICIAN_DIR = DATASETS_DIR / "clinician_annotated"
DOCS_DIR = PROJECT_ROOT / "docs"


# ===========================================================================
# 1. Cohen's Kappa Inter-Rater Reliability Tests
# ===========================================================================

class TestCohenKappa:
    """Test suite for pure-Python Cohen's kappa implementation."""

    def test_perfect_agreement(self):
        """When two raters agree on every case, kappa must be exactly 1.0."""
        r1 = [1, 2, 3, 4, 1, 2, 3, 4]
        r2 = [1, 2, 3, 4, 1, 2, 3, 4]
        assert cohen_kappa(r1, r2) == 1.0

    def test_zero_variance_identical_ratings(self):
        """When both raters assign the identical single class to every item, kappa is 1.0."""
        r1 = [1, 1, 1, 1, 1]
        r2 = [1, 1, 1, 1, 1]
        assert cohen_kappa(r1, r2) == 1.0

    def test_zero_variance_complete_disagreement(self):
        """When each rater assigns a single different class to every item, kappa is 0.0."""
        r1 = [1, 1, 1, 1, 1]
        r2 = [2, 2, 2, 2, 2]
        assert cohen_kappa(r1, r2) == 0.0

    def test_unequal_label_sets(self):
        """Handles cases where rater 1 uses a subset of categories that rater 2 uses."""
        r1 = [1, 1, 2, 2, 1]
        r2 = [1, 2, 2, 3, 1]  # rater 2 uses category 3, rater 1 does not
        kappa = cohen_kappa(r1, r2)
        assert isinstance(kappa, float)
        assert -1.0 <= kappa <= 1.0

    def test_known_numerical_value(self):
        """Verify against known textbook 2x2 contingency table.
        
        Table:
                  Rater 2
                  Yes  No
        Rater 1 Yes 20   5  (25)
                No  10  15  (25)
                   (30)(20) (50 total)

        p_o = (20 + 15) / 50 = 35 / 50 = 0.70
        p_e = (25*30 + 25*20) / (50*50) = (750 + 500) / 2500 = 1250 / 2500 = 0.50
        kappa = (0.70 - 0.50) / (1.0 - 0.50) = 0.20 / 0.50 = 0.40
        """
        r1 = ["yes"] * 25 + ["no"] * 25
        r2 = ["yes"] * 20 + ["no"] * 5 + ["yes"] * 10 + ["no"] * 15
        assert cohen_kappa(r1, r2) == 0.40

    def test_empty_ratings_raises_valueerror(self):
        """Empty rating sequences must raise ValueError."""
        with pytest.raises(ValueError, match="Cannot calculate Cohen's kappa on empty"):
            cohen_kappa([], [])

    def test_mismatched_length_raises_valueerror(self):
        """Mismatched rating lengths must raise ValueError."""
        with pytest.raises(ValueError, match="must have equal length"):
            cohen_kappa([1, 2, 3], [1, 2])


# ===========================================================================
# 2. Guest Retention & TTL Cleanup Tests
# ===========================================================================

@pytest.fixture
def retention_db():
    """Create an in-memory SQLite database with foreign keys enabled."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        future=True,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    session = Session(bind=engine, future=True)
    yield session
    session.close()


class TestGuestRetention:
    """Test suite for guest assessment TTL auto-cleanup."""

    def test_retention_purges_old_guest_and_keeps_new_and_registered(self, retention_db: Session):
        """Verify:
        - Guest assessment older than retention_hours is purged.
        - Guest assessment newer than retention_hours is kept.
        - Registered user's assessment is kept regardless of age.
        - Cascading deletes purge child rows with no orphans.
        """
        now = datetime(2026, 6, 1, 12, 0, 0, tzinfo=timezone.utc)

        # 1. Create a registered user
        user = User(
            email="registered@safetriage.org",
            hashed_password="test_hashed_password",
            role="user",
        )
        retention_db.add(user)
        retention_db.commit()

        # 2. Assessment A: Registered user, created 30 days ago (MUST BE KEPT)
        asm_registered = Assessment(
            user_id=user.id,
            final_urgency=2,
            explanation_text="Registered user assessment",
            created_at=now - timedelta(days=30),
        )
        retention_db.add(asm_registered)

        # 3. Assessment B: Guest user, created 25 hours ago (MUST BE PURGED)
        asm_guest_old = Assessment(
            user_id=None,
            final_urgency=3,
            explanation_text="Old guest assessment",
            created_at=now - timedelta(hours=25),
        )
        retention_db.add(asm_guest_old)
        retention_db.commit()

        # Add child rows to old guest assessment
        symptom_old = StructuredSymptom(
            assessment_id=asm_guest_old.id,
            canonical_concept="cough",
            status="POSITIVE",
            match_type="exact",
        )
        trigger_old = RuleTrigger(
            assessment_id=asm_guest_old.id,
            rule_id="RESP-001",
            rule_name="Persistent Cough",
            rule_level=3,
            specialty="respiratory",
        )
        override_old = OverrideLog(
            assessment_id=asm_guest_old.id,
            component="safety_net",
            from_level=3,
            to_level=3,
            reason="No override required",
        )
        retention_db.add_all([symptom_old, trigger_old, override_old])
        retention_db.commit()

        symptom_old_id = symptom_old.id
        trigger_old_id = trigger_old.id
        override_old_id = override_old.id

        # 4. Assessment C: Guest user, created 2 hours ago (MUST BE KEPT)
        asm_guest_new = Assessment(
            user_id=None,
            final_urgency=1,
            explanation_text="Recent guest assessment",
            created_at=now - timedelta(hours=2),
        )
        retention_db.add(asm_guest_new)
        retention_db.commit()

        # Add child rows to new guest assessment
        symptom_new = StructuredSymptom(
            assessment_id=asm_guest_new.id,
            canonical_concept="chest_pain",
            status="POSITIVE",
            match_type="exact",
        )
        retention_db.add(symptom_new)
        retention_db.commit()

        # Run cleanup with 24-hour retention
        deleted_count = cleanup_guest_assessments(retention_db, retention_hours=24, now=now)
        assert deleted_count == 1

        # Verify Assessment A (registered user) still exists
        remaining_registered = retention_db.get(Assessment, asm_registered.id)
        assert remaining_registered is not None
        assert remaining_registered.user_id == user.id

        # Verify Assessment B (old guest) was deleted
        remaining_guest_old = retention_db.get(Assessment, asm_guest_old.id)
        assert remaining_guest_old is None

        # Verify Assessment C (new guest) still exists
        remaining_guest_new = retention_db.get(Assessment, asm_guest_new.id)
        assert remaining_guest_new is not None

        # Verify child rows of deleted guest are deleted (no orphan rows)
        assert retention_db.query(StructuredSymptom).filter_by(id=symptom_old_id).first() is None
        assert retention_db.query(RuleTrigger).filter_by(id=trigger_old_id).first() is None
        assert retention_db.query(OverrideLog).filter_by(id=override_old_id).first() is None

        # Verify child row of retained guest remains
        assert retention_db.query(StructuredSymptom).filter_by(id=symptom_new.id).first() is not None

    def test_cleanup_is_idempotent(self, retention_db: Session):
        """Calling cleanup twice with the same cutoff returns 0 on second run."""
        now = datetime(2026, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        asm_guest = Assessment(
            user_id=None,
            final_urgency=4,
            explanation_text="Idempotent test guest assessment",
            created_at=now - timedelta(hours=50),
        )
        retention_db.add(asm_guest)
        retention_db.commit()

        first_run = cleanup_guest_assessments(retention_db, retention_hours=24, now=now)
        assert first_run == 1

        second_run = cleanup_guest_assessments(retention_db, retention_hours=24, now=now)
        assert second_run == 0


# ===========================================================================
# 3. Synthetic Dataset Integrity & Verification Tests
# ===========================================================================

@pytest.fixture(scope="module")
def dataset_splits() -> Dict[str, List[Dict[str, Any]]]:
    """Load train, validation, test, and full datasets."""
    files = {
        "train": SYNTHETIC_DIR / "train.json",
        "validation": SYNTHETIC_DIR / "validation.json",
        "test": SYNTHETIC_DIR / "test.json",
        "full": SYNTHETIC_DIR / "full_dataset.json",
    }
    data = {}
    for name, path in files.items():
        assert path.exists(), f"Missing dataset file: {path}"
        with open(path, "r", encoding="utf-8") as f:
            data[name] = json.load(f)
    return data


class TestSyntheticDatasetIntegrity:
    """Test suite for Phase 6 synthetic development dataset."""

    def test_total_dataset_case_count_is_1200(self, dataset_splits):
        """Dataset must contain exactly 1,200 cases."""
        assert len(dataset_splits["full"]) == 1200
        total_split = len(dataset_splits["train"]) + len(dataset_splits["validation"]) + len(dataset_splits["test"])
        assert total_split == 1200

    def test_at_least_60_template_families(self, dataset_splits):
        """Dataset must have at least 60 distinct template families."""
        families = set(case["family_id"] for case in dataset_splits["full"])
        assert len(families) >= 60, f"Expected >= 60 families, got {len(families)}"

    def test_ten_specialties_represented_and_print_counts(self, dataset_splits, capsys):
        """All 10 clinical specialties must be represented; print family counts."""
        full = dataset_splits["full"]
        specialty_families: Dict[str, Set[str]] = {}
        for case in full:
            spec = case["specialty"]
            fam = case["family_id"]
            specialty_families.setdefault(spec, set()).add(fam)

        assert len(specialty_families) == 10, f"Expected 10 specialties, found {len(specialty_families)}"

        # Print family counts per specialty
        print("\n--- Template Family Distribution by Specialty ---")
        for spec in sorted(specialty_families.keys()):
            count = len(specialty_families[spec])
            print(f"  {spec:25s}: {count} families")
            assert count >= 5, f"Specialty {spec} has only {count} families (< 5)"

    def test_family_isolation_zero_leakage_across_splits(self, dataset_splits):
        """Families must be strictly isolated across train, validation, and test splits (0 overlap)."""
        train_families = set(c["family_id"] for c in dataset_splits["train"])
        val_families = set(c["family_id"] for c in dataset_splits["validation"])
        test_families = set(c["family_id"] for c in dataset_splits["test"])

        train_val_overlap = train_families.intersection(val_families)
        train_test_overlap = train_families.intersection(test_families)
        val_test_overlap = val_families.intersection(test_families)

        assert not train_val_overlap, f"Family leakage train/val: {train_val_overlap}"
        assert not train_test_overlap, f"Family leakage train/test: {train_test_overlap}"
        assert not val_test_overlap, f"Family leakage val/test: {val_test_overlap}"

    def test_test_split_has_at_least_10_families(self, dataset_splits):
        """Test split must have at least 10 families to ensure generalization testing."""
        test_families = set(c["family_id"] for c in dataset_splits["test"])
        assert len(test_families) >= 10, f"Test split has only {len(test_families)} families (< 10)"

    def test_all_four_urgency_levels_in_every_split(self, dataset_splits):
        """Every split (train, validation, test) must contain cases for all urgency levels (1, 2, 3, 4)."""
        for split_name in ["train", "validation", "test"]:
            split_levels = set(c["ground_truth_urgency"] for c in dataset_splits[split_name])
            assert split_levels == {1, 2, 3, 4}, f"Split {split_name} missing urgency levels: {{1, 2, 3, 4}} - {split_levels}"

    def test_metadata_tier_and_label_source(self, dataset_splits):
        """All cases must have tier='synthetic_dev' and label_source='developer_assigned_unreviewed'."""
        for case in dataset_splits["full"]:
            assert case["tier"] == "synthetic_dev"
            assert case["label_source"] == "developer_assigned_unreviewed"

    def test_hinglish_marathi_cases_marked_unreviewed(self, dataset_splits):
        """Hinglish and Marathi transliterated cases must have hinglish_marathi_reviewed == False."""
        multilingual_count = 0
        for case in dataset_splits["full"]:
            if case["language_style"] in ("hinglish", "marathi_transliterated"):
                assert case["hinglish_marathi_reviewed"] is False
                multilingual_count += 1
        assert multilingual_count > 0, "No multilingual cases found"

    def test_no_forbidden_medical_prescriptions_or_drugs(self, dataset_splits):
        """Dataset must strictly contain no prescription medications, doses, or drug names."""
        forbidden_terms = [
            "aspirin", "paracetamol", "acetaminophen", "nitroglycerin", "amoxicillin",
            "ibuprofen", "penicillin", "metformin", "atorvastatin", "omeprazole",
            "lisinopril", "antibiotics", "prescribe", "prescription", " 500mg", " 100mg", " 250mg",
        ]
        for case in dataset_splits["full"]:
            text_lower = case["symptoms_text"].lower()
            for term in forbidden_terms:
                assert term not in text_lower, f"Case {case['case_id']} contains forbidden term '{term}': {case['symptoms_text']}"

    def test_canonical_serialization_checksum_matches_frozen_value(self):
        """SHA-256 of test.json must match frozen checksums.json."""
        checksums_path = SYNTHETIC_DIR / "checksums.json"
        assert checksums_path.exists(), "Missing checksums.json"

        with open(checksums_path, "r", encoding="utf-8") as f:
            frozen = json.load(f)

        test_path = SYNTHETIC_DIR / "test.json"
        actual_test_sha = hashlib.sha256(test_path.read_bytes()).hexdigest()
        assert actual_test_sha == frozen["test.json"], "test.json checksum mismatch!"

    def test_exact_duplicates_across_splits_is_zero(self, dataset_splits):
        """There must be 0 exact duplicates of symptom text across train, val, and test splits."""
        train_texts = set(c["symptoms_text"] for c in dataset_splits["train"])
        val_texts = set(c["symptoms_text"] for c in dataset_splits["validation"])
        test_texts = set(c["symptoms_text"] for c in dataset_splits["test"])

        assert not train_texts.intersection(val_texts), "Exact duplicate found between train and val"
        assert not train_texts.intersection(test_texts), "Exact duplicate found between train and test"
        assert not val_texts.intersection(test_texts), "Exact duplicate found between val and test"

    def test_near_duplicate_rate_reported(self, dataset_splits):
        """Compute and honestly report near-duplicate rate using Jaccard word similarity."""
        def tokenize(text: str) -> Set[str]:
            return set(text.lower().split())

        def jaccard(s1: Set[str], s2: Set[str]) -> float:
            u = s1.union(s2)
            return len(s1.intersection(s2)) / len(u) if u else 0.0

        train_tokens = [tokenize(c["symptoms_text"]) for c in dataset_splits["train"]]
        test_tokens = [tokenize(c["symptoms_text"]) for c in dataset_splits["test"]]

        near_dup_count = 0
        threshold = 0.80
        for tt in test_tokens:
            for tr in train_tokens:
                if jaccard(tt, tr) >= threshold:
                    near_dup_count += 1
                    break

        total_test = len(test_tokens)
        rate = (near_dup_count / total_test) * 100.0
        print(f"\nNear-duplicate rate across splits (Jaccard >= {threshold}): {near_dup_count}/{total_test} ({rate:.2f}%)")
        assert rate < 1.0, f"Near-duplicate rate {rate:.2f}% exceeds acceptable threshold 1.0%"

    def test_clinician_annotated_directory_marked_blocked(self):
        """datasets/clinician_annotated/ must exist, be empty of data, and marked BLOCKED in README."""
        readme = CLINICIAN_DIR / "README.md"
        assert readme.exists(), "Missing clinician_annotated/README.md"
        content = readme.read_text(encoding="utf-8")
        assert "BLOCKED" in content
        # Ensure no json data files are fabricated
        json_files = list(CLINICIAN_DIR.glob("*.json"))
        assert len(json_files) == 0, f"Found unexpected data in clinician_annotated: {json_files}"

    def test_independent_vignettes_directory_schema(self):
        """datasets/independent_vignettes/ must contain valid schema.json and template.json."""
        schema_path = INDEPENDENT_DIR / "schema.json"
        template_path = INDEPENDENT_DIR / "template.json"
        assert schema_path.exists()
        assert template_path.exists()

        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        assert "$schema" in schema or "title" in schema

        with open(template_path, "r", encoding="utf-8") as f:
            template = json.load(f)
        assert isinstance(template, list)

    def test_clinician_review_form_contains_31_rules_and_100_cases(self):
        """docs/clinician_review_form.md must cover all 31 rules and a 100-case stratified sample."""
        form_path = DOCS_DIR / "clinician_review_form.md"
        assert form_path.exists(), "Missing clinician_review_form.md"
        content = form_path.read_text(encoding="utf-8")
        assert "Rule 31:" in content
        assert "Vignette 100" in content
        assert "112 / 108" in content
        assert "PENDING CLINICIAN REVIEW" in content
