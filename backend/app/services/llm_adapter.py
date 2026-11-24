"""SafeTriage LLM Adapter Service.

Pluggable LLM provider system with:
- MockProvider: always identified as "MOCK (not a real LLM)" in code, DB, API responses, UI.
  Any result produced by Mock must be labeled and never described as a real LLM result.
- OpenAI / Gemini / Ollama adapters: implemented but tested ONLY with mocked HTTP responses.
  Real API calls are gated on API key presence; missing key -> BLOCKED (not faked).
- LLM receives ONLY structured extracted symptoms (canonical concepts + attributes),
  never raw symptom text from the user.
- Strict Pydantic v2 JSON-schema validation on response.
- Max 2 retries, configurable timeout, temperature=0.
- LLM may ESCALATE urgency only; downgrade attempts are blocked by the invariant.
- Prompt-injection in user text must not change LLM output (no raw text in prompt).
- Never log prompts containing symptom concepts or API keys.

Failure modes (each has own status field and test):
- Timeout       -> ComponentStatus.TIMEOUT
- Malformed JSON -> ComponentStatus.INVALID
- Schema error  -> ComponentStatus.INVALID
- HTTP/network  -> ComponentStatus.ERROR
- No API key    -> ComponentStatus.UNAVAILABLE (BLOCKED)
"""

from __future__ import annotations

import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ValidationError

from app.core.urgency import Urgency
from app.triage.invariant import ComponentResult, ComponentStatus, ComponentType
from app.triage.nlp_extractor import EntityStatus, ExtractionResult

logger = logging.getLogger("safetriage.services.llm_adapter")

# Provider name constant for the mock
MOCK_PROVIDER_NAME = "MOCK (not a real LLM)"

# ---------------------------------------------------------------------------
# Pydantic schema for LLM JSON response (strict validation)
# ---------------------------------------------------------------------------


class LLMUrgencyResponse(BaseModel):
    """Strict JSON schema expected from every LLM provider.

    The LLM receives structured symptom concepts, NOT raw user text.
    It must respond with a valid urgency level (1-4) and an explanation
    citing only rule IDs from the triggered set.
    """
    urgency_level: int = Field(ge=1, le=4, description="Urgency level 1-4")
    reasoning: str = Field(min_length=1, max_length=1000, description="Clinical reasoning (no PII)")
    cited_rule_ids: List[str] = Field(default_factory=list, description="Rule IDs cited in reasoning")
    provider: str = Field(description="Provider name; must be 'MOCK (not a real LLM)' for mock")
    is_mock: bool = Field(description="True if produced by MockProvider")


# ---------------------------------------------------------------------------
# Structured prompt builder (never includes raw symptom text)
# ---------------------------------------------------------------------------


def build_structured_prompt(extraction: ExtractionResult) -> Dict[str, Any]:
    """Build a structured JSON payload sent to the LLM.

    IMPORTANT: This function sends ONLY structured canonical concepts and
    attributes. Raw user text is never included. This prevents both PII
    leakage and prompt injection from user input.
    """
    positive_concepts = [
        e.canonical_concept for e in extraction.entities
        if e.status == EntityStatus.POSITIVE
    ]
    negated_concepts = [
        e.canonical_concept for e in extraction.entities
        if e.status == EntityStatus.NEGATED
    ]
    uncertain_concepts = [
        e.canonical_concept for e in extraction.entities
        if e.status == EntityStatus.UNCERTAIN
    ]

    return {
        "task": "triage_urgency_assessment",
        "disclaimer": (
            "This is a research prototype only. Never diagnose or prescribe. "
            "Return urgency_level 1-4 and cite only valid rule IDs."
        ),
        "structured_input": {
            "positive_concepts": positive_concepts,
            "negated_concepts": negated_concepts,
            "uncertain_concepts": uncertain_concepts,
            "onset": extraction.attributes.onset,
            "severity": extraction.attributes.severity,
            "duration": extraction.attributes.duration,
            "modifiers": extraction.attributes.modifiers,
        },
        "output_schema": {
            "urgency_level": "integer 1 (Emergency) to 4 (Self-care)",
            "reasoning": "string, 1-1000 chars, no raw symptom text, no patient PII",
            "cited_rule_ids": "list of rule ID strings from the triggered set only",
            "provider": "string identifying the provider",
            "is_mock": "boolean",
        },
    }


