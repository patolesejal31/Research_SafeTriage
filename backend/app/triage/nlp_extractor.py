"""SafeTriage NLP Extractor and Clinical Entity Normalizer.

Performs:
1. Input sanitization: unicode normalization (NFKC), length clamping, prompt-injection stripping.
   Sanitization NEVER logs symptom text.
2. Tiered symptom matching:
   - Tier 1: exact normalized matches (multi-word phrases prioritized).
   - Tier 2: explicit lexicon variants (including Indian vernacular Hinglish and Marathi).
   - Tier 3: RapidFuzz fallback ONLY for single tokens >= 5 characters.
     (thresholds: >=90 for 5-7 chars, >=85 for 8+ chars; short words are never fuzzy matched).
     Fuzzy matches are tagged with match_type='fuzzy' and cannot be used to downgrade urgency.
3. Bidirectional NegEx-style negation detection:
   - Pre- and post-negation windows (default 5 tokens).
   - Indian vernacular negators (nahi, nahin, nhi, na, bina, nako, nahi hai, etc.).
   - Terminators (but, however, although, lekin, par, magar, parantu, pan, punct).
   - Pseudo-negations (no change, not only, no relief, no difference).
   - Ambiguous negations ("not sure", "cannot tell") -> UNCERTAIN status.
   - Conjunction rules: "or/nor/ya" chains negation; "and/aur/ani" DOES NOT chain.
   - Level-1 safety net: If chained or ambiguous negation covers a Level-1-relevant
     symptom, it is tagged UNCERTAIN (never NEGATED).
4. Status tagging: POSITIVE, NEGATED, HISTORICAL, THIRD_PARTY, UNCERTAIN.
5. Extraction of onset, duration, severity, modifiers, and age group.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple
import unicodedata

from rapidfuzz import fuzz
import yaml

# Path to lexicon
LEXICON_PATH = Path(__file__).parent / "lexicon.yaml"

# Maximum allowed input length in characters
MAX_INPUT_LENGTH = 2000

# Prompt injection patterns stripped during sanitization
PROMPT_INJECTION_PATTERNS = [
    re.compile(r"(?i)\b(?:ignore|disregard|forget)\s+(?:all\s+)?(?:previous|prior|above)\s+(?:instructions|prompts|rules)\b"),
    re.compile(r"(?i)\b(?:system\s+prompt|system\s+message|system\s+instructions)\b"),
    re.compile(r"(?i)\b(?:you\s+are\s+now|act\s+as|roleplay\s+as)\s+[a-z0-9_ -]+\b"),
    re.compile(r"(?i)\b(?:triage\s+as|rate\s+as|classify\s+as)\s+(?:level\s+)?[1-4]\b"),
    re.compile(r"(?i)\b(?:output\s+only|return\s+only)\s+json\b"),
    re.compile(r"(?i)\bjailbreak\b"),
]

# Negation terminators: immediately halt negation scope
TERMINATORS = {
    "but", "however", "although", "except", "aside", "apart", "still",
    "lekin", "par", "magar", "parantu", "pan", "kintu", "punha",
    ".", ";", "!",
}

# Pseudo-negations: phrases that look like negations but do not negate symptoms
PSEUDO_NEGATIONS = [
    "no change",
    "no relief",
    "no difference",
    "not only",
    "not better",
    "not worse",
]

# Ambiguous negation indicators: uncertainty about presence/absence
AMBIGUOUS_NEGATIONS = [
    "not sure",
    "not certain",
    "cannot tell",
    "can't tell",
    "hard to tell",
    "maybe not",
    "shayad",
    "mahiti nahi",
]

# Pre-negation trigger words (preceding the symptom)
PRE_NEGATORS = {
    "no", "not", "without", "denies", "denied", "free of", "never",
    "rules out", "ruled out", "negative for",
    "nahi", "nahin", "nhi", "na", "bina", "nako", "shillak nahi",
}

# Post-negation trigger phrases/words (following the symptom)
POST_NEGATORS = [
    "nahi hai", "nahin hai", "nhi hai", "nahi ahe", "nako ahe",
    "nahi", "nahin", "nhi", "nako", "absent", "negative", "resolved",
]

# Negation chaining conjunctions (negation carries forward across these)
CHAINING_CONJUNCTIONS = {"or", "nor", "ya", "ki", "va"}

# Non-chaining conjunctions (negation DOES NOT automatically carry forward)
NON_CHAINING_CONJUNCTIONS = {"and", "aur", "ani", "tatha", "evam", "ke", "sath"}

# Third-party mention patterns
THIRD_PARTY_PATTERNS = [
    re.compile(r"\b(?:my\s+)?(?:father|mother|dad|mom|son|daughter|wife|husband|child|baby|friend|colleague|brother|sister|parent|grandpa|grandma)\b", re.IGNORECASE),
    re.compile(r"\b(?:mere\s+|meri\s+)?(?:pitaji|mataji|papa|mummy|beta|beti|patni|pati|dost|bhai|behen|dada|dadi|nana|nani)\b", re.IGNORECASE),
    re.compile(r"\b(?:aai|baba|mulga|mulgi|navra|bayko|mitra|bhau|bahin|aaji|aajoba)\b", re.IGNORECASE),
]

# Historical mention patterns (bidirectional)
HISTORICAL_PATTERNS = [
    re.compile(r"\b(?:history\s+of|past\s+medical\s+history|previously\s+diagnosed|had\s+in\s+the\s+past|in\s+the\s+past|years\s+ago|months\s+ago|weeks\s+ago)\b", re.IGNORECASE),
    re.compile(r"\b(?:pehle\s+bhi\s+tha|pehle\s+hua\s+tha|purana\s+hai|purani\s+bimari|pehle\s+aati\s+thi|pehle)\b", re.IGNORECASE),
    re.compile(r"\b(?:aadhi\s+hota|khup\s+divsan\s+purvi|junat|purvi)\b", re.IGNORECASE),
]

# Vernacular compound patterns with intensifiers
VERNACULAR_COMPOUND_PATTERNS = [
    # Chest pain: chhaati / seene / chaati ... dard / dukhatahe / vedna
    (re.compile(r"\b(?:chhaati|seene|chaati|chhati)\s+(?:mein|me|madhe|var)?\s*(?:(?:bohot|tez|khup|jast|bhaari|severe|halka)\s+)*\s*(?:dard|dukhatahe|dukhat\s+ahe|vedna|dabav)\b", re.IGNORECASE), "chest_pain", True),
    # Abdominal pain: pet / pot / potat ... dard / dukhatahe / vedna / dukhi
    (re.compile(r"\b(?:pet|pot|potat)\s+(?:mein|me|madhe)?\s*(?:(?:bohot|tez|khup|jast|bhaari|severe|halka)\s+)*\s*(?:dard|dukhatahe|dukhat\s+ahe|vedna|dukhi)\b", re.IGNORECASE), "abdominal_pain", False),
    # Headache: sir / sar / doke ... dard / dukhat ahe / dukhi
    (re.compile(r"\b(?:sir|sar|doke|dokat)\s+(?:mein|me|madhe)?\s*(?:(?:bohot|tez|khup|jast|severe|halka)\s+)*\s*(?:dard|dukhatahe|dukhat\s+ahe|dukhi)\b", re.IGNORECASE), "headache", False),
    # Dysuria: peshab / mutra ... jalan / jallan
    (re.compile(r"\b(?:peshab|mutra)\s+(?:mein|me|madhe)?\s*(?:(?:bohot|khup|tez)\s+)*\s*(?:jalan|jallan)\b", re.IGNORECASE), "dysuria", False),
    # Stroke: muh / tond ... tedha / vakra
    (re.compile(r"\b(?:muh|tond)\s+(?:(?:bohot|ekdam)\s+)*\s*(?:tedha|vakra)(?:\s+(?:ho\s+gaya|hona|zala))?\b", re.IGNORECASE), "stroke_symptoms", True),
    # Severe bleeding: khoon / khooni ... ulti / vomiting / waanti
    (re.compile(r"\b(?:khoon|khooni|rakta)\s*(?:ki|chi)?\s*(?:ulti|omiting|waanti)\b", re.IGNORECASE), "severe_bleeding", True),
    # Breathlessness: saans / saas / shwas ... phoolna / tras / dikkat
    (re.compile(r"\b(?:saans|saas|shwas)\s+(?:(?:lene\s+mein|ghyayala)\s+)*(?:(?:bohot|khup)\s+)*\s*(?:phoolna|tras|dikkat|takleef)\b", re.IGNORECASE), "breathlessness", True),
]


class EntityStatus(str, Enum):
    """Clinical status of an extracted symptom entity."""
    POSITIVE = "POSITIVE"         # Patient currently exhibits symptom
    NEGATED = "NEGATED"           # Symptom explicitly absent / ruled out
    HISTORICAL = "HISTORICAL"     # Past occurrence, not an active symptom
    THIRD_PARTY = "THIRD_PARTY"   # Symptom relates to a family member / third party
    UNCERTAIN = "UNCERTAIN"       # Ambiguous presence, or negation conflict on Level-1 symptom


class MatchType(str, Enum):
    """Method by which a symptom was identified in text."""
    EXACT = "exact"
    LEXICON_VARIANT = "lexicon_variant"
    FUZZY = "fuzzy"


@dataclass(frozen=True)
class ExtractedEntity:
    """Structured clinical entity extracted from symptom text."""
    canonical_concept: str
    matched_term: str
    status: EntityStatus
    match_type: MatchType
    fuzzy_score: Optional[float] = None
    level_1_relevant: bool = False
    is_ambiguous: bool = False
    ambiguity_flag: Optional[str] = None
    review_status: str = "UNVERIFIED"
    start_char: int = -1
    end_char: int = -1


@dataclass(frozen=True)
class ExtractedAttributes:
    """Auxiliary clinical attributes extracted from text."""
    onset: Optional[str] = None
    duration: Optional[str] = None
    severity: Optional[str] = None
    modifiers: List[str] = field(default_factory=list)
    age_group: Optional[str] = None


@dataclass(frozen=True)
class ExtractionResult:
    """Complete result of NLP symptom extraction."""
    sanitized_text: str
    entities: List[ExtractedEntity]
    attributes: ExtractedAttributes
    has_prompt_injection: bool = False


class NLPExtractor:
    """Clinical NLP extractor with safety net, NegEx negation, and lexicon matching."""

    def __init__(self, lexicon_path: Optional[Path] = None, negation_window: int = 5):
        self.negation_window = negation_window
        self.lexicon_path = lexicon_path or LEXICON_PATH
        self._load_lexicon()

    def _load_lexicon(self) -> None:
        """Load and index terms from lexicon.yaml."""
        if not self.lexicon_path.exists():
            self.concepts: Dict[str, Any] = {}
            self.ambiguous_terms: Dict[str, Any] = {}
            self.exact_terms_map: Dict[str, Tuple[str, bool, str]] = {}
            self.sorted_phrases: List[str] = []
            return

        with open(self.lexicon_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        self.concepts = data.get("concepts", {})
        self.ambiguous_terms = {
            item["term"].lower(): item for item in data.get("ambiguous_terms", [])
        }

        # Index exact terms (canonical concept, level_1_relevant, review_status)
        self.exact_terms_map = {}
        for concept_name, concept_data in self.concepts.items():
            l1_rel = concept_data.get("level_1_relevant", False)
            for en_term in concept_data.get("english_terms", []):
                self.exact_terms_map[en_term.lower().strip()] = (concept_name, l1_rel, "UNVERIFIED")
            for vern_item in concept_data.get("vernacular_terms", []):
                term = vern_item["term"].lower().strip()
                review_status = vern_item.get("review_status", "UNVERIFIED")
                self.exact_terms_map[term] = (concept_name, l1_rel, review_status)

        # Sort exact phrases by descending length (multi-word first)
        self.sorted_phrases = sorted(self.exact_terms_map.keys(), key=lambda x: -len(x))

    def sanitize(self, raw_text: str) -> tuple[str, bool]:
        """Sanitize raw text without logging symptom content.
        
        Performs:
        - Unicode normalization (NFKC)
        - Length clamping
        - Detection and neutralization of prompt injection patterns
        """
        if not raw_text:
            return "", False

        # Unicode normalization
        norm = unicodedata.normalize("NFKC", raw_text)

        # Length clamping
        if len(norm) > MAX_INPUT_LENGTH:
            norm = norm[:MAX_INPUT_LENGTH]

        # Check and strip prompt injections
        has_injection = False
        sanitized = norm
        for pattern in PROMPT_INJECTION_PATTERNS:
            if pattern.search(sanitized):
                has_injection = True
                sanitized = pattern.sub(" ", sanitized)

        # Collapse whitespace
        sanitized = re.sub(r"\s+", " ", sanitized).strip()
        return sanitized, has_injection

    def extract(self, text: str) -> ExtractionResult:
        """Extract structured clinical entities and attributes from text."""
        sanitized, has_injection = self.sanitize(text)
        if not sanitized:
            return ExtractionResult(
                sanitized_text="",
                entities=[],
                attributes=ExtractedAttributes(),
                has_prompt_injection=has_injection,
            )

        lower_text = sanitized.lower()
        tokens = self._tokenize(lower_text)

        # Identify candidate entities via Tier 1, 2, 3 and compound patterns
        candidates = self._find_entity_candidates(lower_text, tokens)

        # Determine clinical status (Negation, Historical, Third-party)
        entities: List[ExtractedEntity] = []
        for cand in candidates:
            status = self._evaluate_status(cand, candidates, lower_text, tokens)
            ambiguous_info = self.ambiguous_terms.get(cand["matched_term"])

            entity = ExtractedEntity(
                canonical_concept=cand["concept"],
                matched_term=cand["matched_term"],
                status=status,
                match_type=cand["match_type"],
                fuzzy_score=cand.get("fuzzy_score"),
                level_1_relevant=cand["level_1_relevant"],
                is_ambiguous=ambiguous_info is not None,
                ambiguity_flag=ambiguous_info.get("flag_reason") if ambiguous_info else None,
                review_status=cand["review_status"],
                start_char=cand["start_char"],
                end_char=cand["end_char"],
            )
            entities.append(entity)

        # Reconcile contradictory entities (e.g. "severe chest pain but no pain")
        entities = self._reconcile_contradictions(entities)

        # Extract attributes (onset, duration, severity, modifiers, age_group)
        attributes = self._extract_attributes(lower_text)

        return ExtractionResult(
            sanitized_text=sanitized,
            entities=entities,
            attributes=attributes,
            has_prompt_injection=has_injection,
        )

    def _tokenize(self, text: str) -> List[Tuple[str, int, int]]:
        """Tokenize text into (token_str, start_char, end_char)."""
        tokens: List[Tuple[str, int, int]] = []
        for m in re.finditer(r"\b[\w'-]+\b|[.,;!]", text):
            tokens.append((m.group(), m.start(), m.end()))
        return tokens

    def _find_entity_candidates(self, text: str, tokens: List[Tuple[str, int, int]]) -> List[Dict[str, Any]]:
        """Find entity matches using compound patterns, exact lexicon matches, and fuzzy fallback."""
        candidates: List[Dict[str, Any]] = []
        occupied_spans: List[Tuple[int, int]] = []

        # TIER 0: Vernacular compound patterns with optional intensifiers
        for pattern, concept_name, l1_rel in VERNACULAR_COMPOUND_PATTERNS:
            for m in pattern.finditer(text):
                start, end = m.start(), m.end()
                if not any(start < o_end and end > o_start for o_start, o_end in occupied_spans):
                    candidates.append({
                        "concept": concept_name,
                        "matched_term": m.group(),
                        "match_type": MatchType.LEXICON_VARIANT,
                        "fuzzy_score": None,
                        "level_1_relevant": l1_rel,
                        "review_status": "UNVERIFIED",
                        "start_char": start,
                        "end_char": end,
                    })
                    occupied_spans.append((start, end))

        # TIER 1 & 2: Exact matching of sorted phrases (multi-word first)
        for phrase in self.sorted_phrases:
            pattern = r"\b" + re.escape(phrase) + r"\b"
            for m in re.finditer(pattern, text):
                start, end = m.start(), m.end()
                if not any(start < o_end and end > o_start for o_start, o_end in occupied_spans):
                    concept_name, l1_rel, rev_status = self.exact_terms_map[phrase]
                    candidates.append({
                        "concept": concept_name,
                        "matched_term": phrase,
                        "match_type": MatchType.EXACT if " " in phrase or phrase in self.concepts[concept_name].get("english_terms", []) else MatchType.LEXICON_VARIANT,
                        "fuzzy_score": None,
                        "level_1_relevant": l1_rel,
                        "review_status": rev_status,
                        "start_char": start,
                        "end_char": end,
                    })
                    occupied_spans.append((start, end))

        # TIER 3: RapidFuzz fallback ONLY for single tokens >= 5 characters
        single_word_targets: Dict[str, Tuple[str, bool, str]] = {
            phrase: info for phrase, info in self.exact_terms_map.items()
            if " " not in phrase and len(phrase) >= 5
        }

        for tok_str, t_start, t_end in tokens:
            if len(tok_str) < 5 or tok_str in TERMINATORS:
                continue
            if any(t_start >= o_start and t_end <= o_end for o_start, o_end in occupied_spans):
                continue

            best_match: Optional[str] = None
            best_score = 0.0
            threshold = 90.0 if len(tok_str) <= 7 else 85.0

            for target_term in single_word_targets:
                score = fuzz.ratio(tok_str, target_term)
                if score >= threshold and score > best_score:
                    best_score = score
                    best_match = target_term

            if best_match is not None:
                concept_name, l1_rel, rev_status = single_word_targets[best_match]
                candidates.append({
                    "concept": concept_name,
                    "matched_term": tok_str,
                    "match_type": MatchType.FUZZY,
                    "fuzzy_score": round(best_score, 1),
                    "level_1_relevant": l1_rel,
                    "review_status": rev_status,
                    "start_char": t_start,
                    "end_char": t_end,
                })
                occupied_spans.append((t_start, t_end))

        # Sort candidates in appearance order
        candidates.sort(key=lambda c: c["start_char"])
        return candidates

    def _evaluate_status(
        self,
        candidate: Dict[str, Any],
        all_candidates: List[Dict[str, Any]],
        text: str,
        tokens: List[Tuple[str, int, int]],
    ) -> EntityStatus:
        """Evaluate clinical status: third-party, historical, negation, or positive."""
        start_char = candidate["start_char"]
        end_char = candidate["end_char"]
        is_l1 = candidate["level_1_relevant"]

        # 1. Check third-party context
        for tp_pat in THIRD_PARTY_PATTERNS:
            for m in tp_pat.finditer(text):
                if m.start() < end_char and (start_char - m.end() < 80):
                    return EntityStatus.THIRD_PARTY

        # 2. Check historical context (bidirectional: within 80 chars before or after)
        for h_pat in HISTORICAL_PATTERNS:
            for m in h_pat.finditer(text):
                dist = min(abs(start_char - m.end()), abs(m.start() - end_char))
                if dist < 80:
                    return EntityStatus.HISTORICAL

        # 3. Check for pseudo-negation phrases around candidate
        window_text_start = max(0, start_char - 60)
        window_text_end = min(len(text), end_char + 60)
        surrounding_text = text[window_text_start:window_text_end]
        for pseudo in PSEUDO_NEGATIONS:
            if pseudo in surrounding_text:
                return EntityStatus.POSITIVE

        # 4. Check for ambiguous negation phrases ("not sure", "cannot tell")
        for ambig in AMBIGUOUS_NEGATIONS:
            if ambig in surrounding_text:
                return EntityStatus.UNCERTAIN

        # 5. Token-based bidirectional NegEx algorithm
        cand_tok_idx = -1
        for idx, (_, t_s, t_e) in enumerate(tokens):
            if t_s <= start_char and end_char <= t_e:
                cand_tok_idx = idx
                break
            elif t_s <= start_char < t_e:
                cand_tok_idx = idx
                break

        if cand_tok_idx == -1:
            for idx, (_, t_s, _) in enumerate(tokens):
                if t_s >= start_char:
                    cand_tok_idx = idx
                    break

        # A. Check PRE-negation (up to negation_window tokens before candidate)
        pre_negated = False
        if cand_tok_idx != -1:
            start_window = max(0, cand_tok_idx - self.negation_window)
            pre_slice = tokens[start_window:cand_tok_idx]
            intervening_words: List[str] = []
            for t_str, t_s, t_e in reversed(pre_slice):
                if t_str in TERMINATORS or t_str in NON_CHAINING_CONJUNCTIONS:
                    break
                if t_str in PRE_NEGATORS:
                    # Check if another entity sits between this negator and candidate
                    has_intervening_entity = any(
                        t_s < other_c["start_char"] < start_char
                        for other_c in all_candidates
                        if other_c["start_char"] != start_char
                    )
                    if has_intervening_entity:
                        # Only chain if a chaining conjunction (or/nor/ya) was used
                        if any(tok in CHAINING_CONJUNCTIONS for tok in intervening_words):
                            pre_negated = True
                    else:
                        pre_negated = True
                    break
                intervening_words.append(t_str)

        # B. Check POST-negation (e.g., "dard nahi hai", "pain absent")
        post_negated = False
        post_text = text[end_char:min(len(text), end_char + 40)].strip()
        first_word = post_text.split()[0] if post_text.split() else ""
        if first_word not in TERMINATORS and first_word not in NON_CHAINING_CONJUNCTIONS:
            for post_phrase in POST_NEGATORS:
                if re.match(r"\b" + re.escape(post_phrase) + r"\b", post_text):
                    post_negated = True
                    break

        is_negated = pre_negated or post_negated

        if is_negated:
            # Critical Level-1 safety check:
            # If chained or ambiguous context covers a Level-1-relevant symptom, tag UNCERTAIN
            if is_l1:
                has_chaining = any(tok in CHAINING_CONJUNCTIONS for tok, _, _ in tokens[max(0, cand_tok_idx - self.negation_window):cand_tok_idx])
                if has_chaining:
                    return EntityStatus.UNCERTAIN
            return EntityStatus.NEGATED

        return EntityStatus.POSITIVE

    def _reconcile_contradictions(self, entities: List[ExtractedEntity]) -> List[ExtractedEntity]:
        """Resolve conflicting assertions for the same canonical concept.
        
        Clinical safety invariant: A contradiction (e.g. positive and negated for chest pain)
        must NEVER be safely dropped into NEGATED; it must escalate to POSITIVE or UNCERTAIN.
        """
        by_concept: Dict[str, List[ExtractedEntity]] = {}
        for ent in entities:
            by_concept.setdefault(ent.canonical_concept, []).append(ent)

        reconciled: List[ExtractedEntity] = []
        for concept, ent_list in by_concept.items():
            if len(ent_list) == 1:
                reconciled.append(ent_list[0])
                continue

            statuses = {e.status for e in ent_list}
            if EntityStatus.POSITIVE in statuses and EntityStatus.NEGATED in statuses:
                # Contradiction detected!
                first = ent_list[0]
                safe_status = EntityStatus.POSITIVE if first.level_1_relevant else EntityStatus.UNCERTAIN
                reconciled.append(
                    ExtractedEntity(
                        canonical_concept=first.canonical_concept,
                        matched_term=first.matched_term,
                        status=safe_status,
                        match_type=first.match_type,
                        fuzzy_score=first.fuzzy_score,
                        level_1_relevant=first.level_1_relevant,
                        is_ambiguous=True,
                        ambiguity_flag="Contradictory positive and negative assertions in presentation.",
                        review_status=first.review_status,
                        start_char=first.start_char,
                        end_char=first.end_char,
                    )
                )
            else:
                reconciled.extend(ent_list)

        return reconciled

    def _extract_attributes(self, text: str) -> ExtractedAttributes:
        """Extract onset, duration, severity, modifiers, and age group."""
        # Onset
        onset = None
        if re.search(r"\b(?:sudden|abrupt|suddenly|acute|achanak|ekdam)\b", text):
            onset = "sudden"
        elif re.search(r"\b(?:gradual|slowly|over\s+days|progressive)\b", text):
            onset = "gradual"

        # Duration
        duration = None
        dur_match = re.search(r"\b(?:\d+|a|few|several)\s+(?:minute|min|hour|hr|day|week|month)s?\b", text)
        if dur_match:
            duration = dur_match.group()
        elif re.search(r"\b(?:since\s+yesterday|kal\s+se|aaj\s+se|don\s+divas)\b", text):
            duration = "since yesterday"

        # Severity
        severity = None
        if re.search(r"\b(?:severe|excruciating|worst|unbearable|10/10|khup\s+jast|tez|bahut\s+tez|bohot\s+tez)\b", text):
            severity = "severe"
        elif re.search(r"\b(?:moderate|medium|madhyam)\b", text):
            severity = "moderate"
        elif re.search(r"\b(?:mild|slight|minor|halka|thoda)\b", text):
            severity = "mild"

        # Modifiers
        modifiers: List[str] = []
        modifier_patterns = {
            "crushing": r"\b(?:crushing|heavy|pressure|squeezing)\b",
            "worst_ever": r"\b(?:worst\s+headache\s+of\s+life|worst\s+ever|thunderclap)\b",
            "radiating": r"\b(?:radiating|spreading\s+to\s+arm|jaw\s+pain)\b",
            "breathless": r"\b(?:breathless|gasping|can't\s+talk)\b",
            "tearing": r"\b(?:tearing|ripping)\b",
        }
        for mod_name, pat in modifier_patterns.items():
            if re.search(pat, text):
                modifiers.append(mod_name)

        # Age group
        age_group = None
        if re.search(r"\b(?:baby|infant|toddler|child|kid|pediatric|baccha|chota\s+baccha|baal)\b", text):
            age_group = "pediatric"
        elif re.search(r"\b(?:elderly|senior|old\s+age|grandfather|grandmother|aaji|aajoba|buzurg|vridh)\b", text):
            age_group = "elderly"
        elif re.search(r"\b(?:adult|young\s+adult|man|woman)\b", text):
            age_group = "adult"

        return ExtractedAttributes(
            onset=onset,
            duration=duration,
            severity=severity,
            modifiers=modifiers,
            age_group=age_group,
        )
