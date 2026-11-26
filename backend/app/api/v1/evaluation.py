"""Evaluation API endpoints (Researcher role only)."""

import json
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.core.urgency import Urgency
from app.db.models import EvaluationPrediction, EvaluationRun, User
from app.db.session import get_db
from app.schemas.evaluation import (
    EvaluationRunCreateRequest,
    EvaluationRunResponse,
)
from app.triage.pipeline import TriagePipeline

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])


@router.post(
    "/run",
    response_model=EvaluationRunResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Trigger an evaluation run on a dataset split (Researcher only)",
)
def create_evaluation_run(
    req: EvaluationRunCreateRequest,
    current_user: User = Depends(require_role("researcher")),
    db: Session = Depends(get_db),
):
    """Execute evaluation across dataset test cases and record metrics.

    Uses standalone evaluation methods (predict_rule_only, predict_ml_only, predict_llm_only).
    Restricted to researcher role (403 for user role).
    """
    fixture_path = Path(__file__).parent.parent.parent.parent.parent / "datasets" / "test_fixture" / "fixture.json"

    cases = []
    if fixture_path.exists():
        try:
            with open(fixture_path, "r", encoding="utf-8") as f:
                cases = json.load(f)
        except Exception:
            pass

    pipeline = TriagePipeline()
    total = len(cases)
    correct_final = 0
    correct_rule = 0
    undertriaged = 0
    overtriaged = 0

    predictions_to_save: List[EvaluationPrediction] = []

    # Run predictions across cases
    for case in cases:
        case_id = case.get("case_id", "unknown")
        gt_raw = case.get("ground_truth_urgency")
        gt = int(gt_raw) if gt_raw in (1, 2, 3, 4) else 4
        text = case.get("symptoms_text", "")

        # Standalone predictions
        rule_inv = pipeline.predict_rule_only(text)
        ml_inv = pipeline.predict_ml_only(text)
        llm_inv = pipeline.predict_llm_only(text)
        full_res = pipeline.assess(text)

        rule_pred = int(rule_inv.final_urgency) if isinstance(rule_inv.final_urgency, Urgency) else None
        ml_pred = int(ml_inv.final_urgency) if isinstance(ml_inv.final_urgency, Urgency) else None
        llm_pred = int(llm_inv.final_urgency) if isinstance(llm_inv.final_urgency, Urgency) else None
        final_pred = int(full_res.final_urgency) if isinstance(full_res.final_urgency, Urgency) else None

        if final_pred == gt:
            correct_final += 1
        elif final_pred is not None and final_pred > gt:
            # Predicted less urgent than truth -> undertriaged (dangerous)
            undertriaged += 1
        elif final_pred is not None and final_pred < gt:
            # Predicted more urgent than truth -> overtriaged (safe)
            overtriaged += 1

        if rule_pred == gt:
            correct_rule += 1

        pred_record = EvaluationPrediction(
            case_id=case_id,
            ground_truth=gt,
            predicted_rule=rule_pred,
            predicted_ml=ml_pred,
            predicted_llm=llm_pred,
            predicted_final=final_pred,
            rule_status=rule_inv.component_statuses.get(pipeline.engine.__class__.__name__, "OK") if hasattr(rule_inv, "component_statuses") else "OK",
            ml_status=full_res.ml_status.value,
            llm_status=full_res.llm_status.value,
        )
        predictions_to_save.append(pred_record)

    accuracy = (correct_final / total) if total > 0 else 0.0
    rule_accuracy = (correct_rule / total) if total > 0 else 0.0
    undertriage_rate = (undertriaged / total) if total > 0 else 0.0
    overtriage_rate = (overtriaged / total) if total > 0 else 0.0

    metrics = {
        "total_cases": total,
        "correct_predictions": correct_final,
        "accuracy": round(accuracy, 4),
        "rule_only_accuracy": round(rule_accuracy, 4),
        "undertriage_rate": round(undertriage_rate, 4),
        "overtriage_rate": round(overtriage_rate, 4),
    }

    eval_run = EvaluationRun(
        created_by=current_user.id,
        run_name=req.run_name,
        dataset_name=req.dataset_name,
        dataset_version=req.dataset_version,
        split=req.split,
        total_cases=total,
        status="completed",
        metrics_json=json.dumps(metrics),
    )
    db.add(eval_run)
    db.flush()

    for p in predictions_to_save:
        p.run_id = eval_run.id
        db.add(p)

    db.commit()
    db.refresh(eval_run)

    return EvaluationRunResponse(
        id=eval_run.id,
        run_name=eval_run.run_name,
        dataset_name=eval_run.dataset_name,
        dataset_version=eval_run.dataset_version,
        split=eval_run.split,
        total_cases=eval_run.total_cases,
        status=eval_run.status,
        metrics=metrics,
        created_at=eval_run.created_at,
    )


@router.get(
    "/runs",
    response_model=List[EvaluationRunResponse],
    summary="List all evaluation runs (Researcher only)",
)
def list_evaluation_runs(
    current_user: User = Depends(require_role("researcher")),
    db: Session = Depends(get_db),
):
    """Retrieve history of evaluation runs."""
    runs = db.query(EvaluationRun).order_by(EvaluationRun.created_at.desc()).all()
    results = []
    for r in runs:
        m = json.loads(r.metrics_json) if r.metrics_json else None
        results.append(
            EvaluationRunResponse(
                id=r.id,
                run_name=r.run_name,
                dataset_name=r.dataset_name,
                dataset_version=r.dataset_version,
                split=r.split,
                total_cases=r.total_cases,
                status=r.status,
                metrics=m,
                created_at=r.created_at,
            )
        )
    return results


@router.get(
    "/export",
    summary="Export evaluation runs and predictions as structured JSON (Researcher only)",
)
def export_evaluations(
    run_id: Optional[str] = Query(None, description="Optional specific run ID to export"),
    current_user: User = Depends(require_role("researcher")),
    db: Session = Depends(get_db),
):
    """Export complete benchmark results for dissertation analysis and charts."""
    query = db.query(EvaluationRun)
    if run_id:
        query = query.filter(EvaluationRun.id == run_id)

    runs = query.all()
    export_data = []
    for r in runs:
        m = json.loads(r.metrics_json) if r.metrics_json else None
        preds = [
            {
                "case_id": p.case_id,
                "ground_truth": p.ground_truth,
                "predicted_rule": p.predicted_rule,
                "predicted_ml": p.predicted_ml,
                "predicted_llm": p.predicted_llm,
                "predicted_final": p.predicted_final,
            }
            for p in r.predictions
        ]
        export_data.append(
            {
                "run_id": r.id,
                "run_name": r.run_name,
                "dataset_name": r.dataset_name,
                "split": r.split,
                "metrics": m,
                "predictions": preds,
            }
        )

    return {"evaluation_runs": export_data}
