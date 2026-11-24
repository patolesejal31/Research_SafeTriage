"""SafeTriage ML Baseline Service.

Implements a TF-IDF (1-3 gram) + Logistic Regression classifier.

Design rules:
- Uses structured extracted symptoms (canonical concepts) as features, NOT raw symptom text.
- If no trained model file exists: ml_status=UNAVAILABLE (never fake a prediction).
- Model version is tracked via SHA-256 hash of the saved model bytes.
- Vectorizer and model are saved/loaded together (single .joblib file).
- This is a RESEARCH PROTOTYPE BASELINE, not a clinically validated model.
  It may only ESCALATE; the invariant enforces this.
- Do NOT report accuracy until Phase 6 dataset + evaluation are complete.
- Standalone function predict_rule_only(), predict_ml_only(), predict_llm_only()
  are exposed for independent baseline evaluation in Phase 7.

IMPORTANT:
- Never log symptom text that passes through this service.
- ml_status=UNAVAILABLE when model not found or not trained yet.
"""

from __future__ import annotations

import hashlib
import logging
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.core.urgency import Urgency
from app.triage.invariant import ComponentResult, ComponentStatus, ComponentType
from app.triage.nlp_extractor import EntityStatus, ExtractionResult

logger = logging.getLogger("safetriage.services.ml_baseline")

DEFAULT_MODEL_PATH = Path(__file__).parent.parent.parent / "models" / "ml_baseline.pkl"


@dataclass(frozen=True)
class MLPrediction:
    """Output from the ML baseline predictor."""
    component_result: ComponentResult
    model_version_hash: Optional[str]
    # Probabilities per class (1-4), None if unavailable
    class_probabilities: Optional[Dict[int, float]] = None


def _extract_feature_string(extraction: ExtractionResult) -> str:
    """Convert structured extraction to a feature string.

    Uses canonical concepts and attributes ONLY, NOT raw symptom text.
    This is what goes into the vectorizer — never the user's words.
    """
    parts: List[str] = []

    for ent in extraction.entities:
        if ent.status == EntityStatus.POSITIVE:
            parts.append(f"POS_{ent.canonical_concept}")
        elif ent.status == EntityStatus.NEGATED:
            parts.append(f"NEG_{ent.canonical_concept}")
        elif ent.status == EntityStatus.UNCERTAIN:
            parts.append(f"UNC_{ent.canonical_concept}")
        # HISTORICAL and THIRD_PARTY included but tagged
        elif ent.status == EntityStatus.HISTORICAL:
            parts.append(f"HIST_{ent.canonical_concept}")
        elif ent.status == EntityStatus.THIRD_PARTY:
            parts.append(f"THIRD_{ent.canonical_concept}")

    # Append structured attributes
    if extraction.attributes.onset:
        parts.append(f"ONSET_{extraction.attributes.onset}")
    if extraction.attributes.severity:
        parts.append(f"SEV_{extraction.attributes.severity}")
    if extraction.attributes.duration:
        parts.append(f"DUR_present")
    for mod in extraction.attributes.modifiers:
        parts.append(f"MOD_{mod}")

    return " ".join(parts) if parts else "NO_FEATURES"


def _compute_hash(model_bytes: bytes) -> str:
    """Compute SHA-256 hash of serialized model bytes for version tracking."""
    return hashlib.sha256(model_bytes).hexdigest()[:16]


