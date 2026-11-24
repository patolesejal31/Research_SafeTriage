"""Tests for the Raw-Keyword Emergency Safety Net (Stage A Fail-Safe)."""

from pathlib import Path
import pytest

from app.core.urgency import Urgency
from app.triage.nlp_extractor import EntityStatus, ExtractedEntity, MatchType
from app.triage.safety_net import SafetyNet


@pytest.fixture
def safety_net() -> SafetyNet:
    return SafetyNet()


class TestSafetyNetEmergencies:
    """Tests covering immediate Level 1 Emergency activation on high-risk keywords."""

    @pytest.mark.parametrize(
        "text",
        [
            "Patient is experiencing severe chest pain and sweating",
            "I think my uncle is having a heart attack",
            "Child can't breathe and is turning blue",
            "Found patient unconscious on the floor",
            "Person is not responding to voice",
            "Active seizure lasting over 5 minutes",
            "Heavy bleeding from laceration, spurting blood",
            "Patient is coughing blood and gasping for air",
            "Sudden facial droop and slurred speech",
            "Severe throat swelling after bee sting, anaphylaxis",
            "Victim had a snake bite on the leg in the field",
        ],
    )
    def test_english_emergency_keywords_trigger_level_1(self, safety_net: SafetyNet, text: str):
        """Standard English life-threat keywords trigger immediate Stage A Emergency."""
        res = safety_net.evaluate(text)
        assert res.triggered is True
        assert res.urgency == Urgency.EMERGENCY
        assert len(res.matched_keywords) >= 1
        assert "112" in res.emergency_notice
        assert "108" in res.emergency_notice
        assert res.review_status == "UNVERIFIED"

    @pytest.mark.parametrize(
        "text",
        [
            "Dil ka daura pada hai jaldi aao",
            "Chhaati mein dard bohot zyada hai",
            "Saas nahi aa rahi mareez ko",
            "Behosh ho gaya achanak se",
            "Hosh nahi hai bilkul",
            "Lakwa maar gaya ek taraf",
            "Khoon ki ulti ho rahi hai",
            "Saanp ne kata hai",
        ],
    )
    def test_hinglish_emergency_keywords_trigger_level_1(self, safety_net: SafetyNet, text: str):
        """Hinglish emergency keywords trigger immediate Stage A Emergency."""
        res = safety_net.evaluate(text)
        assert res.triggered is True
        assert res.urgency == Urgency.EMERGENCY
        assert len(res.matched_keywords) >= 1

    @pytest.mark.parametrize(
        "text",
        [
            "Chaati madhe dukhatahe aani ghabrahat",
            "Shwas ghyayla tras hoto ahe khup",
            "Shuddhi var nahi ahe aaji",
            "Zatke yet ahet lahan baalala",
            "Khup rakt yetoy hathatun",
            "Saap chavla ahe khetat",
        ],
    )
    def test_marathi_emergency_keywords_trigger_level_1(self, safety_net: SafetyNet, text: str):
        """Marathi transliterated emergency keywords trigger immediate Stage A Emergency."""
        res = safety_net.evaluate(text)
        assert res.triggered is True
        assert res.urgency == Urgency.EMERGENCY
        assert len(res.matched_keywords) >= 1


class TestSafetyNetNLPInteractions:
    """Tests evaluating interaction between safety net and NLP extraction status."""

    def test_fires_when_nlp_extraction_is_none(self, safety_net: SafetyNet):
        """Safety net fires even if NLP extraction is completely None / failed."""
        text = "Patient has severe chest pain."
        res = safety_net.evaluate(text, extracted_entities=None)
        assert res.triggered is True
        assert res.urgency == Urgency.EMERGENCY

    def test_fires_when_nlp_extraction_is_empty(self, safety_net: SafetyNet):
        """Safety net fires even if NLP extractor failed to detect any entities."""
        text = "Severe chest pain"
        res = safety_net.evaluate(text, extracted_entities=[])
        assert res.triggered is True
        assert res.urgency == Urgency.EMERGENCY

    def test_does_not_fire_when_unambiguously_negated(self, safety_net: SafetyNet):
        """When NLP extractor verifies symptom is explicitly NEGATED, safety net does not fire."""
        text = "Patient has no chest pain."
        entity = ExtractedEntity(
            canonical_concept="chest_pain",
            matched_term="chest pain",
            status=EntityStatus.NEGATED,
            match_type=MatchType.EXACT,
            level_1_relevant=True,
        )
        res = safety_net.evaluate(text, extracted_entities=[entity])
        assert res.triggered is False
        assert res.urgency is None

    def test_fires_when_negation_is_ambiguous_or_uncertain(self, safety_net: SafetyNet):
        """When NLP entity is UNCERTAIN (e.g. 'not sure about chest pain'), safety net MUST escalate."""
        text = "Not sure if having chest pain."
        entity = ExtractedEntity(
            canonical_concept="chest_pain",
            matched_term="chest pain",
            status=EntityStatus.UNCERTAIN,
            match_type=MatchType.EXACT,
            level_1_relevant=True,
        )
        res = safety_net.evaluate(text, extracted_entities=[entity])
        assert res.triggered is True
        assert res.urgency == Urgency.EMERGENCY

    def test_empty_input(self, safety_net: SafetyNet):
        """Empty input does not trigger safety net."""
        res = safety_net.evaluate("")
        assert res.triggered is False
        assert res.urgency is None

    def test_nonexistent_keywords_file(self, tmp_path: Path):
        """Safety net handles nonexistent keywords file safely."""
        fake_path = tmp_path / "nonexistent.yaml"
        sn = SafetyNet(keywords_path=fake_path)
        res = sn.evaluate("chest pain")
        assert res.triggered is False