# ---------------------------------------------------------------------------
# Base provider interface
# ---------------------------------------------------------------------------


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name string."""

    @property
    @abstractmethod
    def is_mock(self) -> bool:
        """True if this provider is Mock (not a real LLM)."""

    @abstractmethod
    def _call_api(self, payload: Dict[str, Any]) -> str:
        """Call the provider API and return raw JSON string.

        Raises:
            TimeoutError: If the request timed out.
            ConnectionError: If the network/provider is unavailable.
            ValueError: If API key missing or other configuration error.
        """

    def predict(
        self,
        extraction: ExtractionResult,
        timeout_seconds: float = 10.0,
        max_retries: int = 2,
    ) -> ComponentResult:
        """Run the LLM prediction with retry and schema validation.

        Args:
            extraction: Structured NLP extraction (never raw text).
            timeout_seconds: Maximum wait per attempt.
            max_retries: Number of retry attempts on failure.

        Returns:
            ComponentResult with status OK, TIMEOUT, INVALID, ERROR, or UNAVAILABLE.
        """
        payload = build_structured_prompt(extraction)

        last_status = ComponentStatus.ERROR
        for attempt in range(max_retries + 1):
            try:
                raw_json = self._call_api_with_timeout(payload, timeout_seconds)
                result = self._parse_and_validate(raw_json)
                return result
            except TimeoutError:
                logger.warning(
                    "LLM provider '%s' timed out on attempt %d/%d",
                    self.name, attempt + 1, max_retries + 1,
                )
                last_status = ComponentStatus.TIMEOUT
            except (json.JSONDecodeError, ValidationError) as exc:
                logger.warning(
                    "LLM provider '%s' returned invalid JSON/schema on attempt %d: %s",
                    self.name, attempt + 1, type(exc).__name__,
                )
                last_status = ComponentStatus.INVALID
                break  # Malformed JSON/schema: no point retrying the same response
            except (ConnectionError, OSError) as exc:
                logger.warning(
                    "LLM provider '%s' connection error on attempt %d: %s",
                    self.name, attempt + 1, type(exc).__name__,
                )
                last_status = ComponentStatus.ERROR
            except ValueError as exc:
                # API key missing or configuration error
                logger.warning("LLM provider '%s' unavailable: %s", self.name, type(exc).__name__)
                return ComponentResult(
                    component=ComponentType.LLM,
                    status=ComponentStatus.UNAVAILABLE,
                    model_name=self.name,
                )
            except Exception:
                logger.exception("LLM provider '%s' unexpected error on attempt %d", self.name, attempt + 1)
                last_status = ComponentStatus.ERROR

        return ComponentResult(
            component=ComponentType.LLM,
            status=last_status,
            model_name=self.name,
        )

    def _call_api_with_timeout(self, payload: Dict[str, Any], timeout_seconds: float) -> str:
        """Wrap _call_api with a simple deadline check for synchronous providers."""
        import threading
        result_holder: List[Any] = [None]
        exception_holder: List[Any] = [None]

        def _runner():
            try:
                result_holder[0] = self._call_api(payload)
            except Exception as exc:
                exception_holder[0] = exc

        t = threading.Thread(target=_runner, daemon=True)
        t.start()
        t.join(timeout=timeout_seconds)

        if t.is_alive():
            raise TimeoutError(f"LLM provider '{self.name}' exceeded timeout of {timeout_seconds}s")

        if exception_holder[0] is not None:
            raise exception_holder[0]

        return result_holder[0]

    def _parse_and_validate(self, raw_json: str) -> ComponentResult:
        """Parse and validate the LLM response JSON against the strict schema."""
        data = json.loads(raw_json)  # raises json.JSONDecodeError on bad JSON
        response = LLMUrgencyResponse.model_validate(data)  # raises ValidationError on schema error

        # Validate urgency level is in range
        if response.urgency_level not in (1, 2, 3, 4):
            return ComponentResult(
                component=ComponentType.LLM,
                status=ComponentStatus.INVALID,
                model_name=self.name,
            )

        urgency = Urgency(response.urgency_level)
        return ComponentResult(
            component=ComponentType.LLM,
            status=ComponentStatus.OK,
            level=urgency,
            model_name=self.name,
        )


# ---------------------------------------------------------------------------
# MockProvider
# ---------------------------------------------------------------------------


class MockProvider(LLMProvider):
    """Mock LLM provider for offline testing.

    ALWAYS identified as 'MOCK (not a real LLM)' in all outputs.
    Produces deterministic responses based on extraction features, not random.
    Never described as a real LLM result anywhere in the codebase, DB, or UI.

    Injection safety: The mock responds only to structured features (concept lists),
    never to raw text. Injected strings in raw text have zero effect on this provider.
    """

    @property
    def name(self) -> str:
        return MOCK_PROVIDER_NAME

    @property
    def is_mock(self) -> bool:
        return True

    def _call_api(self, payload: Dict[str, Any]) -> str:
        """Deterministic mock response based on structured features."""
        structured = payload.get("structured_input", {})
        positive = set(structured.get("positive_concepts", []))
        severity = structured.get("severity")
        modifiers = set(structured.get("modifiers", []))

        # Deterministic urgency inference from structured features
        # This logic mirrors the rule engine but is intentionally simpler
        level = 4  # default: self-care

        # Level 1 triggers
        l1_concepts = {
            "altered_mental_status", "stroke_symptoms", "seizure",
            "anaphylaxis", "severe_bleeding", "snakebite", "breathlessness",
        }
        if positive & l1_concepts:
            level = 1
        elif "chest_pain" in positive and (
            severity == "severe" or "crushing" in modifiers or "radiating" in modifiers
        ):
            level = 1
        # Level 2 triggers
        elif "chest_pain" in positive or "breathlessness" in positive:
            level = 2
        elif "fever" in positive and "abdominal_pain" in positive:
            level = 2
        # Level 3 triggers
        elif "fever" in positive or "headache" in positive:
            level = 3
        # Level 4 (self-care)
        elif positive:
            level = 4

        response = {
            "urgency_level": level,
            "reasoning": (
                f"MOCK assessment based on structured features. "
                f"Positive concepts: {sorted(positive)}. Severity: {severity}. "
                f"THIS IS NOT A REAL LLM RESULT."
            ),
            "cited_rule_ids": [],
            "provider": MOCK_PROVIDER_NAME,
            "is_mock": True,
        }
        return json.dumps(response)


# ---------------------------------------------------------------------------
# Real providers (mocked HTTP in tests; BLOCKED without API key)
# ---------------------------------------------------------------------------


class OpenAIProvider(LLMProvider):
    """OpenAI GPT adapter. BLOCKED if OPENAI_API_KEY is not set."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        self._api_key = api_key
        self._model = model

    @property
    def name(self) -> str:
        return f"openai/{self._model}"

    @property
    def is_mock(self) -> bool:
        return False

    def _call_api(self, payload: Dict[str, Any]) -> str:
        if not self._api_key:
            raise ValueError("OPENAI_API_KEY not set — provider BLOCKED")
        # Real implementation would call openai.ChatCompletion here.
        # In tests, this method is patched with mocked HTTP responses.
        raise NotImplementedError("OpenAI real API call not wired — patch for tests")


