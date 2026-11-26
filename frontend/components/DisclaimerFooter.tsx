import React from "react";
import { ShieldAlert, PhoneCall } from "lucide-react";

export function DisclaimerFooter() {
  return (
    <footer aria-label="Clinical Disclaimer and Regulatory Boundaries" className="bg-gray-900 text-gray-300 py-8 px-4 border-t border-gray-800 text-xs">
      <div className="max-w-7xl mx-auto space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-gray-800 pb-4">
          <div className="flex items-center space-x-2 text-white font-bold text-sm">
            <ShieldAlert className="w-5 h-5 text-amber-400" aria-hidden="true" />
            <span>SafeTriage — Clinical Informatics Research Prototype</span>
          </div>

          <div className="flex items-center space-x-3 text-white">
            <span className="text-gray-400">Emergency Hotlines (India):</span>
            <a href="tel:112" className="inline-flex items-center px-2.5 py-1 bg-red-600 rounded text-xs font-bold hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-white">
              <PhoneCall className="w-3 h-3 mr-1" />
              112 (National)
            </a>
            <a href="tel:108" className="inline-flex items-center px-2.5 py-1 bg-red-700 rounded text-xs font-bold hover:bg-red-800 focus:outline-none focus:ring-2 focus:ring-white">
              <PhoneCall className="w-3 h-3 mr-1" />
              108 (Ambulance)
            </a>
          </div>
        </div>

        <div className="text-gray-400 leading-relaxed space-y-1.5">
          <p>
            <strong>NON-DIAGNOSTIC & NON-PRESCRIPTIVE MANDATE:</strong> SafeTriage is an MCA dissertation research
            prototype designed to evaluate hybrid deterministic rule engine + NLP + LLM urgency triage stratification.
            It does not provide clinical diagnoses, does not prescribe medications or dosages, and is not a medical device.
          </p>
          <p>
            Deterministic rules are derived from published guidelines (NICE NG143, IAP, AHA/ACC) but are developer-assigned
            and marked <strong>UNVERIFIED</strong> pending formal clinical panel sign-off.
          </p>
          <p>
            Privacy Notice: Guest assessments are automatically purged after 24 hours. Raw symptom text is never stored
            unless explicit opt-in is granted.
          </p>
        </div>
      </div>
    </footer>
  );
}
