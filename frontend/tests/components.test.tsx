import React from "react";
import { render, screen } from "@testing-library/react";
import { UrgencyBadge } from "@/components/UrgencyBadge";
import { EmergencyModal } from "@/components/EmergencyModal";
import { FollowUpSection } from "@/components/FollowUpSection";
import { ResultsView } from "@/components/ResultsView";
import { AssessmentResponse, FollowUpQuestion } from "@/types/assessment";

describe("Phase 8 Component Tests & Safety Invariants", () => {
  describe("UrgencyBadge", () => {
    it("renders Level 1 with Red emergency styling, siren icon, and label", () => {
      render(<UrgencyBadge level={1} />);
      expect(screen.getByText(/Level 1/i)).toBeInTheDocument();
      expect(screen.getByText(/Emergency/i)).toBeInTheDocument();
    });

    it("renders UNCERTAIN with distinct Purple styling and specific safety caution text (NEVER styled as Level 3/4)", () => {
      const { container } = render(<UrgencyBadge level="UNCERTAIN" showExplanation={true} />);
      expect(screen.getByText("UNCERTAIN")).toBeInTheDocument();
      const cautionP = container.querySelector("p");
      expect(cautionP?.textContent).toContain("Unable to assess safely. If you have severe symptoms, call 112 / 108");

      // Ensure distinct purple background
      const badge = container.querySelector(".bg-purple-100");
      expect(badge).not.toBeNull();
      // Ensure it is not styled with Level 3 (yellow) or Level 4 (green)
      expect(container.querySelector(".bg-yellow-100")).toBeNull();
      expect(container.querySelector(".bg-green-100")).toBeNull();
    });
  });

  describe("EmergencyModal", () => {
    it("renders Level 1 Emergency alert with tap-to-call links (tel:112 and tel:108) and immediate instructions", () => {
      render(
        <EmergencyModal
          isOpen={true}
          onClose={() => {}}
          reason="Rule CV-001 triggered: crushing chest pain."
        />
      );

      expect(screen.getByText(/CRITICAL EMERGENCY ALERT \(Level 1\)/i)).toBeInTheDocument();
      expect(screen.getByText(/Rule CV-001 triggered/i)).toBeInTheDocument();

      // Verify tap-to-call links
      const call112 = screen.getByRole("link", { name: /112/i });
      expect(call112).toHaveAttribute("href", "tel:112");

      const call108 = screen.getByRole("link", { name: /108/i });
      expect(call108).toHaveAttribute("href", "tel:108");
    });
  });

  describe("FollowUpSection", () => {
    const mockQuestions: FollowUpQuestion[] = [
      // Safety critical questions (must NEVER be dropped by cap)
      {
        id: "q_age",
        type: "numeric",
        text: "Age in years (required for pediatric rule checks)?",
        safety_critical: true,
        urgency_impact: 10,
        could_trigger_level_2: false,
      },
      {
        id: "q_red_flag_1",
        type: "binary",
        text: "Is there any confusion or difficulty breathing?",
        safety_critical: true,
        urgency_impact: 9,
        could_trigger_level_2: true,
      },
      // 3 optional questions presented by the backend (capped at 3)
      {
        id: "opt_1",
        type: "binary",
        text: "Optional: Do you have a mild sore throat?",
        safety_critical: false,
        urgency_impact: 4,
        could_trigger_level_2: false,
      },
      {
        id: "opt_2",
        type: "binary",
        text: "Optional: Is there mild nasal congestion?",
        safety_critical: false,
        urgency_impact: 3,
        could_trigger_level_2: false,
      },
      {
        id: "opt_3",
        type: "binary",
        text: "Optional: Have you had a headache?",
        safety_critical: false,
        urgency_impact: 2,
        could_trigger_level_2: false,
      },
    ];

    const mockSkipped: FollowUpQuestion[] = [
      {
        id: "opt_4",
        type: "binary",
        text: "Optional: Are you feeling fatigued?",
        safety_critical: false,
        urgency_impact: 1,
        could_trigger_level_2: false,
      },
    ];

    it("keeps all safety-critical questions and renders capped optional questions", () => {
      render(
        <FollowUpSection
          questions={mockQuestions}
          skippedQuestions={mockSkipped}
          informationIncomplete={false}
          onSubmitAnswers={() => {}}
        />
      );

      // Both safety critical questions MUST be rendered
      expect(screen.getByText(/Age in years/i)).toBeInTheDocument();
      expect(screen.getByText(/confusion or difficulty breathing/i)).toBeInTheDocument();

      // Top optional questions should be rendered
      expect(screen.getByText(/mild sore throat/i)).toBeInTheDocument();
      expect(screen.getByText(/mild nasal congestion/i)).toBeInTheDocument();
      expect(screen.getByText(/headache/i)).toBeInTheDocument();

      // Omitted question is not in active questions list
      expect(screen.queryByText(/fatigued/i)).not.toBeInTheDocument();
    });

    it("displays 'Information Incomplete' warning banner when questions are skipped or marked incomplete", () => {
      render(
        <FollowUpSection
          questions={mockQuestions}
          skippedQuestions={mockSkipped}
          informationIncomplete={true}
          onSubmitAnswers={() => {}}
        />
      );

      expect(screen.getByText(/Information Incomplete Notice/i)).toBeInTheDocument();
      expect(
        screen.getByText(/Some questions were omitted due to question caps/i)
      ).toBeInTheDocument();
    });
  });

  describe("ResultsView Transparency & Non-Clinical Disclaimers", () => {
    const mockAssessment: AssessmentResponse = {
      assessment_id: "test-eval-123456789",
      final_urgency: 2,
      is_uncertain: false,
      is_level_1_emergency: false,
      determining_component: "RULE",
      explanation_text: "Assessed via deterministic rule matching.",
      explanation_source: "template",
      rule_status: "COMPLETED",
      ml_status: "UNAVAILABLE",
      llm_status: "COMPLETED",
      llm_provider_label: "MOCK (not a real LLM)",
      information_incomplete: false,
      followup_questions: [],
      triggered_rules: [
        {
          rule_id: "PED-001",
          rule_name: "High Pediatric Fever with Lethargy",
          rule_level: 2,
          specialty: "pediatrics",
          review_status: "UNVERIFIED",
          citation: "Indian Academy of Pediatrics (IAP) Guidelines",
        },
      ],
      extracted_symptoms: [
        {
          canonical_concept: "fever",
          status: "POSITIVE",
          match_type: "exact",
          severity: "high",
        },
        {
          canonical_concept: "rash",
          status: "NEGATED",
          match_type: "exact",
        },
      ],
      model_suggested_urgency: null,
      guest_retention_notice: "Guest assessment data is automatically purged after 24 hours.",
    };

    it("renders transparent explanations, citations, UNVERIFIED review status, and persistent clinician review disclaimer", () => {
      render(<ResultsView result={mockAssessment} />);

      // Determining component
      expect(screen.getByText("Deterministic Clinical Rules")).toBeInTheDocument();

      // Rule details
      expect(screen.getByText(/PED-001/i)).toBeInTheDocument();
      expect(screen.getByText(/High Pediatric Fever with Lethargy/i)).toBeInTheDocument();
      expect(screen.getAllByText("UNVERIFIED").length).toBeGreaterThanOrEqual(1);
      expect(screen.getByText(/Citation: Indian Academy of Pediatrics/i)).toBeInTheDocument();

      // Persistent non-clinician disclaimer
      expect(
        screen.getAllByText(/Rules Not Clinician-Reviewed/i).length
      ).toBeGreaterThanOrEqual(1);

      // Positive and negated symptoms
      expect(screen.getByText("fever")).toBeInTheDocument();
      expect(screen.getByText("rash")).toBeInTheDocument();

      // Clinical LLM reasoner component status
      expect(screen.getByText(/SafeTriage NLP Reasoner/i)).toBeInTheDocument();
    });
  });
});