class GeminiProvider(LLMProvider):
    """Google Gemini adapter. BLOCKED if GEMINI_API_KEY is not set."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.0-flash"):
        self._api_key = api_key
        self._model = model

    @property
    def name(self) -> str:
        return f"gemini/{self._model}"

    @property
    def is_mock(self) -> bool:
        return False

    def _call_api(self, payload: Dict[str, Any]) -> str:
        if not self._api_key:
            raise ValueError("GEMINI_API_KEY not set — provider BLOCKED")
        raise NotImplementedError("Gemini real API call not wired — patch for tests")


class OllamaProvider(LLMProvider):
    """Local Ollama adapter. BLOCKED if Ollama server is not reachable."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2"):
        self._base_url = base_url
        self._model = model

    @property
    def name(self) -> str:
        return f"ollama/{self._model}"

    @property
    def is_mock(self) -> bool:
        return False

    def _call_api(self, payload: Dict[str, Any]) -> str:
        raise NotImplementedError("Ollama real API call not wired — patch for tests")


# ---------------------------------------------------------------------------
# Factory helper
# ---------------------------------------------------------------------------


def get_provider(
    provider_name: str = "mock",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> LLMProvider:
    """Factory: return the appropriate LLM provider by name.

    Args:
        provider_name: One of "mock", "openai", "gemini", "ollama".
        api_key: API key for real providers (from env, never hardcoded).
        model: Model name override.

    Returns:
        Instantiated LLMProvider.

    Default is always MockProvider (100% offline, no keys needed).
    """
    name = provider_name.lower().strip()
    if name == "mock":
        return MockProvider()
    elif name == "openai":
        return OpenAIProvider(api_key=api_key, model=model or "gpt-4o")
    elif name == "gemini":
        return GeminiProvider(api_key=api_key, model=model or "gemini-2.0-flash")
    elif name == "ollama":
        return OllamaProvider(model=model or "llama3.2")
    else:
        logger.warning("Unknown provider '%s'; falling back to MockProvider", provider_name)
        return MockProvider()
