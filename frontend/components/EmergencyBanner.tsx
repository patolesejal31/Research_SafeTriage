import React from "react";
import { PhoneCall, AlertTriangle } from "lucide-react";

export function EmergencyBanner() {
  return (
    <div
      role="banner"
      aria-label="Medical Emergency Notice"
      className="bg-red-700 text-white px-4 py-2 text-sm font-medium shadow-md"
    >
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center space-x-2">
          <AlertTriangle className="w-5 h-5 text-amber-300 flex-shrink-0" aria-hidden="true" />
          <span>
            <strong>Medical Emergency?</strong> Do not wait for online triage. Call immediate assistance:
          </span>
        </div>
        <div className="flex items-center space-x-3">
          <a
            href="tel:112"
            className="inline-flex items-center px-3 py-1 bg-white text-red-700 rounded-md font-bold text-xs hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-white transition"
            aria-label="Call National Emergency 112"
          >
            <PhoneCall className="w-3.5 h-3.5 mr-1" aria-hidden="true" />
            112 (National Emergency)
          </a>
          <a
            href="tel:108"
            className="inline-flex items-center px-3 py-1 bg-white text-red-700 rounded-md font-bold text-xs hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-white transition"
            aria-label="Call Ambulance 108"
          >
            <PhoneCall className="w-3.5 h-3.5 mr-1" aria-hidden="true" />
            108 (Ambulance)
          </a>
        </div>
      </div>
    </div>
  );
}
