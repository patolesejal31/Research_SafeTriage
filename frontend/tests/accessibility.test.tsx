import React from "react";
import { render, screen } from "@testing-library/react";
import axe from "axe-core";
import { EmergencyBanner } from "@/components/EmergencyBanner";
import { UrgencyBadge } from "@/components/UrgencyBadge";
import { EmergencyModal } from "@/components/EmergencyModal";
import { FollowUpSection } from "@/components/FollowUpSection";
import { FollowUpQuestion } from "@/types/assessment";

describe("Phase 8 Automated Accessibility (axe-core) Checks", () => {
  it("EmergencyBanner passes axe accessibility checks", async () => {
    const { container } = render(<EmergencyBanner />);
    const results = await axe.run(container, {
      rules: {
        "color-contrast": { enabled: false }, // jsdom doesn't compute layout canvas colors
      },
    });
    if (results.violations.length > 0) {
      console.error("Axe violations for EmergencyBanner:", JSON.stringify(results.violations, null, 2));
    }
    expect(results.violations).toEqual([]);
  });

  it("UrgencyBadge passes axe accessibility checks across all urgency levels", async () => {
    const { container } = render(
      <div>
        <UrgencyBadge level={1} />
        <UrgencyBadge level={2} />
        <UrgencyBadge level={3} />
        <UrgencyBadge level={4} />
        <UrgencyBadge level="UNCERTAIN" />
      </div>
    );
    const results = await axe.run(container, {
      rules: {
        "color-contrast": { enabled: false },
      },
    });
    if (results.violations.length > 0) {
      console.error("Axe violations for UrgencyBadge:", JSON.stringify(results.violations, null, 2));
    }
    expect(results.violations).toEqual([]);
  });

  it("EmergencyModal passes axe accessibility checks", async () => {
    const { container } = render(
      <EmergencyModal isOpen={true} onClose={() => {}} rationale="Severe chest pain and diaphoresis detected." />
    );
    const results = await axe.run(container, {
      rules: {
        "color-contrast": { enabled: false },
      },
    });
    if (results.violations.length > 0) {
      console.error("Axe violations for EmergencyModal:", JSON.stringify(results.violations, null, 2));
    }
    expect(results.violations).toEqual([]);
  });

  it("FollowUpSection passes axe accessibility checks with form labels and ARIA", async () => {
    const questions: FollowUpQuestion[] = [
      {
        id: "q_age",
        type: "numeric",
        text: "What is the patient's age in years?",
        safety_critical: true,
        urgency_impact: 10,
        could_trigger_level_2: false,
      },
      {
        id: "q_chest_pain_radiating",
        type: "binary",
        text: "Does the pain radiate to the jaw or arm?",
        safety_critical: true,
        urgency_impact: 9,
        could_trigger_level_2: true,
      },
      {
        id: "q_cough_duration",
        type: "duration",
        text: "How many days have you had the cough?",
        safety_critical: false,
        urgency_impact: 3,
        could_trigger_level_2: false,
      },
    ];

    const { container } = render(
      <FollowUpSection
        questions={questions}
        answers={{}}
        onAnswerChange={() => {}}
        onSubmit={() => {}}
        onSkipOptional={() => {}}
        hasSkippedQuestions={false}
      />
    );

    const results = await axe.run(container, {
      rules: {
        "color-contrast": { enabled: false },
      },
    });
    if (results.violations.length > 0) {
      console.error("Axe violations for FollowUpSection:", JSON.stringify(results.violations, null, 2));
    }
    expect(results.violations).toEqual([]);
  });
});
