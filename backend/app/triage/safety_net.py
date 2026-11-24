"""SafeTriage Raw-Keyword Emergency Safety Net.

Stage A Fail-Safe:
Operates directly on sanitized raw text to capture critical emergency red flags
(e.g., 'chest pain', 'can't breathe', 'unconscious', 'seizure', 'heavy bleeding',
and Hinglish/Marathi equivalents), running EVEN IF NLP extraction fails or mislabels.

Safety Invariant:
A safety-net hit with an ambiguous or failed extraction MUST escalate to Level 1 (Emergency),
not be dropped. Negation applies only when explicitly and unambiguously verified.
"""

from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Any, Dict, List, Optional
import unicodedata

import yaml

from app.core.urgency import Urgency
from app.triage.nlp_extractor import EntityStatus, ExtractedEntity

SAFETY_NET_KEYWORDS_PATH = Path(__file__).parent / "safety_net_keywords.yaml"


@dataclass(frozen=True)
class SafetyNetResult:
    """Result returned by the raw-keyword emergency safety net."""
    triggered: bool
    urgency: Optional[Urgency]
    matched_keywords: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    review_status: str = "UNVERIFIED"
    emergency_notice: Optional[str] = None


class SafetyNet:
    """Deterministic raw-keyword safety net for Stage A preliminary triage."""

    def __init__(self, keywords_path: Optional[Path] = None):
        self.keywords_path = keywords_path or SAFETY_NET_KEYWORDS_PATH
        self._load_keywords()

    def _load_keywords(self) -> None:
        """Load keyword phrases from safety_net_keywords.yaml."""
        if not self.keywords_path.exists():
            self.keywords: List[Dict[str, Any]] = []
            return

        with open(self.keywords_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        self.keywords = data.get("keywords", [])
        # Sort keywords by descending phrase length
        self.keywords.sort(key=lambda k: -len(k.get("phrase", "")))

    def evaluate(
        self,
        text: str,
        extracted_entities: Optional[List[ExtractedEntity]] = None,
    ) -> SafetyNetResult:
        """Evaluate raw text against emergency safety keywords.
        
        Args:
            text: Raw or sanitized presentation text.
            extracted_entities: Optional list of entities from NLPExtractor.
            
        Returns:
            SafetyNetResult indicating whether an immediate Level 1 Emergency was triggered.
        """
        if not text:
            return SafetyNetResult(triggered=False, urgency=None)

        # Normalize unicode and fold case
        norm_text = unicodedata.normalize("NFKC", text).lower()

        matched_phrases: List[str] = []
        matched_categories: List[str] = []
        matched_sources: List[str] = []

        for kw_entry in self.keywords:
            phrase = kw_entry.get("phrase", "").lower()
            if not phrase:
                continue

            # Exact word boundary matching for the phrase
            pattern = r"\b" + re.escape(phrase) + r"\b"
            if re.search(pattern, norm_text):
                # Keyword found in raw text!
                # Check whether NLP extraction explicitly and unambiguously negated it
                is_unambiguously_negated = False
                if extracted_entities:
                    for entity in extracted_entities:
                        # Check if this entity corresponds to the matched phrase
                        if entity.matched_term.lower() == phrase or phrase in entity.canonical_concept.replace("_", " "):
                            if entity.status == EntityStatus.NEGATED:
                                is_unambiguously_negated = True
                            elif entity.status in (EntityStatus.UNCERTAIN, EntityStatus.POSITIVE):
                                # An ambiguous or positive extraction MUST NOT negate the safety net!
                                is_unambiguously_negated = False
                                break

                # Safety Net Invariant:
                # If extraction failed, was corrupted, or was ambiguous, the safety net MUST escalate!
                if not is_unambiguously_negated:
                    matched_phrases.append(phrase)
                    matched_categories.append(kw_entry.get("category", "emergency"))
                    matched_sources.append(kw_entry.get("source", "Standard Clinical Practice"))

        if matched_phrases:
            return SafetyNetResult(
                triggered=True,
                urgency=Urgency.EMERGENCY,
                matched_keywords=list(set(matched_phrases)),
                categories=list(set(matched_categories)),
                sources=list(set(matched_sources)),
                review_status="UNVERIFIED",
                emergency_notice=(
                    "EMERGENCY FIRST SAFETY ALERT: Immediate clinical emergency criteria matched. "
                    "Call National Emergency Services (112 / 108) immediately."
                ),
            )

        return SafetyNetResult(triggered=False, urgency=None)
