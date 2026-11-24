"""Edge cases and branch coverage tests for NLPExtractor."""

from pathlib import Path
import pytest

from app.triage.nlp_extractor import NLPExtractor


class TestNLPExtractorBranches:
    """Tests targeting 100% branch coverage of NLPExtractor."""

    def test_nonexistent_lexicon_path(self, tmp_path: Path):
        """Extractor initializes safely when lexicon file does not exist."""
        fake_path = tmp_path / "nonexistent_lexicon.yaml"
        ext = NLPExtractor(lexicon_path=fake_path)
        res = ext.extract("fever and cough")
        assert res.entities == []
        assert res.sanitized_text == "fever and cough"

    def test_empty_and_whitespace_inputs(self, extractor: NLPExtractor):
        """Empty and whitespace inputs return clean empty ExtractionResult."""
        res_empty = extractor.extract("")
        assert res_empty.sanitized_text == ""
        assert res_empty.entities == []

        res_spaces = extractor.extract("    ")
        assert res_spaces.sanitized_text == ""
        assert res_spaces.entities == []

    def test_moderate_severity_and_gradual_onset(self, extractor: NLPExtractor):
        """Verify extraction of gradual onset and moderate severity."""
        text = "Gradual onset of moderate headache and cough in an adult."
        res = extractor.extract(text)
        assert res.attributes.onset == "gradual"
        assert res.attributes.severity == "moderate"
        assert res.attributes.age_group == "adult"

    def test_mild_severity(self, extractor: NLPExtractor):
        """Verify extraction of mild severity."""
        text = "Mild headache."
        res = extractor.extract(text)
        assert res.attributes.severity == "mild"
