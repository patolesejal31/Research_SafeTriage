/**
 * SafeTriage TypeScript interfaces and types.
 * Strictly non-diagnostic and non-prescriptive.
 */

export type UrgencyLevel = 1 | 2 | 3 | 4;

export type ComponentStatus =
  | "OK"
  | "NO_MATCH"
  | "UNAVAILABLE"
  | "TIMEOUT"
  | "INVALID"
  | "ERROR";

export type DeterminingComponent = "RULE" | "ML" | "LLM" | "SAFETY_NET";

export interface FollowUpQuestion {
  id: string;
  type: "binary" | "single_choice" | "numeric" | "duration";
  text: string;
  safety_critical: boolean;
  urgency_impact: number;
  could_trigger_level_2: boolean;
  options?: string[];
  free_numeric?: boolean;
  context_concept?: string;
}

export interface FollowUpAnswer {
  question_id: string;
  answer_value: string | number | boolean;
}

export interface RuleTrigger {
  rule_id: string;
  rule_name: string;
  rule_level: number;
  specialty: string;
  review_status: string;
  citation?: string;
}

export interface StructuredSymptom {
  canonical_concept: string;
  status: "POSITIVE" | "NEGATED" | "UNCERTAIN" | "HISTORICAL" | "THIRD_PARTY";
  match_type: "exact" | "variant" | "fuzzy";
  fuzzy_score?: number;
  onset?: string;
  severity?: string;
  duration?: string;
}

export interface AssessmentResponse {
  id?: string;
  assessment_id: string;
  final_urgency: UrgencyLevel | null;
  is_uncertain: boolean;
  is_level_1_emergency: boolean;
  determining_component?: DeterminingComponent | string;
  explanation_text: string;
  explanation_source: string;
  rule_status: ComponentStatus;
  ml_status: ComponentStatus;
  llm_status: ComponentStatus;
  llm_provider_label?: string;
  information_incomplete: boolean;
  followup_questions: FollowUpQuestion[];
  skipped_followup_questions?: FollowUpQuestion[];
  triggered_rules: RuleTrigger[];
  extracted_symptoms: StructuredSymptom[];
  model_suggested_urgency?: UrgencyLevel | null;
  model_suggestion_label?: string;
  guest_retention_notice?: string;
  created_at?: string;
}

export interface AssessmentCreateRequest {
  symptoms_text: string;
  age_years?: number;
  age_months?: number;
  sex?: string;
  opt_in_store_raw_symptoms?: boolean;
}

export interface ReassessRequest {
  original_text: string;
  answers: FollowUpAnswer[];
}

export interface UserProfile {
  id: string;
  email: string;
  role: "user" | "researcher";
  opt_in_store_raw_symptoms?: boolean;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
  user: UserProfile;
}
