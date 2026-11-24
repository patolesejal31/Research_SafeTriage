"""001_initial_schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-11-24

"""
from alembic import op
import sqlalchemy as sa

revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='user'),
        sa.Column('opt_in_store_raw_symptoms', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # 2. assessments table
    op.create_table(
        'assessments',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=True),
        sa.Column('anonymous_session_id', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('final_urgency', sa.Integer(), nullable=True),
        sa.Column('is_uncertain', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('rule_urgency', sa.Integer(), nullable=True),
        sa.Column('ml_urgency', sa.Integer(), nullable=True),
        sa.Column('llm_urgency', sa.Integer(), nullable=True),
        sa.Column('rule_status', sa.String(length=32), nullable=False, server_default='UNAVAILABLE'),
        sa.Column('ml_status', sa.String(length=32), nullable=False, server_default='UNAVAILABLE'),
        sa.Column('llm_status', sa.String(length=32), nullable=False, server_default='UNAVAILABLE'),
        sa.Column('information_incomplete', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('explanation_text', sa.Text(), nullable=False),
        sa.Column('explanation_source', sa.String(length=32), nullable=False, server_default='template'),
        sa.Column('llm_faithfulness_passed', sa.Boolean(), nullable=True),
        sa.Column('llm_provider_label', sa.String(length=64), nullable=True),
        sa.Column('age_years', sa.Float(), nullable=True),
        sa.Column('age_band', sa.String(length=64), nullable=True),
        sa.Column('sex', sa.String(length=32), nullable=True),
        sa.Column('opt_in_raw_symptom_storage', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('raw_symptom_text', sa.Text(), nullable=True),
    )
    op.create_index('ix_assessments_user_id', 'assessments', ['user_id'])
    op.create_index('ix_assessments_anonymous_session_id', 'assessments', ['anonymous_session_id'])

    # 3. structured_symptoms table
    op.create_table(
        'structured_symptoms',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('assessment_id', sa.String(length=36), sa.ForeignKey('assessments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('canonical_concept', sa.String(length=128), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('match_type', sa.String(length=32), nullable=False),
        sa.Column('fuzzy_score', sa.Float(), nullable=True),
        sa.Column('onset', sa.String(length=64), nullable=True),
        sa.Column('severity', sa.String(length=64), nullable=True),
        sa.Column('duration', sa.String(length=64), nullable=True),
    )
    op.create_index('ix_structured_symptoms_assessment_id', 'structured_symptoms', ['assessment_id'])

    # 4. rule_triggers table
    op.create_table(
        'rule_triggers',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('assessment_id', sa.String(length=36), sa.ForeignKey('assessments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('rule_id', sa.String(length=64), nullable=False),
        sa.Column('rule_name', sa.String(length=255), nullable=False),
        sa.Column('rule_level', sa.Integer(), nullable=False),
        sa.Column('specialty', sa.String(length=64), nullable=False),
        sa.Column('review_status', sa.String(length=32), nullable=False, server_default='UNVERIFIED'),
    )
    op.create_index('ix_rule_triggers_assessment_id', 'rule_triggers', ['assessment_id'])

    # 5. override_logs table
    op.create_table(
        'override_logs',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('assessment_id', sa.String(length=36), sa.ForeignKey('assessments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('component', sa.String(length=32), nullable=False),
        sa.Column('from_level', sa.Integer(), nullable=True),
        sa.Column('to_level', sa.Integer(), nullable=True),
        sa.Column('reason', sa.String(length=255), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_override_logs_assessment_id', 'override_logs', ['assessment_id'])

    # 6. evaluation_runs table
    op.create_table(
        'evaluation_runs',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('created_by', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('run_name', sa.String(length=128), nullable=False),
        sa.Column('dataset_name', sa.String(length=128), nullable=False),
        sa.Column('dataset_version', sa.String(length=64), nullable=False),
        sa.Column('split', sa.String(length=32), nullable=False, server_default='test'),
        sa.Column('total_cases', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='completed'),
        sa.Column('metrics_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_evaluation_runs_created_by', 'evaluation_runs', ['created_by'])

    # 7. evaluation_predictions table
    op.create_table(
        'evaluation_predictions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('run_id', sa.String(length=36), sa.ForeignKey('evaluation_runs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('case_id', sa.String(length=64), nullable=False),
        sa.Column('ground_truth', sa.Integer(), nullable=False),
        sa.Column('predicted_rule', sa.Integer(), nullable=True),
        sa.Column('predicted_ml', sa.Integer(), nullable=True),
        sa.Column('predicted_llm', sa.Integer(), nullable=True),
        sa.Column('predicted_final', sa.Integer(), nullable=True),
        sa.Column('rule_status', sa.String(length=32), nullable=False, server_default='OK'),
        sa.Column('ml_status', sa.String(length=32), nullable=False, server_default='OK'),
        sa.Column('llm_status', sa.String(length=32), nullable=False, server_default='OK'),
    )
    op.create_index('ix_evaluation_predictions_run_id', 'evaluation_predictions', ['run_id'])

    # 8. experiment_configs table
    op.create_table(
        'experiment_configs',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('config_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_experiment_configs_name', 'experiment_configs', ['name'], unique=True)


def downgrade() -> None:
    op.drop_table('experiment_configs')
    op.drop_table('evaluation_predictions')
    op.drop_table('evaluation_runs')
    op.drop_table('override_logs')
    op.drop_table('rule_triggers')
    op.drop_table('structured_symptoms')
    op.drop_table('assessments')
    op.drop_table('users')