class MLBaseline:
    """TF-IDF + Logistic Regression triage urgency predictor.

    Training requires a dataset (produced in Phase 6). Until trained,
    all predictions return ml_status=UNAVAILABLE.
    """

    def __init__(self, model_path: Optional[Path] = None):
        self.model_path = model_path or DEFAULT_MODEL_PATH
        self._model: Optional[Any] = None
        self._vectorizer: Optional[Any] = None
        self._model_hash: Optional[str] = None
        self._load_model()

    def _load_model(self) -> None:
        """Load model from disk. If not found or corrupted, stays UNAVAILABLE."""
        if not self.model_path.exists():
            logger.info("ML baseline model not found at %s — ml_status=UNAVAILABLE", self.model_path)
            return

        try:
            with open(self.model_path, "rb") as f:
                model_bytes = f.read()
            bundle = pickle.loads(model_bytes)  # noqa: S301
            self._vectorizer = bundle["vectorizer"]
            self._model = bundle["model"]
            self._model_hash = _compute_hash(model_bytes)
            logger.info("ML baseline loaded — version hash: %s", self._model_hash)
        except Exception:
            logger.warning("ML baseline model failed to load — ml_status=UNAVAILABLE")
            self._model = None
            self._vectorizer = None

    def is_available(self) -> bool:
        """Return True if the model is loaded and ready to predict."""
        return self._model is not None and self._vectorizer is not None

    def predict(self, extraction: ExtractionResult) -> MLPrediction:
        """Predict urgency level from structured extraction result.

        Returns ComponentStatus.UNAVAILABLE if no model is loaded.
        Never raises; always returns a typed MLPrediction.
        """
        if not self.is_available():
            return MLPrediction(
                component_result=ComponentResult(
                    component=ComponentType.ML,
                    status=ComponentStatus.UNAVAILABLE,
                    model_name="ml_baseline_logreg",
                ),
                model_version_hash=None,
            )

        try:
            feature_string = _extract_feature_string(extraction)
            X = self._vectorizer.transform([feature_string])
            pred_class = int(self._model.predict(X)[0])
            proba = self._model.predict_proba(X)[0]
            classes = [int(c) for c in self._model.classes_]
            class_probs = dict(zip(classes, [float(p) for p in proba]))

            # Validate the predicted class
            if pred_class not in (1, 2, 3, 4):
                logger.warning("ML produced out-of-range class %d — ml_status=INVALID", pred_class)
                return MLPrediction(
                    component_result=ComponentResult(
                        component=ComponentType.ML,
                        status=ComponentStatus.INVALID,
                        model_name="ml_baseline_logreg",
                    ),
                    model_version_hash=self._model_hash,
                )

            urgency = Urgency(pred_class)
            return MLPrediction(
                component_result=ComponentResult(
                    component=ComponentType.ML,
                    status=ComponentStatus.OK,
                    level=urgency,
                    model_name="ml_baseline_logreg",
                ),
                model_version_hash=self._model_hash,
                class_probabilities=class_probs,
            )

        except Exception:
            logger.exception("ML baseline prediction failed — ml_status=ERROR")
            return MLPrediction(
                component_result=ComponentResult(
                    component=ComponentType.ML,
                    status=ComponentStatus.ERROR,
                    model_name="ml_baseline_logreg",
                ),
                model_version_hash=self._model_hash,
            )

    def train(
        self,
        feature_strings: List[str],
        labels: List[int],
        save_path: Optional[Path] = None,
    ) -> str:
        """Train the TF-IDF + Logistic Regression model.

        Args:
            feature_strings: Structured feature strings (from _extract_feature_string).
            labels: Integer urgency labels (1-4).
            save_path: Where to save the trained model bundle.

        Returns:
            SHA-256 version hash of the saved model.

        Raises:
            ValueError: If labels contain values outside 1-4.
        """
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression

        invalid_labels = [l for l in labels if l not in (1, 2, 3, 4)]
        if invalid_labels:
            raise ValueError(f"Labels must be 1-4; found invalid: {invalid_labels}")

        vectorizer = TfidfVectorizer(
            analyzer="word",
            ngram_range=(1, 3),
            min_df=1,
            max_features=10000,
        )
        X = vectorizer.fit_transform(feature_strings)
        model = LogisticRegression(
            max_iter=1000,
            C=1.0,
            solver="lbfgs",
            random_state=42,
        )
        model.fit(X, labels)

        bundle = {"vectorizer": vectorizer, "model": model}
        model_bytes = pickle.dumps(bundle)
        version_hash = _compute_hash(model_bytes)

        target = save_path or self.model_path
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "wb") as f:
            f.write(model_bytes)

        logger.info("ML baseline trained and saved to %s — hash %s", target, version_hash)

        # Reload into self
        self._vectorizer = vectorizer
        self._model = model
        self._model_hash = version_hash
        return version_hash
